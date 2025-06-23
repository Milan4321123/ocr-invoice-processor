#!/bin/bash

# Frontend API Fix Verification Test
echo "🔍 FRONTEND API FIX VERIFICATION TEST"
echo "====================================="

INVOICE_ID="12760fc2-1d87-4344-9d49-045c864c0de5"
API_URL="http://localhost:8001"

echo "1. Testing BEFORE fix (what was causing the error)..."
echo "   Sending: {\"fields\": {\"projekt\": \"Test\"}}"
BEFORE_RESULT=$(curl -s -X PUT -H "Content-Type: application/json" \
  -d '{"fields": {"projekt": "Before Fix Test"}}' \
  "$API_URL/invoices/$INVOICE_ID/editor")

echo "   Result: $BEFORE_RESULT"
echo ""

echo "2. Testing AFTER fix (what should work now)..."
echo "   Sending: {\"projekt\": \"Test\"}"
AFTER_RESULT=$(curl -s -X PUT -H "Content-Type: application/json" \
  -d '{"projekt": "After Fix Test", "rechnungsbetrag": 1234.56}' \
  "$API_URL/invoices/$INVOICE_ID/editor")

echo "   Result: $AFTER_RESULT"
echo ""

echo "3. Verifying data was saved..."
VERIFY_RESULT=$(curl -s "$API_URL/invoices/$INVOICE_ID/editor" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    fields = data.get('fields', {})
    print('Current projekt:', fields.get('projekt', 'NOT FOUND'))
    print('Current rechnungsbetrag:', fields.get('rechnungsbetrag', 'NOT FOUND'))
except Exception as e:
    print('Error parsing:', e)
")

echo "   $VERIFY_RESULT"
echo ""

echo "✅ Frontend API fix verification complete!"
echo "The 'Bad Request' error should now be resolved."
