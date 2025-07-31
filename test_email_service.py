#!/usr/bin/env python3
"""
Test email service functionality
"""

import requests
import json

# Test email functionality
BACKEND_URL = "http://localhost:8000"

def test_email_service():
    print("🧪 Testing Email Service")
    print("=" * 40)
    
    # First authenticate
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BACKEND_URL}/api/auth/token", json=login_data, timeout=10)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
            
            # Check if there are any invoices to test with
            invoices_response = requests.get(f"{BACKEND_URL}/api/invoices", headers=headers, timeout=10)
            
            if invoices_response.status_code == 200:
                invoices_data = invoices_response.json()
                invoices = invoices_data.get("invoices", [])
                
                if invoices:
                    invoice_id = invoices[0]["id"]
                    print(f"✅ Found invoice for testing: {invoice_id}")
                    
                    # Test editor notification email (this is typically what fails)
                    email_data = {
                        "invoice_id": invoice_id,
                        "editor_email": "incognizant321@gmail.com",
                        "editor_name": "Test User",
                        "changes_summary": [
                            {"field": "rechnungsbetrag", "old_value": "", "new_value": "1000.00"}
                        ]
                    }
                    
                    print("📧 Testing editor notification email...")
                    email_response = requests.post(
                        f"{BACKEND_URL}/api/email/editor-notification",
                        json=email_data,
                        headers=headers,
                        timeout=30
                    )
                    
                    print(f"Email API Status: {email_response.status_code}")
                    if email_response.status_code == 200:
                        print("✅ Email service working!")
                        print(f"Response: {email_response.json()}")
                    else:
                        print("❌ Email service failed")
                        print(f"Error: {email_response.text}")
                        
                        # Check backend logs for email errors
                        print("\n🔍 Possible issues:")
                        print("1. SendGrid API key invalid")
                        print("2. Email service disabled in config")
                        print("3. Network connectivity issues")
                        print("4. SMTP configuration problems")
                else:
                    print("⚠️ No invoices found - create a test invoice first")
            else:
                print(f"❌ Failed to get invoices: {invoices_response.status_code}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == "__main__":
    test_email_service()
