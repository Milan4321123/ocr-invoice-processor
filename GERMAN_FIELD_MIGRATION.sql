-- ================================================================
-- FIELD STANDARDIZATION MIGRATION: ALL GERMAN NAMES
-- Execute this in Supabase SQL Editor to standardize field names
-- ================================================================

-- STEP 1: Rename English columns to German equivalents
-- ================================================================

-- Critical business field: due_date → faelligkeit
ALTER TABLE invoices RENAME COLUMN due_date TO faelligkeit_new;

-- Technical fields that should be German for consistency
ALTER TABLE invoices RENAME COLUMN customer_name TO rechnungsempfaenger_extracted;
ALTER TABLE invoices RENAME COLUMN vendor_name TO rechnungssteller_extracted;
ALTER TABLE invoices RENAME COLUMN invoice_number TO rechnungsnummer_extracted;
ALTER TABLE invoices RENAME COLUMN invoice_date TO rechnungsdatum_extracted;
ALTER TABLE invoices RENAME COLUMN subtotal TO netto_betrag_extracted;
ALTER TABLE invoices RENAME COLUMN total_amount TO brutto_betrag_extracted;

-- STEP 2: Verify the changes
-- ================================================================
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name IN (
    'faelligkeit_new', 
    'rechnungsempfaenger_extracted',
    'rechnungssteller_extracted',
    'rechnungsnummer_extracted',
    'rechnungsdatum_extracted',
    'netto_betrag_extracted',
    'brutto_betrag_extracted',
    'projekt',
    'gewerk',
    'skonto_datum',
    'skonto_prozent'
)
ORDER BY column_name;

-- STEP 3: Update any existing data references if needed
-- ================================================================
-- Note: This step may be needed if there are views or triggers
-- that reference the old column names

-- STEP 4: Verification query
-- ================================================================
-- Check that all business fields now use German names
SELECT 
    COUNT(*) as total_records,
    COUNT(faelligkeit_new) as has_due_date,
    COUNT(projekt) as has_project,
    COUNT(skonto_datum) as has_skonto_date,
    COUNT(skonto_prozent) as has_skonto_percent
FROM invoices;

-- STEP 5: Show final schema with German names
-- ================================================================
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name NOT LIKE '%_old'
ORDER BY column_name;
