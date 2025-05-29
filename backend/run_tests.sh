#!/bin/bash
# filepath: /Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend/run_tests.sh

# Script to run backend tests

echo "🧪 Running Backend Tests for Invoice OCR Processor"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run unit tests (excluding integration tests)
echo ""
echo "🔍 Running Unit Tests..."
echo "========================"
python -m pytest tests/test_main.py -v

# Check if Supabase environment variables are set
if [ -n "$SUPA_URL" ] && [ -n "$SUPA_KEY" ]; then
    echo ""
    echo "🌐 Running Integration Tests..."
    echo "================================"
    python -m pytest tests/test_integration.py -v
else
    echo ""
    echo "⚠️  Skipping Integration Tests"
    echo "==============================="
    echo "To run integration tests, set environment variables:"
    echo "export SUPA_URL='your_supabase_url'"
    echo "export SUPA_KEY='your_supabase_anon_key'"
fi

# Run all tests with coverage (optional)
echo ""
echo "📊 Running All Tests with Coverage..."
echo "===================================="
pip install pytest-cov
python -m pytest tests/ --cov=main --cov-report=term-missing -v

echo ""
echo "✅ Test execution completed!"
