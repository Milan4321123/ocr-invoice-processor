#!/usr/bin/env python3
"""
Debug script to test exactly what the backend is receiving and processing
"""

import requests
import json

API_BASE = "http://localhost:8001"

def debug_field_clearing():
    """Debug exactly what happens when we try to clear a field"""
    
    invoice_id = "b7bff361-279d-4ad5-a774-b2bbfcc11eb8"
    
    print("=== DEBUGGING FIELD CLEARING ===")
    
    # First, set a value
    print("\n1. Setting projekt field to a value...")
    payload = {"fields": {"projekt": "Debug Test Value"}}
    print(f"Sending: {json.dumps(payload, indent=2)}")
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", json=payload)
    print(f"Response: {response.status_code}")
    print(f"Result: {json.dumps(response.json(), indent=2)}")
    
    # Check if it was saved
    print("\n2. Verifying the value was saved...")
    response = requests.get(f"{API_BASE}/invoices/{invoice_id}/editor")
    current_projekt = response.json()['fields']['projekt']
    print(f"Current projekt value: '{current_projekt}'")
    
    # Now try to clear it
    print("\n3. Attempting to clear the field...")
    payload = {"fields": {"projekt": ""}}
    print(f"Sending: {json.dumps(payload, indent=2)}")
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", json=payload)
    print(f"Response: {response.status_code}")
    print(f"Result: {json.dumps(response.json(), indent=2)}")
    
    # Check if it was cleared
    print("\n4. Verifying if the field was cleared...")
    response = requests.get(f"{API_BASE}/invoices/{invoice_id}/editor")
    final_projekt = response.json()['fields']['projekt']
    print(f"Final projekt value: '{final_projekt}'")
    print(f"Cleared successfully: {final_projekt == '' or final_projekt is None}")
    
    # Test with null
    print("\n5. Testing with null value...")
    payload = {"fields": {"projekt": None}}
    print(f"Sending: {json.dumps(payload, indent=2)}")
    
    response = requests.put(f"{API_BASE}/invoices/{invoice_id}/editor", json=payload)
    print(f"Response: {response.status_code}")
    print(f"Result: {json.dumps(response.json(), indent=2)}")
    
    # Check final state
    print("\n6. Final verification...")
    response = requests.get(f"{API_BASE}/invoices/{invoice_id}/editor")
    final_projekt = response.json()['fields']['projekt']
    print(f"Final projekt value after null: '{final_projekt}'")

if __name__ == "__main__":
    debug_field_clearing()
