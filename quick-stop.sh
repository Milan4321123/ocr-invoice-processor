#!/bin/bash

# Quick Stop Script for OCR Invoice Processor
echo "🛑 Stopping OCR Invoice Processor..."

docker-compose down

echo "✅ OCR Invoice Processor Stopped!"
echo ""
echo "💡 Start again with: ./quick-start.sh"
