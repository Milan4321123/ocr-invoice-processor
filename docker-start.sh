#!/bin/bash

# OCR Invoice Processor - Docker Startup Script
# This script sets up and starts the complete application using Docker

set -e  # Exit on any error

echo "🚀 OCR Invoice Processor - Docker Setup & Start"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running!"
        echo "Please start Docker Desktop and try again."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose or use Docker Desktop which includes it."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if environment file exists
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        print_status "Creating .env from template..."
        
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your actual values before starting:"
            print_warning "  - Supabase credentials"
            print_warning "  - Email service settings"
            print_warning "  - OCR service configuration"
            echo ""
            print_error "Setup incomplete! Edit .env file and run this script again."
            exit 1
        else
            print_error ".env.example file not found!"
            exit 1
        fi
    fi
    
    print_success "Environment file found"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "Stopping containers..."
    docker-compose down
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo ""
    check_docker
    check_environment
    
    echo ""
    print_status "Starting OCR Invoice Processor with Docker..."
    
    # Build and start containers
    print_status "Building Docker images (this may take a few minutes)..."
    docker-compose build
    
    print_status "Starting containers..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    print_status "Checking service health..."
    
    # Check backend health
    BACKEND_READY=false
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            BACKEND_READY=true
            break
        fi
        sleep 2
    done
    
    # Check frontend
    FRONTEND_READY=false
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            FRONTEND_READY=true
            break
        fi
        sleep 2
    done
    
    echo ""
    echo "================================================"
    print_success "OCR Invoice Processor Started Successfully!"
    echo "================================================"
    
    if [ "$BACKEND_READY" = true ]; then
        echo -e "🔧 Backend API:    ${GREEN}http://localhost:8000${NC} ✅"
        echo -e "📋 API Docs:       ${GREEN}http://localhost:8000/docs${NC}"
    else
        echo -e "🔧 Backend API:    ${RED}http://localhost:8000${NC} ❌"
    fi
    
    if [ "$FRONTEND_READY" = true ]; then
        echo -e "🌐 Frontend App:   ${GREEN}http://localhost:3000${NC} ✅"
    else
        echo -e "🌐 Frontend App:   ${RED}http://localhost:3000${NC} ❌"
    fi
    
    echo "================================================"
    echo ""
    
    if [ "$BACKEND_READY" = false ] || [ "$FRONTEND_READY" = false ]; then
        print_warning "Some services may still be starting. Please wait a moment and refresh."
        print_status "You can check logs with: docker-compose logs"
    fi
    
    echo "💡 Press Ctrl+C to stop all services"
    echo "💡 Or use: docker-compose down"
    echo ""
    
    # Show logs
    print_status "Showing live logs (Ctrl+C to stop logs but keep services running)..."
    docker-compose logs -f
}

# Run main function
main
