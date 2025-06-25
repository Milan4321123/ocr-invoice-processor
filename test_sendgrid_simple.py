#!/usr/bin/env python3
"""
Simple SendGrid email test - bypasses database issues
"""
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sendgrid_simple():
    """Test SendGrid email sending with minimal setup"""
    print("🧪 Simple SendGrid Test")
    print("=" * 40)
    
    # Get configuration from .env
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    from_name = os.getenv("FROM_NAME", "Invoice Processor")
    
    print(f"📧 SendGrid API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"📧 From Email: {from_email}")
    print(f"📧 From Name: {from_name}")
    print()
    
    if not api_key:
        print("❌ SENDGRID_API_KEY not found in .env file")
        return
    
    try:
        # Create email message
        message = Mail(
            from_email=(from_email, from_name),
            to_emails='adhikarimilan4321@gmail.com',
            subject='🧪 Test Email - Invoice Processor',
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="color: #007bff; margin: 0;">✅ Email Test Successful!</h1>
                    <p style="margin: 10px 0 0 0; color: #666;">Your SendGrid configuration is working correctly.</p>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <h2>🔧 Configuration Test Results</h2>
                    <ul style="color: #333;">
                        <li>✅ SendGrid API Key: Valid</li>
                        <li>✅ Email Service: Connected</li>
                        <li>✅ HTML Rendering: Working</li>
                        <li>✅ Professional Formatting: Active</li>
                    </ul>
                    
                    <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>🎉 Success!</strong> Your invoice email system is ready for production use.
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; color: #666;">
                    <p><strong>Test sent:</strong> {}</p>
                    <p><strong>System:</strong> OCR Invoice Processor</p>
                    <p>This is an automated test email to verify your email configuration.</p>
                </div>
            </div>
            """.format(os.popen('date').read().strip())
        )
        
        # Send via SendGrid
        print("📤 Sending email via SendGrid...")
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        print(f"✅ EMAIL SENT SUCCESSFULLY!")
        print(f"📬 Status Code: {response.status_code}")
        print(f"📧 Message ID: {response.headers.get('X-Message-Id', 'N/A')}")
        print()
        print("🔍 Check your email inbox (and spam folder)")
        print("📧 Email sent to: adhikarimilan4321@gmail.com")
        
    except Exception as e:
        print(f"❌ SendGrid test failed: {e}")
        print()
        print("🔧 Possible solutions:")
        print("1. Check your SendGrid API key")
        print("2. Verify your email is verified in SendGrid")
        print("3. Check your internet connection")

if __name__ == "__main__":
    test_sendgrid_simple()
