#!/usr/bin/env python3
"""
Real Email Test for Completion Flow
Tests the completion email sending to a real email address
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "incognizant321@gmail.com"

async def test_real_completion_email():
    """Test completion email with real recipient"""
    
    print("🧪 Testing Real Completion Email Flow")
    print("=" * 50)
    print(f"📧 Recipient: {TEST_EMAIL}")
    print(f"🔗 API: {API_BASE_URL}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # 1. Get an existing invoice
        print("📋 Step 1: Getting test invoice...")
        async with session.get(f"{API_BASE_URL}/api/invoices") as response:
            if response.status != 200:
                print(f"❌ Failed to get invoices: {response.status}")
                return False
            
            invoices = await response.json()
            if not invoices.get("invoices"):
                print("❌ No invoices found")
                return False
            
            test_invoice = invoices["invoices"][0]
            invoice_id = test_invoice["id"]
            print(f"✅ Using invoice: {invoice_id}")
            print(f"   File: {test_invoice.get('file_name', 'Unknown')}")
            print()
        
        # 2. Prepare completion data with real email
        print("📧 Step 2: Preparing completion data...")
        completion_data = {
            "completion_info": {
                "completed_by": TEST_EMAIL,
                "completed_at": datetime.now().isoformat(),
                "completion_notes": "Real test completion - automated test with actual email"
            },
            "editor_info": {
                "editor_email": TEST_EMAIL,
                "editor_name": "Milan Test User",
                "changes_summary": [
                    {
                        "field": "Status",
                        "old_value": "Bearbeitung",
                        "new_value": "Bearbeitung abgeschlossen",
                        "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    },
                    {
                        "field": "Test Mode",
                        "old_value": "Development",
                        "new_value": "Real Email Test",
                        "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    }
                ]
            }
        }
        
        print(f"✅ Editor Email: {completion_data['editor_info']['editor_email']}")
        print(f"✅ Editor Name: {completion_data['editor_info']['editor_name']}")
        print()
        
        # 3. Send completion request
        print("🚀 Step 3: Sending completion request...")
        async with session.put(
            f"{API_BASE_URL}/api/invoices/{invoice_id}/complete",
            headers={"Content-Type": "application/json"},
            data=json.dumps(completion_data)
        ) as response:
            
            print(f"📡 Response Status: {response.status}")
            
            if response.status == 200:
                result = await response.json()
                print("✅ Completion API call successful!")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Completion Email Sent: {result.get('completion_email_sent')}")
                print(f"   Completion Status: {result.get('completion_status')}")
                print()
                
                if result.get('completion_email_sent'):
                    print("🎉 SUCCESS: Completion email was sent!")
                    print(f"📬 Check your inbox at: {TEST_EMAIL}")
                    print("   Subject should be: ✅ Prüfbericht - Rechnung abgeschlossen")
                    return True
                else:
                    print("❌ ISSUE: Completion email was NOT sent")
                    print("   The API call succeeded but no email was triggered")
                    return False
            else:
                error_data = await response.json()
                print(f"❌ Completion API call failed!")
                print(f"   Status: {response.status}")
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                return False

async def main():
    print("🧪 Real Email Completion Test")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = await test_real_completion_email()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("📧 Check your email inbox for the completion notification")
        print("   If you don't see it, check spam folder")
    else:
        print("❌ TEST FAILED!")
        print("🔧 Check backend logs for email sending errors")
        print("   Possible issues:")
        print("   - SendGrid API key invalid/expired")
        print("   - Email template rendering error")
        print("   - SMTP fallback also failed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
