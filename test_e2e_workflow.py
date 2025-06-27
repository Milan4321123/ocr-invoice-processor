#!/usr/bin/env python3
"""
End-to-end integration tests for the complete upload and processing workflow.
Tests the entire flow from upload to dashboard visibility to editing.
"""
import requests
import json
import time
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

class E2ETestResults:
    """Track end-to-end test results"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.uploaded_invoices = []  # Track uploaded invoices for cleanup
    
    def add_result(self, test_name: str, passed: bool, error: str = None):
        self.total += 1
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")
    
    def add_uploaded_invoice(self, invoice_id: str):
        """Track uploaded invoices for cleanup"""
        self.uploaded_invoices.append(invoice_id)
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"E2E TEST SUMMARY: {self.passed}/{self.total} passed ({self.failed} failed)")
        print(f"Uploaded {len(self.uploaded_invoices)} test invoices")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  • {error}")
        print(f"{'='*60}")

# Global test results
results = E2ETestResults()

# API Configuration
API_BASE = os.getenv('API_URL', 'http://localhost:8000')
FRONTEND_BASE = os.getenv('FRONTEND_URL', 'http://localhost:3000')

def create_test_pdf_content(size_bytes: int = 1000) -> bytes:
    """Create fake PDF content of specified size"""
    content = b"%PDF-1.4\n"
    padding = b"A" * (size_bytes - len(content) - 10)
    content += padding
    content += b"\n%%EOF\n"
    return content

def test_drag_drop_workflow():
    """Test complete drag & drop upload workflow"""
    print("\n🖱 Testing Drag & Drop Workflow")
    print("-" * 40)
    
    # Step 1: Upload via drag & drop API
    filename = "20250627_E2E001_DRAGDROP_TEST.pdf"
    content = create_test_pdf_content(2000)
    
    try:
        files = {'file': (filename, content, 'application/pdf')}
        upload_response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            invoice_id = upload_data.get('id')
            results.add_result("Drag & Drop Upload", invoice_id is not None)
            
            if invoice_id:
                results.add_uploaded_invoice(invoice_id)
                
                # Step 2: Verify invoice appears in dashboard
                time.sleep(1)  # Brief delay for processing
                dashboard_response = requests.get(f"{API_BASE}/api/invoices", timeout=10)
                
                if dashboard_response.status_code == 200:
                    invoices = dashboard_response.json()
                    invoice_found = any(inv.get('id') == invoice_id for inv in invoices)
                    results.add_result("Invoice in Dashboard", invoice_found)
                    
                    if invoice_found:
                        # Step 3: Test PDF viewer access
                        pdf_url = upload_data.get('url')
                        if pdf_url:
                            pdf_response = requests.get(pdf_url, timeout=10)
                            results.add_result("PDF Viewer Access", pdf_response.status_code == 200)
                        
                        # Step 4: Test invoice editor access
                        editor_response = requests.get(f"{API_BASE}/api/invoices/{invoice_id}/editor", timeout=10)
                        if editor_response.status_code == 200:
                            editor_data = editor_response.json()
                            has_required_fields = all(field in editor_data for field in ['invoice', 'dropdowns'])
                            results.add_result("Invoice Editor Access", has_required_fields)
                        else:
                            results.add_result("Invoice Editor Access", False, f"HTTP {editor_response.status_code}")
                    
                else:
                    results.add_result("Invoice in Dashboard", False, f"HTTP {dashboard_response.status_code}")
        else:
            results.add_result("Drag & Drop Upload", False, f"HTTP {upload_response.status_code}")
            
    except Exception as e:
        results.add_result("Drag & Drop Workflow", False, str(e))

def test_folder_watcher_workflow():
    """Test complete folder watcher workflow"""
    print("\n👁 Testing Folder Watcher Workflow")
    print("-" * 40)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Step 1: Add watch folder
            add_data = {
                "folder_path": temp_dir,
                "pattern": "*.pdf",
                "recursive": False,
                "enabled": True
            }
            
            add_response = requests.post(f"{API_BASE}/api/folder-watcher/folders", json=add_data, timeout=10)
            
            if add_response.status_code == 200:
                config_data = add_response.json()
                config_id = config_data.get('config_id')
                results.add_result("Add Watch Folder", config_id is not None)
                
                if config_id:
                    # Step 2: Start folder watcher
                    start_response = requests.post(f"{API_BASE}/api/folder-watcher/start", timeout=10)
                    if start_response.status_code == 200:
                        results.add_result("Start Folder Watcher", True)
                        
                        # Step 3: Create test file in watched folder
                        test_file = Path(temp_dir) / "20250627_E2E002_FOLDERWATCHER_TEST.pdf"
                        test_file.write_bytes(create_test_pdf_content(1500))
                        
                        # Step 4: Wait for processing and check notifications
                        time.sleep(3)
                        
                        notifications_response = requests.get(f"{API_BASE}/api/folder-watcher/notifications?limit=10", timeout=10)
                        if notifications_response.status_code == 200:
                            notifications_data = notifications_response.json()
                            notifications = notifications_data.get('notifications', [])
                            
                            # Look for success notification
                            success_notification = any(
                                notif.get('type') == 'upload_success' and 
                                test_file.name in notif.get('filename', '')
                                for notif in notifications
                            )
                            results.add_result("File Processing Notification", success_notification)
                            
                            # Step 5: Check if invoice appears in dashboard
                            dashboard_response = requests.get(f"{API_BASE}/api/invoices", timeout=10)
                            if dashboard_response.status_code == 200:
                                invoices = dashboard_response.json()
                                folder_invoice = next(
                                    (inv for inv in invoices if inv.get('file_name') == test_file.name),
                                    None
                                )
                                
                                if folder_invoice:
                                    results.add_result("Folder Watcher Invoice in Dashboard", True)
                                    results.add_uploaded_invoice(folder_invoice.get('id'))
                                else:
                                    results.add_result("Folder Watcher Invoice in Dashboard", False, "Invoice not found")
                            else:
                                results.add_result("Folder Watcher Invoice Check", False, f"HTTP {dashboard_response.status_code}")
                        else:
                            results.add_result("Notifications Check", False, f"HTTP {notifications_response.status_code}")
                        
                        # Cleanup: Stop watcher and remove folder
                        requests.post(f"{API_BASE}/api/folder-watcher/stop", timeout=10)
                        requests.delete(f"{API_BASE}/api/folder-watcher/folders/{config_id}", timeout=10)
                        
                    else:
                        results.add_result("Start Folder Watcher", False, f"HTTP {start_response.status_code}")
            else:
                results.add_result("Add Watch Folder", False, f"HTTP {add_response.status_code}")
                
        except Exception as e:
            results.add_result("Folder Watcher Workflow", False, str(e))

def test_manual_upload_workflow():
    """Test manual upload workflow (simulating direct API usage)"""
    print("\n🖐 Testing Manual Upload Workflow")  
    print("-" * 40)
    
    # Manual uploads typically use the same endpoint but could have different handling
    filename = "20250627_E2E003_MANUAL_TEST.pdf"
    content = create_test_pdf_content(3000)
    
    try:
        files = {'file': (filename, content, 'application/pdf')}
        upload_response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            invoice_id = upload_data.get('id')
            results.add_result("Manual Upload", invoice_id is not None)
            
            if invoice_id:
                results.add_uploaded_invoice(invoice_id)
                
                # Test invoice retrieval
                invoice_response = requests.get(f"{API_BASE}/api/invoices/{invoice_id}", timeout=10)
                if invoice_response.status_code == 200:
                    invoice_data = invoice_response.json()
                    has_correct_data = (
                        invoice_data.get('file_name') == filename and
                        invoice_data.get('status') == 'under_review'
                    )
                    results.add_result("Manual Invoice Data", has_correct_data)
                else:
                    results.add_result("Manual Invoice Data", False, f"HTTP {invoice_response.status_code}")
        else:
            results.add_result("Manual Upload", False, f"HTTP {upload_response.status_code}")
            
    except Exception as e:
        results.add_result("Manual Upload Workflow", False, str(e))

def test_invoice_editing_workflow():
    """Test complete invoice editing workflow"""
    print("\n✏️ Testing Invoice Editing Workflow")
    print("-" * 40)
    
    # First upload an invoice to edit
    filename = "20250627_E2E004_EDIT_TEST.pdf"
    content = create_test_pdf_content(2500)
    
    try:
        files = {'file': (filename, content, 'application/pdf')}
        upload_response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            invoice_id = upload_data.get('id')
            results.add_uploaded_invoice(invoice_id)
            
            # Step 1: Access invoice editor
            editor_response = requests.get(f"{API_BASE}/api/invoices/{invoice_id}/editor", timeout=10)
            if editor_response.status_code == 200:
                results.add_result("Access Invoice Editor", True)
                
                # Step 2: Test save functionality
                save_data = {
                    "email": "test@example.com",
                    "extracted_data": {
                        "invoice_number": "TEST-001",
                        "total_amount": "100.00",
                        "vendor": "Test Vendor"
                    },
                    "dropdown_changes": []
                }
                
                save_response = requests.post(
                    f"{API_BASE}/api/invoices/{invoice_id}/save",
                    json=save_data,
                    timeout=15
                )
                
                if save_response.status_code == 200:
                    results.add_result("Save Invoice Changes", True)
                    
                    # Step 3: Test complete functionality
                    complete_data = {
                        "email": "test@example.com",
                        "extracted_data": {
                            "invoice_number": "TEST-001",
                            "total_amount": "100.00",
                            "vendor": "Test Vendor"
                        }
                    }
                    
                    complete_response = requests.post(
                        f"{API_BASE}/api/invoices/{invoice_id}/complete",
                        json=complete_data,
                        timeout=15
                    )
                    
                    if complete_response.status_code == 200:
                        results.add_result("Complete Invoice", True)
                        
                        # Step 4: Verify status change
                        time.sleep(1)
                        updated_response = requests.get(f"{API_BASE}/api/invoices/{invoice_id}", timeout=10)
                        if updated_response.status_code == 200:
                            updated_data = updated_response.json()
                            is_completed = updated_data.get('status') == 'completed'
                            results.add_result("Invoice Status Updated", is_completed)
                        else:
                            results.add_result("Invoice Status Check", False, f"HTTP {updated_response.status_code}")
                    else:
                        results.add_result("Complete Invoice", False, f"HTTP {complete_response.status_code}")
                else:
                    results.add_result("Save Invoice Changes", False, f"HTTP {save_response.status_code}")
            else:
                results.add_result("Access Invoice Editor", False, f"HTTP {editor_response.status_code}")
                
    except Exception as e:
        results.add_result("Invoice Editing Workflow", False, str(e))

def test_dropdown_management_workflow():
    """Test dropdown management workflow"""
    print("\n🔽 Testing Dropdown Management Workflow")
    print("-" * 40)
    
    try:
        # Step 1: Get available dropdowns
        dropdowns_response = requests.get(f"{API_BASE}/api/dropdowns", timeout=10)
        if dropdowns_response.status_code == 200:
            dropdowns_data = dropdowns_response.json()
            has_dropdowns = len(dropdowns_data) > 0
            results.add_result("Get Dropdowns", has_dropdowns)
            
            if has_dropdowns:
                # Step 2: Test adding dropdown item
                first_dropdown = dropdowns_data[0]
                dropdown_id = first_dropdown.get('id')
                
                new_item_data = {
                    "email": "test@example.com",
                    "value": f"E2E Test Item {int(time.time())}",
                    "display_value": f"E2E Test Display {int(time.time())}"
                }
                
                add_item_response = requests.post(
                    f"{API_BASE}/api/dropdowns/{dropdown_id}/items",
                    json=new_item_data,
                    timeout=10
                )
                
                if add_item_response.status_code == 200:
                    results.add_result("Add Dropdown Item", True)
                    
                    # Step 3: Test getting pending changes
                    pending_response = requests.get(f"{API_BASE}/api/dropdowns/pending", timeout=10)
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        has_pending = len(pending_data) > 0
                        results.add_result("Get Pending Changes", has_pending)
                    else:
                        results.add_result("Get Pending Changes", False, f"HTTP {pending_response.status_code}")
                        
                else:
                    results.add_result("Add Dropdown Item", False, f"HTTP {add_item_response.status_code}")
        else:
            results.add_result("Get Dropdowns", False, f"HTTP {dropdowns_response.status_code}")
            
    except Exception as e:
        results.add_result("Dropdown Management Workflow", False, str(e))

def test_error_scenarios():
    """Test various error scenarios"""
    print("\n⚠️ Testing Error Scenarios")
    print("-" * 40)
    
    # Test 1: Invalid file upload
    try:
        invalid_files = {'file': ('invalid.txt', b'text content', 'text/plain')}
        response = requests.post(f"{API_BASE}/api/upload", files=invalid_files, timeout=10)
        results.add_result("Invalid File Type Error", response.status_code == 400)
    except Exception as e:
        results.add_result("Invalid File Type Error", False, str(e))
    
    # Test 2: Non-existent invoice
    try:
        response = requests.get(f"{API_BASE}/api/invoices/non-existent-id", timeout=10)
        results.add_result("Non-existent Invoice Error", response.status_code == 404)
    except Exception as e:
        results.add_result("Non-existent Invoice Error", False, str(e))
    
    # Test 3: Invalid invoice edit
    try:
        response = requests.post(
            f"{API_BASE}/api/invoices/non-existent-id/save",
            json={"email": "test@example.com"},
            timeout=10
        )
        results.add_result("Invalid Invoice Edit Error", response.status_code == 404)
    except Exception as e:
        results.add_result("Invalid Invoice Edit Error", False, str(e))

def test_frontend_integration():
    """Test frontend integration (basic connectivity)"""
    print("\n🌐 Testing Frontend Integration")
    print("-" * 40)
    
    frontend_urls = [
        ("/", "Homepage"),
        ("/upload", "Upload Page"),
        ("/dashboard", "Dashboard"),
        ("/dashboard/folder-watcher", "Folder Watcher Dashboard")
    ]
    
    for url, name in frontend_urls:
        try:
            response = requests.get(f"{FRONTEND_BASE}{url}", timeout=10)
            # Accept 2xx or 3xx status codes for frontend
            is_accessible = 200 <= response.status_code < 400
            results.add_result(f"Frontend {name}", is_accessible)
        except Exception as e:
            results.add_result(f"Frontend {name}", False, str(e))

def test_data_consistency():
    """Test data consistency across different views"""
    print("\n🔄 Testing Data Consistency")
    print("-" * 40)
    
    try:
        # Get invoices from dashboard
        dashboard_response = requests.get(f"{API_BASE}/api/invoices", timeout=10)
        if dashboard_response.status_code == 200:
            dashboard_invoices = dashboard_response.json()
            
            if dashboard_invoices:
                # Pick first invoice and check consistency
                first_invoice = dashboard_invoices[0]
                invoice_id = first_invoice.get('id')
                
                # Get same invoice via direct API
                direct_response = requests.get(f"{API_BASE}/api/invoices/{invoice_id}", timeout=10)
                if direct_response.status_code == 200:
                    direct_invoice = direct_response.json()
                    
                    # Check key fields match
                    fields_match = all(
                        first_invoice.get(field) == direct_invoice.get(field)
                        for field in ['id', 'file_name', 'status', 'created_at']
                    )
                    results.add_result("Data Consistency", fields_match)
                else:
                    results.add_result("Data Consistency", False, f"Direct API failed: {direct_response.status_code}")
            else:
                results.add_result("Data Consistency", True, "No invoices to check")
        else:
            results.add_result("Data Consistency", False, f"Dashboard API failed: {dashboard_response.status_code}")
            
    except Exception as e:
        results.add_result("Data Consistency", False, str(e))

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning Up Test Data")
    print("-" * 40)
    
    cleaned_count = 0
    for invoice_id in results.uploaded_invoices:
        try:
            delete_response = requests.delete(f"{API_BASE}/api/invoices/{invoice_id}", timeout=10)
            if delete_response.status_code == 200:
                cleaned_count += 1
        except Exception as e:
            print(f"    Failed to delete {invoice_id}: {e}")
    
    print(f"    Cleaned up {cleaned_count}/{len(results.uploaded_invoices)} test invoices")

def run_all_e2e_tests():
    """Run all end-to-end tests"""
    print("🚀 Starting End-to-End Integration Tests")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print(f"Frontend Base: {FRONTEND_BASE}")
    print()
    
    try:
        # Core workflow tests
        test_drag_drop_workflow()
        test_folder_watcher_workflow()
        test_manual_upload_workflow()
        test_invoice_editing_workflow()
        test_dropdown_management_workflow()
        
        # Integration and consistency tests
        test_frontend_integration()
        test_data_consistency()
        
        # Error handling tests
        test_error_scenarios()
        
    finally:
        # Always try to clean up
        cleanup_test_data()
    
    # Print summary
    results.summary()
    
    # Return success status
    return results.failed == 0

if __name__ == "__main__":
    success = run_all_e2e_tests()
    exit(0 if success else 1)
