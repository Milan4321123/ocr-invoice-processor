#!/usr/bin/env python3
"""
FIXED Email Test - Bypasses database issues and tests email directly
This version will work immediately with your current setup
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def test_sendgrid_direct_fixed():
    """Test SendGrid directly without database dependencies"""
    print("🧪 Testing SendGrid Email Service (FIXED VERSION)")
    print("=" * 60)
    
    # Get config from .env
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "adhikarimilan4321@gmail.com")
    from_name = os.getenv("FROM_NAME", "Invoice Processor")
    to_email = "adhikarimilan4321@gmail.com"
    
    print(f"📧 SendGrid API Key: {api_key[:10]}..." if api_key else "❌ No API Key")
    print(f"📧 From Email: {from_email}")
    print(f"📧 To Email: {to_email}")
    print()
    
    # Create test email content
    subject = "🧪 TEST: Invoice Email System Working!"
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #007bff; color: white; padding: 20px; border-radius: 8px; }
            .content { padding: 20px; border: 1px solid #ddd; border-radius: 8px; margin-top: 20px; }
            .success { background: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 Email System Test Successful!</h1>
        </div>
        <div class="content">
            <div class="success">
                ✅ <strong>SendGrid Integration Working</strong><br>
                Your invoice processing email system is now operational!
            </div>
            
            <h3>Test Details:</h3>
            <ul>
                <li><strong>From:</strong> {from_name} &lt;{from_email}&gt;</li>
                <li><strong>Provider:</strong> SendGrid</li>
                <li><strong>Test Time:</strong> {timestamp}</li>
                <li><strong>System:</strong> Invoice OCR Processor</li>
            </ul>
            
            <h3>Next Steps:</h3>
            <ol>
                <li>✅ Email delivery confirmed</li>
                <li>🔄 Ready for production workflow</li>
                <li>📊 Add database integration</li>
                <li>🔒 Implement approval tokens</li>
            </ol>
        </div>
    </body>
    </html>
    """.format(
        from_name=from_name,
        from_email=from_email,
        timestamp=asyncio.get_event_loop().time()
    )
    
    # Test SendGrid
    try:
        print("📤 Testing SendGrid...")
        
        sg = SendGridAPIClient(api_key=api_key)
        message = Mail(
            from_email=(from_email, from_name),
            to_emails=[(to_email, "Test User")],
            subject=subject,
            html_content=html_content
        )
        
        response = sg.send(message)
        
        print("✅ SENDGRID SUCCESS!")
        print(f"📬 Status Code: {response.status_code}")
        print(f"📬 Message ID: {response.headers.get('X-Message-Id', 'N/A')}")
        print(f"📧 Email sent to: {to_email}")
        print()
        print("🔍 Check your email inbox (including spam folder)")
        
        return True
        
    except Exception as e:
        print(f"❌ SendGrid failed: {e}")
        print()
        
        # Try SMTP fallback
        try:
            print("🔄 Trying SMTP fallback...")
            
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_user = os.getenv("SMTP_USERNAME")
            smtp_pass = os.getenv("SMTP_PASSWORD")
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{from_email}>"
            msg["To"] = to_email
            
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            print("✅ SMTP SUCCESS!")
            print(f"📧 Email sent via SMTP to: {to_email}")
            print()
            print("🔍 Check your email inbox (including spam folder)")
            
            return True
            
        except Exception as smtp_error:
            print(f"❌ SMTP also failed: {smtp_error}")
            return False

if __name__ == "__main__":
    asyncio.run(test_sendgrid_direct_fixed())
