-- Database Migration Script for Skonto Reminder System
-- Phase 2: Add Skonto tracking fields to public.invoices_clean table
-- Version: 2.0
-- Date: 2025-07-01
-- Matches existing schema with proper field types and constraints

-- ============================================================================
-- SKONTO TRACKING FIELDS MIGRATION
-- ============================================================================

-- Add Skonto reminder tracking fields (matching existing schema style)
ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_reminder_sent BOOLEAN DEFAULT FALSE;

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_reminder_sent_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_reminder_email CHARACTER VARYING(255);

-- Add Skonto decision tracking fields
ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_decision CHARACTER VARYING(20) DEFAULT 'pending';

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_decision_timestamp TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_decision_email CHARACTER VARYING(255);

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS actual_skonto_savings NUMERIC(10,2);

-- Add constraint for skonto_decision values (matching existing constraint style)
ALTER TABLE public.invoices_clean 
ADD CONSTRAINT check_skonto_decision CHECK (
    (skonto_decision)::text = ANY (
        ARRAY[
            'pending'::text,
            'taken'::text,
            'missed'::text,
            'not_applicable'::text
        ]
    )
);

-- Add indexes for performance (matching existing index style)
CREATE INDEX IF NOT EXISTS idx_invoices_skonto_reminder 
ON public.invoices_clean USING btree (skonto_reminder_sent, skonto_datum) 
WHERE skonto_datum IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_invoices_skonto_decision 
ON public.invoices_clean USING btree (skonto_decision, skonto_datum) 
WHERE skonto_datum IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_invoices_skonto_expiry 
ON public.invoices_clean USING btree (skonto_datum) 
WHERE skonto_datum IS NOT NULL AND skonto_reminder_sent = FALSE;

-- ============================================================================
-- SKONTO REPORTING VIEWS
-- ============================================================================

-- Create view for Skonto performance tracking
CREATE OR REPLACE VIEW skonto_performance_summary AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_invoices_with_skonto,
    COUNT(CASE WHEN skonto_decision = 'taken' THEN 1 END) as skonto_taken_count,
    COUNT(CASE WHEN skonto_decision = 'missed' THEN 1 END) as skonto_missed_count,
    COUNT(CASE WHEN skonto_reminder_sent = TRUE THEN 1 END) as reminders_sent_count,
    COALESCE(SUM(CASE WHEN skonto_decision = 'taken' THEN actual_skonto_savings END), 0) as total_savings_achieved,
    COALESCE(SUM(CASE WHEN skonto_decision = 'missed' AND skonto_prozent IS NOT NULL AND rechnungsbetrag IS NOT NULL 
        THEN (rechnungsbetrag * skonto_prozent / 100) END), 0) as total_savings_missed,
    ROUND(
        COUNT(CASE WHEN skonto_decision = 'taken' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(CASE WHEN skonto_decision IN ('taken', 'missed') THEN 1 END), 0) * 100, 2
    ) as skonto_success_rate
FROM public.invoices_clean 
WHERE skonto_datum IS NOT NULL 
  AND skonto_prozent IS NOT NULL
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- Create view for current Skonto opportunities
CREATE OR REPLACE VIEW current_skonto_opportunities AS
SELECT 
    id,
    file_name,
    rechnungssteller,
    rechnungsempfaenger,
    rechnungsbetrag,
    skonto_datum,
    skonto_prozent,
    (rechnungsbetrag * skonto_prozent / 100) as potential_savings,
    (skonto_datum - CURRENT_DATE) as days_until_expiry,
    skonto_reminder_sent,
    skonto_decision,
    CASE 
        WHEN (skonto_datum - CURRENT_DATE) <= 1 THEN 'urgent'
        WHEN (skonto_datum - CURRENT_DATE) <= 3 THEN 'important'
        WHEN (skonto_datum - CURRENT_DATE) <= 7 THEN 'upcoming'
        ELSE 'future'
    END as urgency_level
FROM public.invoices_clean 
WHERE skonto_datum IS NOT NULL 
  AND skonto_prozent IS NOT NULL
  AND skonto_decision IN ('pending')
  AND skonto_datum >= CURRENT_DATE
ORDER BY skonto_datum ASC;

-- ============================================================================
-- AUTOMATED SKONTO FUNCTIONS
-- ============================================================================

-- Function to get invoices needing Skonto reminders
CREATE OR REPLACE FUNCTION get_invoices_needing_skonto_reminders(days_ahead INT DEFAULT 7)
RETURNS TABLE (
    invoice_id UUID,
    file_name CHARACTER VARYING,
    rechnungssteller CHARACTER VARYING,
    rechnungsempfaenger CHARACTER VARYING,
    rechnungsbetrag NUMERIC,
    skonto_datum DATE,
    skonto_prozent NUMERIC,
    potential_savings NUMERIC,
    days_until_expiry INT,
    bauleiter_email CHARACTER VARYING
) 
LANGUAGE SQL
STABLE
AS $$
    SELECT 
        id as invoice_id,
        file_name,
        rechnungssteller,
        rechnungsempfaenger,
        rechnungsbetrag,
        skonto_datum,
        skonto_prozent,
        (rechnungsbetrag * skonto_prozent / 100) as potential_savings,
        (skonto_datum - CURRENT_DATE) as days_until_expiry,
        bauleiter_email
    FROM public.invoices_clean 
    WHERE skonto_datum IS NOT NULL 
      AND skonto_prozent IS NOT NULL
      AND skonto_reminder_sent = FALSE
      AND skonto_decision = 'pending'
      AND skonto_datum >= CURRENT_DATE
      AND skonto_datum <= (CURRENT_DATE + INTERVAL '%s days')
      AND approval_status = 'approved'  -- Only send reminders for approved invoices
    ORDER BY skonto_datum ASC;
