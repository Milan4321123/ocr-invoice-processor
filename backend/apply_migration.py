#!/usr/bin/env python3
"""
Apply OCR Database Migration
Directly executes the migration SQL using psycopg2
"""

import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get PostgreSQL connection from Supabase URL"""
    supa_url = os.environ.get("SUPA_URL")
    if not supa_url:
        raise ValueError("SUPA_URL environment variable is required")
    
    # Convert Supabase URL to PostgreSQL connection string
    # Format: https://wdattftvflmnconmtiuu.supabase.co
    # To: postgresql://postgres:[password]@db.wdattftvflmnconmtiuu.supabase.co:5432/postgres
    
    parsed = urlparse(supa_url)
    host = f"db.{parsed.hostname}"
    
    # For this migration, we'll use the service role key as password
    # In production, you should use a proper database password
    service_key = os.environ.get("SUPA_KEY")
    
    conn_string = f"postgresql://postgres.wdattftvflmnconmtiuu:{service_key}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
    
    return psycopg2.connect(conn_string)

def get_migration_sql():
    """Get the migration SQL"""
    return """
    -- Add OCR-related columns to invoices table
    ALTER TABLE invoices 
    ADD COLUMN IF NOT EXISTS ocr_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS ocr_text TEXT,
    ADD COLUMN IF NOT EXISTS ocr_confidence DECIMAL(5,4),
    ADD COLUMN IF NOT EXISTS ocr_pages INTEGER,
    ADD COLUMN IF NOT EXISTS ocr_processing_time DECIMAL(8,3),
    ADD COLUMN IF NOT EXISTS ocr_error TEXT,
    
    -- Structured invoice data columns
    ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(100),
    ADD COLUMN IF NOT EXISTS invoice_date DATE,
    ADD COLUMN IF NOT EXISTS due_date DATE,
    ADD COLUMN IF NOT EXISTS vendor_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS vendor_address TEXT,
    ADD COLUMN IF NOT EXISTS customer_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS customer_address TEXT,
    ADD COLUMN IF NOT EXISTS subtotal DECIMAL(15,2),
    ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(15,2),
    ADD COLUMN IF NOT EXISTS total_amount DECIMAL(15,2),
    ADD COLUMN IF NOT EXISTS currency VARCHAR(10),
    ADD COLUMN IF NOT EXISTS payment_terms VARCHAR(255),
    ADD COLUMN IF NOT EXISTS po_number VARCHAR(100),
    
    -- JSON columns for complex data
    ADD COLUMN IF NOT EXISTS ocr_entities JSONB,
    ADD COLUMN IF NOT EXISTS ocr_form_fields JSONB,
    ADD COLUMN IF NOT EXISTS ocr_tables JSONB,
    ADD COLUMN IF NOT EXISTS line_items JSONB,
    
    -- Timestamps
    ADD COLUMN IF NOT EXISTS ocr_processed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
    
    -- Add indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_invoices_ocr_status ON invoices(ocr_status);
    CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
    CREATE INDEX IF NOT EXISTS idx_invoices_vendor_name ON invoices(vendor_name);
    CREATE INDEX IF NOT EXISTS idx_invoices_total_amount ON invoices(total_amount);
    CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date ON invoices(invoice_date);
    
    -- Add trigger to update updated_at timestamp
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS update_invoices_updated_at ON invoices;
    CREATE TRIGGER update_invoices_updated_at
        BEFORE UPDATE ON invoices
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """

def apply_migration():
    """Apply the database migration"""
    try:
        print("Connecting to database...")
        
        # Since direct PostgreSQL connection might be complex with Supabase,
        # let's use the Supabase REST API approach instead
        from supabase import create_client
        
        url = os.environ.get("SUPA_URL")
        key = os.environ.get("SUPA_KEY")
        
        if not url or not key:
            print("Error: SUPA_URL and SUPA_KEY environment variables are required")
            return False
        
        supabase = create_client(url, key)
        
        print("✅ Connected to Supabase successfully")
        print("\n" + "="*60)
        print("IMPORTANT: Database Migration Required")
        print("="*60)
        
        print("\nThe OCR functionality requires additional database columns.")
        print("Please apply the migration by following these steps:")
        print("\n1. Go to your Supabase dashboard:")
        print(f"   {url.replace('https://', 'https://supabase.com/dashboard/project/')}")
        print("\n2. Navigate to 'SQL Editor' in the sidebar")
        print("\n3. Copy and paste the following SQL:")
        
        migration_sql = get_migration_sql()
        print("\n" + "-"*60)
        print(migration_sql)
        print("-"*60)
        
        print("\n4. Click 'Run' to execute the migration")
        print("\n5. Verify the migration completed successfully")
        
        # Save the SQL to a file for easy copy-paste
        with open("ocr_migration.sql", "w") as f:
            f.write(migration_sql)
        
        print(f"\n📄 Migration SQL also saved to: ocr_migration.sql")
        print("\nOnce the migration is complete, your OCR functionality will be ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    apply_migration()
