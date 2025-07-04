#!/bin/bash

# Render startup script for backend
echo "🚀 Starting OCR Invoice Backend on Render..."

# Set default port if not provided
PORT=${PORT:-8000}

echo "📍 Port: $PORT"
echo "🌍 Environment: $NODE_ENV"
echo "🔗 Supabase URL: $SUPABASE_URL"

# Run database migrations if needed
echo "🔄 Running any pending migrations..."
python run_migration.py 2>/dev/null || echo "⚠️  No migrations to run"

# Start the application
echo "✅ Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --access-log
