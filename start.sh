#!/bin/bash

# OCR Invoice Processor - Development Server Script
# Runs both backend (FastAPI) and frontend (Next.js) in parallel

echo "🚀 Starting OCR Invoice Processor Development Servers..."
echo "=================================================="

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend server
echo "📦 Starting Backend (FastAPI)..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started successfully!"
echo "=================================================="
echo "🔧 Backend API:  http://localhost:8000"
echo "🌐 Frontend App: http://localhost:3000"
echo "📋 API Docs:     http://localhost:8000/docs"
echo "=================================================="
echo ""
echo "💡 Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
