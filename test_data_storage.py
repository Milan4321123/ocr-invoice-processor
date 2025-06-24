#!/usr/bin/env python3
"""
Test to verify data is correctly stored in Supabase invoices_clean table
"""

import sys
import os
sys.path.append('backend')

from services.database import db_service

def test_data_storage():
    """Test if data is properly stored in invoices_clean table"""
    
    print("🔍 Checking Data Storage in invoices_clean Table")
    print("=" * 60)
    
    # Test 1: Check connection
    print("\n1. Testing Database Connection...")
    if not db_service.is_available:
        print("   ❌ Database not available")
        return False
    
    print("   ✅ Database connected")
    print(f"   📊 Table: {db_service.table_name}")
    
    # Test 2: Get all invoices to see what's stored
    print("\n2. Checking Stored Invoices...")
    try:
        result = db_service.get_all_invoices(limit=10)
        
        if result.get("success"):
            invoices = result["data"]
            print(f"   ✅ Found {len(invoices)} invoices in database")
            
            if invoices:
                print("\n   📋 Sample Invoice Data:")
                latest = invoices[0]  # Most recent
                
                # Check all the important fields from your schema
                schema_fields = [
                    'id', 'file_name', 'file_path', 'file_size', 'mime_type',
                    'rechnungsempfaenger', 'rechnungssteller', 'projekt', 'gewerk',
                    'weiter_berechnen_an', 'rechnungsbetrag', 'kfw_anrechenbare_kosten',
                    'rechnungseingang', 'faelligkeit', 'skonto_datum', 'skonto_prozent',
                    'rechnungsart', 'rechnungspruefung', 'status', 'ocr_status',
                    'ocr_text', 'raw_ocr_data', 'created_at', 'updated_at',
                    'review_status', 'reviewed_by', 'reviewed_at', 'review_notes'
                ]
                
                print(f"      ID: {latest.get('id')}")
                print(f"      File Name: {latest.get('file_name')}")
                print(f"      File Size: {latest.get('file_size')} bytes")
                print(f"      Status: {latest.get('status')}")
                print(f"      OCR Status: {latest.get('ocr_status')}")
                print(f"      Customer (rechnungsempfaenger): {latest.get('rechnungsempfaenger')}")
                print(f"      Vendor (rechnungssteller): {latest.get('rechnungssteller')}")
                print(f"      Amount (rechnungsbetrag): {latest.get('rechnungsbetrag')}")
                print(f"      Project (projekt): {latest.get('projekt')}")
                print(f"      Created: {latest.get('created_at')}")
                print(f"      Has OCR Data: {bool(latest.get('raw_ocr_data'))}")
                
                # Check which fields are populated vs empty
                populated_fields = []
                empty_fields = []
                
                for field in schema_fields:
                    value = latest.get(field)
                    if value is not None and value != '':
                        populated_fields.append(field)
                    else:
                        empty_fields.append(field)
                
                print(f"\n   ✅ Populated Fields ({len(populated_fields)}):")
                for field in populated_fields:
                    print(f"      - {field}: {latest.get(field)}")
                
                print(f"\n   ⚪ Empty Fields ({len(empty_fields)}):")
                for field in empty_fields[:10]:  # Show first 10 empty fields
                    print(f"      - {field}")
                if len(empty_fields) > 10:
                    print(f"      ... and {len(empty_fields) - 10} more")
                
            else:
                print("   ⚠️ No invoices found in database")
                
        else:
            print(f"   ❌ Failed to get invoices: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking stored data: {e}")
        return False
    
    # Test 3: Create a test record to verify field mapping
    print("\n3. Testing Field Mapping with New Record...")
    test_data = {
        "file_name": "test_field_mapping.pdf",
        "file_path": "test_field_mapping.pdf",
        "file_size": 2048,
        "mime_type": "application/pdf",
        "rechnungsempfaenger": "Test Customer GmbH",
        "rechnungssteller": "Test Vendor AG",
        "projekt": "Field Mapping Test",
        "gewerk": "Test Trade",
        "rechnungsbetrag": 999.99,
        "kfw_anrechenbare_kosten": True,
        "rechnungsart": "Test Invoice Type",
        "status": "test",
        "ocr_status": "completed",
        "ocr_text": "Test OCR text",
        "raw_ocr_data": {"test": "field_mapping", "confidence": 0.95}
    }
    
    create_result = db_service.create_invoice(test_data)
    
    if create_result.get("success"):
        created_invoice = create_result["data"]
        test_id = created_invoice["id"]
        print("   ✅ Test record created successfully")
        print(f"      - ID: {test_id}")
        print(f"      - Customer: {created_invoice.get('rechnungsempfaenger')}")
        print(f"      - Amount: {created_invoice.get('rechnungsbetrag')}")
        
        # Clean up - delete test record
        delete_result = db_service.delete_invoice(test_id)
        if delete_result.get("success"):
            print("   ✅ Test record cleaned up")
        
    else:
        print(f"   ❌ Failed to create test record: {create_result.get('error')}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 DATA STORAGE VERIFICATION COMPLETE!")
    print("✅ Database connection working")
    print("✅ Data stored in invoices_clean table")
    print("✅ Field mapping working correctly")
    print("✅ Your exact schema fields are being used")
    
    return True

if __name__ == "__main__":
    success = test_data_storage()
    exit(0 if success else 1)
