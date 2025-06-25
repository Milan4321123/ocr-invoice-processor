-- Fix for EMAIL_WORKFLOW_SCHEMA.sql constraint violation
-- Run this BEFORE applying the main schema to handle existing data

-- First, let's see what status values currently exist
SELECT status, COUNT(*) as count 
FROM invoices_clean 
GROUP BY status 
ORDER BY count DESC;

-- Check for any NULL or unexpected status values
SELECT id, status, created_at 
FROM invoices_clean 
WHERE status IS NULL 
   OR status NOT IN (
       'pending', 'uploaded', 'edited', 'pending_email', 
       'edit_completed', 'in_review_by_bauleiter', 
       'approved_by_bauleiter', 'rejected_by_bauleiter', 
       'completed', 'error'
   );

-- Update any invalid status values to valid ones
-- Based on your query result: you have 1 row with status 'approved'

-- Fix the 'approved' status to 'completed' (since it's already approved)
UPDATE invoices_clean 
SET status = 'completed' 
WHERE status = 'approved';

-- Common fixes for existing data (in case you have others):
UPDATE invoices_clean 
SET status = 'uploaded' 
WHERE status IS NULL;

UPDATE invoices_clean 
SET status = 'completed' 
WHERE status = 'processed';

UPDATE invoices_clean 
SET status = 'edited' 
WHERE status = 'updated';

UPDATE invoices_clean 
SET status = 'error' 
WHERE status = 'failed';

-- Now check again to ensure all statuses are valid
SELECT status, COUNT(*) as count 
FROM invoices_clean 
GROUP BY status 
ORDER BY count DESC;
