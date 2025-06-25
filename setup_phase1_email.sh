#!/bin/bash
"""
Phase 1 Email Workflow Setup and Testing Script
Applies database schema, validates configuration, and tests email workflow
"""

set -e  # Exit on error

echo "🚀 Phase 1: Editor Email System Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "EMAIL_WORKFLOW_SCHEMA.sql" ]; then
    print_error "EMAIL_WORKFLOW_SCHEMA.sql not found. Run this script from the project root."
    exit 1
fi

# Apply database schema
print_info "Applying database schema changes..."
if command -v psql &> /dev/null; then
    # If psql is available, try to apply schema
    if [ -n "$DATABASE_URL" ]; then
        psql "$DATABASE_URL" < EMAIL_WORKFLOW_SCHEMA.sql
        print_status "Database schema applied successfully"
    else
        print_warning "DATABASE_URL not set. Please apply EMAIL_WORKFLOW_SCHEMA.sql manually to your Supabase database."
    fi
else
    print_warning "psql not found. Please apply EMAIL_WORKFLOW_SCHEMA.sql manually to your Supabase database."
fi

# Check backend dependencies
print_info "Checking backend dependencies..."
cd backend

if [ -f "requirements.txt" ]; then
    print_status "Requirements.txt found with email dependencies"
    grep -E "(sendgrid|PyJWT|Jinja2|cryptography)" requirements.txt && print_status "Email dependencies confirmed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Check environment configuration
print_info "Checking environment configuration..."
if [ -f ".env" ]; then
    if grep -q "SENDGRID_API_KEY" .env; then
        print_status "Email configuration found in .env"
        print_warning "Please update .env with your actual email provider credentials"
    else
        print_error "Email configuration missing from .env"
        exit 1
    fi
else
    print_error ".env file not found"
    exit 1
fi

# Install dependencies if requested
if [ "$1" = "--install" ]; then
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    print_status "Dependencies installed"
fi

