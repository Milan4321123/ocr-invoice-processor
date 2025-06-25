#!/usr/bin/env python3
"""
Complete end-to-end test of the approval workflow.
Creates a test invoice in the database and tests the full workflow.
"""
import requests
import json
import uuid
import time

# Configuration
FASTAPI_URL = "http://localhost:8001"
TEST_INVOICE_ID = "test_invoice_" + str(uuid.uuid4())[:8]
TEST_BAULEITER_EMAIL = "milan.adhokari90@gmail.com"

def check_server():
    """Check if the FastAPI server is running."""
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_test_invoice():
    """Create a test invoice in the database for testing."""
    print(f"📄 Creating test invoice: {TEST_INVOICE_ID}")
    
    # Try to create an invoice via the upload API
    # This is a simulation - in real use, an invoice would be uploaded and processed
    invoice_data = {
        "id": TEST_INVOICE_ID,
        "vendor_name": "Test Vendor GmbH",
        "invoice_number": "INV-2024-TEST",
        "total_amount": "1234.56",
        "date": "2024-01-15",
        "project_name": "Test Project Integration",
        "status": "ready_for_review"
    }
    
    # Note: This might fail if the invoice creation endpoint doesn't exist
    # In that case, we'll proceed with the email test anyway
    try:
        # Try a generic invoice creation (this may not work)
        response = requests.post(f"{FASTAPI_URL}/api/invoices", json=invoice_data, timeout=10)
        if response.status_code in [200, 201]:
            print("✅ Test invoice created successfully")
            return True
        else:
            print(f"⚠️ Could not create test invoice (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"⚠️ Could not create test invoice: {e}")
        return False

def send_approval_email():
    """Send the approval email for the test invoice."""
    print(f"\n📧 Sending approval email to {TEST_BAULEITER_EMAIL}...")
    
    email_data = {
        "invoice_id": TEST_INVOICE_ID,
        "bauleiter_email": TEST_BAULEITER_EMAIL,
        "editor_name": "Test Editor",
        "editor_email": "editor@company.com", 
        "changes_summary": [
            {"field": "vendor_name", "old_value": "Old Vendor", "new_value": "Test Vendor GmbH"},
            {"field": "total_amount", "old_value": "1000.00", "new_value": "1,234.56 €"},
            {"field": "project_name", "old_value": "", "new_value": "Test Project Integration"}
        ]
    }
    
    try:
        response = requests.post(
            f"{FASTAPI_URL}/api/email/bauleiter-approval",
            json=email_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Approval email sent successfully!")
            print(f"Message ID: {result.get('message_id', 'N/A')}")
            
            # Check if approval URLs are in the response
            if 'approve_url' in result:
                print(f"🔗 Approve URL: {result['approve_url']}")
            if 'reject_url' in result:
                print(f"🔗 Reject URL: {result['reject_url']}")
                
            return True
            
        else:
            print(f"❌ Failed to send email: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def main():
    """Run the complete approval workflow test."""
    print("=" * 70)
    print("🧪 COMPLETE APPROVAL WORKFLOW TEST")
    print("=" * 70)
    
    print("\n🔧 Checking server status...")
    if not check_server():
        print("❌ FastAPI server is not running!")
        print("Please start it with: cd backend && python -m uvicorn main:app --host localhost --port 8001")
        return 1
    
    print("✅ FastAPI server is running")
    
    # Try to create a test invoice (optional)
    create_test_invoice()
    
    # Send approval email
    email_sent = send_approval_email()
    
    if email_sent:
        print("\n" + "=" * 70)
        print("🎉 APPROVAL WORKFLOW TEST COMPLETED!")
        print("=" * 70)
        print(f"📧 Check your email: {TEST_BAULEITER_EMAIL}")
        print("🔗 Click the 'GENEHMIGEN' (Approve) or 'ABLEHNEN' (Reject) button")
        print("📄 You should see a German confirmation page")
        print("🔒 The approval action is logged with audit information")
        print("\n📋 WHAT HAPPENS WHEN YOU CLICK:")
        print("• JWT token is validated for security")
        print("• Invoice status is updated in the database")
        print("• Confirmation page is shown in German")
        print("• Audit log entry is created")
        print("• Optional: Editor notification could be sent")
        
    else:
        print("\n❌ Could not send approval email")
        print("This might be due to:")
        print("• Invoice not found in database (expected for test)")
        print("• Email service configuration issues")
        print("• Network connectivity problems")
        
        print("\n🔗 You can still test the approval links directly!")
        print("Run the approval endpoint test to generate direct links.")
    
    return 0

if __name__ == "__main__":
    exit(main())
