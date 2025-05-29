#!/bin/bash
# Test Real OCR Functionality
echo "🚀 Testing Real OCR Functionality"
echo "=================================="

echo ""
echo "1️⃣ Testing OCR Status Endpoint..."
curl -s -X GET "http://localhost:8000/ocr/status" | python3 -m json.tool

echo ""
echo "2️⃣ Testing System Health..."
curl -s -X GET "http://localhost:8000/health" | python3 -m json.tool

echo ""
echo "3️⃣ Testing Invoice Upload with OCR..."
UPLOAD_RESULT=$(curl -s -X POST "http://localhost:8000/invoices/upload" \
  -F "file=@test_invoice.pdf" \
  -F "vendor_name=Test Vendor OCR" \
  -F "invoice_number=OCR-TEST-001" \
  -F "amount=250.00")

echo "Upload Result:"
echo "$UPLOAD_RESULT" | python3 -m json.tool

# Extract invoice ID
INVOICE_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('invoice_id', ''))" 2>/dev/null)

if [ ! -z "$INVOICE_ID" ]; then
    echo ""
    echo "4️⃣ Getting OCR Data for Invoice ID: $INVOICE_ID"
    curl -s -X GET "http://localhost:8000/invoices/$INVOICE_ID/ocr" | python3 -m json.tool
else
    echo "❌ Could not extract invoice ID from upload result"
fi

echo ""
echo "✅ OCR Test Complete!"
