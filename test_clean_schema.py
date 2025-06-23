#!/usr/bin/env python3

import os
import sys
import json
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPA_URL")
key = os.getenv("SUPA_KEY")

if not url or not key:
    print("Missing Supabase credentials!")
    exit(1)

print(f"Testing new invoices_clean table...")

# Create Supabase client
supabase = create_client(url, key)

try:
    # Test insert into new clean table
    test_data = {
        "file_name": "clean_test_invoice.pdf",
        "file_path": "test/clean_test_invoice.pdf",
        "rechnungsempfaenger": "Test Customer Clean",
        "rechnungssteller": "Test Vendor Clean", 
        "projekt": "Test Project Clean",
        "gewerk": "Test Trade Clean",
        "rechnungsbetrag": 500.00,  # New field name
        "rechnungseingang": "2024-06-23",  # New field name
        "faelligkeit": "2024-07-23",
        "rechnungsart": "Standard",
        "status": "processed",
        "ocr_status": "completed"
    }
    
    print(f"Inserting test record into invoices_clean...")
    insert_result = supabase.table("invoices_clean").insert(test_data).execute()
    
    if insert_result.data:
        print(f"✅ SUCCESS: Record inserted with ID: {insert_result.data[0]['id']}")
        
        # Test query
        print(f"Testing query...")
        query_result = supabase.table("invoices_clean").select("*").execute()
        print(f"✅ Query successful: Found {len(query_result.data)} records")
        
        if query_result.data:
            record = query_result.data[0]
            print(f"Sample record:")
            print(f"  - ID: {record.get('id')}")
            print(f"  - Filename: {record.get('file_name')}")
            print(f"  - Vendor: {record.get('rechnungssteller')}")
            print(f"  - Customer: {record.get('rechnungsempfaenger')}")
            print(f"  - Amount: {record.get('rechnungsbetrag')}")
            print(f"  - Date: {record.get('rechnungseingang')}")
            print(f"  - Project: {record.get('projekt')}")
            print(f"  - Trade: {record.get('gewerk')}")
        
        print(f"\n✅ NEW CLEAN SCHEMA IS WORKING PERFECTLY!")
        
    else:
        print("❌ Insert failed: No data returned")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
