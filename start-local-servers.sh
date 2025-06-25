#!/bin/bash
"""
Complete startup script for OCR Invoice Processor
Starts both backend and frontend with proper monitoring
"""

set -e  # Exit on any error

# Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
PROJECT_ROOT="/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING: $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR: $1${NC}"
}

print_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] INFO: $1${NC}"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        print_warning "Killing existing process on port $port (PID: $pid)"
        kill -9 $pid
        sleep 2
    fi
}

# Function to start backend
start_backend() {
    print_info "Starting Backend Server on port $BACKEND_PORT..."
    
    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    # Check if port is available
    if ! check_port $BACKEND_PORT; then
        print_warning "Port $BACKEND_PORT is in use"
        kill_port $BACKEND_PORT
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    print_info "Installing Python dependencies..."
    pip install -q -r requirements.txt
    
    # Start FastAPI server
    print_status "🚀 Starting FastAPI server..."
    uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    BACKEND_PID=$!
    
    # Wait for backend to start
    print_info "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
            print_status "✅ Backend started successfully on http://localhost:$BACKEND_PORT"
            return 0
        fi
        sleep 1
    done
    
    print_error "Backend failed to start within 30 seconds"
    return 1
}

# Function to start frontend
start_frontend() {
    print_info "Starting Frontend Server on port $FRONTEND_PORT..."
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_warning "Frontend directory not found: $FRONTEND_DIR"
        print_info "Skipping frontend startup..."
        return 0
    fi
    
    # Check if port is available
    if ! check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is in use"
        kill_port $FRONTEND_PORT
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing Node.js dependencies..."
        npm install
    fi
    
    # Start React/Next.js server
    print_status "🚀 Starting Frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    print_info "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
            print_status "✅ Frontend started successfully on http://localhost:$FRONTEND_PORT"
            return 0
        fi
        sleep 1
    done
    
    print_warning "Frontend may take longer to start or directory not found"
    return 0
}

# Function to show status
show_status() {
    echo ""
    echo "=================================="
    echo "🟢 OCR Invoice Processor Status"
    echo "=================================="
    
    # Backend status
    if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
        print_status "✅ Backend: http://localhost:$BACKEND_PORT (RUNNING)"
        print_info "   📋 API Docs: http://localhost:$BACKEND_PORT/docs"
        print_info "   🔍 Health: http://localhost:$BACKEND_PORT/health"
        print_info "   📧 Email Test: http://localhost:$BACKEND_PORT/api/email/test"
    else
        print_error "❌ Backend: Not responding on port $BACKEND_PORT"
    fi
    
    # Frontend status
    if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
        print_status "✅ Frontend: http://localhost:$FRONTEND_PORT (RUNNING)"
    else
        print_warning "⚠️  Frontend: Not running or not available"
    fi
    
    echo ""
    echo "=================================="
    echo "🧪 Testing Commands Available:"
    echo "=================================="
    echo "cd $PROJECT_ROOT && python test_email_complete.py"
    echo "cd $PROJECT_ROOT && python test_bauleiter_approval.py"
    echo "cd $PROJECT_ROOT && python test_confirmation_email_fix.py"
    echo "cd $PROJECT_ROOT && python test_complete_approval_workflow.py"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "🛑 Shutting down servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on our ports
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    print_status "✅ Cleanup complete"
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM EXIT

# Main execution
main() {
    echo "🏁 Starting OCR Invoice Processor..."
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    
    # Start backend
    if start_backend; then
        print_status "Backend startup successful"
    else
        print_error "Backend startup failed"
        exit 1
    fi
    
    # Start frontend (optional)
    start_frontend
    
    # Show status
    show_status
    
    # Keep running
    print_info "🎯 Services are running. Press Ctrl+C to stop all services."
    print_info "📧 To test approval workflow:"
    print_info "   1. Run: python test_bauleiter_approval.py"
    print_info "   2. Check email: incognizant321@gmail.com"
    print_info "   3. Click GENEHMIGEN in the email"
    print_info "   4. You should receive a confirmation email"
    
    # Wait for user interrupt
    wait
}

# Run main function
main "$@"
