#!/usr/bin/env python3
"""
Test the unified status tracking system
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_status_workflow():
    """Test the 3-stage status workflow"""
    
    print("=== Testing Unified Status Tracking System ===\n")
    
    # 1. Get an existing invoice to test with
    print("1. Fetching invoices...")
    response = requests.get(f"{BASE_URL}/api/invoices")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch invoices: {response.status_code}")
        return
    
    invoices = response.json().get("invoices", [])
    if not invoices:
        print("❌ No invoices found to test with")
        return
    
    # Use the first invoice
    test_invoice = invoices[0]
    invoice_id = test_invoice["id"]
    
    print(f"📄 Testing with invoice: {invoice_id}")
    print(f"   - Current status: {test_invoice.get('status')}")
    print(f"   - Current review_status: {test_invoice.get('review_status')}")
    
    # 2. Test editing (should move to "in Bearbeitung" stage)
    print(f"\n2. Testing edit workflow (should move to 'in Bearbeitung')...")
    
    edit_data = {
        "fields": {
            "projekt": "TEST PROJECT - Unified Database Service",
            "rechnungsbetrag": 9999.99
        },
        "editor_info": {
            "editor_email": "test@example.com",
            "editor_name": "Test Editor"
        }
    }
    
    edit_response = requests.put(
        f"{BASE_URL}/api/invoices/{invoice_id}/editor",
        json=edit_data
    )
    
    if edit_response.status_code == 200:
        print("✅ Edit request successful")
        
        # Check the updated status
        check_response = requests.get(f"{BASE_URL}/api/invoices/{invoice_id}")
        if check_response.status_code == 200:
            updated_invoice = check_response.json()["invoice"]
            print(f"   - New status: {updated_invoice.get('status')}")
            print(f"   - New review_status: {updated_invoice.get('review_status')}")
            
            # Verify it's in the correct stage
            if updated_invoice.get('status') == 'edited' and updated_invoice.get('review_status') == 'under_review':
                print("✅ SUCCESS: Invoice correctly moved to 'in Bearbeitung' stage!")
            else:
                print(f"❌ FAILED: Expected status='edited' and review_status='under_review'")
                print(f"   Got: status='{updated_invoice.get('status')}', review_status='{updated_invoice.get('review_status')}'")
        else:
            print(f"❌ Failed to fetch updated invoice: {check_response.status_code}")
    else:
        print(f"❌ Edit failed: {edit_response.status_code}")
        print(f"   Error: {edit_response.text}")
    
    # 3. Test completion (should move to "abgeschlossen" stage)
    print(f"\n3. Testing completion workflow (should move to 'abgeschlossen')...")
    
    complete_data = {
        "completion_info": {
            "completed_by": "Test User",
            "completion_notes": "Test completion via unified database service"
        }
    }
    
    complete_response = requests.put(
        f"{BASE_URL}/api/invoices/{invoice_id}/complete",
        json=complete_data
    )
    
    if complete_response.status_code == 200:
        print("✅ Completion request successful")
        
        # Check the final status
        final_response = requests.get(f"{BASE_URL}/api/invoices/{invoice_id}")
        if final_response.status_code == 200:
            final_invoice = final_response.json()["invoice"]
            print(f"   - Final status: {final_invoice.get('status')}")
            print(f"   - Final review_status: {final_invoice.get('review_status')}")
            
            # Verify it's in the correct stage
            if final_invoice.get('status') == 'completed' and final_invoice.get('review_status') == 'completed_review':
                print("✅ SUCCESS: Invoice correctly moved to 'abgeschlossen' stage!")
            else:
                print(f"❌ FAILED: Expected status='completed' and review_status='completed_review'")
                print(f"   Got: status='{final_invoice.get('status')}', review_status='{final_invoice.get('review_status')}'")
        else:
            print(f"❌ Failed to fetch final invoice: {final_response.status_code}")
    else:
        print(f"❌ Completion failed: {complete_response.status_code}")
        print(f"   Error: {complete_response.text}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_status_workflow()
