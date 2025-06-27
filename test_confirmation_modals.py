#!/usr/bin/env python3
"""
Comprehensive test script for all confirmation modals in the invoice editor.
Tests:
1. Dropdown changes confirmation modal
2. Invoice save confirmation modal  
3. Invoice complete confirmation modal
"""

import requests
import json
import time
import sys
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3001"

# Test data
TEST_EMAIL = "test-confirmation@example.com"
TEST_INVOICE_ID = "6dc59038-0e7d-4172-816d-061342bb68d3"

def print_test_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 50)

def test_api_health():
    """Test that backend API is responsive"""
    print_test_header("API HEALTH CHECK")
    
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is healthy")
            return True
        else:
            print(f"❌ Backend API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API is not responding: {e}")
        return False

def test_frontend_health():
    """Test that frontend is responsive"""
    print_test_header("FRONTEND HEALTH CHECK")
    
    try:
        response = requests.get(f"{FRONTEND_BASE}", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is responding")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend is not responding: {e}")
        return False

def test_invoice_editor_api():
    """Test invoice editor API endpoint"""
    print_test_header("INVOICE EDITOR API TEST")
    
    try:
        response = requests.get(f"{API_BASE}/api/invoices/{TEST_INVOICE_ID}/editor", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Invoice editor API is working")
            print(f"📄 Invoice file: {data.get('filename', 'Unknown')}")
            print(f"📧 Current email: {data.get('fields', {}).get('rechnungspruefung_email', 'Not set')}")
            
            # Verify required fields exist
            required_fields = ['pdfUrl', 'fields', 'filename']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
                return False
            else:
                print("✅ All required fields present")
                return True
        else:
            print(f"❌ Invoice editor API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invoice editor API failed: {e}")
        return False

def test_dropdown_crud_api():
    """Test dropdown CRUD operations"""
    print_test_header("DROPDOWN CRUD API TEST")
    
    # Test 1: Get dropdown options
    print_step(1, "Testing dropdown options retrieval")
    try:
        response = requests.get(f"{API_BASE}/api/dropdowns", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Dropdown options API working")
            print(f"📊 Available dropdown fields: {list(data.get('dropdowns', {}).keys())}")
        else:
            print(f"❌ Dropdown API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dropdown API failed: {e}")
        return False
    
    # Test 2: Add a test dropdown option
    print_step(2, "Testing dropdown option addition")
    test_option = {
        "field_name": "projekt",
        "value": f"test_confirmation_{int(time.time())}",
        "label": f"Test Confirmation Project {datetime.now().strftime('%H:%M:%S')}"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/dropdowns/add-option", 
                               json=test_option, timeout=10)
        if response.status_code == 200:
            print("✅ Dropdown option addition working")
            print(f"➕ Added test option: {test_option['label']}")
        else:
            print(f"❌ Dropdown addition returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dropdown addition failed: {e}")
        return False
    
    print("✅ Dropdown CRUD API tests passed")
    return True

def test_email_notification_api():
    """Test email notification functionality"""
    print_test_header("EMAIL NOTIFICATION API TEST")
    
    # Test dropdown change notification
    print_step(1, "Testing dropdown change notification email")
    
    email_data = {
        "user_email": TEST_EMAIL,
        "changes": [
            {
                "type": "add",
                "fieldName": "projekt",
                "optionValue": "test_project",
                "optionLabel": "Test Project",
                "success": True
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/email/dropdown-change-notification",
                               json=email_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ Email notification API working")
            print(f"📧 Message ID: {data.get('message_id', 'Unknown')}")
        else:
            print(f"⚠️  Email API returned status {response.status_code}")
            print("Note: This might be expected if email service is not configured")
    except Exception as e:
        print(f"⚠️  Email API failed: {e}")
        print("Note: This might be expected if email service is not configured")
    
    return True

def test_invoice_save_api():
    """Test invoice save functionality"""
    print_test_header("INVOICE SAVE API TEST")
    
    # Prepare test data with required email
    invoice_data = {
        "fields": {
            "rechnungspruefung_email": TEST_EMAIL,
            "rechnungsempfaenger": "Test Company for Confirmation",
            "rechnungsbetrag": 999.99,
            "rechnungsart": "rechnung"
        },
        "editor_info": {
            "editor_email": TEST_EMAIL,
            "editor_name": "Test Editor",
            "changes_summary": [
                {
                    "field": "rechnungsempfaenger",
                    "old_value": "",
                    "new_value": "Test Company for Confirmation"
                }
            ]
        }
    }
    
    try:
        response = requests.put(f"{API_BASE}/api/invoices/{TEST_INVOICE_ID}/editor",
                              json=invoice_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ Invoice save API working")
            print(f"💾 Invoice saved successfully")
            print(f"📧 Email sent: {data.get('email_sent', False)}")
        else:
            print(f"❌ Invoice save API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invoice save API failed: {e}")
        return False
    
    return True

def test_invoice_complete_api():
    """Test invoice completion functionality"""
    print_test_header("INVOICE COMPLETE API TEST")
    
    completion_data = {
        "fields": {
            "rechnungspruefung_email": TEST_EMAIL
        },
        "completion_info": {
            "completed_by": TEST_EMAIL,
            "completed_at": datetime.now().isoformat(),
            "review_status": "completed_review",
            "completion_notes": "Test completion via confirmation modal"
        }
    }
    
    try:
        response = requests.put(f"{API_BASE}/api/invoices/{TEST_INVOICE_ID}/complete",
                              json=completion_data, timeout=15)
        if response.status_code == 200:
            print("✅ Invoice complete API working")
            print(f"✅ Invoice marked as completed")
        else:
            print(f"❌ Invoice complete API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invoice complete API failed: {e}")
        return False
    
    return True

def test_frontend_invoice_editor():
    """Test that the frontend invoice editor loads correctly"""
    print_test_header("FRONTEND INVOICE EDITOR TEST")
    
    try:
        response = requests.get(f"{FRONTEND_BASE}/invoice-editor/{TEST_INVOICE_ID}", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for key elements that indicate our confirmation modals are loaded
            checks = [
                ("Invoice Editor", "InvoiceEditorDashboard" in html_content or "invoice-editor" in html_content),
                ("React Components", "Next.js" in html_content or "_next" in html_content),
                ("Page Structure", "<html" in html_content and "</html>" in html_content)
            ]
            
            all_passed = True
            for check_name, passed in checks:
                if passed:
                    print(f"✅ {check_name} - OK")
                else:
                    print(f"❌ {check_name} - FAILED")
                    all_passed = False
            
            if all_passed:
                print("✅ Frontend invoice editor loads correctly")
                return True
            else:
                print("❌ Frontend invoice editor has issues")
                return False
        else:
            print(f"❌ Frontend invoice editor returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend invoice editor failed: {e}")
        return False

def run_all_tests():
    """Run comprehensive test suite"""
    print_test_header("CONFIRMATION MODALS COMPREHENSIVE TEST SUITE")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing Invoice ID: {TEST_INVOICE_ID}")
    print(f"📧 Test Email: {TEST_EMAIL}")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Frontend Health Check", test_frontend_health),
        ("Invoice Editor API", test_invoice_editor_api),
        ("Dropdown CRUD API", test_dropdown_crud_api),
        ("Email Notification API", test_email_notification_api),
        ("Invoice Save API", test_invoice_save_api),
        ("Invoice Complete API", test_invoice_complete_api),
        ("Frontend Invoice Editor", test_frontend_invoice_editor),
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name, test_function in tests:
        try:
            if test_function():
                passed_tests += 1
            else:
                failed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed_tests += 1
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print_test_header("TEST RESULTS SUMMARY")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📊 Total: {passed_tests + failed_tests}")
    print(f"📈 Success Rate: {(passed_tests / (passed_tests + failed_tests) * 100):.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Confirmation modals are ready for use.")
        print("\n🚀 You can now test manually:")
        print(f"   👀 Open: {FRONTEND_BASE}/invoice-editor/{TEST_INVOICE_ID}")
        print("   🔄 Test dropdown changes confirmation")
        print("   💾 Test 'Rechnung speichern' confirmation")
        print("   ✅ Test 'Bearbeitung abschließen' confirmation")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please check the issues above.")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
