#!/usr/bin/env python3
"""
Test script to verify the invoice save with email notification functionality
"""
import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_INVOICE_ID = "3441971d-ecc4-4c41-af0d-3444b36908e9"  # Using a real invoice ID

def test_invoice_save_with_email():
    """Test saving invoice data with email notification"""
    
    print("🧪 Testing invoice save with email notification...")
    
    # Test data
    invoice_data = {
        "fields": {
            "rechnungsempfaenger": "Test Customer GmbH",
            "rechnungssteller": "Test Vendor",
            "projekt": "Test Project Updated",
            "gewerk": "Electrical Work",
            "rechnungsbetrag": 2500.75,
            "rechnungseingang": "2025-06-26",
            "faelligkeit": "2025-07-26",
            "skonto_datum": "2025-07-06",
            "skonto_prozent": 2.5,
            "rechnungsart": "rechnung",
            "kfw_anrechenbar": True,
            "rechnungspruefung_email": "test@example.com",
            "weiter_berechnen_an": "Finance Department"
        },
        "editor_info": {
            "editor_email": "test@example.com",
            "editor_name": "Test Editor",
            "changes_summary": [
                {
                    "field": "projekt",
                    "old_value": "Test Project",
                    "new_value": "Test Project Updated"
                },
                {
                    "field": "rechnungsbetrag",
                    "old_value": "2000.00",
                    "new_value": "2500.75"
                }
            ]
        }
    }
    
    try:
        # Send PUT request to update invoice
        response = requests.put(
            f"{API_BASE_URL}/api/invoices/{TEST_INVOICE_ID}/editor",
            json=invoice_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📤 Request sent to: {response.url}")
        print(f"📝 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice save successful!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            if result.get("email_sent"):
                print("📧 Email notification was sent!")
            else:
                print("📧 Email notification was NOT sent (check logs)")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_get_invoice():
    """Test getting invoice data to verify update"""
    
    print("\n🔍 Testing invoice data retrieval...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/invoices/{TEST_INVOICE_ID}/editor",
            timeout=10
        )
        
        print(f"📤 Request sent to: {response.url}")
        print(f"📝 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice data retrieved successfully!")
            print(f"📋 Invoice fields: {json.dumps(result.get('fields', {}), indent=2)}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Starting invoice save email notification tests...\n")
    
    # Test save with email
    test_invoice_save_with_email()
    
    # Wait a moment
    time.sleep(2)
    
    # Test retrieval to verify data was saved
    test_get_invoice()
    
    print("\n✨ Testing complete!")
