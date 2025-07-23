#!/usr/bin/env python3
"""
Enhanced Completion Test with Detailed Error Logging
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "incognizant321@gmail.com"

async def test_with_error_logging():
    """Test completion with enhanced error details"""
    
    print("🔍 Enhanced Completion Test")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Get invoice
        async with session.get(f"{API_BASE_URL}/api/invoices") as response:
            invoices = await response.json()
            invoice_id = invoices["invoices"][0]["id"]
            invoice_data = invoices["invoices"][0]
            
            print(f"📋 Using invoice: {invoice_id}")
            print(f"   File: {invoice_data.get('file_name', 'N/A')}")
            print(f"   Status: {invoice_data.get('status', 'N/A')}")
            print(f"   Review Status: {invoice_data.get('review_status', 'N/A')}")
            print()
        
        # Test completion with detailed request
        completion_data = {
            "completion_info": {
                "completed_by": TEST_EMAIL,
                "completed_at": datetime.now().isoformat(),
                "completion_notes": "Enhanced test with full logging"
            },
            "editor_info": {
                "editor_email": TEST_EMAIL,
                "editor_name": "Milan Enhanced Test",
                "changes_summary": [
                    {
                        "field": "Status",
                        "old_value": "Bearbeitung",
                        "new_value": "Abgeschlossen",
                        "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    }
                ]
            }
        }
        
        print("🚀 Sending enhanced completion request...")
        print(f"📧 Target email: {TEST_EMAIL}")
        print(f"👤 Editor name: {completion_data['editor_info']['editor_name']}")
        print()
        
        async with session.put(
            f"{API_BASE_URL}/api/invoices/{invoice_id}/complete",
            headers={"Content-Type": "application/json"},
            data=json.dumps(completion_data)
        ) as response:
            
            print(f"📡 Response Status: {response.status}")
            
            if response.status == 200:
                result = await response.json()
                print("✅ API call successful")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Invoice ID: {result.get('invoice_id')}")
                print(f"   Completion Status: {result.get('completion_status')}")
                print(f"   Completed At: {result.get('completed_at')}")
                print(f"   📧 Completion Email Sent: {result.get('completion_email_sent')}")
                print(f"   Email Note: {result.get('email_note', 'N/A')}")
                
                if result.get('completion_email_sent'):
                    print("\n🎉 SUCCESS: Email was sent!")
                    print(f"   Check inbox at: {TEST_EMAIL}")
                    return True
                else:
                    print("\n❌ EMAIL NOT SENT")
                    print("   Possible reasons:")
                    print("   1. Template rendering failed")
                    print("   2. SendGrid call failed (despite working in isolation)")
                    print("   3. Data validation failed")
                    print("   4. Exception caught and logged as warning")
                    return False
            else:
                error_data = await response.json()
                print(f"❌ API call failed: {response.status}")
                print(f"   Error: {error_data}")
                return False

async def main():
    print("🔬 Enhanced Completion Email Test")
    print("=" * 60)
    print("This test will:")
    print("✓ Use a real invoice from your database")
    print("✓ Send to your actual email address")
    print("✓ Provide detailed error analysis")
    print("=" * 60)
    
    success = await test_with_error_logging()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if success:
        print("🎉 Email sending is working!")
        print("📧 Check your email inbox for the completion notification")
    else:
        print("❌ Email sending is failing in the completion flow")
        print()
        print("🔧 NEXT STEPS TO FIX:")
        print("1. Check backend console/logs for error messages")
        print("2. Verify template rendering with invoice data")
        print("3. Check email service initialization in API context")
        print("4. Test email service imports and dependencies")
        print()
        print("💡 Since SendGrid works in isolation, the issue is likely:")
        print("   - Template data formatting")
        print("   - Missing invoice fields required by template")
        print("   - Import/dependency issue in the completion endpoint")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
