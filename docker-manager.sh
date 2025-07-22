#!/bin/bash
# OCR Invoice Processor - Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project name
PROJECT_NAME="ocr-invoice-processor"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  OCR Invoice Processor Docker${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
}

# Function to show status
show_status() {
    print_header
    print_status "Checking Docker status..."
    check_docker
    print_status "Docker is running ✓"
    
    echo
    print_status "Container Status:"
    docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "No containers running"
    
    echo
    print_status "Service Health Checks:"
    
    # Check backend
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "✅ Backend (http://localhost:8000) - Healthy"
    else
        echo "❌ Backend (http://localhost:8000) - Not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend (http://localhost:3000) - Healthy"
    else
        echo "❌ Frontend (http://localhost:3000) - Not responding"
    fi
}

# Function to start services
start_services() {
    print_header
    print_status "Starting OCR Invoice Processor..."
    check_docker
    
    if [ ! -f ".env" ]; then
        print_warning "No .env file found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env file. Please edit it with your configuration."
        else
            print_error "No .env.example file found. Please create .env manually."
            exit 1
        fi
    fi
    
    print_status "Building and starting containers..."
    docker-compose -f docker-compose.dev.yml up -d --build
    
    print_status "Waiting for services to start..."
    sleep 10
    
    show_status
    
    echo
    print_status "🎉 OCR Invoice Processor is now running!"
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
}

# Function to stop services
stop_services() {
    print_header
    print_status "Stopping OCR Invoice Processor..."
    docker-compose -f docker-compose.dev.yml down
    print_status "Services stopped."
}

# Function to restart services
restart_services() {
    print_header
    print_status "Restarting OCR Invoice Processor..."
    docker-compose -f docker-compose.dev.yml restart
    print_status "Services restarted."
    show_status
}

# Function to show logs
show_logs() {
    print_header
    print_status "Showing application logs..."
    docker-compose -f docker-compose.dev.yml logs -f
}

# Function to clean up
cleanup() {
    print_header
    print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up Docker resources..."
        docker-compose -f docker-compose.dev.yml down -v
        docker system prune -f
        print_status "Cleanup complete."
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to rebuild
rebuild() {
    print_header
    print_status "Rebuilding containers..."
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.dev.yml build --no-cache
    docker-compose -f docker-compose.dev.yml up -d
    print_status "Rebuild complete."
    show_status
}

# Function to open in browser
open_browser() {
    print_status "Opening application in browser..."
    if command -v open >/dev/null 2>&1; then
        open http://localhost:3000
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open http://localhost:3000
    else
        print_status "Please open http://localhost:3000 in your browser"
    fi
}

# Function to show help
show_help() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Start the application containers"
    echo "  stop      Stop the application containers"
    echo "  restart   Restart the application containers"
    echo "  status    Show current status"
    echo "  logs      Show application logs (follow mode)"
    echo "  rebuild   Rebuild containers from scratch"
    echo "  cleanup   Remove all containers and volumes"
    echo "  open      Open application in browser"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start    # Start the application"
    echo "  $0 status   # Check if everything is running"
    echo "  $0 logs     # View real-time logs"
}

# Main script logic
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    rebuild)
        rebuild
        ;;
    cleanup)
        cleanup
        ;;
    open)
        open_browser
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac
