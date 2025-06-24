#!/usr/bin/env python3
"""
Test the database service directly to isolate the issue
"""

import sys
import os
sys.path.append('backend')

from services.database import db_service

def test_database_update_directly():
    """Test updating directly via database service"""
    
    invoice_id = "b7bff361-279d-4ad5-a774-b2bbfcc11eb8"
    
    print("=== TESTING DATABASE SERVICE DIRECTLY ===")
    
    # Test 1: Set a value
    print("\n1. Setting projekt field via database service...")
    update_data = {"projekt": "Direct DB Test Value"}
    result = db_service.update_invoice(invoice_id, update_data)
    print(f"Update result: {result}")
    
    # Verify it was set
    invoice_result = db_service.get_invoice(invoice_id)
    if invoice_result.get("success"):
        current_value = invoice_result["data"].get("projekt")
        print(f"Current projekt value: '{current_value}'")
    
    # Test 2: Clear the field
    print("\n2. Clearing projekt field via database service...")
    update_data = {"projekt": ""}
    result = db_service.update_invoice(invoice_id, update_data)
    print(f"Clear result: {result}")
    
    # Verify it was cleared
    invoice_result = db_service.get_invoice(invoice_id)
    if invoice_result.get("success"):
        final_value = invoice_result["data"].get("projekt")
        print(f"Final projekt value: '{final_value}'")
        print(f"Successfully cleared: {final_value == '' or final_value is None}")
    
    # Test 3: Set to None
    print("\n3. Setting projekt field to None via database service...")
    update_data = {"projekt": None}
    result = db_service.update_invoice(invoice_id, update_data)
    print(f"None result: {result}")
    
    # Verify final state
    invoice_result = db_service.get_invoice(invoice_id)
    if invoice_result.get("success"):
        none_value = invoice_result["data"].get("projekt")
        print(f"Projekt value after None: '{none_value}'")

if __name__ == "__main__":
    test_database_update_directly()