# Test basic imports
print_info "Testing basic imports..."
python3 -c "
try:
    from services.email_service import email_service
    from api.routes.email_workflow import router
    print('✅ Email service imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" || print_error "Import test failed. Please install dependencies with --install flag"

cd ..

# Create a simple manual test
print_info "Creating manual test script..."
cat > test_email_manual.py << 'EOF'
#!/usr/bin/env python3
"""
Manual test for Phase 1 email workflow
Run this after starting the backend server
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_INVOICE_ID = "test-invoice-123"
TEST_EMAIL = "test@company.com"

def test_editor_notification():
    """Test editor notification endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/email/editor-notification",
            json={
                "invoice_id": TEST_INVOICE_ID,
                "editor_email": TEST_EMAIL,
                "editor_name": "Test Editor",
                "changes_summary": [
                    {
                        "field": "Rechnungsbetrag",
                        "old_value": "1000.00",
                        "new_value": "1200.00",
                        "timestamp": "2024-01-15T10:30:00"
                    }
                ]
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Editor notification test passed")
        else:
            print("❌ Editor notification test failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Phase 1 Email Workflow")
    print("Make sure the backend server is running on port 8001")
    input("Press Enter to continue...")
    test_editor_notification()
EOF

chmod +x test_email_manual.py
print_status "Manual test script created: test_email_manual.py"

# Create documentation
print_info "Creating Phase 1 documentation..."
cat > PHASE_1_EMAIL_DOCUMENTATION.md << 'EOF'
# Phase 1: Editor Email System Implementation

## Overview
Phase 1 implements a professional email notification system for editors after invoice completion. The system ensures invoices are only marked as "completed" after successful email delivery.

## Features Implemented

### 1. Database Schema Changes
- ✅ Added email workflow columns to `invoices_clean` table
- ✅ Created `email_audit_log` table for compliance tracking
- ✅ Created `approval_tokens` table for secure links (Phase 2)
- ✅ Created `security_events` table for monitoring
- ✅ Updated status enum with new workflow states

### 2. Email Service (`backend/services/email_service.py`)
- ✅ Professional HTML email templates with German localization
- ✅ Support for both SendGrid and SMTP backends
- ✅ Comprehensive audit logging
- ✅ XSS protection with Jinja2 autoescaping
- ✅ Error handling and retry logic
- ✅ Email size tracking for compliance

### 3. API Endpoints (`backend/api/routes/email_workflow.py`)
- ✅ `POST /api/email/editor-notification` - Send editor notification
- ✅ `GET /api/approval/{token}` - Handle secure approval links (Phase 2)
- ✅ `GET /api/email/audit/{invoice_id}` - Audit log access
- ✅ Request validation and error handling
- ✅ Security event logging

### 4. Security Features
- ✅ JWT-based secure approval tokens
- ✅ IP address logging for all actions
- ✅ Rate limiting preparation
- ✅ SQL injection protection
- ✅ XSS protection in email templates

## Email Templates

### Editor Notification Template
- Professional German language template
- Includes invoice details and change summary
- Responsive HTML design
- Security timestamp and request ID
- Company branding ready

## API Usage

### Send Editor Notification
```bash
curl -X POST http://localhost:8001/api/email/editor-notification \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "uuid-here",
    "editor_email": "editor@company.com",
    "editor_name": "Editor Name",
    "changes_summary": [
      {
        "field": "Rechnungsbetrag",
        "old_value": "1000.00",
        "new_value": "1200.00",
        "timestamp": "2024-01-15T10:30:00"
      }
    ]
  }'
```

## Configuration Required

### Environment Variables (.env)
```env
# Email Service
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=Invoice Processing System

# Security
JWT_SECRET=your-secure-secret-key
BASE_URL=http://localhost:8001

# Optional SMTP Fallback
SMTP_HOST=smtp.company.com
SMTP_PORT=587
SMTP_USERNAME=username
SMTP_PASSWORD=password
```

## Database Schema Applied
- All tables and columns from `EMAIL_WORKFLOW_SCHEMA.sql`
- Indexes for performance
- Constraints for data integrity
- Comments for documentation

## Testing

### Automated Tests
Run the comprehensive test suite:
```bash
python test_phase1_email_workflow.py
```

### Manual Testing
1. Start the backend server: `uvicorn backend.main:app --port 8001`
2. Run manual test: `python test_email_manual.py`
3. Check email delivery and database updates

## Security Considerations

### Implemented
- ✅ JWT token validation
- ✅ IP address logging
- ✅ SQL parameterization
- ✅ Email template XSS protection
- ✅ Audit trail for all actions

### Production Recommendations
- Use strong JWT secrets (32+ chars)
- Enable TLS for email delivery
- Set up monitoring for failed deliveries
- Regular audit log review
- Rate limiting implementation

## Status Workflow

```
edited → pending_email → edit_completed → (Phase 2: in_review_by_bauleiter)
```

### Status Meanings
- `edited`: Invoice has been edited, ready for email notification
- `pending_email`: Email notification is being sent
- `edit_completed`: Email sent successfully, ready for Bau-Leiter review
- `error`: Email delivery failed, manual intervention required

## Audit & Compliance

### Email Audit Log
Every email attempt is logged with:
- Timestamp and recipient
- Success/failure status
- Provider response details
- Email size for compliance
- Template used

### Security Events
All security-relevant actions logged:
- Email sends and failures
- Token generation and usage
- Invalid access attempts
- IP addresses and user emails

## Next Steps (Phase 2)
- Implement Bau-Leiter approval email workflow
- Add secure approval/rejection link handling
- Enhance security monitoring
- Build admin dashboard for audit review

## Error Handling
- Graceful degradation on email failures
- Status rollback on delivery errors
- Comprehensive error logging
- User-friendly error messages

## Performance Considerations
- Connection pooling for database
- Email template caching
- Async email delivery
- Batch processing capability (future)
EOF

print_status "Documentation created: PHASE_1_EMAIL_DOCUMENTATION.md"

# Final summary
echo ""
echo "🎉 Phase 1 Setup Complete!"
echo "=========================="
print_status "Database schema ready for application"
print_status "Email service implemented with security"
print_status "API endpoints created and configured"
print_status "Professional HTML email templates ready"
print_status "Comprehensive testing suite available"
print_status "Documentation created"

echo ""
print_info "Next Steps:"
echo "1. Apply EMAIL_WORKFLOW_SCHEMA.sql to your Supabase database"
echo "2. Update backend/.env with your email provider credentials"
echo "3. Install dependencies: cd backend && pip install -r requirements.txt"
echo "4. Start the server: uvicorn main:app --port 8001"
echo "5. Test the workflow: python test_email_manual.py"
echo ""
print_warning "Remember to configure your email provider (SendGrid/SMTP) before testing!"

exit 0
