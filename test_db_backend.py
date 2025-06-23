#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend')

from services.database import DatabaseService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing database service...")

# Create database service instance
db_service = DatabaseService()

if not db_service.is_available:
    print("❌ Database service not available!")
    exit(1)

print(f"✅ Database service is available")

try:
    # Check current records
    result = db_service.get_invoices(limit=100)
    
    if result["success"]:
        print(f"✅ Current records in database: {len(result['data'])}")
        
        if result["data"]:
            print("\nExisting records:")
            for i, record in enumerate(result["data"]):
                print(f"  {i+1}. ID: {record.get('id')}")
                print(f"      filename: {record.get('filename')}")
                print(f"      status: {record.get('status')}")
                print(f"      created_at: {record.get('created_at')}")
                print()
        else:
            print("No records found")
            
        # Try to create a test record using the backend's method
        print("\nTrying to create a test record...")
        
        test_invoice = {
            "filename": "test-debug.pdf",
            "file_path": "uploads/test-debug.pdf",
            "file_size": 12345,
            "mime_type": "application/pdf",
            "status": "uploaded",
            "rechnungssteller": "Debug Test Company",
            "rechnungsnummer": "DEBUG-001",
            "rechnungsdatum": "2024-01-01",
            "brutto_betrag": 150.00,
            "netto_betrag": 125.00,
            "currency": "EUR",
            "source_type": "drag_drop"
        }
        
        create_result = db_service.create_invoice(test_invoice)
        
        if create_result["success"]:
            print(f"✅ Successfully created test invoice: {create_result['data']['id']}")
            
            # Check if we can retrieve it
            check_result = db_service.get_all_invoices()
            if check_result["success"]:
                print(f"✅ Total records after insert: {len(check_result['data'])}")
                
                # Try to delete the test record to clean up
                test_id = create_result['data']['id']
                delete_result = db_service.delete_invoice(test_id)
                if delete_result["success"]:
                    print(f"✅ Successfully cleaned up test record")
                else:
                    print(f"⚠️  Could not delete test record: {delete_result.get('error')}")
            else:
                print(f"❌ Could not verify insert: {check_result.get('error')}")
        else:
            print(f"❌ Failed to create test invoice: {create_result.get('error')}")
    else:
        print(f"❌ Failed to query database: {result.get('error')}")

except Exception as e:
    print(f"❌ Error during database test: {e}")
    import traceback
    traceback.print_exc()
