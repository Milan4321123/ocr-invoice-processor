-- Email Workflow Schema for Prüfbericht System
-- Adds email notification and approval workflow support to invoices_clean table

-- Add email workflow columns to invoices_clean table
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

-- First, fix any existing invalid status values before applying constraint
-- Update NULL status values
UPDATE invoices_clean SET status = 'uploaded' WHERE status IS NULL;

-- Update common invalid status values to valid ones
UPDATE invoices_clean SET status = 'completed' WHERE status = 'processed';
UPDATE invoices_clean SET status = 'edited' WHERE status = 'updated';
UPDATE invoices_clean SET status = 'error' WHERE status = 'failed';
UPDATE invoices_clean SET status = 'pending' WHERE status = 'new';
UPDATE invoices_clean SET status = 'uploaded' WHERE status = 'received';

-- Check for any remaining invalid status values
DO $$
DECLARE
    invalid_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO invalid_count
    FROM invoices_clean 
    WHERE status NOT IN (
        'pending', 'uploaded', 'edited', 'pending_email', 
        'edit_completed', 'in_review_by_bauleiter', 
        'approved_by_bauleiter', 'rejected_by_bauleiter', 
        'completed', 'error'
    );
    
    IF invalid_count > 0 THEN
        RAISE NOTICE 'Found % rows with invalid status values. Please check and update manually.', invalid_count;
        -- Show the invalid values
        RAISE NOTICE 'Invalid status values found:';
    END IF;
END $$;

-- Now safely update status enum to include new workflow states
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

-- Add approval status constraint
ALTER TABLE invoices_clean DROP CONSTRAINT IF EXISTS check_approval_status;
ALTER TABLE invoices_clean ADD CONSTRAINT check_approval_status 
CHECK (approval_status = ANY (ARRAY[
    'pending'::text,
    'approved'::text,
    'rejected'::text
]));

-- Create email audit log table for security and compliance
CREATE TABLE IF NOT EXISTS email_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices_clean(id) ON DELETE CASCADE,
    email_type VARCHAR(50) NOT NULL, -- 'editor_notification', 'bauleiter_approval'
    recipient_email VARCHAR(255) NOT NULL,
    subject TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    send_success BOOLEAN NOT NULL,
    provider_message_id VARCHAR(255),
    provider_response JSONB,
    template_used VARCHAR(100),
    email_size_bytes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create approval tokens table for secure email link handling
CREATE TABLE IF NOT EXISTS approval_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    invoice_id UUID NOT NULL REFERENCES invoices_clean(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL, -- 'approve', 'reject'
    user_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE NULL,
    used_by_ip VARCHAR(45) NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    nonce VARCHAR(255) NOT NULL
);

-- Create security events log for monitoring
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_email VARCHAR(255),
    invoice_id UUID,
    token_id UUID,
    event_data JSONB,
    risk_level VARCHAR(20) DEFAULT 'low',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_audit_invoice_id ON email_audit_log(invoice_id);
CREATE INDEX IF NOT EXISTS idx_email_audit_sent_at ON email_audit_log(sent_at);
CREATE INDEX IF NOT EXISTS idx_approval_tokens_invoice_id ON approval_tokens(invoice_id);
CREATE INDEX IF NOT EXISTS idx_approval_tokens_expires_at ON approval_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices_clean(status);
CREATE INDEX IF NOT EXISTS idx_invoices_approval_status ON invoices_clean(approval_status);

-- Add comments for documentation
COMMENT ON COLUMN invoices_clean.editor_email IS 'Email of person who edited the invoice';
COMMENT ON COLUMN invoices_clean.edit_completed_at IS 'When the edit was marked as completed';
COMMENT ON COLUMN invoices_clean.edit_bericht_sent_at IS 'When the edit notification email was sent';
COMMENT ON COLUMN invoices_clean.bauleiter_email IS 'Email of Bau-Leiter assigned to this invoice';
COMMENT ON COLUMN invoices_clean.bauleiter_review_sent_at IS 'When approval request was sent to Bau-Leiter';
COMMENT ON COLUMN invoices_clean.approval_status IS 'Current approval status (pending/approved/rejected)';
COMMENT ON COLUMN invoices_clean.change_summary IS 'JSON summary of all changes made during editing';
COMMENT ON COLUMN invoices_clean.email_logs IS 'JSON log of all emails sent for this invoice';

COMMENT ON TABLE email_audit_log IS 'Audit trail for all emails sent by the system';
COMMENT ON TABLE approval_tokens IS 'Secure tokens for email approval links';
COMMENT ON TABLE security_events IS 'Security monitoring and threat detection';

-- Note: Skipping dropdown_options inserts as the table has a constraint 
-- that only allows specific field names (rechnungsempfaenger, rechnungssteller, etc.)
-- and 'email_templates' is not in the allowed list.
-- Email templates will be handled directly in the application code.

-- Email workflow schema application completed successfully!
SELECT 'Email workflow schema applied successfully! All tables and columns created.' as result;
