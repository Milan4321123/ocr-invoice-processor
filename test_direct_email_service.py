#!/usr/bin/env python3
"""
Direct Email Service Test
Tests the email service directly to diagnose the issue
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')
sys.path.append('backend/services')

from email_service import EmailService

async def test_email_service_directly():
    """Test the email service directly"""
    
    print("🧪 Testing Email Service Directly")
    print("=" * 50)
    
    # Initialize email service
    try:
        email_service = EmailService()
        print("✅ Email service initialized")
        print(f"   SendGrid API Key: {'Yes' if email_service.sendgrid_api_key else 'No'}")
        print(f"   SMTP Host: {email_service.smtp_host}")
        print(f"   From Email: {email_service.from_email}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize email service: {e}")
        return False
    
    # Test completion notification
    try:
        print("📧 Testing completion notification...")
        
        # Mock invoice data
        test_invoice_data = {
            "id": "test-123",
            "rechnungsnummer": "TEST-001",
            "lieferant": "Test Supplier GmbH",
            "rechnungsdatum": "2025-07-23",
            "rechnungsbetrag": 1500.00,
            "currency": "EUR",
            "file_path": "test/invoice.pdf"
        }
        
        result = await email_service.send_editor_notification(
            invoice_data=test_invoice_data,
            editor_email="incognizant321@gmail.com",
            editor_name="Milan Test User",
            changes_summary=[
                {
                    "field": "Status",
                    "old_value": "Bearbeitung", 
                    "new_value": "Abgeschlossen",
                    "timestamp": "23.07.2025 07:20:00"
                }
            ],
            request_id="TEST-REQ-001",
            is_completion=True
        )
        
        print(f"📧 Email sending result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   Error: {result.get('error')}")
        print(f"   Provider: {result.get('provider')}")
        
        if result.get('success'):
            print("🎉 SUCCESS: Email sent directly!")
            return True
        else:
            print("❌ FAILED: Email not sent")
            return False
            
    except Exception as e:
        print(f"❌ Exception during email test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🔬 Direct Email Service Diagnostic Test")
    print("=" * 60)
    
    success = await test_email_service_directly()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Email service is working correctly!")
        print("   The issue may be in the API endpoint logic")
    else:
        print("❌ Email service has issues!")
        print("   Check SendGrid API key or SMTP configuration")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
