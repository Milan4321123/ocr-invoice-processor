#!/bin/bash

# OCR Invoice Processor - Stop Development Servers Script

echo "🛑 Stopping OCR Invoice Processor Development Servers..."
echo "=================================================="

# Kill Python backend processes
echo "📦 Stopping Backend (FastAPI)..."
pkill -f "python.*main.py" && echo "✅ Backend stopped" || echo "ℹ️  Backend was not running"

# Kill Node.js frontend processes (Next.js dev server)
echo "🎨 Stopping Frontend (Next.js)..."
pkill -f "node.*next.*dev" && echo "✅ Frontend stopped" || echo "ℹ️  Frontend was not running"

# Alternative: Kill all node processes on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✅ Port 3000 cleared" || echo "ℹ️  Port 3000 was free"

# Alternative: Kill all python processes on port 8000  
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Port 8000 cleared" || echo "ℹ️  Port 8000 was free"

echo "=================================================="
echo "✅ All development servers stopped!"
