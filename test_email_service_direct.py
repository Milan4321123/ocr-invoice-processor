#!/usr/bin/env python3
"""
Test the email service directly to debug SendGrid issues
"""

import asyncio
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
sys.path.insert(0, 'backend')

from services.email_service import EmailService

async def test_email_service_direct():
    """Test the email service directly"""
    print("🧪 Testing EmailService directly...")
    
    # Initialize email service
    email_service = EmailService()
    
    # Check configuration
    print(f"SendGrid API Key configured: {'Yes' if email_service.sendgrid_api_key else 'No'}")
    print(f"SMTP Host configured: {'Yes' if email_service.smtp_host else 'No'}")
    print(f"From Email: {email_service.from_email}")
    
    if email_service.sendgrid_api_key:
        print(f"SendGrid API Key (first 20 chars): {email_service.sendgrid_api_key[:20]}...")
    
    print()
    
    # Test data
    test_invoice_data = {
        "id": "test-123",
        "rechnungsempfaenger": "Test Company",
        "rechnungssteller": "Test Supplier",
        "projekt": "Test Project",
        "gewerk": "Elektro",
        "rechnungsbetrag": "1500.00",
        "file_path": "test.pdf"
    }
    
    test_email = "test@company.de"
    test_name = "Test Editor"
    
    print(f"Attempting to send completion email to: {test_email}")
    
    try:
        # Test the send_editor_notification method directly
        result = await email_service.send_editor_notification(
            invoice_data=test_invoice_data,
            editor_email=test_email,
            editor_name=test_name,
            changes_summary=[
                {
                    "field": "Status",
                    "old_value": "Bearbeitung",
                    "new_value": "Abgeschlossen",
                    "timestamp": "23.07.2025 06:55:00"
                }
            ],
            request_id="test-request",
            is_completion=True
        )
        
        print(f"Email send result: {result}")
        
        if result["success"]:
            print("✅ Email sent successfully!")
            print(f"   Provider: {result.get('provider', 'unknown')}")
            print(f"   Message ID: {result.get('message_id', 'none')}")
        else:
            print("❌ Email sending failed!")
            print(f"   Error: {result.get('error', 'unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during email sending: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_sendgrid_directly():
    """Test SendGrid API directly to isolate issues"""
    print("\n🧪 Testing SendGrid API directly...")
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # Read API key from environment
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            # Try reading from .env file
            env_path = "backend/.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('SENDGRID_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            break
        
        if not api_key:
            print("❌ No SendGrid API key found")
            return
            
        print(f"Using API key: {api_key[:20]}...")
        
        # Create SendGrid client
        sg = SendGridAPIClient(api_key=api_key)
        
        # Create test email
        message = Mail(
            from_email="noreply@company.com",
            to_emails="test@company.de",
            subject="SendGrid Test Email",
            html_content="<h1>Test email from SendGrid</h1><p>This is a test.</p>"
        )
        
        # Send email
        print("Attempting to send test email via SendGrid...")
        response = sg.send(message)
        
        print(f"SendGrid response status: {response.status_code}")
        print(f"SendGrid response headers: {response.headers}")
        print(f"SendGrid response body: {response.body}")
        
        if response.status_code == 202:
            print("✅ SendGrid test email sent successfully!")
        else:
            print("❌ SendGrid test email failed!")
            
    except Exception as e:
        print(f"❌ SendGrid direct test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test runner"""
    print("🚀 Starting Direct Email Service Test...")
    print("=" * 60)
    
    await test_email_service_direct()
    await test_sendgrid_directly()
    
    print("\n" + "=" * 60)
    print("📊 Direct email testing completed")

if __name__ == "__main__":
    asyncio.run(main())
