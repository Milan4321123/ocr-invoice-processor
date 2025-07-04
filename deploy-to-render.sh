#!/bin/bash

# Render Deployment Script for OCR Invoice Processor
# This script helps deploy to Render without breaking localhost setup

set -e

echo "🚀 Starting Render Deployment Process..."

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

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    print_error "render.yaml not found. Please run this script from the project root."
    exit 1
fi

print_status "Checking prerequisites..."

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "Git is required but not installed."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This directory is not a git repository."
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_status "Current branch: $CURRENT_BRANCH"

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes. Consider committing them first."
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

print_status "Creating deployment branch 'deployy'..."

# Create or switch to deployment branch
if git show-ref --verify --quiet refs/heads/deployy; then
    print_status "Deployment branch 'deployy' already exists. Switching to it..."
    git checkout deployy
    git merge $CURRENT_BRANCH --no-edit
else
    print_status "Creating new deployment branch 'deployy'..."
    git checkout -b deployy
fi

print_status "Pushing deployment branch to origin..."
git push origin deployy --force

print_success "✅ Code pushed to deployment branch!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 NEXT STEPS - RENDER DASHBOARD SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Go to https://render.com and sign in"
echo "2. Click 'New +' and select 'Blueprint'"
echo "3. Connect your GitHub repository: https://github.com/Milan4321123/ocr-invoice-processor"
echo "4. Select branch: deployy"
echo "5. Render will automatically detect render.yaml"
echo ""
echo "🔑 IMPORTANT: Set these environment variables in Render Dashboard:"
echo ""
echo "Backend Service (ocr-invoice-backend):"
echo "  • SUPABASE_SERVICE_ROLE_KEY = [Your Supabase Service Role Key]"
echo "  • SUPABASE_ANON_KEY = [Your Supabase Anonymous Key]"
echo "  • SENDGRID_API_KEY = [Your SendGrid API Key]"
echo "  • JWT_SECRET = [Generate a secure random string]"
echo ""
echo "Frontend Service (ocr-invoice-frontend):"
echo "  • NEXT_PUBLIC_SUPABASE_ANON_KEY = [Same as backend SUPABASE_ANON_KEY]"
echo ""
echo "📋 HOW TO GET YOUR KEYS:"
echo "  • Supabase keys: https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api"
echo "  • SendGrid API key: https://app.sendgrid.com/settings/api_keys"
echo "  • JWT Secret: Use a password generator for a 64-character random string"
echo ""
echo "🚀 After setting environment variables, Render will automatically deploy!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Switch back to original branch
print_status "Switching back to original branch: $CURRENT_BRANCH"
git checkout $CURRENT_BRANCH

print_success "🎉 Deployment preparation complete!"
print_status "Your localhost setup remains unchanged and will continue to work normally."

echo ""
echo "🔍 MONITORING YOUR DEPLOYMENT:"
echo "  • Backend URL: https://ocr-invoice-backend.onrender.com"
echo "  • Frontend URL: https://ocr-invoice-frontend.onrender.com"
echo "  • Health Check: https://ocr-invoice-backend.onrender.com/api/health"
echo ""
echo "⚠️  First deployment may take 10-15 minutes as Render builds Docker images."
echo ""
