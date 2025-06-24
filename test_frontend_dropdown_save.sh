#!/bin/bash

# Test script to verify frontend dropdown save functionality
# This simulates the frontend request after the fix

INVOICE_ID="8c9c349b-1474-44ec-a6fb-9f92bef180e1"
API_URL="http://localhost:8001"

echo "🧪 Testing Frontend Dropdown Save Fix"
echo "=================================="

# First, get current invoice state
echo "📋 Current invoice state:"
curl -s "${API_URL}/invoices/${INVOICE_ID}/editor" | jq '.fields | {rechnungsempfaenger, rechnungssteller, projekt, gewerk}'

echo -e "\n🔄 Simulating frontend save with dropdown selections..."

# Test the corrected payload format (what frontend now sends after fix)
RESPONSE=$(curl -s -X PUT "${API_URL}/invoices/${INVOICE_ID}/editor" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "rechnungsempfaenger": "Test Dropdown Customer",
      "rechnungssteller": "Test Dropdown Vendor",
      "projekt": "Test Dropdown Project", 
      "gewerk": "elektroinstallation",
      "rechnungsbetrag": 1234.56,
      "rechnungsart": "rechnung"
    },
    "review_status": "under_review",
    "reviewed_by": "test@example.com"
  }')

echo "📤 Response:"
echo "$RESPONSE" | jq '.'

echo -e "\n✅ Verifying updates persisted:"
curl -s "${API_URL}/invoices/${INVOICE_ID}/editor" | jq '.fields | {rechnungsempfaenger, rechnungssteller, projekt, gewerk, rechnungsbetrag, rechnungsart}'

echo -e "\n🎉 Frontend dropdown save test completed!"
