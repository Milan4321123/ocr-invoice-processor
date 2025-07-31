#!/bin/bash

# Quick Start Script for OCR Invoice Processor
echo "🚀 Starting OCR Invoice Processor..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Run ./company-setup.sh first or copy .env.example to .env"
    exit 1
fi

# Start with simple Docker Compose (no nginx)
docker-compose -f docker-compose.simple.yml up -d

echo ""
echo "✅ OCR Invoice Processor Started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Stop with: ./quick-stop.sh"
echo "💡 View logs: docker-compose -f docker-compose.simple.yml logs -f"
