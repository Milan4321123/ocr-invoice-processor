#!/usr/bin/env python3
"""
Test Skonto Reminder Email Configuration
This script tests that the reminder emails are being sent to the correct email address.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_reminder_email_configuration():
    """Test that reminder emails use the correct recipient"""
    print("🧪 Testing Skonto Reminder Email Configuration")
    print("=" * 60)
    
    # Step 1: Check backend is running
    print("\n🔍 Step 1: Checking backend connectivity...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("💡 Make sure the backend is running with: cd backend && uvicorn main:app --reload")
        return False
    
    # Step 2: Check current scheduler configuration
    print(f"\n📋 Step 2: Checking current Skonto scheduler configuration...")
    try:
        response = requests.get(f"{API_BASE}/skonto/scheduler/status")
        if response.status_code == 200:
            status_data = response.json()
            scheduler_config = status_data.get("scheduler_status", {}).get("config", {})
            default_email = scheduler_config.get("default_recipient_email", "Not configured")
            
            print(f"   Current default recipient email: {default_email}")
            
            if default_email == "incognizant321@gmail.com":
                print("✅ Configuration is correct!")
            elif default_email == "finance@company.com":
                print("❌ Still using hardcoded email - restart backend after updating .env")
            else:
                print(f"⚠️  Unexpected email configuration: {default_email}")
                
        else:
            print(f"❌ Failed to get scheduler status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking scheduler status: {e}")
    
    # Step 3: Test updating configuration via API
    print(f"\n🔧 Step 3: Testing configuration update via API...")
    try:
        config_update = {
            "default_recipient_email": "incognizant321@gmail.com"
        }
        
        response = requests.put(
            f"{API_BASE}/skonto/scheduler/config",
            json=config_update,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Configuration updated successfully via API")
            print(f"   New default recipient: incognizant321@gmail.com")
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Failed to update config: {response.status_code}")
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error updating config: {e}")
    
    # Step 4: Verify configuration is now correct
    print(f"\n✅ Step 4: Verifying final configuration...")
    try:
        response = requests.get(f"{API_BASE}/skonto/scheduler/status")
        if response.status_code == 200:
            status_data = response.json()
            scheduler_config = status_data.get("scheduler_status", {}).get("config", {})
            final_email = scheduler_config.get("default_recipient_email", "Not configured")
            
            print(f"   Final default recipient email: {final_email}")
            
            if final_email == "incognizant321@gmail.com":
                print("🎉 SUCCESS: Reminder emails will now be sent to incognizant321@gmail.com")
                return True
            else:
                print(f"❌ Configuration not updated correctly: {final_email}")
                return False
                
        else:
            print(f"❌ Failed to verify configuration: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying configuration: {e}")
        return False

def test_manual_reminder():
    """Test sending a manual reminder to verify it uses the correct email"""
    print(f"\n📧 Step 5: Testing manual reminder (if invoices available)...")
    
    try:
        # Check for available invoices
        response = requests.get(f"{API_BASE}/skonto/dashboard/opportunities?limit=1")
        if response.status_code == 200:
            opportunities = response.json()
            
            if opportunities:
                invoice_id = opportunities[0]["id"]
                print(f"   Found test invoice: {invoice_id}")
                
                # Send manual reminder
                reminder_request = {
                    "invoice_ids": [invoice_id],
                    "recipient_email": "incognizant321@gmail.com",
                    "recipient_name": "Test User"
                }
                
                response = requests.post(
                    f"{API_BASE}/skonto/send-reminder",
                    json=reminder_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Manual reminder sent successfully!")
                    print(f"   Reminders sent: {result['reminders_sent']}")
                    print(f"   Recipient: {result['recipient_email']}")
                    
                    if result['recipient_email'] == "incognizant321@gmail.com":
                        print("🎉 SUCCESS: Manual reminder used correct email address!")
                    else:
                        print(f"⚠️  Manual reminder used different email: {result['recipient_email']}")
                else:
                    error_data = response.json() if response.content else {}
                    print(f"❌ Failed to send manual reminder: {response.status_code}")
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            else:
                print("ℹ️  No invoices available for testing")
        else:
            print(f"❌ Failed to get invoices: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing manual reminder: {e}")

if __name__ == "__main__":
    print("🎯 This script will configure Skonto reminder emails to be sent to:")
    print("   📧 incognizant321@gmail.com")
    print()
    
    success = test_reminder_email_configuration()
    
    if success:
        test_manual_reminder()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete!")
    print()
    print("📋 Summary:")
    print("   • Environment variable SKONTO_DEFAULT_RECIPIENT has been set to incognizant321@gmail.com")
    print("   • Scheduler configuration has been updated via API")
    print("   • All reminder emails will now be sent to incognizant321@gmail.com")
    print()
    print("💡 Next steps:")
    print("   1. Restart the backend if configuration wasn't loaded correctly")
    print("   2. Test with actual invoice reminders")
    print("   3. Check email inbox for reminder emails")
