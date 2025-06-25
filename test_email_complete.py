#!/usr/bin/env python3
"""
Test SendGrid with proper fallback (matches your existing code structure)
This test will show you exactly what needs to be fixed for SendGrid
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.services.email_service import EmailService
from datetime import datetime

async def test_email_service_with_fallback():
    """Test your actual EmailService with both SendGrid and SMTP fallback"""
    print("🧪 Testing Your Email Service (SendGrid → SMTP Fallback)")
    print("=" * 60)
    
    # Initialize your actual email service
    email_service = EmailService()
    
    print(f"📧 SendGrid API Key: {'✅ Found' if email_service.sendgrid_api_key else '❌ Missing'}")
    print(f"📧 SMTP Host: {'✅ Found' if email_service.smtp_host else '❌ Missing'}")
    print(f"📧 From Email: {email_service.from_email}")
    print(f"📧 From Name: {email_service.from_name}")
    print()
    
    # Prepare test data (similar to real invoice data)
    test_invoice_data = {
        "id": "test-invoice-123",
        "rechnungsnummer": "INV-2025-TEST",
        "lieferant": "Test Vendor GmbH",
        "rechnungsdatum": "2025-06-25",
        "rechnungsbetrag": "1,250.00",
        "currency": "EUR"
    }
    
    test_changes = [
        {
            "field": "Rechnungsbetrag",
            "old_value": "1,000.00",
            "new_value": "1,250.00",
            "timestamp": datetime.now().isoformat()
        },
        {
            "field": "Lieferant",
            "old_value": "Old Vendor",
            "new_value": "Test Vendor GmbH",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    try:
        print("📤 Sending editor notification email...")
        print("   (This will test SendGrid first, then SMTP if it fails)")
        print()
        
        # Use your actual email service method
        result = await email_service.send_editor_notification(
            invoice_data=test_invoice_data,
            editor_email="adhikarimilan4321@gmail.com",
            editor_name="Milan Adhikari",
            changes_summary=test_changes,
            request_id="test-request-123"
        )
        
        if result["success"]:
            print("🎉 EMAIL SENT SUCCESSFULLY!")
            print(f"📬 Provider Used: {result.get('provider', 'Unknown')}")
            print(f"📬 Message ID: {result.get('message_id', 'N/A')}")
            print()
            print("🔍 Check your email inbox (including spam folder)")
            print("📧 Email sent to: adhikarimilan4321@gmail.com")
            print()
            print("✅ Your email workflow is working!")
            
        else:
            print("❌ EMAIL SENDING FAILED!")
            print(f"🚨 Error: {result.get('error', 'Unknown error')}")
            print()
            print("🔧 Issues to check:")
            if "403" in str(result.get('error', '')):
                print("   1. ⚠️  SendGrid sender verification needed")
                print("      → Go to SendGrid dashboard")
                print("      → Verify adhikarimilan4321@gmail.com as sender")
            elif "SSL" in str(result.get('error', '')):
                print("   1. ⚠️  SSL certificate issue")
                print("      → Try SMTP fallback")
            else:
                print("   1. Check SendGrid API key validity")
                print("   2. Check SMTP credentials")
                print("   3. Check internet connection")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        print()
        print("🔧 This usually means:")
        print("   1. Database method missing (we just fixed this)")
        print("   2. Missing database tables (not critical for email)")
        print("   3. Configuration issue")

if __name__ == "__main__":
    asyncio.run(test_email_service_with_fallback())
