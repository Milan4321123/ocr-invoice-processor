-- Add review status columns to invoices_clean table
-- Run this in Supabase SQL Editor

ALTER TABLE invoices_clean 
ADD COLUMN review_status text,
ADD COLUMN reviewed_by text,
ADD COLUMN reviewed_at timestamptz,
ADD COLUMN review_notes text;

-- Set default review status for existing records
UPDATE invoices_clean 
SET review_status = 'pending' 
WHERE review_status IS NULL;

-- Add check constraint for valid review statuses
ALTER TABLE invoices_clean 
ADD CONSTRAINT check_review_status 
CHECK (review_status IN ('pending', 'under_review', 'completed_review', 'needs_attention'));

-- Add comment for documentation
COMMENT ON COLUMN invoices_clean.review_status IS 'Review status: pending, under_review, completed_review, needs_attention';
COMMENT ON COLUMN invoices_clean.reviewed_by IS 'Email of person who reviewed the invoice';
COMMENT ON COLUMN invoices_clean.reviewed_at IS 'Timestamp when review was completed';
COMMENT ON COLUMN invoices_clean.review_notes IS 'Additional notes from the review process';
