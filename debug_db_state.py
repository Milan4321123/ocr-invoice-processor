#!/usr/bin/env python3

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    print("Missing Supabase credentials!")
    exit(1)

print(f"Connecting to Supabase at: {url}")

# Create Supabase client
supabase = create_client(url, key)

try:
    # Check if table exists and get all records
    result = supabase.table("invoices").select("*").execute()
    
    print(f"Query successful!")
    print(f"Number of records: {len(result.data)}")
    
    if result.data:
        print("\nRecords found:")
        for i, record in enumerate(result.data):
            print(f"Record {i+1}: ID={record.get('id')}, filename={record.get('filename')}, created_at={record.get('created_at')}")
    else:
        print("No records found in the invoices table")
        
    # Let's also check the table structure
    print("\nTrying to describe table structure...")
    
    # Try to insert a test record to see if table works
    test_data = {
        "filename": "debug_test.pdf",
        "file_path": "test/debug_test.pdf",
        "status": "processed",
        "supplier": "Test Supplier",
        "invoice_number": "TEST-001",
        "invoice_date": "2024-01-01",
        "total_amount": 100.50,
        "currency": "EUR"
    }
    
    print(f"\nTrying to insert test record...")
    insert_result = supabase.table("invoices").insert(test_data).execute()
    print(f"Insert successful: {len(insert_result.data)} record(s) created")
    
    if insert_result.data:
        print(f"Inserted record ID: {insert_result.data[0]['id']}")
        
        # Now check if we can retrieve it
        check_result = supabase.table("invoices").select("*").execute()
        print(f"After insert - Total records: {len(check_result.data)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
