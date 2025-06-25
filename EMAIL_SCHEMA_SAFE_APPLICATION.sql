-- Step-by-Step Email Schema Application for Supabase
-- Run these commands one by one in your Supabase SQL Editor

-- STEP 1: Check what status values currently exist
SELECT 'Current status values:' as info;
SELECT status, COUNT(*) as count 
FROM invoices_clean 
GROUP BY status 
ORDER BY count DESC;

-- STEP 2: Identify invalid status values
SELECT 'Invalid status values (these will cause the constraint error):' as info;
SELECT status, COUNT(*) as count
FROM invoices_clean 
WHERE status NOT IN (
    'pending', 'uploaded', 'edited', 'pending_email', 
    'edit_completed', 'in_review_by_bauleiter', 
    'approved_by_bauleiter', 'rejected_by_bauleiter', 
    'completed', 'error'
)
GROUP BY status;

-- STEP 3: Fix the invalid status values
-- Uncomment and modify these UPDATE statements based on your actual data

-- Fix NULL values
UPDATE invoices_clean SET status = 'uploaded' WHERE status IS NULL;

-- Fix common alternative status names (uncomment if you have these)
-- UPDATE invoices_clean SET status = 'completed' WHERE status = 'processed';
-- UPDATE invoices_clean SET status = 'edited' WHERE status = 'updated';
-- UPDATE invoices_clean SET status = 'error' WHERE status = 'failed';
-- UPDATE invoices_clean SET status = 'pending' WHERE status = 'new';
-- UPDATE invoices_clean SET status = 'uploaded' WHERE status = 'received';

-- If you have other status values, add them here:
-- UPDATE invoices_clean SET status = 'correct_status' WHERE status = 'your_invalid_status';

-- STEP 4: Verify all status values are now valid
SELECT 'After fixes - remaining invalid values:' as info;
SELECT status, COUNT(*) as count
FROM invoices_clean 
WHERE status NOT IN (
    'pending', 'uploaded', 'edited', 'pending_email', 
    'edit_completed', 'in_review_by_bauleiter', 
    'approved_by_bauleiter', 'rejected_by_bauleiter', 
    'completed', 'error'
)
GROUP BY status;

-- STEP 5: Only run this if STEP 4 shows zero rows
-- Add the email workflow columns (safe - won't fail)
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS editor_email VARCHAR(255);
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS editor_name VARCHAR(255);
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS edit_completed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS edit_bericht_sent_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS bauleiter_email VARCHAR(255);
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS bauleiter_review_sent_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS approval_method VARCHAR(50);
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS change_summary JSONB;
ALTER TABLE invoices_clean ADD COLUMN IF NOT EXISTS email_logs JSONB;

-- STEP 6: Apply the status constraint (only after STEP 4 shows zero invalid rows)
ALTER TABLE invoices_clean DROP CONSTRAINT IF EXISTS check_status;
ALTER TABLE invoices_clean ADD CONSTRAINT check_status 
CHECK (status = ANY (ARRAY[
    'pending'::text,
    'uploaded'::text,
    'edited'::text,
    'pending_email'::text,
    'edit_completed'::text,
    'in_review_by_bauleiter'::text,
    'approved_by_bauleiter'::text,
    'rejected_by_bauleiter'::text,
    'completed'::text,
    'error'::text
]));

-- STEP 7: Apply approval status constraint
ALTER TABLE invoices_clean DROP CONSTRAINT IF EXISTS check_approval_status;
ALTER TABLE invoices_clean ADD CONSTRAINT check_approval_status 
CHECK (approval_status = ANY (ARRAY[
    'pending'::text,
    'approved'::text,
    'rejected'::text
]));

-- Success message
SELECT 'Email workflow columns and constraints applied successfully!' as result;
