#!/usr/bin/env python3
"""
Direct test of email service to debug completion email issues
"""

import asyncio
import json
import requests
from datetime import datetime

# Test completion email directly
def test_completion_email_direct():
    print("🧪 Testing completion email flow directly...")
    
    # Use a real invoice ID from the system
    invoice_id = "7088bf03-6097-462c-91ee-26ca9e7dc1d4"
    test_email = "test.editor@company.de"
    
    # Prepare completion data exactly as frontend does
    completion_data = {
        "completion_info": {
            "completed_by": test_email,
            "completed_at": datetime.now().isoformat(),
            "completion_notes": "Direct test completion - automated test"
        },
        "editor_info": {
            "editor_email": test_email,
            "editor_name": "Test Editor Direct",
            "changes_summary": [
                {
                    "field": "Status",
                    "old_value": "Bearbeitung",
                    "new_value": "Bearbeitung abgeschlossen",
                    "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                }
            ]
        }
    }
    
    print(f"Testing with invoice ID: {invoice_id}")
    print(f"Test email: {test_email}")
    print(f"Completion data: {json.dumps(completion_data, indent=2)}")
    print()
    
    # Make the API call
    try:
        response = requests.put(
            f"http://localhost:8000/api/invoices/{invoice_id}/complete",
            headers={"Content-Type": "application/json"},
            json=completion_data,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check specific email fields
            completion_email_sent = result.get("completion_email_sent", False)
            email_sent = result.get("email_sent", False)
            
            print(f"\n📧 Email Status:")
            print(f"   completion_email_sent: {completion_email_sent}")
            print(f"   email_sent: {email_sent}")
            
            if completion_email_sent:
                print("✅ Completion email was sent successfully!")
            else:
                print("❌ Completion email was NOT sent")
                print("💡 This indicates an issue in the email service")
                
        else:
            print(f"❌ API call failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error making API call: {str(e)}")

if __name__ == "__main__":
    test_completion_email_direct()
