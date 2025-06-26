#!/bin/bash

echo "🔄 Testing Folder Watcher Frontend Integration"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}Testing Backend API Endpoints:${NC}"
echo "-------------------------------"

# Test folder watcher status
echo -n "• Status endpoint: "
status_response=$(curl -s "http://localhost:8000/api/folder-watcher/status")
if echo "$status_response" | grep -q '"status"'; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test folders endpoint
echo -n "• Folders endpoint: "
folders_response=$(curl -s "http://localhost:8000/api/folder-watcher/folders")
if echo "$folders_response" | grep -q '\['; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test statistics endpoint
echo -n "• Statistics endpoint: "
stats_response=$(curl -s "http://localhost:8000/api/folder-watcher/statistics")
if echo "$stats_response" | grep -q '"statistics"'; then
    echo -e "${GREEN}✓ Working${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

echo ""
echo -e "${BLUE}Testing Frontend Accessibility:${NC}"
echo "--------------------------------"

# Test frontend pages
echo -n "• Dashboard page: "
dashboard_status=$(curl -s -w "%{http_code}" "http://localhost:3000/dashboard" | tail -c 3)
if [ "$dashboard_status" = "200" ]; then
    echo -e "${GREEN}✓ Accessible${NC}"
else
    echo -e "${RED}✗ Not accessible (HTTP $dashboard_status)${NC}"
fi

echo -n "• Folder watcher page: "
fw_status=$(curl -s -w "%{http_code}" "http://localhost:3000/dashboard/folder-watcher" | tail -c 3)
if [ "$fw_status" = "200" ]; then
    echo -e "${GREEN}✓ Accessible${NC}"
else
    echo -e "${RED}✗ Not accessible (HTTP $fw_status)${NC}"
fi

echo ""
echo -e "${BLUE}Current System Status:${NC}"
echo "----------------------"

# Show folder watcher status
echo "Backend Status:"
echo "$status_response" | jq '.' 2>/dev/null || echo "$status_response"

echo ""
echo "Watched Folders:"
echo "$folders_response" | jq '.' 2>/dev/null || echo "$folders_response"

echo ""
echo -e "${GREEN}✅ Integration Test Complete!${NC}"
echo ""
echo "Frontend URLs:"
echo "• Main Dashboard: http://localhost:3000/dashboard"
echo "• Folder Watcher: http://localhost:3000/dashboard/folder-watcher"
echo "• Upload Page: http://localhost:3000/upload"
echo ""
echo "Backend API:"
echo "• Folder Watcher API: http://localhost:8000/api/folder-watcher/status"
echo "• Invoices API: http://localhost:8000/api/invoices"
