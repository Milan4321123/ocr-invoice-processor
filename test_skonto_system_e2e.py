#!/usr/bin/env python3
"""
Comprehensive Skonto System End-to-End Test
Tests the complete workflow with database integration
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Test configuration
TEST_EMAIL = "incognizant321@gmail.com"
API_BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on different port
TEST_INVOICE_DATA = {
    "file_name": "TEST_SKONTO_E2E.pdf",
    "rechnungssteller": "Test Supplier for Skonto",
    "rechnungsempfaenger": "Test Company",
    "projekt": "Skonto Test Project",
    "gewerk": "Testing",
    "rechnungsbetrag": 1000.00,
    "skonto_datum": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
    "skonto_prozent": 2.5,
    "approval_status": "approved",
    "status": "completed",
    "bauleiter_email": TEST_EMAIL
}

def test_api_connection():
    """Test if the backend API is running"""
    print("🔗 Testing API connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend API is running")
            return True
        else:
            print(f"   ❌ Backend API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to backend API: {e}")
        print(f"   💡 Make sure your backend is running on {API_BASE_URL}")
        return False

def test_database_schema():
    """Test if the Skonto fields were added to the database"""
    print("\n🗄️ Testing database schema...")
    try:
        from backend.services.database import db_service
        
        if not db_service.is_available:
            print("   ❌ Database service is not available")
            return False
        
        # Test database connection
        print("   🔍 Checking database connection...")
        
        # Try to query the invoices table to check if Skonto fields exist
        try:
            response = db_service.client.table("invoices_clean").select(
                "id, skonto_reminder_sent, skonto_decision, actual_skonto_savings"
            ).limit(1).execute()
            
            print("   ✅ Database schema validation successful")
            print(f"   📊 Skonto tracking fields are available")
            return True
            
        except Exception as e:
            print(f"   ❌ Skonto fields not found in database: {e}")
            print("   💡 Please run the database migration script first")
            return False
            
    except ImportError as e:
        print(f"   ❌ Cannot import database service: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def create_test_invoice():
    """Create a test invoice with Skonto data"""
    print("\n📝 Creating test invoice...")
    try:
        from backend.services.database import db_service
        
        # Create test invoice
        result = db_service.create_invoice(TEST_INVOICE_DATA)
        
        if result["success"]:
            invoice_id = result["data"]["id"]
            print(f"   ✅ Test invoice created: {invoice_id}")
            print(f"   📄 File: {TEST_INVOICE_DATA['file_name']}")
            print(f"   💰 Amount: {TEST_INVOICE_DATA['rechnungsbetrag']} EUR")
            print(f"   💸 Skonto: {TEST_INVOICE_DATA['skonto_prozent']}% until {TEST_INVOICE_DATA['skonto_datum']}")
            return invoice_id
        else:
            print(f"   ❌ Failed to create test invoice: {result['error']}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error creating test invoice: {e}")
        return None

def test_skonto_reminder_api(invoice_id):
    """Test the Skonto reminder API endpoint"""
    print("\n📧 Testing Skonto reminder API...")
    try:
        # Test send reminder endpoint
        url = f"{API_BASE_URL}/api/invoices/{invoice_id}/send-skonto-reminder"
        data = {
            "recipient_email": TEST_EMAIL,
            "recipient_name": "Test User"
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Skonto reminder API successful")
            print(f"   📧 Email sent to: {result.get('recipient_email')}")
            print(f"   💰 Potential savings: {result.get('potential_savings')} EUR")
            print(f"   ⏰ Days until expiry: {result.get('days_until_expiry')}")
            return True
        else:
            print(f"   ❌ Skonto reminder API failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   📋 Error details: {error_detail}")
            except:
                print(f"   📋 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Skonto reminder API: {e}")
        return False

def test_skonto_due_api():
    """Test the invoices with Skonto due API"""
    print("\n📊 Testing Skonto due API...")
    try:
        url = f"{API_BASE_URL}/api/invoices/skonto-due"
        params = {"days_ahead": 10}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Skonto due API successful")
            print(f"   📈 Found {result.get('total', 0)} invoices with Skonto due")
            
            if result.get('invoices'):
                for i, invoice in enumerate(result['invoices'][:3]):  # Show first 3
                    print(f"   📄 Invoice {i+1}: {invoice.get('file_name')} - {invoice.get('potential_savings')} EUR potential")
            
            return True
        else:
            print(f"   ❌ Skonto due API failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   📋 Error details: {error_detail}")
            except:
                print(f"   📋 Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Skonto due API: {e}")
        return False

def test_database_updates(invoice_id):
    """Test if database was properly updated after reminder"""
    print("\n🔍 Testing database updates...")
    try:
        from backend.services.database import db_service
        
        # Get updated invoice data
        result = db_service.get_invoice(invoice_id)
        
        if result["success"]:
            invoice_data = result["data"]
            
            # Check if reminder was marked as sent
            reminder_sent = invoice_data.get("skonto_reminder_sent")
            reminder_sent_at = invoice_data.get("skonto_reminder_sent_at")
            skonto_decision = invoice_data.get("skonto_decision")
            
            print(f"   📊 Database state after reminder:")
            print(f"   📧 Reminder sent: {reminder_sent}")
            print(f"   📅 Reminder sent at: {reminder_sent_at}")
            print(f"   🎯 Skonto decision: {skonto_decision}")
            
            if reminder_sent:
                print("   ✅ Database correctly updated after reminder")
                return True
            else:
                print("   ❌ Database was not updated after reminder")
                return False
        else:
            print(f"   ❌ Failed to retrieve invoice data: {result['error']}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing database updates: {e}")
        return False

def test_skonto_decision_simulation(invoice_id):
    """Simulate Skonto decision processing"""
    print("\n🎯 Testing Skonto decision processing...")
    try:
        from backend.services.database import db_service
        
        # Simulate taking Skonto
        test_savings = 25.00  # 2.5% of 1000 EUR
        
        result = db_service.update_skonto_decision(
            invoice_id=invoice_id,
            decision="taken",
            actual_savings=test_savings,
            decision_timestamp=datetime.now().isoformat(),
            decision_email=TEST_EMAIL
        )
        
        if result["success"]:
            print("   ✅ Skonto decision processing successful")
            print(f"   💰 Savings recorded: {test_savings} EUR")
            
            # Verify the update
            invoice_result = db_service.get_invoice(invoice_id)
            if invoice_result["success"]:
                updated_data = invoice_result["data"]
                print(f"   🎯 Decision status: {updated_data.get('skonto_decision')}")
                print(f"   💸 Actual savings: {updated_data.get('actual_skonto_savings')}")
                return True
            else:
                print("   ❌ Failed to verify decision update")
                return False
        else:
            print(f"   ❌ Skonto decision processing failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Skonto decision: {e}")
        return False

def cleanup_test_data(invoice_id):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    try:
        from backend.services.database import db_service
        
        if db_service.client:
            # Delete test invoice
            response = db_service.client.table("invoices_clean").delete().eq("id", invoice_id).execute()
            print(f"   ✅ Test invoice {invoice_id} cleaned up")
        else:
            print("   ⚠️ Database not available for cleanup")
            
    except Exception as e:
        print(f"   ❌ Error during cleanup: {e}")

def main():
    """Run comprehensive Skonto system test"""
    print("🚀 COMPREHENSIVE SKONTO SYSTEM TEST")
    print("=" * 60)
    print(f"📧 Test email: {TEST_EMAIL}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"📅 Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Track test results
    tests = []
    invoice_id = None
    
    try:
        # Test 1: API Connection
        tests.append(("API Connection", test_api_connection()))
        
        # Test 2: Database Schema
        tests.append(("Database Schema", test_database_schema()))
        
        # Test 3: Create Test Invoice
        invoice_id = create_test_invoice()
        tests.append(("Create Test Invoice", invoice_id is not None))
        
        if invoice_id:
            # Test 4: Skonto Reminder API
            tests.append(("Skonto Reminder API", test_skonto_reminder_api(invoice_id)))
            
            # Test 5: Skonto Due API
            tests.append(("Skonto Due API", test_skonto_due_api()))
            
            # Test 6: Database Updates
            tests.append(("Database Updates", test_database_updates(invoice_id)))
            
            # Test 7: Skonto Decision Processing
            tests.append(("Skonto Decision Processing", test_skonto_decision_simulation(invoice_id)))
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        # Always attempt cleanup
        if invoice_id:
            cleanup_test_data(invoice_id)
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Skonto system is working correctly!")
        print("\n📋 What's been validated:")
        print("   ✅ Database schema with Skonto tracking fields")
        print("   ✅ API endpoints for sending reminders")
        print("   ✅ API endpoints for querying Skonto opportunities")
        print("   ✅ Database updates after reminder sending")
        print("   ✅ Skonto decision processing and savings tracking")
        print(f"\n📧 Check {TEST_EMAIL} for the test reminder email!")
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        print("\n🔧 Common issues:")
        print("   • Backend server not running")
        print("   • Database migration not applied")
        print("   • Environment variables not set")
        print("   • Email service configuration missing")
        return 1

if __name__ == "__main__":
    exit(main())