$$;

-- Function to calculate Skonto savings potential
CREATE OR REPLACE FUNCTION calculate_total_skonto_potential()
RETURNS TABLE (
    total_opportunities INT,
    total_potential_savings NUMERIC,
    urgent_count INT,
    urgent_potential NUMERIC,
    monthly_average_savings NUMERIC
)
LANGUAGE SQL
STABLE
AS $$
    WITH skonto_stats AS (
        SELECT 
            COUNT(*) as opportunities,
            SUM(rechnungsbetrag * skonto_prozent / 100) as potential,
            COUNT(CASE WHEN (skonto_datum - CURRENT_DATE) <= 3 THEN 1 END) as urgent,
            SUM(CASE WHEN (skonto_datum - CURRENT_DATE) <= 3 
                THEN (rechnungsbetrag * skonto_prozent / 100) END) as urgent_potential
        FROM public.invoices_clean 
        WHERE skonto_datum IS NOT NULL 
          AND skonto_prozent IS NOT NULL
          AND skonto_decision = 'pending'
          AND skonto_datum >= CURRENT_DATE
    ),
    monthly_avg AS (
        SELECT 
            AVG(monthly_savings) as avg_savings
        FROM (
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                SUM(actual_skonto_savings) as monthly_savings
            FROM public.invoices_clean 
            WHERE skonto_decision = 'taken'
              AND created_at >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', created_at)
        ) monthly_data
    )
    SELECT 
        s.opportunities::INT,
        COALESCE(s.potential, 0)::NUMERIC,
        s.urgent::INT,
        COALESCE(s.urgent_potential, 0)::NUMERIC,
        COALESCE(m.avg_savings, 0)::NUMERIC
    FROM skonto_stats s
    CROSS JOIN monthly_avg m;
$$;

-- ============================================================================
-- AUDIT AND LOGGING ENHANCEMENTS
-- ============================================================================

-- Add audit trigger for Skonto decision changes (optional if audit_log table exists)
CREATE OR REPLACE FUNCTION audit_skonto_decisions()
RETURNS TRIGGER AS $$
BEGIN
    -- Log Skonto decision changes
    IF OLD.skonto_decision IS DISTINCT FROM NEW.skonto_decision THEN
        -- Note: This assumes an audit_log table exists
        -- Remove this section if no audit table is available
        INSERT INTO audit_log (
            table_name,
            record_id,
            action,
            old_values,
            new_values,
            changed_by,
            changed_at
        ) VALUES (
            'invoices_clean',
            NEW.id,
            'skonto_decision_change',
            json_build_object('skonto_decision', OLD.skonto_decision, 'actual_skonto_savings', OLD.actual_skonto_savings),
            json_build_object('skonto_decision', NEW.skonto_decision, 'actual_skonto_savings', NEW.actual_skonto_savings),
            NEW.skonto_decision_email,
            NOW()
        );
    END IF;
    
    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    -- If audit_log table doesn't exist, just continue without logging
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create audit trigger if audit_log table exists
-- DROP TRIGGER IF EXISTS trigger_audit_skonto_decisions ON public.invoices_clean;
-- CREATE TRIGGER trigger_audit_skonto_decisions
--     AFTER UPDATE ON public.invoices_clean
--     FOR EACH ROW
--     EXECUTE FUNCTION audit_skonto_decisions();

-- ============================================================================
-- SAMPLE DATA AND VALIDATION
-- ============================================================================

-- Verify migration completed successfully
DO $$
DECLARE
    column_count INT;
BEGIN
    SELECT COUNT(*)
    INTO column_count
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'invoices_clean'
      AND column_name IN (
          'skonto_reminder_sent',
          'skonto_reminder_sent_at',
          'skonto_decision',
          'actual_skonto_savings'
      );
    
    IF column_count = 4 THEN
        RAISE NOTICE 'SUCCESS: All Skonto tracking fields added successfully';
    ELSE
        RAISE EXCEPTION 'FAILED: Expected 4 Skonto fields, found %', column_count;
    END IF;
END $$;

-- Create sample data for testing (optional - comment out for production)
/*
INSERT INTO public.invoices_clean (
    file_name, rechnungssteller, rechnungsempfaenger, rechnungsbetrag, 
    skonto_datum, skonto_prozent, approval_status,
    created_at, updated_at
) VALUES 
    ('TEST_SKONTO_001.pdf', 'Test Supplier A', 'Company ABC', 1500.00, '2025-07-10', 2.5, 'approved', NOW(), NOW()),
    ('TEST_SKONTO_002.pdf', 'Test Supplier B', 'Company ABC', 2000.00, '2025-07-05', 3.0, 'approved', NOW(), NOW()),
    ('TEST_SKONTO_003.pdf', 'Test Supplier C', 'Company ABC', 800.00, '2025-07-15', 2.0, 'approved', NOW(), NOW())
ON CONFLICT (file_name) DO NOTHING;
*/

-- ============================================================================
-- PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE public.invoices_clean;

-- Show index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
  AND tablename = 'invoices_clean'
  AND indexname LIKE '%skonto%'
ORDER BY idx_scan DESC;

-- Migration completed successfully
SELECT 'Skonto Reminder System Database Migration Completed Successfully' as status;
