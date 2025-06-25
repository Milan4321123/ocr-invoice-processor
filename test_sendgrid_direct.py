#!/usr/bin/env python3
"""
Direct SendGrid email test - tests SendGrid configuration without database dependencies
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.email_service import EmailService
import asyncio

async def test_sendgrid_direct():
    """Test SendGrid email sending directly"""
    print("🧪 Testing SendGrid Email Service")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailService()
    
    # Test email data
    test_data = {
        "invoice_id": "TEST-001",
        "editor_email": "adhikarimilan4321@gmail.com",
        "editor_name": "Milan Adhikari",
        "invoice_number": "INV-2025-001",
        "vendor_name": "Test Vendor GmbH",
        "invoice_amount": "€1,250.00",
        "changes_summary": [
            {
                "field": "Rechnungsbetrag",
                "old_value": "€1,000.00",
                "new_value": "€1,250.00",
                "timestamp": "2025-06-25T10:30:00"
            },
            {
                "field": "Lieferant",
                "old_value": "Old Vendor",
                "new_value": "Test Vendor GmbH",
                "timestamp": "2025-06-25T10:31:00"
            }
        ]
    }
    
    try:
        print(f"📧 Sending test email to: {test_data['editor_email']}")
        print(f"📋 Invoice: {test_data['invoice_number']}")
        print(f"🏢 Vendor: {test_data['vendor_name']}")
        print(f"💰 Amount: {test_data['invoice_amount']}")
        print()
        
        # Send the email
        result = await email_service.send_editor_notification(
            invoice_data=test_data,
            editor_email=test_data['editor_email'],
            editor_name=test_data['editor_name'],
            changes_summary=test_data['changes_summary']
        )
        
        if result['success']:
            print("✅ EMAIL SENT SUCCESSFULLY!")
            print(f"📬 Message ID: {result.get('message_id', 'N/A')}")
            print(f"📧 Provider: {result.get('provider', 'N/A')}")
            print()
            print("🔍 Check your email inbox (including spam folder)")
            print("📧 Email sent to: adhikarimilan4321@gmail.com")
        else:
            print("❌ EMAIL SENDING FAILED!")
            print(f"🚨 Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sendgrid_direct())
