#!/usr/bin/env python3
"""
Test the clean database service with your exact invoices_clean schema
"""

import sys
import os
import asyncio
sys.path.append('backend')

from services.database import db_service

async def test_database_service():
    """Test the clean database service"""
    
    print("🧪 Testing Clean Database Service")
    print("=" * 50)
    
    # Test 1: Check connection
    print("\n1. Testing Database Connection...")
    if db_service.is_available:
        print("   ✅ Database service connected successfully")
    else:
        print("   ❌ Database service not available")
        return False
    
    # Test 2: Create invoice with your exact schema fields
    print("\n2. Testing Invoice Creation...")
    test_invoice = {
        "file_name": "20250624_DBTEST_VENDOR_INVOICE.pdf",
        "file_path": "20250624_DBTEST_VENDOR_INVOICE.pdf", 
        "file_size": 1024,
        "mime_type": "application/pdf",
        "rechnungsempfaenger": "Test Customer GmbH",
        "rechnungssteller": "Test Vendor AG", 
        "projekt": "Test Project",
        "gewerk": "Elektro",
        "rechnungsbetrag": 1500.50,
        "kfw_anrechenbare_kosten": True,
        "rechnungsart": "Schlussrechnung",
        "status": "uploaded",
        "ocr_status": "completed",
        "ocr_text": "Sample OCR text",
        "raw_ocr_data": {"test": "ocr_data"}
    }
    
    create_result = db_service.create_invoice(test_invoice)
    
    if create_result.get("success"):
        invoice_id = create_result["data"]["id"]
        print("   ✅ Invoice created successfully")
        print(f"      - ID: {invoice_id}")
        print(f"      - File name: {create_result['data']['file_name']}")
        print(f"      - Vendor: {create_result['data']['rechnungssteller']}")
        print(f"      - Amount: {create_result['data']['rechnungsbetrag']}")
    else:
        print(f"   ❌ Invoice creation failed: {create_result.get('error')}")
        return False
    
    # Test 3: Get invoice by ID
    print("\n3. Testing Invoice Retrieval...")
    get_result = db_service.get_invoice(invoice_id)
    
    if get_result.get("success"):
        invoice = get_result["data"]
        print("   ✅ Invoice retrieved successfully")
        print(f"      - File name: {invoice['file_name']}")
        print(f"      - Customer: {invoice['rechnungsempfaenger']}")
        print(f"      - Project: {invoice['projekt']}")
        print(f"      - KfW eligible: {invoice['kfw_anrechenbare_kosten']}")
    else:
        print(f"   ❌ Invoice retrieval failed: {get_result.get('error')}")
        return False
    
    # Test 4: Update invoice
    print("\n4. Testing Invoice Update...")
    update_data = {
        "rechnungsbetrag": 2000.00,
        "status": "processed",
        "review_status": "completed_review"
    }
    
    update_result = db_service.update_invoice(invoice_id, update_data)
    
    if update_result.get("success"):
        updated_invoice = update_result["data"]
        print("   ✅ Invoice updated successfully")
        print(f"      - New amount: {updated_invoice['rechnungsbetrag']}")
        print(f"      - New status: {updated_invoice['status']}")
        print(f"      - Review status: {updated_invoice['review_status']}")
    else:
        print(f"   ❌ Invoice update failed: {update_result.get('error')}")
        return False
    
    # Test 5: Get all invoices
    print("\n5. Testing Get All Invoices...")
    all_result = db_service.get_all_invoices(limit=10)
    
    if all_result.get("success"):
        invoices = all_result["data"]
        print(f"   ✅ Retrieved {len(invoices)} invoices")
        print(f"      - Total in response: {all_result['total']}")
        if invoices:
            print(f"      - Latest: {invoices[0]['file_name']}")
    else:
        print(f"   ❌ Get all invoices failed: {all_result.get('error')}")
        return False
    
    # Test 6: Clean up - delete test invoice
    print("\n6. Testing Invoice Deletion...")
    delete_result = db_service.delete_invoice(invoice_id)
    
    if delete_result.get("success"):
        print("   ✅ Invoice deleted successfully")
    else:
        print(f"   ❌ Invoice deletion failed: {delete_result.get('error')}")
    
    print("\n" + "=" * 50)
    print("🎉 DATABASE SERVICE TEST COMPLETED!")
    print("✅ All core operations working with your exact schema")
    print("✅ Ready for use in upload service and routes")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_database_service())
    exit(0 if success else 1)
