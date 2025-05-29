#!/usr/bin/env python3
"""
Simple Database Migration Checker and Applier
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def check_and_apply_migration():
    """Check current database schema and guide migration"""
    try:
        url = os.environ.get("SUPA_URL")
        key = os.environ.get("SUPA_KEY")
        
        supabase = create_client(url, key)
        
        print("🔍 Checking current database schema...")
        
        # Try to query the invoices table to see current structure
        try:
            result = supabase.table('invoices').select('*').limit(1).execute()
            print("✅ Successfully connected to invoices table")
            
            # Check if OCR columns exist by trying to select them
            try:
                ocr_check = supabase.table('invoices').select('ocr_status').limit(1).execute()
                print("✅ OCR columns already exist - migration not needed!")
                return True
            except Exception:
                print("⚠️  OCR columns not found - migration needed")
                
        except Exception as e:
            print(f"❌ Error accessing invoices table: {e}")
            return False
        
        print("\n" + "="*60)
        print("DATABASE MIGRATION REQUIRED")
        print("="*60)
        print("\nTo complete the OCR setup, please apply the database migration:")
        print(f"\n1. Open Supabase Dashboard: {url.replace('https://', 'https://supabase.com/dashboard/project/')}")
        print("2. Go to 'SQL Editor' in the sidebar")
        print("3. Copy the SQL from 'ocr_migration.sql' file and execute it")
        
        print(f"\n📄 Migration file location:")
        print(f"   {os.path.abspath('ocr_migration.sql')}")
        
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    check_and_apply_migration()
