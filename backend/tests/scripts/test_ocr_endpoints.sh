#!/bin/bash
# Invoice OCR Endpoint Testing Script - Organized Test Suite
# ==========================================================
# Enhanced script for testing OCR endpoints with better error handling and organization

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Constants and Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BACKEND_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
readonly BASE_URL="${BASE_URL:-http://localhost:8000}"
readonly TEST_INVOICE="test_invoice.pdf"
readonly TIMEOUT_SECONDS=10

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_section() {
    echo ""
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

log_test() {
    echo -e "${BLUE}$1${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
  -h, --help          Show this help message
  -u, --url URL       Base URL for API endpoints (default: http://localhost:8000)
  -f, --file FILE     Test invoice file to upload (default: test_invoice.pdf)
  -t, --timeout SEC   Request timeout in seconds (default: 10)
  -v, --verbose       Enable verbose output

Examples:
  $0                                    # Test with default settings
  $0 -u http://localhost:3000          # Test with custom URL
  $0 -f custom_invoice.pdf             # Test with custom file
  $0 -v -t 30                         # Verbose mode with 30s timeout
EOF
}

# Function to check if server is running
check_server() {
    log_info "Checking if server is running at $BASE_URL..."
    
    if curl -s --max-time 5 "$BASE_URL/health" > /dev/null 2>&1; then
        log_success "Server is running and responding"
        return 0
    else
        log_error "Server is not responding at $BASE_URL"
        log_info "Make sure the backend server is running:"
        log_info "  cd $BACKEND_ROOT && python main.py"
        return 1
    fi
}

# Function to make API request with error handling
make_api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    log_test "Testing: $description"
    log_info "Request: $method $BASE_URL$endpoint"
    
    local response
    local http_code
    
    if [[ "$method" == "GET" ]]; then
        response=$(curl -s --max-time "$TIMEOUT_SECONDS" -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    elif [[ "$method" == "POST" ]]; then
        response=$(curl -s --max-time "$TIMEOUT_SECONDS" -w "%{http_code}" -X POST "$BASE_URL$endpoint" $data 2>/dev/null)
    fi
    
    if [[ -z "$response" ]]; then
        log_error "No response received"
        return 1
    fi
    
    # Extract HTTP code (last 3 characters)
    http_code="${response: -3}"
    # Extract response body (all but last 3 characters)
    local response_body="${response%???}"
    
    log_info "HTTP Status: $http_code"
    
    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        log_success "Request successful"
        
        # Pretty print JSON if possible
        if echo "$response_body" | python3 -m json.tool > /dev/null 2>&1; then
            echo "$response_body" | python3 -m json.tool
        else
            echo "$response_body"
        fi
        
        # Return the response body for further processing
        echo "$response_body"
        return 0
    else
        log_error "Request failed"
        echo "$response_body"
        return 1
    fi
}

# Function to test OCR status endpoint
test_ocr_status() {
    log_section "1️⃣ Testing OCR Status Endpoint"
    make_api_request "GET" "/ocr/status" "" "OCR service status check"
}

# Function to test health endpoint
test_health_endpoint() {
    log_section "2️⃣ Testing System Health Endpoint"
    make_api_request "GET" "/health" "" "System health check"
}

# Function to test invoice upload with OCR
test_invoice_upload() {
    log_section "3️⃣ Testing Invoice Upload with OCR Processing"
    
    # Check if test file exists
    local test_file="$BACKEND_ROOT/$TEST_INVOICE"
    if [[ ! -f "$test_file" ]]; then
        log_error "Test invoice file not found: $test_file"
        log_info "Available PDF files in backend directory:"
        find "$BACKEND_ROOT" -name "*.pdf" -type f | head -5
        return 1
    fi
    
    log_info "Using test file: $test_file"
    
    local upload_data='-F "file=@'"$test_file"'" -F "vendor_name=Test Vendor OCR" -F "invoice_number=OCR-TEST-001" -F "amount=250.00"'
    
    local upload_result
    upload_result=$(make_api_request "POST" "/invoices/upload" "$upload_data" "Invoice upload with OCR processing")
    
    if [[ $? -eq 0 ]]; then
        # Extract invoice ID for further testing
        local invoice_id
        invoice_id=$(echo "$upload_result" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('invoice_id', ''))" 2>/dev/null || echo "")
        
        if [[ -n "$invoice_id" ]]; then
            log_success "Invoice uploaded successfully with ID: $invoice_id"
            echo "$invoice_id"  # Return the ID for further use
            return 0
        else
            log_warning "Upload successful but could not extract invoice ID"
            return 1
        fi
    else
        log_error "Invoice upload failed"
        return 1
    fi
}

# Function to test OCR data retrieval
test_ocr_data_retrieval() {
    local invoice_id="$1"
    
    log_section "4️⃣ Testing OCR Data Retrieval"
    log_info "Retrieving OCR data for Invoice ID: $invoice_id"
    
    make_api_request "GET" "/invoices/$invoice_id/ocr" "" "OCR data retrieval for uploaded invoice"
}

# Function to test invoice listing
test_invoice_listing() {
    log_section "5️⃣ Testing Invoice Listing"
    make_api_request "GET" "/invoices" "" "Retrieve all invoices list"
}

# Function to run comprehensive endpoint tests
run_comprehensive_tests() {
    local exit_code=0
    
    log_section "🚀 Invoice OCR Endpoint Testing Suite"
    log_info "Base URL: $BASE_URL"
    log_info "Test File: $TEST_INVOICE"
    log_info "Timeout: ${TIMEOUT_SECONDS}s"
    
    # Navigate to backend root
    cd "$BACKEND_ROOT" || {
        log_error "Failed to navigate to backend directory: $BACKEND_ROOT"
        exit 1
    }
    
    # Check if server is running
    if ! check_server; then
        exit 1
    fi
    
    # Run individual tests
    test_ocr_status || exit_code=1
    test_health_endpoint || exit_code=1
    
    # Test upload and get invoice ID
    local invoice_id
    if invoice_id=$(test_invoice_upload); then
        # Test OCR data retrieval if upload was successful
        test_ocr_data_retrieval "$invoice_id" || exit_code=1
    else
        exit_code=1
    fi
    
    # Test invoice listing
    test_invoice_listing || exit_code=1
    
    # Final summary
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        log_success "All OCR endpoint tests completed successfully!"
        log_info "OCR functionality is working properly."
    else
        log_error "Some OCR endpoint tests failed. Please check the output above."
        log_info "Common issues:"
        log_info "  • Server not running (run: python main.py)"
        log_info "  • Missing test files"
        log_info "  • Network connectivity issues"
        log_info "  • Database connection problems"
    fi
    
    return $exit_code
}

# Main execution function
main() {
    run_comprehensive_tests
}

# Parse command line arguments
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -f|--file)
            TEST_INVOICE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT_SECONDS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            log_error "Unknown argument: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run main function
main
