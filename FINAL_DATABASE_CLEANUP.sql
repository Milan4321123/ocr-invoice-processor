-- ===================================================================
-- FINAL DATABASE CLEANUP - OPTIONAL ENHANCEMENT
-- ===================================================================
-- This script completes the German field standardization by:
-- 1. Renaming faelligkeit_new → faelligkeit (for consistency)
-- 2. Cleaning up any remaining English column artifacts
-- 
-- ⚠️  IMPORTANT: This is OPTIONAL and should be done during maintenance
-- ⚠️  Current system works perfectly with faelligkeit_new
-- ===================================================================

-- Step 1: Rename faelligkeit_new to faelligkeit for consistency
-- (Frontend already uses 'faelligkeit', database uses 'faelligkeit_new')
ALTER TABLE invoices RENAME COLUMN faelligkeit_new TO faelligkeit;

-- Step 2: Add comment to document the German standard
COMMENT ON COLUMN invoices.faelligkeit IS 'Due date (German standard - Fälligkeitsdatum)';
COMMENT ON COLUMN invoices.projekt IS 'Project name (German standard)';
COMMENT ON COLUMN invoices.brutto_betrag IS 'Gross amount (German standard - Bruttobetrag)';
COMMENT ON COLUMN invoices.skonto_datum IS 'Discount date (German standard)';
COMMENT ON COLUMN invoices.skonto_prozent IS 'Discount percentage (German standard)';
COMMENT ON COLUMN invoices.rechnungsart IS 'Invoice type (German standard)';

-- Step 3: Update any constraints or indexes that reference the old column name
-- (Run this if there are any constraints on faelligkeit_new)
-- This is environment-specific and may not be needed

-- ===================================================================
-- VERIFICATION QUERIES
-- ===================================================================

-- Verify the column rename worked
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
  AND column_name IN ('faelligkeit', 'faelligkeit_new', 'projekt', 'brutto_betrag')
ORDER BY column_name;

-- Test data integrity after rename
SELECT id, projekt, brutto_betrag, faelligkeit, skonto_datum, skonto_prozent 
FROM invoices 
WHERE projekt LIKE '%German%' 
LIMIT 3;

-- ===================================================================
-- ROLLBACK PLAN (if needed)
-- ===================================================================

-- If anything goes wrong, rollback with:
-- ALTER TABLE invoices RENAME COLUMN faelligkeit TO faelligkeit_new;
