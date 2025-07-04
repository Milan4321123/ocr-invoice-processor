#!/bin/bash

# Render startup script for OCR Invoice Processor Backend
echo "🚀 Starting OCR Invoice Processor Backend on Render..."

# Set default port if not provided by Render
export PORT=${PORT:-8000}

echo "📡 Starting server on port $PORT..."

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
