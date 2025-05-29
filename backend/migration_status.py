#!/usr/bin/env python3
"""
OCR Database Migration Status and Instructions
Complete guide for applying the database migration
"""

import os
from dotenv import load_dotenv

load_dotenv()

def show_migration_status():
    """Show complete migration status and instructions"""
    
    print("🚀 OCR INVOICE PROCESSOR - DATABASE MIGRATION STATUS")
    print("=" * 70)
    
    # Check connection
    try:
        from supabase import create_client
        url = os.environ.get("SUPA_URL")
        key = os.environ.get("SUPA_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials not found in .env file")
            return
        
        client = create_client(url, key)
        
        # Test basic connection
        result = client.table('invoices').select('id').limit(1).execute()
        print(f"✅ Database connection successful")
        print(f"📊 Current invoices table has {len(result.data)} record(s)")
        
        # Check OCR columns
        try:
            ocr_test = client.table('invoices').select('ocr_status').limit(1).execute()
            print("✅ OCR columns already exist - migration complete!")
            print("\n🎉 Your OCR system is ready to use!")
            return
        except Exception:
            print("⚠️  OCR columns not found - migration required")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    print("\n📋 MIGRATION REQUIRED")
    print("-" * 40)
    print("The OCR functionality needs additional database columns.")
    print("\n🔧 TO APPLY THE MIGRATION:")
    print("1. Open your Supabase dashboard:")
    print(f"   https://supabase.com/dashboard/project/{url.split('//')[1].split('.')[0]}")
    print("\n2. Navigate to 'SQL Editor' in the left sidebar")
    print("\n3. Copy the migration SQL below and paste it into the editor:")
    print("\n4. Click 'Run' to execute")
    
    print("\n" + "="*70)
    print("MIGRATION SQL (Copy this):")
    print("="*70)
    
    # Read and display the migration SQL
    try:
        with open("ocr_migration.sql", "r") as f:
            migration_sql = f.read()
        print(migration_sql)
    except FileNotFoundError:
        print("❌ Migration file not found. Please run database_migration.py first.")
        return
    
    print("="*70)
    
    print("\n✅ AFTER MIGRATION:")
    print("• Your database will have OCR columns for storing extracted data")
    print("• Invoice uploads will automatically process OCR (when enabled)")
    print("• New API endpoints will be available for OCR operations")
    
    print("\n🔑 NEXT STEPS AFTER MIGRATION:")
    print("1. Set up Google Cloud Document AI credentials")
    print("2. Enable OCR in .env file (ENABLE_OCR=true)")
    print("3. Test OCR functionality with sample invoices")
    
    print(f"\n📂 Project location: {os.getcwd()}")
    print("📄 Migration file: ocr_migration.sql")

if __name__ == "__main__":
    show_migration_status()
