-- ================================================================
-- ADD SKONTO COLUMNS TO INVOICES TABLE
-- Run this in Supabase SQL Editor to add missing skonto fields
-- ================================================================

-- Add skonto (discount) related columns
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS skonto_datum DATE;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS skonto_prozent NUMERIC(5,2);

-- Add other business fields that might be missing
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS rechnungsart VARCHAR(100);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS kfw_anrechenbar BOOLEAN DEFAULT FALSE;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS rechnungspruefung_email VARCHAR(255);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS weiter_berechnen_an VARCHAR(255);

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name IN ('skonto_datum', 'skonto_prozent', 'rechnungsart', 'kfw_anrechenbar', 'rechnungspruefung_email', 'weiter_berechnen_an')
ORDER BY column_name;
