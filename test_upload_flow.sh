#!/bin/bash

# Simple Upload to Dashboard Flow Test
# Tests the basic workflow: Upload → Dashboard → View

echo "🧪 Testing Upload → Dashboard → View Flow"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API URL
API_URL="http://localhost:8000"

echo -e "${YELLOW}1. Checking if backend is running...${NC}"
if curl -s "$API_URL" > /dev/null; then
    echo -e "${GREEN}✅ Backend is running on $API_URL${NC}"
else
    echo -e "${RED}❌ Backend is not running. Please start it with: cd backend && python main.py${NC}"
    exit 1
fi

echo -e "${YELLOW}2. Testing API health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$API_URL/api/health" | grep -o '"status":"healthy"' || echo "")
if [ -n "$HEALTH_RESPONSE" ]; then
    echo -e "${GREEN}✅ Health endpoint working${NC}"
else
    echo -e "${RED}❌ Health endpoint not responding correctly${NC}"
fi

echo -e "${YELLOW}3. Testing invoices list endpoint...${NC}"
INVOICES_RESPONSE=$(curl -s "$API_URL/api/invoices")
if echo "$INVOICES_RESPONSE" | grep -q "invoices"; then
    echo -e "${GREEN}✅ Invoices endpoint working${NC}"
    echo "📊 Response preview: $(echo "$INVOICES_RESPONSE" | head -c 100)..."
else
    echo -e "${RED}❌ Invoices endpoint not working${NC}"
    echo "Response: $INVOICES_RESPONSE"
fi

echo -e "${YELLOW}4. Testing mock invoice editor endpoint...${NC}"
EDITOR_RESPONSE=$(curl -s "$API_URL/api/invoices/test-123/editor")
if echo "$EDITOR_RESPONSE" | grep -q "pdfUrl"; then
    echo -e "${GREEN}✅ Invoice editor endpoint working${NC}"
    echo "📊 Response preview: $(echo "$EDITOR_RESPONSE" | head -c 100)..."
else
    echo -e "${RED}❌ Invoice editor endpoint not working${NC}"
    echo "Response: $EDITOR_RESPONSE"
fi

echo ""
echo -e "${YELLOW}🎯 Next Steps for Manual Testing:${NC}"
echo "1. Start frontend: cd frontend && npm run dev"
echo "2. Open http://localhost:3000/upload"
echo "3. Upload a test PDF with pattern: YYYYMMDD_TEST_VENDOR_INVOICE.pdf"
echo "4. Go to http://localhost:3000/dashboard"
echo "5. Click 'Edit' on your uploaded invoice"
echo "6. Verify PDF loads and form appears"

echo ""
echo -e "${GREEN}🔗 Test URLs:${NC}"
echo "• Backend API: $API_URL"
echo "• Frontend: http://localhost:3000"
echo "• Upload: http://localhost:3000/upload"
echo "• Dashboard: http://localhost:3000/dashboard"
echo ""
