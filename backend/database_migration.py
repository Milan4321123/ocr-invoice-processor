"""
Database Schema Migration for OCR Features
Adds OCR-related columns to the invoices table to store structured data
"""

import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_migration_sql():
    """Get SQL statements for OCR schema migration"""
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

def run_migration():
    """Run the database migration"""
    try:
        # Initialize Supabase client
        url = os.environ.get("SUPA_URL")
        key = os.environ.get("SUPA_KEY")
        
        if not url or not key:
            print("Error: SUPA_URL and SUPA_KEY environment variables are required")
            return False
        
        supabase = create_client(url, key)
        
        # Get migration SQL
        migration_sql = get_migration_sql()
        
        # Execute migration (Note: Supabase Python client doesn't support raw SQL execution)
        # This migration would need to be run directly in the Supabase SQL editor
        # or via the Supabase CLI
        
        print("Migration SQL generated successfully!")
        print("=" * 60)
        print("Please run the following SQL in your Supabase SQL editor:")
        print("=" * 60)
        print(migration_sql)
        print("=" * 60)
        
        # Alternatively, save to file
        with open("ocr_migration.sql", "w") as f:
            f.write(migration_sql)
        
        print("Migration SQL also saved to 'ocr_migration.sql'")
        print("\nTo apply the migration:")
        print("1. Copy the SQL above and run it in Supabase SQL editor")
        print("2. Or use Supabase CLI: supabase db apply ocr_migration.sql")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()
