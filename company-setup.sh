#!/bin/bash

# OCR Invoice Processor - Company Deployment Script
# Quick setup script for company environments

set -e

echo "🏢 OCR Invoice Processor - Company Setup"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "\n${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to create directories
create_directories() {
    print_step "Creating necessary directories..."
    mkdir -p logs
    mkdir -p backend/uploads
    mkdir -p backend/keys
    mkdir -p nginx/ssl
}

# Function to setup environment
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.production" ]; then
            cp .env.production .env
            print_info "Created .env from production template"
        elif [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Created .env from example template"
        else
            print_error "No environment template found!"
            exit 1
        fi
        
        echo ""
        print_info "⚠️  IMPORTANT: Edit .env file with your actual credentials:"
        print_info "   - Supabase database URL and keys"
        print_info "   - SendGrid API key for emails"
        print_info "   - JWT secret for security"
        print_info "   - Google Cloud credentials (if using OCR)"
        echo ""
        read -p "Press Enter after editing .env file..."
    else
        print_info ".env file already exists"
    fi
}

# Function to create nginx config
create_nginx_config() {
    print_step "Creating Nginx configuration..."
    
    mkdir -p nginx
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    
    upstream backend {
        server backend:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend docs
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    
    print_info "Nginx configuration created"
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Install from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running! Please start Docker Desktop."
        exit 1
    fi
    
    print_info "✅ All prerequisites met"
}

# Function to create startup scripts
create_startup_scripts() {
    print_step "Creating startup scripts..."
    
    # Quick start script
    cat > quick-start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting OCR Invoice Processor..."
docker-compose up -d
echo "✅ Started! Visit http://localhost:3000"
echo "💡 Stop with: docker-compose down"
EOF
    
    # Quick stop script
    cat > quick-stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping OCR Invoice Processor..."
docker-compose down
echo "✅ Stopped!"
EOF
    
    chmod +x quick-start.sh quick-stop.sh
    print_info "Created quick-start.sh and quick-stop.sh"
}

# Main setup function
main() {
    echo ""
    check_prerequisites
    create_directories
    setup_environment
    create_nginx_config
    create_startup_scripts
    
    echo ""
    echo "================================================"
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Make sure .env file has correct values"
    echo "2. Run: ./docker-start.sh (full setup)"
    echo "   OR: ./quick-start.sh (quick start)"
    echo ""
    echo "Application will be available at:"
    echo "  🌐 Frontend: http://localhost:3000"
    echo "  🔧 Backend:  http://localhost:8000"
    echo "  📋 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Stop with: ./quick-stop.sh or docker-compose down"
    echo ""
}

# Run main function
main
