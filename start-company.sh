#!/bin/bash

# OCR Invoice Processor - Company Edition
# Startup script for Mac/Linux

# Colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo "========================================"
echo -e "${BOLD}   OCR INVOICE PROCESSOR - COMPANY${NC}"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo ""
    echo -e "${BLUE}📥 Please install Docker Desktop from:${NC}"
    echo "   https://www.docker.com/products/docker-desktop"
    echo ""
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available!${NC}"
    echo ""
    echo -e "${BLUE}📥 Please install Docker Compose or update Docker Desktop${NC}"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo ""
    echo -e "${YELLOW}🚀 Please start Docker Desktop and try again${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Setting up environment file...${NC}"
    cp environment.template .env
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file with your company settings:${NC}"
    echo "   - Database URLs (Supabase)"
    echo "   - Email configuration (SendGrid)"
    echo "   - Company information"
    echo "   - Admin credentials"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

echo -e "${BLUE}🚀 Starting OCR Invoice Processor...${NC}"
echo "   This may take a few minutes on first start (downloading images)"
echo ""

# Build and start containers
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo -e "${GREEN}✅ SUCCESS! APPLICATION IS RUNNING${NC}"
    echo "========================================"
    echo ""
    echo -e "${BLUE}🌐 Access your application:${NC}"
    echo ""
    echo "   📊 Main Application: http://localhost:3000"
    echo "   🔧 API Backend:     http://localhost:8000"
    echo "   📖 API Documentation: http://localhost:8000/docs"
    echo ""
    echo -e "${BLUE}💡 What to do next:${NC}"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Login with admin credentials from .env file"
    echo "   3. Start processing invoices!"
    echo ""
    echo -e "${BLUE}🛑 To stop: ./stop-company.sh${NC}"
    echo -e "${BLUE}📊 To view logs: docker-compose logs -f${NC}"
    echo ""
    
    # Open browser on Mac
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Opening application in browser..."
        sleep 3
        open http://localhost:3000
    fi
else
    echo ""
    echo -e "${RED}❌ FAILED TO START APPLICATION${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Troubleshooting:${NC}"
    echo "   1. Check Docker is running properly"
    echo "   2. Check ports 3000 and 8000 are available"
    echo "   3. Check .env file is configured correctly"
    echo "   4. Run: docker-compose logs"
    echo ""
fi