#!/usr/bin/env python3
"""
Test script to verify partial field updates work correctly
"""

import requests
import json

API_BASE = "http://localhost:8001"

def test_partial_field_update():
    """Test that individual field changes are saved correctly"""
    
    # Get an existing invoice ID
    print("Getting invoice list...")
    response = requests.get(f"{API_BASE}/invoices")
    if not response.ok:
        print(f"❌ Failed to get invoices: {response.status_code}")
        return
    
    invoices = response.json().get("invoices", [])
    if not invoices:
        print("❌ No invoices found to test with")
        return
    
    invoice_id = invoices[0]["id"]
    print(f"Testing with invoice: {invoice_id}")
    
    # Get current editor data
    print("\n1. Getting current editor data...")
    response = requests.get(f"{API_BASE}/invoices/{invoice_id}/editor")
    if not response.ok:
        print(f"❌ Failed to get editor data: {response.status_code}")
        return
    
    current_data = response.json()
    print(f"Current fields: {json.dumps(current_data['fields'], indent=2)}")
    
    # Test 1: Update just one string field
    print("\n2. Testing single string field update...")
    test_payload_1 = {
        "fields": {
            "rechnungsempfaenger": "Single Field Test Customer",
            # Only sending one field that changed
        }
    }
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", 
                           json=test_payload_1)
    if response.ok:
        result = response.json()
        print(f"✅ Single field update successful: {result['updated_fields']}")
    else:
        print(f"❌ Single field update failed: {response.status_code} - {response.text}")
    
    # Test 2: Update just one numeric field
    print("\n3. Testing single numeric field update...")
    test_payload_2 = {
        "fields": {
            "rechnungsbetrag": 123.45,
            # Only sending one numeric field
        }
    }
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", 
                           json=test_payload_2)
    if response.ok:
        result = response.json()
        print(f"✅ Single numeric update successful: {result['updated_fields']}")
    else:
        print(f"❌ Single numeric update failed: {response.status_code} - {response.text}")
    
    # Test 3: Clear a field (set to empty)
    print("\n4. Testing field clearing (empty string)...")
    test_payload_3 = {
        "fields": {
            "projekt": "",  # Clearing this field
        }
    }
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", 
                           json=test_payload_3)
    if response.ok:
        result = response.json()
        print(f"✅ Field clearing successful: {result['updated_fields']}")
    else:
        print(f"❌ Field clearing failed: {response.status_code} - {response.text}")
    
    # Test 4: Mixed update (multiple fields)
    print("\n5. Testing mixed field update...")
    test_payload_4 = {
        "fields": {
            "rechnungsempfaenger": "Mixed Test Customer",
            "rechnungsbetrag": 987.65,
            "gewerk": "Mixed Test Work",
        }
    }
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", 
                           json=test_payload_4)
    if response.ok:
        result = response.json()
        print(f"✅ Mixed update successful: {result['updated_fields']}")
    else:
        print(f"❌ Mixed update failed: {response.status_code} - {response.text}")
    
    # Verify final state
    print("\n6. Verifying final state...")
    response = requests.get(f"{API_BASE}/invoices/{invoice_id}/editor")
    if response.ok:
        final_data = response.json()
        print(f"Final fields: {json.dumps(final_data['fields'], indent=2)}")
        
        # Check specific values
        fields = final_data['fields']
        print(f"\nVerification:")
        print(f"- rechnungsempfaenger: '{fields.get('rechnungsempfaenger')}' (should be 'Mixed Test Customer')")
        print(f"- rechnungsbetrag: {fields.get('rechnungsbetrag')} (should be 987.65)")
        print(f"- gewerk: '{fields.get('gewerk')}' (should be 'Mixed Test Work')")
        print(f"- projekt: '{fields.get('projekt')}' (should be empty or null)")
    else:
        print(f"❌ Failed to verify final state: {response.status_code}")

if __name__ == "__main__":
    test_partial_field_update()
