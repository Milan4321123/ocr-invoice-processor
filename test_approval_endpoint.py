#!/usr/bin/env python3
"""
Comprehensive test for the approval endpoint integration.
Tests the full workflow: email sending -> approval link click -> status update.
"""
import sys
import os
import time
import requests
import subprocess
import signal
import jwt
from datetime import datetime, timedelta
import uuid

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import email_service
from services.database import db_service

# Test configuration
TEST_INVOICE_ID = "test_invoice_12345"
TEST_EDITOR_EMAIL = "editor@company.com"
TEST_BAULEITER_EMAIL = "milan.adhokari90@gmail.com"  # Your email for testing
FASTAPI_URL = "http://localhost:8001"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secure-jwt-secret")

class FastAPITestServer:
    """Context manager to start and stop FastAPI server for testing."""
    
    def __init__(self):
        self.process = None
    
    def __enter__(self):
        print("🚀 Starting FastAPI server for testing...")
        # Change to backend directory and start server
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "localhost", "--port", "8001"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{FASTAPI_URL}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ FastAPI server started successfully")
                    return self
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        raise Exception("Failed to start FastAPI server")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            print("🛑 Stopping FastAPI server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print("✅ FastAPI server stopped")

def generate_test_token(invoice_id: str, action: str, user_email: str) -> str:
    """Generate a test approval token."""
    payload = {
        "invoice_id": invoice_id,
        "action": action,
        "user_email": user_email,
        "nonce": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def test_approval_endpoint_directly():
    """Test the approval endpoint directly with generated tokens."""
    print("\n🧪 Testing approval endpoint directly...")
    
    # Test approve action
    approve_token = generate_test_token(TEST_INVOICE_ID, "approve", TEST_BAULEITER_EMAIL)
    approve_url = f"{FASTAPI_URL}/api/approval/{approve_token}"
    
    print(f"Testing approve URL: {approve_url}")
    response = requests.get(approve_url)
    print(f"Approve response status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Approve endpoint working")
        print(f"Response preview: {response.text[:200]}...")
    else:
        print(f"❌ Approve endpoint failed: {response.text}")
    
    # Test reject action
    reject_token = generate_test_token(TEST_INVOICE_ID, "reject", TEST_BAULEITER_EMAIL)
    reject_url = f"{FASTAPI_URL}/api/approval/{reject_token}"
    
    print(f"\nTesting reject URL: {reject_url}")
    response = requests.get(reject_url)
    print(f"Reject response status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Reject endpoint working")
        print(f"Response preview: {response.text[:200]}...")
    else:
        print(f"❌ Reject endpoint failed: {response.text}")

def test_email_workflow_with_approval():
    """Test the complete email workflow with actual approval links."""
    print("\n📧 Testing complete email workflow...")
    
    # Send bauleiter approval email
    email_url = f"{FASTAPI_URL}/api/email/bauleiter-approval"
    email_data = {
        "invoice_id": TEST_INVOICE_ID,
        "bauleiter_email": TEST_BAULEITER_EMAIL,
        "editor_name": "Test Editor",
        "editor_email": TEST_EDITOR_EMAIL,
        "changes_summary": [
            {"field": "vendor_name", "old_value": "Old Vendor", "new_value": "Test Vendor GmbH"},
            {"field": "total_amount", "old_value": "1000.00", "new_value": "1,234.56"}
        ]
    }
    
    print(f"Sending bauleiter approval request to: {email_url}")
    response = requests.post(email_url, json=email_data)
    print(f"Email workflow response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Email workflow completed successfully")
        print(f"Response: {result}")
        
        # Extract approval URLs from response if available
        if "approval_urls" in result:
            approve_url = result["approval_urls"]["approve"]
            reject_url = result["approval_urls"]["reject"]
            
            print(f"\n🔗 Testing approval URLs from email:")
            print(f"Approve URL: {approve_url}")
            print(f"Reject URL: {reject_url}")
            
            # Test the actual URLs that were sent in the email
            print("\nTesting approve URL...")
            approve_response = requests.get(approve_url)
            print(f"Approve response: {approve_response.status_code}")
            
            print("\nTesting reject URL...")
            reject_response = requests.get(reject_url)
            print(f"Reject response: {reject_response.status_code}")
    else:
        print(f"❌ Email workflow failed: {response.text}")

def test_health_endpoint():
    """Test that the server is running properly."""
    print("\n❤️ Testing health endpoint...")
    try:
        response = requests.get(f"{FASTAPI_URL}/health")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is healthy")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def main():
    """Run the complete approval endpoint test."""
    print("=" * 60)
    print("🧪 APPROVAL ENDPOINT INTEGRATION TEST")
    print("=" * 60)
    
    # Check environment setup
    print("\n🔧 Checking environment setup...")
    if not os.getenv("JWT_SECRET"):
        print("⚠️ Warning: JWT_SECRET not set in environment")
    
    if not os.getenv("SENDGRID_API_KEY"):
        print("⚠️ Warning: SENDGRID_API_KEY not set")
    
    try:
        with FastAPITestServer():
            # Test basic health
            test_health_endpoint()
            
            # Test approval endpoints directly
            test_approval_endpoint_directly()
            
            # Test complete email workflow
            test_email_workflow_with_approval()
            
        print("\n" + "=" * 60)
        print("✅ APPROVAL ENDPOINT TEST COMPLETED")
        print("=" * 60)
        
        print("\n📋 NEXT STEPS:")
        print("1. Check your email for the approval/reject links")
        print("2. Click the links to test the full workflow")
        print("3. Verify that invoice status updates correctly")
        print("4. Check audit logs for security tracking")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
