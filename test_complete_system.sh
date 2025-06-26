#!/bin/bash

echo "🧪 COMPREHENSIVE SYSTEM TEST - Invoice Management with Dropdown Integration"
echo "========================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TEST_COUNT=0
PASS_COUNT=0

function run_test() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    TEST_COUNT=$((TEST_COUNT + 1))
    echo -e "\n${BLUE}Test ${TEST_COUNT}: ${test_name}${NC}"
    echo "Command: $command"
    
    # Run the command and capture output
    output=$(eval "$command" 2>&1)
    exit_code=$?
    
    if [[ $exit_code -eq 0 ]] && [[ "$output" == *"$expected"* ]]; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Expected: $expected"
        echo "Got: $output"
    fi
}

function check_server() {
    local server_name="$1"
    local url="$2"
    
    echo -e "\n${YELLOW}Checking ${server_name}...${NC}"
    if curl -s -f "$url" > /dev/null; then
        echo -e "${GREEN}✅ ${server_name} is running${NC}"
        return 0
    else
        echo -e "${RED}❌ ${server_name} is not responding${NC}"
        return 1
    fi
}

echo -e "\n${YELLOW}🔍 STEP 1: Server Status Check${NC}"
check_server "Frontend" "http://localhost:3000"
check_server "Backend API" "http://localhost:8000/docs"

echo -e "\n${YELLOW}🗄️ STEP 2: Database Integration Tests${NC}"

# Test 1: Get all dropdown options
run_test "Get all dropdown options" \
    "curl -s -X GET 'http://localhost:8000/api/dropdowns'" \
    "rechnungsempfaenger"

# Test 2: Get specific field options
run_test "Get specific field (projekt) options" \
    "curl -s -X GET 'http://localhost:8000/api/dropdowns/projekt'" \
    "Wohnbau Mitte 2024"

# Test 3: Add new dropdown option
run_test "Add new dropdown option" \
    "curl -s -X POST 'http://localhost:8000/api/dropdowns/add-option' -H 'Content-Type: application/json' -d '{\"field_name\": \"gewerk\", \"value\": \"test_gewerk_$(date +%s)\", \"label\": \"Test Gewerk $(date +%s)\"}'" \
    "\"success\":true"

# Test 4: Verify the new option exists
sleep 1
run_test "Verify new option was saved" \
    "curl -s -X GET 'http://localhost:8000/api/dropdowns/gewerk'" \
    "Test Gewerk"

echo -e "\n${YELLOW}📋 STEP 3: Invoice Management Tests${NC}"

# Test 5: Get invoices
run_test "Get invoices list" \
    "curl -s -X GET 'http://localhost:8000/api/invoices'" \
    "invoices"

# Test 6: Get specific invoice (if exists)
invoice_id=$(curl -s -X GET 'http://localhost:8000/api/invoices' | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [[ -n "$invoice_id" ]]; then
    run_test "Get specific invoice" \
        "curl -s -X GET 'http://localhost:8000/api/invoices/$invoice_id'" \
        "file_name"
else
    echo -e "${YELLOW}⏭️  Skipping invoice detail test (no invoices found)${NC}"
fi

echo -e "\n${YELLOW}🌐 STEP 4: Frontend Integration Tests${NC}"

# Test 7: Frontend main page loads
run_test "Frontend main page loads" \
    "curl -s -I 'http://localhost:3000' | head -1" \
    "200 OK"

# Test 8: Frontend dashboard loads
run_test "Frontend dashboard loads" \
    "curl -s -I 'http://localhost:3000/dashboard' | head -1" \
    "200 OK"

# Test 9: Frontend dropdown test page loads
run_test "Frontend dropdown test page loads" \
    "curl -s -I 'http://localhost:3000/dropdown-test' | head -1" \
    "200 OK"

echo -e "\n${YELLOW}🔄 STEP 5: End-to-End Workflow Test${NC}"

# Test 10: Create a new dropdown option via API and verify it's accessible
timestamp=$(date +%s)
test_value="e2e_test_$timestamp"
test_label="E2E Test Company $timestamp"

run_test "Create test dropdown option" \
    "curl -s -X POST 'http://localhost:8000/api/dropdowns/add-option' -H 'Content-Type: application/json' -d '{\"field_name\": \"rechnungsempfaenger\", \"value\": \"$test_value\", \"label\": \"$test_label\"}'" \
    "\"success\":true"

sleep 1

run_test "Verify test option is retrievable" \
    "curl -s -X GET 'http://localhost:8000/api/dropdowns/rechnungsempfaenger'" \
    "$test_label"

echo -e "\n${YELLOW}📊 STEP 6: Summary Report${NC}"

# Get statistics
total_rechnungsempfaenger=$(curl -s -X GET 'http://localhost:8000/api/dropdowns/rechnungsempfaenger' | grep -o '"total":[0-9]*' | cut -d':' -f2)
total_projekt=$(curl -s -X GET 'http://localhost:8000/api/dropdowns/projekt' | grep -o '"total":[0-9]*' | cut -d':' -f2)
total_gewerk=$(curl -s -X GET 'http://localhost:8000/api/dropdowns/gewerk' | grep -o '"total":[0-9]*' | cut -d':' -f2)
total_invoices=$(curl -s -X GET 'http://localhost:8000/api/invoices' | grep -o '"total":[0-9]*' | cut -d':' -f2)

echo -e "\n📈 System Statistics:"
echo "  • Rechnungsempfänger options: ${total_rechnungsempfaenger:-0}"
echo "  • Projekt options: ${total_projekt:-0}"
echo "  • Gewerk options: ${total_gewerk:-0}"
echo "  • Total invoices: ${total_invoices:-0}"

echo -e "\n${YELLOW}🎯 FINAL RESULTS${NC}"
echo "========================================================================"
echo -e "Tests passed: ${GREEN}${PASS_COUNT}${NC}/${TEST_COUNT}"

if [[ $PASS_COUNT -eq $TEST_COUNT ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is fully functional.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
    exit 1
fi
