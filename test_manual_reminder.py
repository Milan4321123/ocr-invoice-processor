#!/usr/bin/env python3
"""
Test Manual Skonto Reminder with Specific Email
This script tests sending a manual reminder to verify the email address.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_manual_reminder_with_specific_email():
    """Test sending a manual reminder to the specific email address"""
    print("🧪 Testing Manual Skonto Reminder")
    print("=" * 50)
    
    # First, get some available invoices
    try:
        print("📋 Getting available invoices...")
        response = requests.get(f"{API_BASE}/skonto/dashboard/opportunities?limit=5")
        
        if response.status_code == 200:
            opportunities = response.json()
            print(f"   Found {len(opportunities)} Skonto opportunities")
            
            if opportunities:
                # Take the first invoice for testing
                test_invoice = opportunities[0]
                invoice_id = test_invoice["id"]
                
                print(f"   Using invoice: {invoice_id}")
                print(f"   Invoice number: {test_invoice.get('invoice_number', 'N/A')}")
                print(f"   Amount: €{test_invoice.get('amount', 0)}")
                print(f"   Potential savings: €{test_invoice.get('potential_savings', 0)}")
                
                # Send manual reminder to specific email
                print(f"\n📧 Sending manual reminder to incognizant321@gmail.com...")
                
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
                    print(f"   Total invoices: {result['total_invoices']}")
                    print(f"   Recipient email: {result['recipient_email']}")
                    print(f"   Errors: {len(result.get('errors', []))}")
                    
                    if result.get('errors'):
                        print("   Errors encountered:")
                        for error in result['errors']:
                            print(f"     - {error}")
                    
                    if result['recipient_email'] == "incognizant321@gmail.com":
                        print("\n🎉 SUCCESS: Reminder was sent to the correct email address!")
                        print("   Check your inbox at incognizant321@gmail.com for the reminder email")
                    else:
                        print(f"\n⚠️  Warning: Email was sent to {result['recipient_email']} instead")
                        
                else:
                    error_data = response.json() if response.content else {}
                    print(f"❌ Failed to send reminder: {response.status_code}")
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                    
            else:
                print("ℹ️  No Skonto opportunities found")
                print("   You may need to create test invoices with Skonto data")
                
        else:
            print(f"❌ Failed to get opportunities: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_invoice_reminder():
    """Test sending reminder directly to an invoice"""
    print(f"\n📧 Testing direct invoice reminder...")
    
    try:
        # Get any completed invoice for testing
        response = requests.get(f"{API_BASE}/invoices?limit=5")
        
        if response.status_code == 200:
            invoices = response.json()
            
            # Find an invoice with Skonto data
            test_invoice = None
            for invoice in invoices:
                if invoice.get('skonto_datum') and invoice.get('skonto_prozent'):
                    test_invoice = invoice
                    break
            
            if test_invoice:
                invoice_id = test_invoice['id']
                print(f"   Using invoice: {invoice_id}")
                
                # Send reminder with explicit recipient email
                response = requests.post(
                    f"{API_BASE}/invoices/{invoice_id}/send-skonto-reminder?recipient_email=incognizant321@gmail.com&recipient_name=Test+User"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Direct invoice reminder sent!")
                    print(f"   Invoice ID: {result['invoice_id']}")
                    print(f"   Recipient: {result['recipient_email']}")
                    print(f"   Message ID: {result.get('message_id', 'N/A')}")
                    
                    if result['recipient_email'] == "incognizant321@gmail.com":
                        print("\n🎉 SUCCESS: Direct reminder sent to correct email!")
                    
                else:
                    error_data = response.json() if response.content else {}
                    print(f"❌ Failed to send direct reminder: {response.status_code}")
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            else:
                print("ℹ️  No invoices with Skonto data found")
        else:
            print(f"❌ Failed to get invoices: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing direct reminder: {e}")

if __name__ == "__main__":
    print("🎯 Testing Skonto Reminder Email Functionality")
    print("   Target email: incognizant321@gmail.com")
    print()
    
    test_manual_reminder_with_specific_email()
    test_direct_invoice_reminder()
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")
    print()
    print("📋 Key Points:")
    print("   • Manual reminders can be sent to any specified email address")
    print("   • Direct invoice reminders also accept a recipient_email parameter")
    print("   • The system will use incognizant321@gmail.com when specified")
    print("   • Check the email inbox for the actual reminder messages")
    print()
    print("💡 To ensure all automatic reminders use incognizant321@gmail.com:")
    print("   1. Environment variable SKONTO_DEFAULT_RECIPIENT is set correctly")
    print("   2. Manual reminders can always override the recipient")
    print("   3. Check email provider logs for delivery status")
