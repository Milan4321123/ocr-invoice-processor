#!/usr/bin/env python3
"""
Test the completion endpoint with context-aware emails.
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

def test_completion_endpoint():
    print("🧪 Testing completion endpoint with context-aware emails...")
    
    # First, try to get an existing invoice to test with
    try:
        response = requests.get(f"{API_BASE}/invoices", headers=HEADERS)
        if response.status_code == 200:
            invoices = response.json()
            if invoices:
                # Use the first invoice for testing
                test_invoice = invoices[0]
                invoice_id = test_invoice["id"]
                print(f"📋 Using test invoice: {invoice_id}")
                
                # Test completion with editor info
                completion_data = {
                    "completion_info": {
                        "completed_by": "test_editor@example.com",
                        "completion_notes": "Test completion for context-aware emails"
                    },
                    "editor_info": {
                        "editor_email": "test_editor@example.com",
                        "editor_name": "Test Editor",
                        "changes_summary": [
                            {
                                "field": "Status",
                                "old_value": "Bearbeitung",
                                "new_value": "Abgeschlossen",
                                "timestamp": "2025-01-15 10:30:00"
                            }
                        ]
                    }
                }
                
                print("📤 Sending completion request...")
                response = requests.put(
                    f"{API_BASE}/invoices/{invoice_id}/complete",
                    headers=HEADERS,
                    json=completion_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Completion successful!")
                    print(f"📧 Completion email sent: {result.get('completion_email_sent', False)}")
                    print(f"📋 Message: {result.get('message', 'N/A')}")
                    return True
                else:
                    print(f"❌ Completion failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            else:
                print("❌ No invoices found for testing")
                return False
        else:
            print(f"❌ Failed to get invoices: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_completion_endpoint()
    print(f"\n🎉 Test {'PASSED' if success else 'FAILED'}")
