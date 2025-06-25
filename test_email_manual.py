#!/usr/bin/env python3
"""
Manual test for Phase 1 email workflow
Run this after starting the backend server
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_INVOICE_ID = "test-invoice-123"
TEST_EMAIL = "adhikarimilan4321@gmail.com"

def test_editor_notification():
    """Test editor notification endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/email/editor-notification",
            json={
                "invoice_id": TEST_INVOICE_ID,
                "editor_email": TEST_EMAIL,
                "editor_name": "Test Editor",
                "changes_summary": [
                    {
                        "field": "Rechnungsbetrag",
                        "old_value": "1000.00",
                        "new_value": "1200.00",
                        "timestamp": "2024-01-15T10:30:00"
                    }
                ]
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Editor notification test passed")
        else:
            print("❌ Editor notification test failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Phase 1 Email Workflow")
    print("Make sure the backend server is running on port 8001")
    input("Press Enter to continue...")
    test_editor_notification()
