#!/usr/bin/env python3
"""
Verify OCR Database Migration
Quick script to verify that the migration was applied successfully
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def verify_migration():
    """Verify that the OCR migration was applied successfully"""
    
    try:
        url = os.environ.get("SUPA_URL")
        key = os.environ.get("SUPA_KEY")
        
        client = create_client(url, key)
        
        print("🔍 Verifying OCR database migration...")
        
        # Test OCR columns
        ocr_columns = [
            'ocr_status', 'ocr_text', 'ocr_confidence', 'ocr_pages',
            'invoice_number', 'vendor_name', 'total_amount', 'ocr_entities'
        ]
        
        success_count = 0
        
        for column in ocr_columns:
            try:
                result = client.table('invoices').select(column).limit(1).execute()
                print(f"✅ {column} - OK")
                success_count += 1
            except Exception as e:
                print(f"❌ {column} - Missing")
        
        print(f"\n📊 Migration Status: {success_count}/{len(ocr_columns)} columns found")
        
        if success_count == len(ocr_columns):
            print("\n🎉 MIGRATION SUCCESSFUL!")
            print("✅ All OCR columns are present")
            print("✅ Database is ready for OCR functionality")
            
            print("\n🔄 Next Steps:")
            print("1. Set up Google Cloud Document AI credentials")
            print("2. Update ENABLE_OCR=true in .env file")
            print("3. Test OCR endpoints")
            
            return True
        else:
            print(f"\n⚠️  MIGRATION INCOMPLETE")
            print(f"Missing {len(ocr_columns) - success_count} columns")
            print("Please re-run the migration SQL in Supabase dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_migration()
