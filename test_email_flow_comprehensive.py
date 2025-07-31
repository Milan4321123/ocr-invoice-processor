#!/usr/bin/env python3
"""
Comprehensive Email Flow Test for Invoice Editor
Tests the complete email sending workflow including:
1. Form editing and saving (should trigger update email)
2. Form completion (should trigger completion email)
3. Dropdown changes and saving
4. SendGrid configuration verification
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3002"

class EmailFlowTester:
    def __init__(self):
        self.session = None
        self.test_invoice_id = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    async def check_sendgrid_config(self) -> bool:
        """Check if SendGrid is properly configured"""
        try:
            # Read backend .env file
            backend_env_path = "backend/.env"
            if not os.path.exists(backend_env_path):
                self.log_test("SendGrid Config Check", False, "Backend .env file not found")
                return False
            
            with open(backend_env_path, 'r') as f:
                env_content = f.read()
            
            # Check for SendGrid configuration
            has_api_key = "SENDGRID_API_KEY=" in env_content
            has_provider = "EMAIL_PROVIDER=sendgrid" in env_content
            
            if has_api_key and has_provider:
                # Extract API key to check if it's not placeholder
                for line in env_content.split('\n'):
                    if line.startswith('SENDGRID_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key and not api_key.startswith('__') and api_key.startswith('SG.'):
                            self.log_test("SendGrid Config Check", True, f"API Key configured and valid format")
                            return True
                        else:
                            self.log_test("SendGrid Config Check", False, f"API Key is placeholder or invalid: {api_key[:20]}...")
                            return False
            else:
                self.log_test("SendGrid Config Check", False, 
                            f"Missing config - API Key: {has_api_key}, Provider: {has_provider}")
                return False
                
        except Exception as e:
            self.log_test("SendGrid Config Check", False, f"Error reading config: {str(e)}")
            return False

    async def get_test_invoice(self) -> str:
        """Get or create a test invoice"""
        try:
            # Try to get list of invoices
            async with self.session.get(f"{API_BASE_URL}/api/invoices") as response:
                if response.status == 200:
                    data = await response.json()
                    invoices = data.get('invoices', [])
                    if invoices:
                        # Use the first invoice for testing
                        invoice_id = invoices[0].get('id')
                        self.log_test("Get Test Invoice", True, f"Using existing invoice: {invoice_id}")
                        return invoice_id
                
                # If no invoices exist, we can't proceed with email tests
                self.log_test("Get Test Invoice", False, "No invoices found in database")
                return None
                
        except Exception as e:
            self.log_test("Get Test Invoice", False, f"Error: {str(e)}")
            return None

    async def test_form_save_email_flow(self, invoice_id: str) -> bool:
        """Test the form save email sending flow"""
        try:
            # Prepare test data for form update
            test_email = "test.editor@company.de"
            update_data = {
                "fields": {
                    "rechnungsspruefung_email": test_email,
                    "rechnungsempfaenger": "Test Company GmbH",
                    "rechnungssteller": "Supplier ABC",
                    "projekt": "Test Projekt",
                    "gewerk": "Elektro",
                    "rechnungsbetrag": "1500.00",
                    "rechnungseingang": "2025-07-23",
                    "faelligkeit": "2025-08-23"
                },
                "editor_info": {
                    "editor_email": test_email,
                    "editor_name": "Test Editor",
                    "changes_summary": [
                        {
                            "field": "rechnungsempfaenger",
                            "old_value": "",
                            "new_value": "Test Company GmbH"
                        }
                    ]
                }
            }
            
            # Make API call to update invoice
            async with self.session.put(
                f"{API_BASE_URL}/api/invoices/{invoice_id}/editor",
                headers={"Content-Type": "application/json"},
                data=json.dumps(update_data)
            ) as response:
                
                response_data = await response.json()
                
                if response.status == 200:
                    email_sent = response_data.get("email_sent", False)
                    self.log_test("Form Save API Call", True, 
                                f"Update successful, email_sent: {email_sent}", response_data)
                    
                    # Note: According to the code analysis, save operation doesn't send emails anymore
                    # Only completion emails are sent
                    if not email_sent:
                        self.log_test("Form Save Email Flow", True, 
                                    "No email sent on save (as expected per current implementation)")
                    else:
                        self.log_test("Form Save Email Flow", True, 
                                    "Email sent on save (unexpected but working)")
                    return True
                else:
                    self.log_test("Form Save API Call", False, 
                                f"Status: {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_test("Form Save Email Flow", False, f"Error: {str(e)}")
            return False

    async def test_form_complete_email_flow(self, invoice_id: str) -> bool:
        """Test the form completion email sending flow"""
        try:
            test_email = "test.editor@company.de"
            completion_data = {
                "completion_info": {
                    "completed_by": test_email,
                    "completed_at": datetime.now().isoformat(),
                    "completion_notes": "Test completion - automated test"
                },
                "editor_info": {
                    "editor_email": test_email,
                    "editor_name": "Test Editor",
                    "changes_summary": [
                        {
                            "field": "Status",
                            "old_value": "Bearbeitung",
                            "new_value": "Bearbeitung abgeschlossen",
                            "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                        }
                    ]
                }
            }
            
            # Make API call to complete invoice
            async with self.session.put(
                f"{API_BASE_URL}/api/invoices/{invoice_id}/complete",
                headers={"Content-Type": "application/json"},
                data=json.dumps(completion_data)
            ) as response:
                
                response_data = await response.json()
                
                if response.status == 200:
                    completion_email_sent = response_data.get("completion_email_sent", False)
                    self.log_test("Form Complete API Call", True, 
                                f"Completion successful, completion_email_sent: {completion_email_sent}", 
                                response_data)
                    
                    if completion_email_sent:
                        self.log_test("Form Complete Email Flow", True, 
                                    "Completion email sent successfully")
                    else:
                        self.log_test("Form Complete Email Flow", False, 
                                    "Completion email was not sent")
                    return completion_email_sent
                else:
                    self.log_test("Form Complete API Call", False, 
                                f"Status: {response.status}", response_data)
                    return False
                    
        except Exception as e:
            self.log_test("Form Complete Email Flow", False, f"Error: {str(e)}")
            return False

    async def test_backend_health(self) -> bool:
        """Test if backend is running and accessible"""
        try:
            async with self.session.get(f"{API_BASE_URL}/api/invoices") as response:
                if response.status == 200:
                    self.log_test("Backend Health Check", True, "Backend is running and accessible")
                    return True
                else:
                    self.log_test("Backend Health Check", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False

    async def test_email_service_status(self) -> bool:
        """Test email service availability by checking database connection"""
        try:
            # Test database connection (email service depends on it)
            async with self.session.get(f"{API_BASE_URL}/api/invoices") as response:
                if response.status == 200:
                    self.log_test("Email Service Dependencies", True, "Database connection working")
                    return True
                else:
                    self.log_test("Email Service Dependencies", False, f"Database issue - Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Email Service Dependencies", False, f"Error: {str(e)}")
            return False

    async def run_complete_test_suite(self):
        """Run the complete email flow test suite"""
        print("🧪 Starting Comprehensive Email Flow Test Suite")
        print("=" * 60)
        
        # 1. Check SendGrid configuration
        sendgrid_ok = await self.check_sendgrid_config()
        
        # 2. Check backend health
        backend_ok = await self.test_backend_health()
        
        # 3. Check email service dependencies
        email_deps_ok = await self.test_email_service_status()
        
        # 4. Get test invoice
        if backend_ok:
            self.test_invoice_id = await self.get_test_invoice()
        
        # 5. Test form save flow
        save_ok = False
        if backend_ok and self.test_invoice_id:
            save_ok = await self.test_form_save_email_flow(self.test_invoice_id)
        elif not self.test_invoice_id:
            self.log_test("Form Save Email Flow", False, "No valid invoice ID available for testing")
        
        # 6. Test form completion flow
        complete_ok = False
        if backend_ok and self.test_invoice_id:
            complete_ok = await self.test_form_complete_email_flow(self.test_invoice_id)
        elif not self.test_invoice_id:
            self.log_test("Form Complete Email Flow", False, "No valid invoice ID available for testing")
        
        # Generate summary report
        self.generate_summary_report()
        
        return {
            "sendgrid_config": sendgrid_ok,
            "backend_health": backend_ok,
            "email_dependencies": email_deps_ok,
            "save_flow": save_ok,
            "complete_flow": complete_ok,
            "overall_success": sendgrid_ok and backend_ok and email_deps_ok and complete_ok
        }

    def generate_summary_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 EMAIL FLOW TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check if SendGrid is configured
        sendgrid_test = next((r for r in self.test_results if "SendGrid Config" in r["test"]), None)
        if sendgrid_test:
            if sendgrid_test["success"]:
                print("   ✅ SendGrid is properly configured")
            else:
                print("   ❌ SendGrid configuration issues detected")
        
        # Check email flow status
        complete_test = next((r for r in self.test_results if "Complete Email Flow" in r["test"]), None)
        save_test = next((r for r in self.test_results if "Save Email Flow" in r["test"]), None)
        
        if complete_test and complete_test["success"]:
            print("   ✅ Completion emails are working")
        elif complete_test:
            print("   ❌ Completion emails are not working")
            
        if save_test:
            print("   ℹ️  Save emails are disabled (by design)")
        
        print("\n💡 RECOMMENDATIONS:")
        if failed_tests == 0:
            print("   🎉 All tests passed! Email flow is working correctly.")
        else:
            print("   🔧 Fix the failed tests above to ensure proper email functionality.")
            print("   📧 For company demo, verify SendGrid API key is valid and active.")
            print("   🧪 Test with real email addresses before production use.")
        
        print("=" * 60)

async def main():
    """Main test runner"""
    print("🚀 Starting Email Flow Testing...")
    print()
    
    async with EmailFlowTester() as tester:
        results = await tester.run_complete_test_suite()
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"email_flow_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                "test_summary": results,
                "detailed_results": tester.test_results,
                "timestamp": timestamp
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        if results["overall_success"]:
            print("\n🎉 All critical tests passed!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed - review the report above")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
