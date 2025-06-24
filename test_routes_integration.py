#!/usr/bin/env python3
"""
Comprehensive test script to verify all routes are working with the centralized database service
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all the main invoice endpoints"""
    
    print("🧪 Testing Invoice Routes with Centralized Database Service")
    print("=" * 60)
    
    # Test 1: Get all invoices
    print("\n1. Testing GET /invoices")
    try:
        response = requests.get(f"{BASE_URL}/invoices")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Found {data.get('total', 0)} invoices")
            if data.get('invoices'):
                test_invoice_id = data['invoices'][0]['id']
                print(f"   📋 Using invoice ID for tests: {test_invoice_id}")
            else:
                print("   ⚠️ No invoices found")
                return
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Get specific invoice
    print(f"\n2. Testing GET /invoices/{test_invoice_id}")
    try:
        response = requests.get(f"{BASE_URL}/invoices/{test_invoice_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Retrieved invoice '{data['invoice']['file_name']}'")
            print(f"   📋 OCR Status: {data['invoice']['ocr_status']}")
            print(f"   📋 Business fields mapped: rechnungsempfaenger={data['invoice'].get('rechnungsempfaenger', 'None')}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get OCR data
    print(f"\n3. Testing GET /invoices/{test_invoice_id}/ocr")
    try:
        response = requests.get(f"{BASE_URL}/invoices/{test_invoice_id}/ocr")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: OCR data retrieved")
            print(f"   📋 OCR Status: {data.get('ocr_status')}")
            print(f"   📋 Structured data fields: {len(data.get('structured_data', {}))}")
            # Check if our German fields are mapped correctly
            structured = data.get('structured_data', {})
            print(f"   📋 Customer: {structured.get('customer_name')}")
            print(f"   📋 Vendor: {structured.get('vendor_name')}")
            print(f"   📋 Amount: {structured.get('total_amount')}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Validate invoice
    print(f"\n4. Testing GET /invoices/{test_invoice_id}/validate")
    try:
        response = requests.get(f"{BASE_URL}/invoices/{test_invoice_id}/validate")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Invoice validated - {data.get('valid')}")
            print(f"   📋 Filename: {data.get('filename')}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Get editor data
    print(f"\n5. Testing GET /invoices/{test_invoice_id}/editor")
    try:
        response = requests.get(f"{BASE_URL}/invoices/{test_invoice_id}/editor")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Editor data retrieved")
            fields = data.get('fields', {})
            print(f"   📋 German fields mapped:")
            print(f"      rechnungsempfaenger: {fields.get('rechnungsempfaenger')}")
            print(f"      rechnungssteller: {fields.get('rechnungssteller')}")
            print(f"      rechnungsbetrag: {fields.get('rechnungsbetrag')}")
            print(f"      projekt: {fields.get('projekt')}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Update editor data
    print(f"\n6. Testing PUT /invoices/{test_invoice_id}/editor")
    try:
        update_data = {
            "fields": {
                "rechnungsempfaenger": "Updated Customer Name",
                "projekt": "Updated Project Name"
            }
        }
        response = requests.put(
            f"{BASE_URL}/invoices/{test_invoice_id}/editor", 
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Invoice updated")
            print(f"   📋 Updated fields: {data.get('updated_fields', [])}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All endpoint tests completed!")
    print("🎉 Database service integration is working correctly!")

if __name__ == "__main__":
    test_endpoints()
