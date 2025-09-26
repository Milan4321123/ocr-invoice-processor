#!/bin/bash

# 🔍 CORS Testing Script for Render Deployment
# Tests if frontend can communicate with backend after CORS fix

echo "🔍 Testing CORS Configuration on Render..."
echo "=========================================="

BACKEND_URL="https://ocr-invoice-backend.onrender.com"
FRONTEND_URL="https://ocr-invoice-frontend.onrender.com"

echo ""
echo "🔗 Testing Cross-Origin Request..."
echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
echo ""

# Test 1: Simple preflight request
echo "📋 Test 1: CORS Preflight Request"
curl -s -I -X OPTIONS \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  "$BACKEND_URL/api/invoices" | grep -E "(Access-Control|HTTP)"

echo ""

# Test 2: Actual API request with Origin header
echo "📋 Test 2: GET Invoices with Origin Header"
curl -s -H "Origin: $FRONTEND_URL" "$BACKEND_URL/api/invoices" | head -100

echo ""

# Test 3: Check what origins are allowed
echo "📋 Test 3: Check CORS Headers"
curl -s -I -H "Origin: $FRONTEND_URL" "$BACKEND_URL/api/health" | grep -i "access-control"

echo ""
echo "✅ If you see 'Access-Control-Allow-Origin' headers, CORS is working!"
echo "❌ If no CORS headers, add FRONTEND_URL environment variable to backend service"