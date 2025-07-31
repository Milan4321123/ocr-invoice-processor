#!/bin/bash

# OCR Invoice Processor - Status Script
# Check the status of backend and frontend services

echo "📊 OCR Invoice Processor Status"
echo "==============================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    local url=$3
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service is running on port $port${NC}"
        echo -e "   URL: $url"
        
        # Try to get PID
        local pid=$(lsof -ti:$port 2>/dev/null | head -1)
        if [ ! -z "$pid" ]; then
            echo -e "   PID: $pid"
        fi
    else
        echo -e "${RED}❌ $service is not running on port $port${NC}"
        echo -e "   URL: $url (not accessible)"
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name endpoint responding${NC}"
    else
        echo -e "${RED}❌ $name endpoint not responding${NC}"
    fi
}

echo -e "${BLUE}🔍 Checking services...${NC}"
echo ""

# Check Backend
echo -e "${BLUE}Backend Service:${NC}"
check_port 8000 "Backend" "http://localhost:8000"
test_endpoint "http://localhost:8000/api/health" "Backend Health"
echo ""

# Check Frontend
echo -e "${BLUE}Frontend Service:${NC}"
check_port 3000 "Frontend" "http://localhost:3000"
test_endpoint "http://localhost:3000" "Frontend"
echo ""

# Check PID files
echo -e "${BLUE}🔍 PID Files:${NC}"
if [ -f ".backend.pid" ]; then
    backend_pid=$(cat .backend.pid)
    if ps -p $backend_pid > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend PID file exists and process is running ($backend_pid)${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend PID file exists but process is not running ($backend_pid)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No backend PID file found${NC}"
fi

if [ -f ".frontend.pid" ]; then
    frontend_pid=$(cat .frontend.pid)
    if ps -p $frontend_pid > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend PID file exists and process is running ($frontend_pid)${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend PID file exists but process is not running ($frontend_pid)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No frontend PID file found${NC}"
fi

echo ""

# Check log files
echo -e "${BLUE}📝 Log Files:${NC}"
if [ -f "backend.log" ]; then
    backend_log_size=$(wc -l < backend.log)
    echo -e "${BLUE}📄 backend.log exists ($backend_log_size lines)${NC}"
    echo -e "   Last 3 lines:"
    tail -3 backend.log | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠️  No backend.log found${NC}"
fi

if [ -f "frontend.log" ]; then
    frontend_log_size=$(wc -l < frontend.log)
    echo -e "${BLUE}📄 frontend.log exists ($frontend_log_size lines)${NC}"
    echo -e "   Last 3 lines:"
    tail -3 frontend.log | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠️  No frontend.log found${NC}"
fi

echo ""

# Summary
echo "==============================="
backend_running=$(lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 && echo "true" || echo "false")
frontend_running=$(lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 && echo "true" || echo "false")

if [ "$backend_running" = "true" ] && [ "$frontend_running" = "true" ]; then
    echo -e "${GREEN}🎉 All services are running!${NC}"
    echo -e "${BLUE}🌐 Open http://localhost:3000 to use the application${NC}"
elif [ "$backend_running" = "true" ] && [ "$frontend_running" = "false" ]; then
    echo -e "${YELLOW}⚠️  Backend is running but frontend is down${NC}"
    echo -e "${BLUE}🚀 Run ./start.sh to start both services${NC}"
elif [ "$backend_running" = "false" ] && [ "$frontend_running" = "true" ]; then
    echo -e "${YELLOW}⚠️  Frontend is running but backend is down${NC}"
    echo -e "${BLUE}🚀 Run ./start.sh to start both services${NC}"
else
    echo -e "${RED}❌ Both services are down${NC}"
    echo -e "${BLUE}🚀 Run ./start.sh to start the application${NC}"
fi

echo "==============================="