-- Simple Skonto Tracking - Just the Essentials
-- Add only the 4 columns we actually need

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_reminder_sent BOOLEAN DEFAULT FALSE;

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_reminder_sent_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS skonto_decision CHARACTER VARYING(20) DEFAULT 'pending';

ALTER TABLE public.invoices_clean 
ADD COLUMN IF NOT EXISTS actual_skonto_savings NUMERIC(10,2);

-- Simple constraint
ALTER TABLE public.invoices_clean 
ADD CONSTRAINT check_skonto_decision CHECK (
    skonto_decision IN ('pending', 'taken', 'missed', 'not_applicable')
);

-- One index for performance
CREATE INDEX IF NOT EXISTS idx_skonto_reminders 
ON public.invoices_clean (skonto_datum, skonto_reminder_sent) 
WHERE skonto_datum IS NOT NULL;

-- Verify it worked
SELECT 'Skonto fields added successfully' as result;