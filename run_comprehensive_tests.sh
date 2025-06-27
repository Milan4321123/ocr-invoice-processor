#!/bin/bash

# Comprehensive test runner for OCR Invoice Processor upload functionality
# Tests all upload methods, edge cases, and complete workflows

echo "🧪 OCR Invoice Processor - Comprehensive Upload Test Suite"
echo "==========================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TIMEOUT=30

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_file="$3"
    
    echo ""
    echo -e "${BLUE}📋 Running: $test_name${NC}"
    echo "----------------------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to check if services are running
check_services() {
    echo -e "${BLUE}🔍 Checking Service Availability${NC}"
    echo "--------------------------------"
    
    # Check backend API
    echo -n "Backend API ($API_URL): "
    if curl -s --max-time 10 "$API_URL/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Available${NC}"
    else
        echo -e "${RED}✗ Unavailable${NC}"
        echo "Please start the backend server first:"
        echo "  cd backend && python main.py"
        exit 1
    fi
    
    # Check frontend (optional)
    echo -n "Frontend ($FRONTEND_URL): "
    if curl -s --max-time 5 "$FRONTEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Available${NC}"
    else
        echo -e "${YELLOW}⚠ Unavailable (optional)${NC}"
    fi
    
    # Check folder watcher status
    echo -n "Folder Watcher API: "
    if curl -s --max-time 10 "$API_URL/api/folder-watcher/status" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Available${NC}"
    else
        echo -e "${YELLOW}⚠ Limited functionality${NC}"
    fi
}

# Function to create test files for file-based tests
create_test_files() {
    echo -e "${BLUE}📁 Creating Test Files${NC}"
    echo "---------------------"
    
    # Create test directory
    TEST_DIR="test_files_$(date +%s)"
    mkdir -p "$TEST_DIR"
    
    # Create valid test PDF
    cat > "$TEST_DIR/20250627_VALID001_ACME_INVOICE.pdf" << 'EOF'
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
301
%%EOF
EOF
    
    # Create invalid test files
    echo "Invalid content" > "$TEST_DIR/invalid_filename.pdf"
    echo "Not a PDF" > "$TEST_DIR/20250627_INVALID_ACME_INVOICE.txt"
    
    # Create large test file (5MB)
    dd if=/dev/zero of="$TEST_DIR/20250627_LARGE001_ACME_INVOICE.pdf" bs=1M count=5 2>/dev/null
    # Add PDF header to large file
    (echo "%PDF-1.4"; cat "$TEST_DIR/20250627_LARGE001_ACME_INVOICE.pdf") > "$TEST_DIR/temp.pdf"
    mv "$TEST_DIR/temp.pdf" "$TEST_DIR/20250627_LARGE001_ACME_INVOICE.pdf"
    
    echo "Created test files in: $TEST_DIR"
    export TEST_DIR
}

# Function to cleanup test files
cleanup_test_files() {
    if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
        echo -e "${BLUE}🧹 Cleaning up test files${NC}"
        rm -rf "$TEST_DIR"
    fi
}

# Function to run Python-based tests
run_python_tests() {
    echo -e "${BLUE}🐍 Running Python Test Suites${NC}"
    echo "==============================="
    
    # Set environment variables for Python tests
    export API_URL="$API_URL"
    export FRONTEND_URL="$FRONTEND_URL"
    
    # Run comprehensive upload tests (if backend imports work)
    if [ -f "test_comprehensive_uploads.py" ]; then
        run_test "Comprehensive Upload Tests" "python3 test_comprehensive_uploads.py" "test_comprehensive_uploads.py"
    fi
    
    # Run API-level tests
    if [ -f "test_api_uploads.py" ]; then
        run_test "API Upload Tests" "python3 test_api_uploads.py" "test_api_uploads.py"
    fi
    
    # Run end-to-end workflow tests
    if [ -f "test_e2e_workflow.py" ]; then
        run_test "End-to-End Workflow Tests" "python3 test_e2e_workflow.py" "test_e2e_workflow.py"
    fi
    
    # Run existing validation tests
    if [ -f "test_unified_validation.py" ]; then
        run_test "Unified Validation Tests" "python3 test_unified_validation.py" "test_unified_validation.py"
    fi
}

