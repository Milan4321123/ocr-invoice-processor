#!/usr/bin/env python3
"""
Debug Completion Email Flow
Tests the completion flow with detailed error tracking
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "incognizant321@gmail.com"

async def debug_completion_flow():
    """Debug the completion flow step by step"""
    
    print("🔍 Debug Completion Email Flow")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Get an invoice
        async with session.get(f"{API_BASE_URL}/api/invoices") as response:
            invoices = await response.json()
            invoice_id = invoices["invoices"][0]["id"]
            print(f"📋 Using invoice: {invoice_id}")
        
        # Try a minimal completion first (without editor info)
        print("\n🧪 Test 1: Completion without editor info")
        minimal_data = {
            "completion_info": {
                "completed_by": TEST_EMAIL,
                "completion_notes": "Minimal test"
            }
        }
        
        async with session.put(
            f"{API_BASE_URL}/api/invoices/{invoice_id}/complete",
            headers={"Content-Type": "application/json"},
            data=json.dumps(minimal_data)
        ) as response:
            result = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Email sent: {result.get('completion_email_sent', 'N/A')}")
        
        # Try with editor info but minimal data
        print("\n🧪 Test 2: Completion with minimal editor info")
        minimal_editor_data = {
            "completion_info": {
                "completed_by": TEST_EMAIL,
                "completion_notes": "Minimal editor test"
            },
            "editor_info": {
                "editor_email": TEST_EMAIL,
                "editor_name": "Test User"
            }
        }
        
        async with session.put(
            f"{API_BASE_URL}/api/invoices/{invoice_id}/complete",
            headers={"Content-Type": "application/json"},
            data=json.dumps(minimal_editor_data)
        ) as response:
            result = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Email sent: {result.get('completion_email_sent', 'N/A')}")
        
        # Try with full editor info
        print("\n🧪 Test 3: Completion with full editor info")
        full_data = {
            "completion_info": {
                "completed_by": TEST_EMAIL,
                "completion_notes": "Full test with all data"
            },
            "editor_info": {
                "editor_email": TEST_EMAIL,
                "editor_name": "Test User Full",
                "changes_summary": [
                    {
                        "field": "test_field",
                        "old_value": "old",
                        "new_value": "new",
                        "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    }
                ]
            }
        }
        
        async with session.put(
            f"{API_BASE_URL}/api/invoices/{invoice_id}/complete",
            headers={"Content-Type": "application/json"},
            data=json.dumps(full_data)
        ) as response:
            result = await response.json()
            print(f"   Status: {response.status}")
            print(f"   Email sent: {result.get('completion_email_sent', 'N/A')}")
            print(f"   Full response: {json.dumps(result, indent=2)}")
        
        # Test SendGrid directly
        print("\n🧪 Test 4: Direct SendGrid test")
        try:
            test_sendgrid_data = {
                "to_email": TEST_EMAIL,
                "subject": "Direct SendGrid Test",
                "content": "This is a direct test of SendGrid from the Invoice Processor"
            }
            
            # This endpoint doesn't exist, but let's try anyway
            async with session.post(
                f"{API_BASE_URL}/api/test-email",
                headers={"Content-Type": "application/json"},
                data=json.dumps(test_sendgrid_data)
            ) as response:
                print(f"   Direct email test status: {response.status}")
                if response.status != 404:
                    result = await response.json()
                    print(f"   Result: {result}")
                else:
                    print("   Direct email endpoint not available (expected)")
        except Exception as e:
            print(f"   Direct email test error: {e}")

async def main():
    print("🔬 Debug Completion Email Flow")
    print("=" * 60)
    
    await debug_completion_flow()
    
    print("\n" + "=" * 60)
    print("🎯 Key Findings:")
    print("   - Check which test scenarios trigger emails")
    print("   - Look for patterns in success/failure")
    print("   - Minimal vs full data comparison")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
