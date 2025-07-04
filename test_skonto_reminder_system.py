#!/usr/bin/env python3
"""
Test Skonto Reminder Logic
This script tests the Skonto reminder sending functionality.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_skonto_reminder_system():
    """Test the Skonto reminder system functionality"""
    print("🧪 Testing Skonto Reminder System")
    print("=" * 50)
    
    # Step 1: Check if backend is running
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
        return False
    
    # Step 2: Check scheduler status
    print("\n📊 Step 2: Checking Skonto scheduler status...")
    try:
        response = requests.get(f"{API_BASE}/skonto/scheduler/status")
        if response.status_code == 200:
            status_data = response.json()
            scheduler_status = status_data.get("scheduler_status", {})
            
            print(f"   Enabled: {scheduler_status.get('enabled', 'Unknown')}")
            print(f"   Running: {scheduler_status.get('is_running', 'Unknown')}")
            print(f"   Last run: {scheduler_status.get('last_run', 'Never')}")
            print(f"   Total runs: {scheduler_status.get('stats', {}).get('total_runs', 0)}")
            print(f"   Total reminders sent: {scheduler_status.get('stats', {}).get('total_reminders_sent', 0)}")
            print(f"   Total errors: {scheduler_status.get('stats', {}).get('total_errors', 0)}")
            
            if not scheduler_status.get('enabled'):
                print("⚠️  Scheduler is disabled")
            elif not scheduler_status.get('is_running'):
                print("⚠️  Scheduler is not running")
            else:
                print("✅ Scheduler appears to be working")
                
        else:
            print(f"❌ Failed to get scheduler status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking scheduler status: {e}")
    
    # Step 3: Check for current Skonto opportunities
    print("\n📋 Step 3: Checking current Skonto opportunities...")
    try:
        response = requests.get(f"{API_BASE}/skonto/dashboard/opportunities?limit=10")
        if response.status_code == 200:
            opportunities = response.json()
            print(f"   Found {len(opportunities)} Skonto opportunities")
            
            if opportunities:
                print("   Top opportunities:")
                for i, opp in enumerate(opportunities[:3], 1):
                    print(f"   {i}. Invoice: {opp.get('invoice_number', 'N/A')}")
                    print(f"      Amount: €{opp.get('amount', 0)}")
                    print(f"      Skonto: {opp.get('skonto_percentage', 0)}%")
                    print(f"      Due date: {opp.get('skonto_date', 'N/A')}")
                    print(f"      Days until expiry: {opp.get('days_until_expiry', 'N/A')}")
                    print(f"      Reminder sent: {opp.get('reminder_sent', False)}")
                    print(f"      Potential savings: €{opp.get('potential_savings', 0)}")
                    print()
            else:
                print("   No Skonto opportunities found")
                
        else:
            print(f"❌ Failed to get opportunities: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting opportunities: {e}")
    
    # Step 4: Test manual reminder check
    print("\n🔧 Step 4: Testing manual reminder check...")
    try:
        print("   Triggering manual Skonto reminder check...")
        response = requests.post(f"{API_BASE}/skonto/scheduler/run-check")
        
        if response.status_code == 200:
            result_data = response.json()
            result = result_data.get("result", {})
            
            print("✅ Manual check completed successfully")
            print(f"   Enabled: {result.get('enabled', 'Unknown')}")
            print(f"   Duration: {result.get('duration_seconds', 0):.2f} seconds")
            print(f"   Invoices found: {result.get('invoices_found', 0)}")
            print(f"   Reminders sent: {result.get('reminders_sent', 0)}")
            print(f"   Errors: {len(result.get('errors', []))}")
            print(f"   Dry run: {result.get('dry_run', False)}")
            
            if result.get('errors'):
                print("   Errors encountered:")
                for error in result.get('errors', []):
                    print(f"     - {error}")
                    
            if result.get('reminders_sent', 0) > 0:
                print("✅ Reminders were sent successfully!")
            elif result.get('invoices_found', 0) == 0:
                print("ℹ️  No invoices found requiring reminders")
            elif result.get('dry_run'):
                print("ℹ️  Running in dry-run mode (no emails actually sent)")
            else:
                print("⚠️  No reminders sent (check logs for details)")
                
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Manual check failed: {response.status_code}")
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error running manual check: {e}")
    
    # Step 5: Check email service configuration
    print("\n📧 Step 5: Checking email service configuration...")
    try:
        # This is indirect - we'll check if there are any email-related health indicators
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("   Email configuration check:")
            print("   Note: Check backend logs for email provider status")
            print("   Recommended: Verify SENDGRID_API_KEY or SMTP settings in backend/.env")
        
    except Exception as e:
        print(f"❌ Error checking email configuration: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Skonto Reminder System Test Complete")
    print("\n💡 To verify email sending:")
    print("   1. Check backend logs for email provider initialization")
    print("   2. Ensure valid email credentials in backend/.env")
    print("   3. Create test invoices with upcoming Skonto dates")
    print("   4. Run manual check and monitor logs")

if __name__ == "__main__":
    test_skonto_reminder_system()
