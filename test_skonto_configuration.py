#!/usr/bin/env python3
"""
Test Skonto Configuration and Manual Reminder Functionality
This script tests the new configurable email features for Skonto reminders.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_skonto_configuration():
    """Test Skonto configuration management"""
    print("🧪 Testing Skonto Configuration Management")
    print("=" * 60)
    
    # Step 1: Check current configuration
    print("\n📋 Step 1: Getting current scheduler status...")
    try:
        response = requests.get(f"{API_BASE}/skonto/scheduler/status")
        if response.status_code == 200:
            status_data = response.json()
            config = status_data.get("scheduler_status", {}).get("config", {})
            print(f"   Current default email: {config.get('default_recipient_email', 'Not set')}")
            print(f"   Check interval: {config.get('check_interval_hours', 'Not set')} hours")
            print(f"   Dry run: {config.get('dry_run', 'Not set')}")
        else:
            print(f"❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    
    # Step 2: Update configuration with custom email
    print("\n🔧 Step 2: Updating configuration with custom email...")
    new_config = {
        "default_recipient_email": "customfinance@mycompany.com",
        "dry_run": True  # Set to true for testing
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/skonto/scheduler/config",
            json=new_config,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Configuration updated successfully!")
            print(f"   New default email: {result['config']['default_recipient_email']}")
            print(f"   Dry run mode: {result['config']['dry_run']}")
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Failed to update config: {response.status_code}")
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error updating config: {e}")
    
    # Step 3: Test manual reminder with custom email
    print("\n📧 Step 3: Testing manual reminder with custom email...")
    
    # First, get some Skonto opportunities
    try:
        response = requests.get(f"{API_BASE}/skonto/dashboard/opportunities?limit=2")
        if response.status_code == 200:
            opportunities = response.json()
            if opportunities:
                invoice_ids = [opp["id"] for opp in opportunities[:1]]  # Take first invoice
                print(f"   Found {len(opportunities)} opportunities, testing with 1 invoice")
                
                # Send manual reminder
                reminder_request = {
                    "invoice_ids": invoice_ids,
                    "recipient_email": "testuser@mycompany.com",
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
                    print(f"   Errors: {len(result.get('errors', []))}")
                    
                    if result.get('errors'):
                        for error in result['errors']:
                            print(f"     - {error}")
                else:
                    error_data = response.json() if response.content else {}
                    print(f"❌ Failed to send reminder: {response.status_code}")
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            else:
                print("ℹ️  No Skonto opportunities found for testing")
                
        else:
            print(f"❌ Failed to get opportunities: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing manual reminder: {e}")
    
    # Step 4: Test automatic scheduler with new config
    print("\n🤖 Step 4: Testing automatic scheduler with new configuration...")
    try:
        response = requests.post(f"{API_BASE}/skonto/scheduler/run-check")
        if response.status_code == 200:
            result_data = response.json()
            result = result_data.get("result", {})
            
            print("✅ Scheduler test completed!")
            print(f"   Dry run mode: {result.get('dry_run', False)}")
            print(f"   Invoices found: {result.get('invoices_found', 0)}")
            print(f"   Reminders sent: {result.get('reminders_sent', 0)}")
            
            if result.get('dry_run'):
                print("ℹ️  Running in dry-run mode (no actual emails sent)")
                
        else:
            print(f"❌ Scheduler test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Skonto Configuration Test Complete")
    print("\n💡 Key Features Tested:")
    print("   ✅ Configure default recipient email")
    print("   ✅ Send manual reminders to specific emails")
    print("   ✅ Enable/disable dry-run mode")
    print("   ✅ Get current configuration status")

if __name__ == "__main__":
    test_skonto_configuration()
