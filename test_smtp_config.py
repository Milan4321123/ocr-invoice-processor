#!/usr/bin/env python3
"""
SMTP Configuration Test
Tests SMTP authentication and email sending functionality
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def test_smtp_authentication():
    """Test SMTP authentication with Gmail"""
    
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    print("🔧 SMTP Configuration Test")
    print("=" * 40)
    print(f"Host: {smtp_host}")
    print(f"Port: {smtp_port}")
    print(f"Username: {smtp_username}")
    print(f"Password: {'*' * len(smtp_password) if smtp_password else 'Not set'}")
    print()
    
    try:
        # Create SMTP connection
        print("📡 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        
        # Enable security
        print("🔒 Starting TLS encryption...")
        server.starttls()
        
        # Login
        print("🔑 Authenticating with credentials...")
        server.login(smtp_username, smtp_password)
        
        print("✅ SMTP Authentication successful!")
        
        # Test sending an email
        print("📧 Sending test email...")
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = smtp_username  # Send to self for testing
        msg['Subject'] = "SMTP Test - Invoice Processor"
        
        body = """
        This is a test email from the Invoice Processor system.
        
        SMTP Configuration is working correctly!
        
        Timestamp: """ + str(os.popen('date').read().strip()) + """
        
        Best regards,
        Invoice Processor System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(smtp_username, smtp_username, text)
        
        print("✅ Test email sent successfully!")
        
        server.quit()
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication failed: {e}")
        print("💡 Check if:")
        print("   - Username and password are correct")
        print("   - 2-factor authentication is enabled (use app password)")
        print("   - 'Less secure app access' is enabled (if not using app password)")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

def test_gmail_app_password_format():
    """Test if the password looks like a Gmail app password"""
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_password:
        print("❌ No SMTP password configured")
        return False
    
    # Gmail app passwords are 16 characters, all lowercase, with spaces every 4 chars
    # Example: "abcd efgh ijkl mnop"
    
    # Remove spaces for analysis
    clean_password = smtp_password.replace(' ', '')
    
    print("🔍 Password Format Analysis:")
    print(f"   Length: {len(smtp_password)} characters")
    print(f"   Clean Length: {len(clean_password)} characters")
    print(f"   Has spaces: {'Yes' if ' ' in smtp_password else 'No'}")
    print(f"   All lowercase: {'Yes' if clean_password.islower() else 'No'}")
    print(f"   All alphanumeric: {'Yes' if clean_password.isalnum() else 'No'}")
    
    if len(clean_password) == 16 and clean_password.islower() and clean_password.isalnum():
        print("✅ Password format looks like a valid Gmail App Password")
        return True
    else:
        print("⚠️  Password format doesn't match typical Gmail App Password format")
        print("💡 Gmail App Passwords should be:")
        print("   - 16 characters long")
        print("   - All lowercase letters and numbers")
        print("   - Usually formatted with spaces every 4 characters")
        return False

if __name__ == "__main__":
    print("🧪 Testing SMTP Configuration for Invoice Processor")
    print("=" * 60)
    
    # Test password format
    password_format_ok = test_gmail_app_password_format()
    print()
    
    # Test SMTP authentication
    smtp_ok = test_smtp_authentication()
    
    print("\n" + "=" * 60)
    print("📊 SMTP Test Summary")
    print("=" * 60)
    
    if password_format_ok and smtp_ok:
        print("🎉 All SMTP tests passed! Email sending should work correctly.")
    elif smtp_ok:
        print("✅ SMTP authentication works, but password format is unusual.")
    else:
        print("❌ SMTP tests failed. Email sending will not work.")
        print("\n💡 To fix Gmail SMTP issues:")
        print("   1. Enable 2-Factor Authentication on your Gmail account")
        print("   2. Generate an App Password for 'Mail'")
        print("   3. Use the App Password (not your regular password)")
        print("   4. Format: 'abcd efgh ijkl mnop' (with spaces)")
    
    print("=" * 60)
