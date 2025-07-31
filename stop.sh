#!/bin/bash

# OCR Invoice Processor - Stop Script
# Simple script to stop both backend and frontend services

echo "🛑 Stopping OCR Invoice Processor..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to stop process by PID file
stop_by_pid() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${BLUE}🛑 Stopping $service_name (PID: $pid)...${NC}"
            kill $pid
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  Force stopping $service_name...${NC}"
                kill -9 $pid
            fi
            
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name process not found (PID: $pid)${NC}"
        fi
        
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No $service_name PID file found${NC}"
    fi
}

# Function to stop processes by port
stop_by_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${BLUE}🛑 Stopping $service_name processes on port $port...${NC}"
        echo $pids | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✅ Stopped processes on port $port${NC}"
    fi
}

# Stop using PID files first
stop_by_pid ".backend.pid" "Backend"
stop_by_pid ".frontend.pid" "Frontend"

# Fallback: stop by port
echo -e "${BLUE}🔍 Checking for remaining processes...${NC}"
stop_by_port 8000 "Backend"
stop_by_port 3000 "Frontend"

# Stop any remaining Python processes that might be the backend
echo -e "${BLUE}🔍 Stopping any remaining backend processes...${NC}"
pkill -f "python.*main.py" 2>/dev/null && echo -e "${GREEN}✅ Stopped Python backend processes${NC}"

# Stop any remaining npm/node processes for the frontend
echo -e "${BLUE}🔍 Stopping any remaining frontend processes...${NC}"
pkill -f "npm.*dev" 2>/dev/null && echo -e "${GREEN}✅ Stopped npm dev processes${NC}"
pkill -f "next.*dev" 2>/dev/null && echo -e "${GREEN}✅ Stopped Next.js dev processes${NC}"

# Clean up log files (optional)
echo -e "${BLUE}🧹 Cleaning up...${NC}"
if [ -f "backend.log" ]; then
    echo -e "${BLUE}📝 Backend log saved as backend.log${NC}"
fi
if [ -f "frontend.log" ]; then
    echo -e "${BLUE}📝 Frontend log saved as frontend.log${NC}"
fi

# Remove any temporary files
rm -f .backend.pid .frontend.pid 2>/dev/null

echo ""
echo "=================================="
echo -e "${GREEN}🎉 OCR Invoice Processor Stopped Successfully!${NC}"
echo ""
echo -e "${BLUE}📝 Logs preserved:${NC}"
echo -e "   Backend:  backend.log"
echo -e "   Frontend: frontend.log"
echo ""
echo -e "${BLUE}🚀 To start again:${NC}"
echo -e "   Run: ./start.sh"
echo "=================================="