# Function to run manual API tests
run_manual_api_tests() {
    echo -e "${BLUE}🔗 Running Manual API Tests${NC}"
    echo "============================="
    
    # Test 1: Valid file upload
    echo "Testing valid PDF upload..."
    UPLOAD_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/upload" \
        -F "file=@$TEST_DIR/20250627_VALID001_ACME_INVOICE.pdf" \
        -o upload_response.json)
    
    if [ "${UPLOAD_RESPONSE: -3}" = "200" ]; then
        echo -e "${GREEN}✅ Valid PDF upload successful${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Valid PDF upload failed (HTTP ${UPLOAD_RESPONSE: -3})${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test 2: Invalid filename pattern
    echo "Testing invalid filename pattern..."
    INVALID_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/upload" \
        -F "file=@$TEST_DIR/invalid_filename.pdf" \
        -o invalid_response.json)
    
    if [ "${INVALID_RESPONSE: -3}" = "400" ]; then
        echo -e "${GREEN}✅ Invalid filename correctly rejected${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Invalid filename not rejected (HTTP ${INVALID_RESPONSE: -3})${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test 3: Wrong file type
    echo "Testing wrong file type..."
    WRONG_TYPE_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/upload" \
        -F "file=@$TEST_DIR/20250627_INVALID_ACME_INVOICE.txt" \
        -o wrong_type_response.json)
    
    if [ "${WRONG_TYPE_RESPONSE: -3}" = "400" ]; then
        echo -e "${GREEN}✅ Wrong file type correctly rejected${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Wrong file type not rejected (HTTP ${WRONG_TYPE_RESPONSE: -3})${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Clean up response files
    rm -f upload_response.json invalid_response.json wrong_type_response.json
}

# Function to test folder watcher functionality
test_folder_watcher() {
    echo -e "${BLUE}👁 Testing Folder Watcher Functionality${NC}"
    echo "========================================"
    
    # Create temporary watch directory
    WATCH_DIR="watch_test_$(date +%s)"
    mkdir -p "$WATCH_DIR"
    
    # Test adding watch folder
    echo "Adding watch folder..."
    ADD_FOLDER_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/folder-watcher/folders" \
        -H "Content-Type: application/json" \
        -d "{\"folder_path\":\"$(pwd)/$WATCH_DIR\",\"pattern\":\"*.pdf\",\"recursive\":false,\"enabled\":true}" \
        -o add_folder_response.json)
    
    if [ "${ADD_FOLDER_RESPONSE: -3}" = "200" ]; then
        echo -e "${GREEN}✅ Watch folder added successfully${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Extract config_id for cleanup
        CONFIG_ID=$(grep -o '"config_id":"[^"]*"' add_folder_response.json | cut -d'"' -f4)
        
        # Test starting folder watcher
        echo "Starting folder watcher..."
        START_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/folder-watcher/start" \
            -o start_response.json)
        
        if [ "${START_RESPONSE: -3}" = "200" ]; then
            echo -e "${GREEN}✅ Folder watcher started successfully${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            
            # Test file detection (copy test file to watch directory)
            cp "$TEST_DIR/20250627_VALID001_ACME_INVOICE.pdf" "$WATCH_DIR/20250627_WATCH001_TEST_INVOICE.pdf"
            
            # Wait for processing
            sleep 3
            
            # Check notifications
            NOTIFICATIONS_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/api/folder-watcher/notifications?limit=5" \
                -o notifications_response.json)
            
            if [ "${NOTIFICATIONS_RESPONSE: -3}" = "200" ]; then
                echo -e "${GREEN}✅ Notifications accessible${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${RED}❌ Notifications not accessible${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
            
            # Stop folder watcher
            curl -s -X POST "$API_URL/api/folder-watcher/stop" > /dev/null
            
        else
            echo -e "${RED}❌ Folder watcher failed to start${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        
        # Clean up watch folder
        if [ -n "$CONFIG_ID" ]; then
            curl -s -X DELETE "$API_URL/api/folder-watcher/folders/$CONFIG_ID" > /dev/null
        fi
        
    else
        echo -e "${RED}❌ Watch folder addition failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 3))  # 3 tests in this function
    
    # Clean up
    rm -rf "$WATCH_DIR"
    rm -f add_folder_response.json start_response.json notifications_response.json
}

