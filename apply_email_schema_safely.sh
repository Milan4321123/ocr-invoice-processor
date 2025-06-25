#!/bin/bash
"""
Safe Email Workflow Schema Application Script
Handles existing data and applies schema changes step by step
"""

echo "🔧 Safe Email Workflow Schema Application"
echo "========================================"

echo "Step 1: Checking current status values..."

# First, let's check what status values exist in your database
echo "Current status values in your database:"
echo "SELECT status, COUNT(*) FROM invoices_clean GROUP BY status;"

echo ""
echo "Step 2: Apply the fixed schema..."
echo "Please run these SQL commands in your Supabase SQL editor:"

echo ""
echo "-- STEP 1: Check existing status values"
cat << 'EOF'
SELECT status, COUNT(*) as count 
FROM invoices_clean 
GROUP BY status 
ORDER BY count DESC;
EOF

echo ""
echo "-- STEP 2: Fix invalid status values"
cat << 'EOF'
-- Update NULL status values
UPDATE invoices_clean SET status = 'uploaded' WHERE status IS NULL;

-- Update common invalid status values to valid ones
UPDATE invoices_clean SET status = 'completed' WHERE status = 'processed';
UPDATE invoices_clean SET status = 'edited' WHERE status = 'updated';
UPDATE invoices_clean SET status = 'error' WHERE status = 'failed';
UPDATE invoices_clean SET status = 'pending' WHERE status = 'new';
UPDATE invoices_clean SET status = 'uploaded' WHERE status = 'received';

-- Add any other mappings based on YOUR specific data
-- UPDATE invoices_clean SET status = 'correct_status' WHERE status = 'your_specific_invalid_status';
EOF

echo ""
echo "-- STEP 3: Check for remaining invalid values"
cat << 'EOF'
SELECT id, status, created_at 
FROM invoices_clean 
WHERE status NOT IN (
    'pending', 'uploaded', 'edited', 'pending_email', 
    'edit_completed', 'in_review_by_bauleiter', 
    'approved_by_bauleiter', 'rejected_by_bauleiter', 
    'completed', 'error'
)
LIMIT 10;
EOF

echo ""
echo "-- STEP 4: Apply the email workflow schema (run this after fixing status values)"
echo "-- Use the updated EMAIL_WORKFLOW_SCHEMA.sql file"

echo ""
echo "🎯 Manual Steps:"
echo "1. Run STEP 1 to see what status values you have"
echo "2. Run STEP 2 to fix common invalid values"  
echo "3. Run STEP 3 to check if any invalid values remain"
echo "4. If STEP 3 shows invalid values, update them manually"
echo "5. Then run the full EMAIL_WORKFLOW_SCHEMA.sql"

echo ""
echo "📋 Common Status Mappings You Might Need:"
echo "  'new' → 'pending'"
echo "  'received' → 'uploaded'"
echo "  'processed' → 'completed'"
echo "  'updated' → 'edited'"
echo "  'failed' → 'error'"
echo "  NULL → 'uploaded'"

echo ""
echo "⚠️  If you have custom status values, you'll need to map them manually"
echo "   before applying the schema constraint."

exit 0
