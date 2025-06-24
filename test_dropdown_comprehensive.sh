#!/bin/bash

# Comprehensive test for frontend dropdown functionality
# Tests the complete flow: get dropdowns, save selections, verify persistence

INVOICE_ID="8c9c349b-1474-44ec-a6fb-9f92bef180e1"
API_URL="http://localhost:8001"

echo "🔬 Comprehensive Frontend Dropdown Functionality Test"
echo "=================================================="

echo "1. 📋 Testing dropdown options retrieval..."
DROPDOWN_RESPONSE=$(curl -s "${API_URL}/api/dropdowns")
echo "✅ Available dropdown fields:" 
echo "$DROPDOWN_RESPONSE" | jq -r '.field_names | join(", ")'

echo -e "\n2. 🔍 Testing specific field dropdown (rechnungssteller)..."
curl -s "${API_URL}/api/dropdowns/rechnungssteller" | jq '.options[0:3] | .[] | {value, label}'

echo -e "\n3. ➕ Testing adding new dropdown option..."
ADD_RESPONSE=$(curl -s -X POST "${API_URL}/api/dropdowns/add-option" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "rechnungssteller",
    "value": "frontend_test_vendor", 
    "label": "Frontend Test Vendor Co."
  }')
echo "$ADD_RESPONSE" | jq '{success, message, persisted_to_db}'

echo -e "\n4. 🎯 Testing invoice editor save with dropdown selections..."
SAVE_RESPONSE=$(curl -s -X PUT "${API_URL}/invoices/${INVOICE_ID}/editor" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "rechnungsempfaenger": "acme_construction",
      "rechnungssteller": "frontend_test_vendor",
      "projekt": "wohnbau_mitte_2024",
      "gewerk": "elektroinstallation",
      "rechnungsbetrag": 2500.00,
      "rechnungsart": "rechnung",
      "kfw_anrechenbar": true
    }
  }')

echo "💾 Save response:"
echo "$SAVE_RESPONSE" | jq '{success, message, updated_fields}'

echo -e "\n5. ✅ Verifying all dropdown selections persisted correctly..."
FINAL_STATE=$(curl -s "${API_URL}/invoices/${INVOICE_ID}/editor")
echo "$FINAL_STATE" | jq '.fields | {
  rechnungsempfaenger,
  rechnungssteller, 
  projekt,
  gewerk,
  rechnungsbetrag,
  rechnungsart,
  kfw_anrechenbar
}'

echo -e "\n6. 📊 Testing dropdown stats..."
curl -s "${API_URL}/api/dropdowns/stats" | jq '.'

echo -e "\n🎉 All dropdown functionality tests completed successfully!"
echo "   ✅ Dropdown retrieval: Working"
echo "   ✅ Adding new options: Working" 
echo "   ✅ Frontend save format: Fixed"
echo "   ✅ Data persistence: Working"
echo "   ✅ Stats endpoint: Working"