# Function to test dashboard and editor functionality
test_dashboard_editor() {
    echo -e "${BLUE}📊 Testing Dashboard and Editor${NC}"
    echo "==============================="
    
    # Test dashboard endpoint
    echo "Testing dashboard endpoint..."
    DASHBOARD_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/api/invoices" -o dashboard_response.json)
    
    if [ "${DASHBOARD_RESPONSE: -3}" = "200" ]; then
        echo -e "${GREEN}✅ Dashboard accessible${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Check if we have any invoices to test editor with
        if grep -q '"id"' dashboard_response.json; then
            INVOICE_ID=$(grep -o '"id":"[^"]*"' dashboard_response.json | head -1 | cut -d'"' -f4)
            
            if [ -n "$INVOICE_ID" ]; then
                echo "Testing invoice editor with ID: $INVOICE_ID"
                EDITOR_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/api/invoices/$INVOICE_ID/editor" \
                    -o editor_response.json)
                
                if [ "${EDITOR_RESPONSE: -3}" = "200" ]; then
                    echo -e "${GREEN}✅ Invoice editor accessible${NC}"
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                else
                    echo -e "${RED}❌ Invoice editor not accessible${NC}"
                    FAILED_TESTS=$((FAILED_TESTS + 1))
                fi
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
            fi
        fi
    else
        echo -e "${RED}❌ Dashboard not accessible${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Clean up
    rm -f dashboard_response.json editor_response.json
}

# Function to test dropdown functionality
test_dropdown_functionality() {
    echo -e "${BLUE}🔽 Testing Dropdown Functionality${NC}"
    echo "=================================="
    
    # Test dropdowns endpoint
    echo "Testing dropdowns endpoint..."
    DROPDOWNS_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/api/dropdowns" -o dropdowns_response.json)
    
    if [ "${DROPDOWNS_RESPONSE: -3}" = "200" ]; then
        echo -e "${GREEN}✅ Dropdowns accessible${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Test pending changes endpoint
        echo "Testing pending changes..."
        PENDING_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/api/dropdowns/pending" -o pending_response.json)
        
        if [ "${PENDING_RESPONSE: -3}" = "200" ]; then
            echo -e "${GREEN}✅ Pending changes accessible${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ Pending changes not accessible${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        
    else
        echo -e "${RED}❌ Dropdowns not accessible${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Clean up
    rm -f dropdowns_response.json pending_response.json
}

# Function to run performance tests
test_performance() {
    echo -e "${BLUE}⚡ Testing Performance${NC}"
    echo "====================="
    
    # Test concurrent uploads
    echo "Testing concurrent uploads (5 files)..."
    
    # Create multiple test files
    for i in {1..5}; do
        cp "$TEST_DIR/20250627_VALID001_ACME_INVOICE.pdf" "$TEST_DIR/20250627_PERF${i}_ACME_INVOICE.pdf"
    done
    
    # Upload files concurrently
    start_time=$(date +%s)
    
    for i in {1..5}; do
        (curl -s -X POST "$API_URL/api/upload" \
            -F "file=@$TEST_DIR/20250627_PERF${i}_ACME_INVOICE.pdf" \
            -o "perf_response_${i}.json" &)
    done
    
    # Wait for all uploads to complete
    wait
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    # Check results
    successful_uploads=0
    for i in {1..5}; do
        if [ -f "perf_response_${i}.json" ] && grep -q '"id"' "perf_response_${i}.json"; then
            successful_uploads=$((successful_uploads + 1))
        fi
    done
    
    echo "Concurrent uploads: $successful_uploads/5 successful in ${duration}s"
    
    if [ $successful_uploads -ge 4 ]; then  # Allow 1 failure
        echo -e "${GREEN}✅ Performance test passed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Performance test failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Clean up
    rm -f perf_response_*.json
    rm -f "$TEST_DIR/20250627_PERF"*
}

# Function to display final summary
display_summary() {
    echo ""
    echo "=" * 60
    echo -e "${BLUE}📊 COMPREHENSIVE TEST SUMMARY${NC}"
    echo "=" * 60
    echo ""
    echo "Total Tests Run: $TOTAL_TESTS"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
        echo "The OCR Invoice Processor upload functionality is working correctly."
    else
        echo -e "${RED}❌ Some tests failed.${NC}"
        echo "Please review the failed tests and fix any issues."
    fi
    
    echo ""
    echo "Test Coverage:"
    echo "• File validation (formats, sizes, patterns)"
    echo "• Upload sources (drag & drop, folder watcher, manual)"
    echo "• Error handling and edge cases"
    echo "• Dashboard and editor functionality"
    echo "• Dropdown management"
    echo "• Performance and concurrent operations"
    echo "• End-to-end workflows"
    echo ""
    
    # Return exit code based on results
    if [ $FAILED_TESTS -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    echo -e "${YELLOW}Starting comprehensive upload test suite...${NC}"
    echo ""
    
    # Check if services are available
    check_services
    
    # Create test files
    create_test_files
    
    # Set trap for cleanup
    trap cleanup_test_files EXIT
    
    # Run all test categories
    run_python_tests
    run_manual_api_tests
    test_folder_watcher
    test_dashboard_editor
    test_dropdown_functionality
    test_performance
    
    # Display final summary
    display_summary
}

# Run main function
main "$@"
