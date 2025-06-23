#!/bin/bash

# OCR Invoice Processor - Development Startup Script
echo "🚀 Starting OCR Invoice Processor Development Environment..."

# Start backend in background
echo "📦 Starting Backend (FastAPI) on port 8001..."
cd backend && python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background  
echo "🎨 Starting Frontend (Next.js) on port 3000..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services Started Successfully!"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Backend:  http://localhost:8001"
echo "🔗 API Health: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for processes
wait
