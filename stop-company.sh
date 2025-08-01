#!/bin/bash

# OCR Invoice Processor - Stop Script

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "🛑 Stopping OCR Invoice Processor..."
echo ""

# Stop containers
if command -v docker-compose &> /dev/null; then
    docker-compose down
else
    docker compose down
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Application stopped successfully!${NC}"
    echo ""
    echo -e "${YELLOW}💡 To start again: ./start-company.sh${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Error stopping application${NC}"
    echo -e "${YELLOW}💡 Try: docker-compose down --remove-orphans${NC}"
    echo ""
fi