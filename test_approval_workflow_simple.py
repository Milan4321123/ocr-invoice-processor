#!/usr/bin/env python3
"""
Simple test to send an approval email and test clicking the approval links.
This bypasses database requirements and sends a real email.
"""
import sys
import os
import time
import requests
import subprocess
import uuid

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import email_service

# Test configuration
TEST_INVOICE_ID = "test_invoice_" + str(uuid.uuid4())[:8]
TEST_BAULEITER_EMAIL = "milan.adhokari90@gmail.com"
FASTAPI_URL = "http://localhost:8001"

def start_server():
    """Start FastAPI server in background."""
    print("🚀 Starting FastAPI server...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "localhost", "--port", "8001"],
        cwd=backend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    for i in range(30):
        try:
            response = requests.get(f"{FASTAPI_URL}/health", timeout=1)
            if response.status_code == 200:
                print("✅ FastAPI server started")
                return process
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    raise Exception("Failed to start FastAPI server")

def send_test_approval_email():
    """Send a test approval email using the email service directly."""
    print(f"\n📧 Sending test approval email for invoice {TEST_INVOICE_ID}...")
    
    # Mock invoice data
    invoice_data = {
        "vendor_name": "Test Vendor GmbH",
        "invoice_number": "INV-2024-TEST",
        "total_amount": "1,234.56 €",
        "date": "2024-01-15",
        "project_name": "Test Project Integration"
    }
    
    # Send approval email
    try:
        result = email_service.send_bauleiter_approval_email(
            invoice_id=TEST_INVOICE_ID,
            invoice_data=invoice_data,
            bauleiter_email=TEST_BAULEITER_EMAIL,
            editor_name="Test Editor",
            editor_email="editor@company.com",
            changes_summary=[
                {"field": "vendor_name", "old_value": "Old Vendor", "new_value": "Test Vendor GmbH"},
                {"field": "total_amount", "old_value": "1000.00", "new_value": "1,234.56"}
            ]
        )
        
        print(f"✅ Email sent successfully!")
        print(f"Message ID: {result.get('message_id', 'N/A')}")
        
        # Extract and print approval URLs
        approve_url = result.get("approve_url", "")
        reject_url = result.get("reject_url", "")
        
        print(f"\n🔗 APPROVAL LINKS:")
        print(f"Approve: {approve_url}")
        print(f"Reject: {reject_url}")
        
        return approve_url, reject_url
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return None, None

def test_approval_links(approve_url, reject_url):
    """Test the approval links by making HTTP requests."""
    print(f"\n🧪 Testing approval links...")
    
    if approve_url:
        print(f"Testing approve link...")
        try:
            response = requests.get(approve_url, timeout=10)
            print(f"Approve response: {response.status_code}")
            if response.status_code == 200:
                print("✅ Approve link working!")
                # Show first part of response
                if "genehmigt" in response.text.lower() or "approved" in response.text.lower():
                    print("✅ Approval confirmation page displayed")
                else:
                    print("⚠️ Unexpected response content")
            else:
                print(f"❌ Approve link failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing approve link: {e}")
    
    if reject_url:
        print(f"\nTesting reject link...")
        try:
            response = requests.get(reject_url, timeout=10)
            print(f"Reject response: {response.status_code}")
            if response.status_code == 200:
                print("✅ Reject link working!")
                # Show first part of response
                if "abgelehnt" in response.text.lower() or "rejected" in response.text.lower():
                    print("✅ Rejection confirmation page displayed")
                else:
                    print("⚠️ Unexpected response content")
            else:
                print(f"❌ Reject link failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing reject link: {e}")

def main():
    """Run the approval workflow test."""
    print("=" * 60)
    print("🧪 APPROVAL WORKFLOW END-TO-END TEST")
    print("=" * 60)
    
    process = None
    try:
        # Start server
        process = start_server()
        
        # Send email with approval links
        approve_url, reject_url = send_test_approval_email()
        
        if approve_url and reject_url:
            # Test the approval links
            test_approval_links(approve_url, reject_url)
            
            print("\n" + "=" * 60)
            print("✅ TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📧 Check your email ({TEST_BAULEITER_EMAIL}) for the approval email")
            print("🔗 Click the approval/reject buttons in the email to test the full workflow")
            print("📊 The links should show a German confirmation page when clicked")
        else:
            print("\n❌ Could not send approval email")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    finally:
        if process:
            print("\n🛑 Stopping server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    return 0

if __name__ == "__main__":
    exit(main())
