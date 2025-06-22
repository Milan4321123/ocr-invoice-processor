-- ================================================================
-- PHASE 3 DATABASE MIGRATION: Folder Watcher Integration
-- Execute this in Supabase SQL Editor to fix folder watcher uploads
-- ================================================================

-- Add missing columns for Phase 1 Common Upload Service
-- These columns are required for the upload service to work properly

-- 1. Source tracking columns
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS source_type VARCHAR(50) DEFAULT 'drag_drop';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS source_metadata JSONB DEFAULT '{}';

-- 2. OCR status columns (for manual OCR processing)
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS ocr_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS ocr_text TEXT DEFAULT '';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS ocr_pages INTEGER DEFAULT 0;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS ocr_error TEXT;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS ocr_processed_at TIMESTAMP WITH TIME ZONE;

-- 3. Enhanced invoice data columns (structured OCR results)
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(100);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS invoice_date DATE;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS due_date DATE;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS vendor_name VARCHAR(255);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS vendor_address TEXT;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_name VARCHAR(255);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_address TEXT;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS subtotal DECIMAL(10,2);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(10,2);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10,2);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'EUR';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_terms VARCHAR(255);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS po_number VARCHAR(100);

-- 4. Complex OCR data columns (JSON storage)
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS entities JSONB DEFAULT '[]';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS form_fields JSONB DEFAULT '[]';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS tables JSONB DEFAULT '[]';
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS line_items JSONB DEFAULT '[]';

-- 5. Add compatibility columns for the upload service
-- The upload service expects 'filename' but the table has 'file_name'
-- We'll add both columns and keep them synchronized
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS filename VARCHAR(255);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS url TEXT;

-- Update existing records to populate the new filename column
UPDATE invoices SET filename = file_name WHERE filename IS NULL AND file_name IS NOT NULL;

-- Create a trigger to keep filename and file_name synchronized
CREATE OR REPLACE FUNCTION sync_filename_fields()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- If filename is set but file_name is not, copy it
        IF NEW.filename IS NOT NULL AND NEW.file_name IS NULL THEN
            NEW.file_name = NEW.filename;
        END IF;
        -- If file_name is set but filename is not, copy it
        IF NEW.file_name IS NOT NULL AND NEW.filename IS NULL THEN
            NEW.filename = NEW.file_name;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for filename synchronization
DROP TRIGGER IF EXISTS sync_filename_trigger ON invoices;
CREATE TRIGGER sync_filename_trigger
    BEFORE INSERT OR UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION sync_filename_fields();

-- 6. Update indexes for better performance on new columns
CREATE INDEX IF NOT EXISTS idx_invoices_source_type ON invoices(source_type);
CREATE INDEX IF NOT EXISTS idx_invoices_ocr_status ON invoices(ocr_status);
CREATE INDEX IF NOT EXISTS idx_invoices_filename ON invoices(filename);

-- 7. Update the trigger to handle the new updated_at timestamp
-- (The trigger should already exist from the original schema)

-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================

-- Check if all columns were added successfully
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'invoices' 
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- Verify existing data integrity
SELECT 
    COUNT(*) as total_invoices,
    COUNT(CASE WHEN source_type IS NOT NULL THEN 1 END) as has_source_type,
    COUNT(CASE WHEN filename IS NOT NULL THEN 1 END) as has_filename,
    COUNT(CASE WHEN ocr_status IS NOT NULL THEN 1 END) as has_ocr_status
FROM invoices;

-- Show sample of migrated data
SELECT 
    id,
    filename,
    file_name,
    source_type,
    ocr_status,
    status,
    created_at
FROM invoices 
ORDER BY created_at DESC 
LIMIT 5;
