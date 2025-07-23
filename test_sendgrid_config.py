#!/usr/bin/env python3
"""
SendGrid Configuration Test
Tests SendGrid API key and email sending functionality
"""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

async def test_sendgrid_api():
    """Test SendGrid API connectivity"""
    
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    
    print("🔧 SendGrid Configuration Test")
    print("=" * 40)
    print(f"API Key: {api_key[:20]}..." if api_key else "Not set")
    print(f"From Email: {from_email}")
    print()
    
    if not api_key or not api_key.startswith('SG.'):
        print("❌ SendGrid API key is not configured or invalid format")
        return False
    
    try:
        # Test SendGrid API with a simple validation call
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test with SendGrid API validation endpoint
        async with aiohttp.ClientSession() as session:
            print("📡 Testing SendGrid API connectivity...")
            
            # Use the API key validation endpoint
            async with session.get(
                'https://api.sendgrid.com/v3/user/profile',
                headers=headers
            ) as response:
                
                if response.status == 200:
                    profile = await response.json()
                    print("✅ SendGrid API key is valid!")
                    print(f"   Account: {profile.get('username', 'Unknown')}")
                    return True
                elif response.status == 401:
                    print("❌ SendGrid API key is invalid or expired")
                    return False
                else:
                    print(f"⚠️  SendGrid API returned status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing SendGrid API: {e}")
        return False

async def test_sendgrid_email_send():
    """Test sending an actual email via SendGrid"""
    
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    
    if not api_key:
        print("❌ No SendGrid API key configured")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Prepare test email
        email_data = {
            "personalizations": [
                {
                    "to": [{"email": from_email, "name": "Test Recipient"}],
                    "subject": "SendGrid Test - Invoice Processor"
                }
            ],
            "from": {"email": from_email, "name": "Invoice Processor"},
            "content": [
                {
                    "type": "text/plain",
                    "value": "This is a test email from the Invoice Processor system.\n\nSendGrid integration is working correctly!\n\nTimestamp: " + str(asyncio.get_event_loop().time())
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            print("📧 Sending test email via SendGrid...")
            
            async with session.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers=headers,
                data=json.dumps(email_data)
            ) as response:
                
                if response.status == 202:
                    print("✅ Test email sent successfully via SendGrid!")
                    return True
                else:
                    print(f"❌ SendGrid email sending failed with status: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error sending email via SendGrid: {e}")
        return False

async def main():
    print("🧪 Testing SendGrid Configuration for Invoice Processor")
    print("=" * 60)
    
    # Test API connectivity
    api_ok = await test_sendgrid_api()
    print()
    
    # Test email sending if API is working
    email_ok = False
    if api_ok:
        email_ok = await test_sendgrid_email_send()
    
    print("\n" + "=" * 60)
    print("📊 SendGrid Test Summary")
    print("=" * 60)
    
    if api_ok and email_ok:
        print("🎉 SendGrid is working perfectly! This should be used as primary email provider.")
    elif api_ok:
        print("✅ SendGrid API is valid, but email sending had issues.")
    else:
        print("❌ SendGrid tests failed. Check API key configuration.")
    
    print("\n💡 Email Provider Priority:")
    print("   1. SendGrid (Primary) - " + ("✅ Working" if api_ok else "❌ Failed"))
    print("   2. SMTP (Fallback) - ❌ Authentication Failed")
    print("\n🔧 Recommendation:")
    if api_ok:
        print("   Use SendGrid as primary. Fix SMTP as backup.")
    else:
        print("   Fix both SendGrid and SMTP configurations.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
