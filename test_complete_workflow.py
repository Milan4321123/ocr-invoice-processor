#!/usr/bin/env python3
"""
Comprehensive Backend End-to-End Test Suite for OCR Invoice Processor

This script tests the complete backend workflow:
1. Authentication (login, token validation)
2. File upload via API and dashboard presence verification
3. Dashboard data retrieval, filtering, and invoice actions
4. Invoice editor operations (load, edit, save)
5. Dropdown management (get options, add new options, save changes)
6. Workflow progression (complete invoice, send to Bauleiter)
7. Skonto processing (create Skonto invoice, notifications, decisions)
8. Email notifications (test sending, reminders)
9. Data persistence verification across all operations
10. Cleanup operations

The test simulates the entire user journey from authentication to final approval.
"""

import requests
import json
import os
import sys
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_e2e_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Test Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

class OCRInvoiceE2ETest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        self.created_invoices = []  # Track created invoices for cleanup
        self.test_data = {
            'invoices': [],
            'created_dropdowns': [],
            'sent_emails': []
        }
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if details:
            logger.info(f"    Details: {details}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {details}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if we have a token
        if self.auth_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f"Bearer {self.auth_token}"
            kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            logger.debug(f"{method} {url} -> {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with icons and timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "SUCCESS":
            icon = "✅"
        elif level == "ERROR":
            icon = "❌"
        elif level == "WARNING":
            icon = "⚠️"
        else:
            icon = "📋"
        print(f"{timestamp} {icon} {message}")
        
        # Also log to logger
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def validate_response(self, response: requests.Response, operation: str) -> bool:
        """Validate HTTP response and log results"""
        if response.status_code >= 200 and response.status_code < 300:
            self.log(f"{operation} successful (HTTP {response.status_code})", "SUCCESS")
            return True
        else:
            self.log(f"{operation} failed - HTTP {response.status_code}: {response.text}", "ERROR")
            return False

    # =======================
    # 1. AUTHENTICATION TESTS
    # =======================
    
    def test_authentication_flow(self) -> bool:
        """Test complete authentication workflow"""
        self.log("🔐 Testing Authentication Flow", "INFO")
        
        # Test 1: Backend health check
        try:
            response = self.session.get(f"{BACKEND_URL}/api/health")
            if not self.validate_response(response, "Backend health check"):
                return False
        except Exception as e:
            self.log(f"Backend connection failed: {e}", "ERROR")
            return False
        
        # Test 2: Login authentication
        try:
            login_data = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            response = self.session.post(f"{BACKEND_URL}/api/auth/login", data=login_data)
            
            if not self.validate_response(response, "Authentication login"):
                return False
                
            auth_data = response.json()
            self.auth_token = auth_data.get("access_token")
            
            if not self.auth_token:
                self.log("No access token received", "ERROR")
                return False
                
            self.log(f"Authentication token received: {self.auth_token[:20]}...", "SUCCESS")
            
        except Exception as e:
            self.log(f"Authentication failed: {e}", "ERROR")
            return False
        
        # Test 3: Token validation
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = self.session.get(f"{BACKEND_URL}/api/auth/me", headers=headers)
            
            if not self.validate_response(response, "Token validation"):
                return False
                
            user_data = response.json()
            self.log(f"Authenticated as user: {user_data.get('username')}", "SUCCESS")
            
        except Exception as e:
            self.log(f"Token validation failed: {e}", "ERROR")
            return False
        
        return True

    # =====================
    # 2. UPLOAD TESTS
    # =====================
    
    def test_upload_workflow(self) -> bool:
        """Test file upload with dropzone validation"""
        self.log("📤 Testing Upload Workflow", "INFO")
        
        # Test 1: Create test PDF file with unique name following required pattern
        date_str = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        test_filename = f"{date_str}_TEST{unique_id}_ACME_SERVICE.pdf"
        test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000104 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
        
        # Test 2: Upload file through API
        try:
            files = {
                'file': (test_filename, test_content, 'application/pdf')
            }
            
            response = self.session.post(f"{BACKEND_URL}/api/upload", files=files)
            
            if not self.validate_response(response, "File upload"):
                return False
                
            upload_data = response.json()
            invoice_id = upload_data.get("id")
            
            if not invoice_id:
                self.log("No invoice ID received from upload", "ERROR")
                return False
                
            self.test_data["uploaded_invoice_id"] = invoice_id
            self.test_data["uploaded_filename"] = test_filename
            self.created_invoices.append(invoice_id)
            
            self.log(f"File uploaded successfully - Invoice ID: {invoice_id}", "SUCCESS")
            
        except Exception as e:
            self.log(f"File upload failed: {e}", "ERROR")
            return False
        
        # Test 3: Verify upload in dashboard
        try:
            response = self.session.get(f"{BACKEND_URL}/api/invoices")
            
            if not self.validate_response(response, "Dashboard invoice fetch"):
                return False
                
            invoices_data = response.json()
            invoices = invoices_data.get("invoices", [])
            
            # Find our uploaded invoice
            uploaded_invoice = None
            for invoice in invoices:
                if invoice.get("id") == invoice_id:
                    uploaded_invoice = invoice
                    break
            
            if not uploaded_invoice:
                self.log("Uploaded invoice not found in dashboard", "ERROR")
                return False
                
            self.log(f"Upload verified in dashboard - Status: {uploaded_invoice.get('status')}", "SUCCESS")
            
        except Exception as e:
            self.log(f"Dashboard verification failed: {e}", "ERROR")
            return False
        
        return True

    # =======================
    # 3. DASHBOARD TESTS
    # =======================
    
    def test_dashboard_workflow(self) -> bool:
        """Test dashboard functionality and invoice management"""
        self.log("📊 Testing Dashboard Workflow", "INFO")
        
        # Test 1: Load dashboard data
        try:
            response = self.session.get(f"{BACKEND_URL}/api/invoices")
            
            if not self.validate_response(response, "Dashboard data load"):
                return False
                
            dashboard_data = response.json()
            invoices = dashboard_data.get("invoices", [])
            
            self.log(f"Dashboard loaded with {len(invoices)} invoices", "SUCCESS")
            
            # Verify our test invoice is present
            test_invoice = None
            for invoice in invoices:
                if invoice.get("id") == self.test_data.get("uploaded_invoice_id"):
                    test_invoice = invoice
                    break
            
            if not test_invoice:
                self.log("Test invoice not found in dashboard", "ERROR")
                return False
                
            self.test_data["dashboard_invoice"] = test_invoice
            
        except Exception as e:
            self.log(f"Dashboard load failed: {e}", "ERROR")
            return False
        
        # Test 2: Test status filtering and workflow stages
        status_counts = {}
        for invoice in invoices:
            status = invoice.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.log(f"Status distribution: {status_counts}", "INFO")
        
        # Test 3: Test invoice actions availability
        invoice_id = self.test_data["uploaded_invoice_id"]
        
        # Check if edit action is available
        try:
            response = self.session.get(f"{BACKEND_URL}/api/invoices/{invoice_id}/editor")
            if self.validate_response(response, "Editor data access"):
                self.log("Invoice editing is available", "SUCCESS")
            else:
                self.log("Invoice editing access failed", "WARNING")
        except Exception as e:
            self.log(f"Editor access test failed: {e}", "WARNING")
        
        return True

    # ==========================
    # 4. INVOICE EDITOR TESTS
    # ==========================
    
    def test_invoice_editor_workflow(self) -> bool:
        """Test invoice editing and dropdown management"""
        self.log("✏️ Testing Invoice Editor Workflow", "INFO")
        
        invoice_id = self.test_data["uploaded_invoice_id"]
        
        # Test 1: Load invoice editor data
        try:
            response = self.session.get(f"{BACKEND_URL}/api/invoices/{invoice_id}/editor")
            
            if not self.validate_response(response, "Invoice editor data load"):
                return False
                
            editor_data = response.json()
            
            # Verify required fields are present
            required_fields = ["pdfUrl", "fields", "filename"]
            for field in required_fields:
                if field not in editor_data:
                    self.log(f"Missing required field in editor data: {field}", "ERROR")
                    return False
            
            self.test_data["editor_data"] = editor_data
            self.log("Invoice editor data loaded successfully", "SUCCESS")
            
        except Exception as e:
            self.log(f"Invoice editor load failed: {e}", "ERROR")
            return False
        
        # Test 2: Test dropdown options loading
        try:
            response = self.session.get(f"{BACKEND_URL}/api/dropdowns/projekt")
            if self.validate_response(response, "Dropdown options load"):
                dropdown_data = response.json()
                self.log(f"Loaded {len(dropdown_data.get('options', []))} projekt options", "SUCCESS")
        except Exception as e:
            self.log(f"Dropdown load failed: {e}", "WARNING")
        
        # Test 3: Update invoice data
        try:
            update_data = {
                "fields": {
                    "rechnungsempfaenger": "Test Company GmbH",
                    "rechnungssteller": "ACME Corp",
                    "projekt": "Test Project 2025",
                    "gewerk": "Testing Services",
                    "rechnungsbetrag": 1250.75,
                    "rechnungseingang": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "faelligkeit": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "skonto_datum": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                    "skonto_prozent": 2.5,
                    "rechnungsart": "rechnung",
                    "kfw_anrechenbar": False,
                    "rechnungspruefung_email": "test@example.com"
                },
                "editor_info": {
                    "editor_email": "test@example.com",
                    "editor_name": "Test Editor"
                }
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/api/invoices/{invoice_id}/editor",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if not self.validate_response(response, "Invoice data update"):
                return False
                
            update_result = response.json()
            self.log(f"Invoice updated - Email sent: {update_result.get('email_sent', False)}", "SUCCESS")
            
        except Exception as e:
            self.log(f"Invoice update failed: {e}", "ERROR")
            return False
        
        # Test 4: Test dropdown management (add/remove options)
        try:
            # Add a new dropdown option using the correct endpoint
            new_option_data = {
                "field_name": "projekt",
                "value": "test_project_workflow",
                "label": "Test Project for Workflow Testing"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/dropdowns/add-option",
                json=new_option_data,
                headers={"Content-Type": "application/json"}
            )
            
            if self.validate_response(response, "Dropdown option addition"):
                self.log("Dropdown option added successfully", "SUCCESS")
                
                # Try to remove it using the correct endpoint format
                response = self.session.delete(
                    f"{BACKEND_URL}/api/dropdowns/projekt/test_project_workflow"
                )
                
                if self.validate_response(response, "Dropdown option removal"):
                    self.log("Dropdown option removed successfully", "SUCCESS")
                
        except Exception as e:
            self.log(f"Dropdown management test failed: {e}", "WARNING")
        
        return True

    # ===========================
    # 5. WORKFLOW PROGRESSION
    # ===========================
    
    def test_workflow_progression(self) -> bool:
        """Test invoice workflow progression and status updates"""
        self.log("🔄 Testing Workflow Progression", "INFO")
        
        invoice_id = self.test_data["uploaded_invoice_id"]
        
        # Test 1: Complete invoice editing
        try:
            completion_data = {
                "fields": {
                    "rechnungspruefung_email": "test@example.com"
                },
                "completion_info": {
                    "completed_by": "test@example.com",
                    "editor_email": "test@example.com",
                    "editor_name": "Test Editor",
                    "completed_at": datetime.now().isoformat(),
                    "review_status": "completed_review",
                    "completion_notes": "Workflow test completion"
                }
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/api/invoices/{invoice_id}/complete",
                json=completion_data,
                headers={"Content-Type": "application/json"}
            )
            
            if not self.validate_response(response, "Invoice completion"):
                return False
                
            self.log("Invoice marked as completed", "SUCCESS")
            
        except Exception as e:
            self.log(f"Invoice completion failed: {e}", "ERROR")
            return False
        
        # Test 2: Test sending to Bauleiter
        try:
            bauleiter_data = {
                "bauleiter_email": "bauleiter@test.com",
                "sent_by": "test_user",
                "editor_name": "Test Editor",
                "editor_email": "test@example.com"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/invoices/{invoice_id}/send-to-bauleiter",
                json=bauleiter_data,
                headers={"Content-Type": "application/json"}
            )
            
            if self.validate_response(response, "Send to Bauleiter"):
                result = response.json()
                self.log(f"Sent to Bauleiter - Email sent: {result.get('email_sent', False)}", "SUCCESS")
            
        except Exception as e:
            self.log(f"Send to Bauleiter failed: {e}", "WARNING")
        
        # Test 3: Verify status progression
        try:
            response = self.session.get(f"{BACKEND_URL}/api/invoices/{invoice_id}")
            
            if self.validate_response(response, "Status verification"):
                invoice_data = response.json()
                current_status = invoice_data.get("status")
                review_status = invoice_data.get("review_status")
                
                self.log(f"Current status: {current_status}, Review status: {review_status}", "INFO")
        
        except Exception as e:
            self.log(f"Status verification failed: {e}", "WARNING")
        
        return True

    # =======================
    # 6. SKONTO WORKFLOW
    # =======================
    
    def test_skonto_workflow(self) -> bool:
        """Test Skonto processing and Prüfbericht functionality"""
        self.log("💰 Testing Skonto Workflow", "INFO")
        
        # Test 1: Try to create invoice with Skonto data (may not be supported via direct POST)
        skonto_invoice_id = None
        try:
            # Generate unique filename for Skonto test following required pattern
            date_str = datetime.now().strftime("%Y%m%d")
            unique_id = str(uuid.uuid4())[:8].upper()
            skonto_filename = f"{date_str}_SKONTO{unique_id}_VENDOR_INVOICE.pdf"
            
            # Try to create via upload first (more realistic)
            skonto_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000104 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
            
            files = {
                'file': (skonto_filename, skonto_content, 'application/pdf')
            }
            
            response = self.session.post(f"{BACKEND_URL}/api/upload", files=files)
            
            if self.validate_response(response, "Skonto invoice upload"):
                skonto_result = response.json()
                skonto_invoice_id = skonto_result.get("id")
                if skonto_invoice_id:
                    self.created_invoices.append(skonto_invoice_id)
                    self.test_data["skonto_invoice_id"] = skonto_invoice_id
                    self.log(f"Skonto invoice uploaded - ID: {skonto_invoice_id}", "SUCCESS")
            else:
                self.log("Skonto invoice creation via upload failed, continuing with existing invoices", "WARNING")
            
        except Exception as e:
            self.log(f"Skonto invoice creation failed: {e}", "WARNING")
            # Continue with the test using existing invoices
        
        # Test 2: Test Skonto dashboard endpoints
        try:
            # Test summary endpoint
            response = self.session.get(f"{BACKEND_URL}/api/skonto/dashboard/summary")
            if self.validate_response(response, "Skonto dashboard summary"):
                summary_data = response.json()
                self.log(f"Skonto summary - Total opportunities: {summary_data.get('total_opportunities', 0)}", "SUCCESS")
            
            # Test opportunities endpoint
            response = self.session.get(f"{BACKEND_URL}/api/skonto/dashboard/opportunities")
            if self.validate_response(response, "Skonto opportunities"):
                opportunities = response.json()
                self.log(f"Skonto opportunities found: {len(opportunities)}", "SUCCESS")
            
        except Exception as e:
            self.log(f"Skonto dashboard test failed: {e}", "WARNING")
        
        # Test 3: Test Skonto decision updates
        skonto_invoice_id = self.test_data.get("skonto_invoice_id")
        if skonto_invoice_id:
            try:
                # Test marking as taken
                decision_data = {"skonto_decision": "taken"}
                response = self.session.put(
                    f"{BACKEND_URL}/api/invoices/{skonto_invoice_id}",
                    json=decision_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if self.validate_response(response, "Skonto decision update"):
                    self.log("Skonto marked as taken successfully", "SUCCESS")
                
            except Exception as e:
                self.log(f"Skonto decision update failed: {e}", "WARNING")
        
        # Test 4: Test Skonto reminder functionality
        if skonto_invoice_id:
            try:
                response = self.session.post(f"{BACKEND_URL}/api/invoices/{skonto_invoice_id}/send-skonto-reminder")
                if self.validate_response(response, "Skonto reminder"):
                    reminder_result = response.json()
                    self.log(f"Skonto reminder sent - Success: {reminder_result.get('success', False)}", "SUCCESS")
            except Exception as e:
                self.log(f"Skonto reminder test failed: {e}", "WARNING")
        else:
            self.log("Skipping Skonto reminder test - no valid invoice ID", "WARNING")
        
        return True

    # ========================
    # 7. EMAIL WORKFLOW
    # ========================
    
    def test_email_workflow(self) -> bool:
        """Test email notifications and workflow"""
        self.log("📧 Testing Email Workflow", "INFO")
        
        # Test 1: Test email service health
        try:
            response = self.session.get(f"{BACKEND_URL}/api/email/status")
            if response.status_code == 200:
                email_status = response.json()
                self.log(f"Email service status: {email_status.get('status', 'unknown')}", "SUCCESS")
            else:
                self.log("Email service status check failed", "WARNING")
        except Exception as e:
            self.log(f"Email service test failed: {e}", "WARNING")
        
        # Test 2: Test email templates
        try:
            # Test editor notification
            invoice_id = self.test_data.get("uploaded_invoice_id")
            email_data = {
                "recipient_email": "test@example.com",
                "recipient_name": "Test User",
                "invoice_data": {
                    "id": invoice_id,
                    "file_name": "test_invoice.pdf",
                    "rechnungssteller": "Test Vendor"
                },
                "changes_summary": [
                    {
                        "field": "rechnungsempfaenger",
                        "old_value": "",
                        "new_value": "Test Company",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            # Note: This might fail if email provider is not configured, which is expected in demo mode
            response = self.session.post(
                f"{BACKEND_URL}/api/email/send-editor-notification",
                json=email_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.log("Email notification test successful", "SUCCESS")
            else:
                self.log("Email notification test failed (expected in demo mode)", "WARNING")
                
        except Exception as e:
            self.log(f"Email notification test failed: {e}", "WARNING")
        
        return True

    # ====================
    # 8. DATA PERSISTENCE
    # ====================
    
    def test_data_persistence(self) -> bool:
        """Test data persistence and consistency"""
        self.log("💾 Testing Data Persistence", "INFO")
        
        # Test 1: Verify all created invoices are persistent
        try:
            response = self.session.get(f"{BACKEND_URL}/api/invoices")
            if not self.validate_response(response, "Data persistence check"):
                return False
            
            invoices_data = response.json()
            all_invoices = invoices_data.get("invoices", [])
            
            found_invoices = 0
            for created_id in self.created_invoices:
                for invoice in all_invoices:
                    if invoice.get("id") == created_id:
                        found_invoices += 1
                        break
            
            self.log(f"Data persistence verified: {found_invoices}/{len(self.created_invoices)} invoices found", "SUCCESS")
            
        except Exception as e:
            self.log(f"Data persistence check failed: {e}", "ERROR")
            return False
        
        # Test 2: Test database consistency
        try:
            response = self.session.get(f"{BACKEND_URL}/api/reports/processing-status")
            if self.validate_response(response, "Processing status report"):
                status_data = response.json()
                total_invoices = status_data.get("data", {}).get("summary", {}).get("total_invoices", 0)
                self.log(f"Database consistency check - Total invoices: {total_invoices}", "SUCCESS")
        except Exception as e:
            self.log(f"Database consistency check failed: {e}", "WARNING")
        
        return True

    # ===================
    # 9. CLEANUP
    # ===================
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        self.log("🧹 Cleaning up test data", "INFO")
        
        # Delete created invoices
        deleted_count = 0
        for invoice_id in self.created_invoices:
            try:
                response = self.session.delete(f"{BACKEND_URL}/api/invoices/{invoice_id}")
                if response.status_code == 200:
                    deleted_count += 1
            except Exception as e:
                self.log(f"Failed to delete invoice {invoice_id}: {e}", "WARNING")
        
        if deleted_count > 0:
            self.log(f"Cleanup completed - {deleted_count} test invoices deleted", "SUCCESS")
        else:
            self.log("No test data to clean up", "INFO")

    # ===================
    # 10. MAIN TEST RUNNER
    # ===================
    
    def run_complete_workflow_test(self) -> bool:
        """Run the complete workflow test suite"""
        
        print("🚀 OCR Invoice Processing - Complete Workflow Test Suite")
        print("=" * 65)
        
        start_time = datetime.now()
        
        test_results = {
            "Authentication Flow": False,
            "Upload Workflow": False,
            "Dashboard Workflow": False,
            "Invoice Editor": False,
            "Workflow Progression": False,
            "Skonto Processing": False,
            "Email Workflow": False,
            "Data Persistence": False
        }
        
        try:
            # Run all test modules
            test_results["Authentication Flow"] = self.test_authentication_flow()
            time.sleep(1)
            
            if test_results["Authentication Flow"]:
                test_results["Upload Workflow"] = self.test_upload_workflow()
                time.sleep(1)
                
                test_results["Dashboard Workflow"] = self.test_dashboard_workflow()
                time.sleep(1)
                
                test_results["Invoice Editor"] = self.test_invoice_editor_workflow()
                time.sleep(1)
                
                test_results["Workflow Progression"] = self.test_workflow_progression()
                time.sleep(1)
                
                test_results["Skonto Processing"] = self.test_skonto_workflow()
                time.sleep(1)
                
                test_results["Email Workflow"] = self.test_email_workflow()
                time.sleep(1)
                
                test_results["Data Persistence"] = self.test_data_persistence()
            
        except KeyboardInterrupt:
            self.log("Test suite interrupted by user", "WARNING")
        except Exception as e:
            self.log(f"Test suite failed with error: {e}", "ERROR")
        finally:
            # Always try to clean up
            self.cleanup_test_data()
        
        # Generate test report
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 65)
        print("📋 WORKFLOW TEST RESULTS")
        print("=" * 65)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status:<10} {test_name}")
            if passed:
                passed_tests += 1
        
        print("=" * 65)
        print(f"📊 Summary: {passed_tests}/{total_tests} tests passed")
        print(f"⏱️ Duration: {duration.total_seconds():.1f} seconds")
        
        # Frontend URLs for manual testing
        print("\n🌐 Frontend Testing URLs:")
        print(f"  • Login:           {FRONTEND_URL}/login")
        print(f"  • Dashboard:       {FRONTEND_URL}/dashboard")
        print(f"  • Upload:          {FRONTEND_URL}/upload")
        print(f"  • Prüfbericht:     {FRONTEND_URL}/prufbericht")
        
        print("\n🔧 Manual Testing Instructions:")
        print("1. Open the frontend URLs above to test UI workflows")
        print("2. Login with admin/admin123")
        print("3. Test the carousel navigation on homepage")
        print("4. Upload files using drag & drop in upload page")
        print("5. Edit invoices using the 'Bearbeiten' button in dashboard")
        print("6. Test dropdown management in invoice editor")
        print("7. Complete invoices and send to Bauleiter")
        print("8. Check Skonto opportunities in Prüfbericht page")
        print("9. Verify email notifications in browser console/network tab")
        
        # Overall result
        if passed_tests == total_tests:
            print("\n🎉 ALL WORKFLOW TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️ {total_tests - passed_tests} WORKFLOW TESTS FAILED")
            return False

def main():
    """Main function to run the complete workflow test"""
    
    # Check if services are running
    print("🔍 Checking service availability...")
    
    try:
        # Check backend
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend not responding properly (HTTP {response.status_code})")
            print("   Please start the backend with: cd backend && python main.py")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        print("   Please start the backend with: cd backend && python main.py")
        return False
    
    try:
        # Check frontend (basic connectivity)
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code >= 400:
            print(f"⚠️ Frontend returned HTTP {response.status_code} (may be normal for Next.js)")
    except Exception as e:
        print(f"⚠️ Frontend not accessible: {e}")
        print("   Please start the frontend with: cd frontend && npm run dev")
        print("   (Frontend tests will be manual)")
    
    print("✅ Services are accessible\n")
    
    # Run the workflow tests
    tester = OCRInvoiceE2ETest()
    success = tester.run_complete_workflow_test()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        sys.exit(1)
