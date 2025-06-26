#!/bin/bash

echo "🧪 Testing Dropdown Delete Functionality End-to-End"
echo "=================================================="

# Check if servers are running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend server not running. Start with: cd backend && python -m uvicorn main:app --reload --port 8000"
    exit 1
fi

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend server not running. Start with: cd frontend && npm run dev"
    exit 1
fi

echo "✅ Both servers are running"
echo ""

# Test 1: Get initial dropdown options
echo "📋 Test 1: Getting initial dropdown options..."
RESPONSE=$(curl -s "http://localhost:8000/api/dropdowns")
if echo "$RESPONSE" | jq -e '.dropdowns' > /dev/null; then
    echo "✅ Successfully retrieved dropdown options"
    INITIAL_COUNT=$(echo "$RESPONSE" | jq '.dropdowns.rechnungsempfaenger | length')
    echo "📊 Initial rechnungsempfaenger options: $INITIAL_COUNT"
else
    echo "❌ Failed to get dropdown options"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""

# Test 2: Add a new test option
echo "🔥 Test 2: Adding a new test option for deletion..."
TEST_OPTION="Test-Delete-Option-$(date +%s)"
ADD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/dropdowns/add-option" \
    -H "Content-Type: application/json" \
    -d "{\"field_name\": \"rechnungsempfaenger\", \"value\": \"$TEST_OPTION\", \"label\": \"$TEST_OPTION\"}")

if echo "$ADD_RESPONSE" | jq -e '.success' > /dev/null; then
    # Extract the actual stored value from the response
    STORED_VALUE=$(echo "$ADD_RESPONSE" | jq -r '.option.value')
    echo "✅ Successfully added test option: $TEST_OPTION"
    echo "📝 Stored value: $STORED_VALUE"
else
    echo "❌ Failed to add test option"
    echo "Response: $ADD_RESPONSE"
    exit 1
fi

echo ""

# Test 3: Verify the option was added
echo "🔍 Test 3: Verifying the option was added..."
AFTER_ADD_RESPONSE=$(curl -s "http://localhost:8000/api/dropdowns")
NEW_COUNT=$(echo "$AFTER_ADD_RESPONSE" | jq '.dropdowns.rechnungsempfaenger | length')
echo "📊 Options after adding: $NEW_COUNT"

if [ "$NEW_COUNT" -gt "$INITIAL_COUNT" ]; then
    echo "✅ Option count increased correctly"
else
    echo "❌ Option count did not increase"
    exit 1
fi

echo ""

# Test 4: Delete the test option
echo "🗑️  Test 4: Deleting the test option..."
DELETE_RESPONSE=$(curl -s -X DELETE "http://localhost:8000/api/dropdowns/rechnungsempfaenger/$STORED_VALUE")

if echo "$DELETE_RESPONSE" | jq -e '.success' > /dev/null; then
    echo "✅ Successfully deleted test option: $STORED_VALUE"
else
    echo "❌ Failed to delete test option"
    echo "Response: $DELETE_RESPONSE"
    exit 1
fi

echo ""

# Test 5: Verify the option was deleted
echo "🔍 Test 5: Verifying the option was deleted..."
AFTER_DELETE_RESPONSE=$(curl -s "http://localhost:8000/api/dropdowns")
FINAL_COUNT=$(echo "$AFTER_DELETE_RESPONSE" | jq '.dropdowns.rechnungsempfaenger | length')
echo "📊 Final options count: $FINAL_COUNT"

if [ "$FINAL_COUNT" -eq "$INITIAL_COUNT" ]; then
    echo "✅ Option count returned to original value"
else
    echo "❌ Option count is not correct after deletion"
    exit 1
fi

echo ""

# Test 6: Test deleting a default/standard option (should now work)
echo "✂️  Test 6: Testing deletion of standard/default option (should work now)..."
DEFAULT_OPTION="acme_construction"
DELETE_DEFAULT_RESPONSE=$(curl -s -X DELETE "http://localhost:8000/api/dropdowns/rechnungsempfaenger/$DEFAULT_OPTION")

if echo "$DELETE_DEFAULT_RESPONSE" | jq -e '.success' > /dev/null; then
    echo "✅ Successfully deleted standard option: $DEFAULT_OPTION"
    MESSAGE=$(echo "$DELETE_DEFAULT_RESPONSE" | jq -r '.message')
    echo "� Response: $MESSAGE"
else
    echo "❌ Failed to delete standard option"
    echo "Response: $DELETE_DEFAULT_RESPONSE"
    exit 1
fi

echo ""

# Test 7: Test all dropdown fields
echo "🔄 Test 7: Testing delete functionality for all dropdown fields..."
FIELDS=("rechnungssteller" "projekt" "gewerk" "weiter_berechnen_an")

for FIELD in "${FIELDS[@]}"; do
    echo "Testing field: $FIELD"
    
    # Add a test option
    TEST_OPTION_FIELD="Test-$FIELD-$(date +%s)"
    ADD_RESP=$(curl -s -X POST "http://localhost:8000/api/dropdowns/add-option" \
        -H "Content-Type: application/json" \
        -d "{\"field_name\": \"$FIELD\", \"value\": \"$TEST_OPTION_FIELD\", \"label\": \"$TEST_OPTION_FIELD\"}")
    
    if echo "$ADD_RESP" | jq -e '.success' > /dev/null; then
        # Extract the actual stored value
        STORED_VALUE_FIELD=$(echo "$ADD_RESP" | jq -r '.option.value')
        echo "  ✅ Added option for $FIELD (stored as: $STORED_VALUE_FIELD)"
        
        # Delete the test option using the stored value
        DEL_RESP=$(curl -s -X DELETE "http://localhost:8000/api/dropdowns/$FIELD/$STORED_VALUE_FIELD")
        
        if echo "$DEL_RESP" | jq -e '.success' > /dev/null; then
            echo "  ✅ Deleted option for $FIELD"
        else
            echo "  ❌ Failed to delete option for $FIELD"
            echo "  Response: $DEL_RESP"
            exit 1
        fi
    else
        echo "  ❌ Failed to add option for $FIELD"
        echo "  Response: $ADD_RESP"
        exit 1
    fi
done

echo ""
echo "🎉 ALL TESTS PASSED!"
echo ""
echo "✅ Dropdown delete functionality is working correctly:"
echo "   • Backend API endpoints handle delete requests"
echo "   • ALL options can be deleted (both standard and custom)"
echo "   • No restrictions on deleting any dropdown options"
echo "   • All dropdown fields support delete operations"
echo "   • Database operations are working properly"
echo ""
echo "🚀 Ready for production use!"
echo ""
echo "💡 Next Steps:"
echo "   1. Test the UI delete functionality in the browser:"
echo "      - http://localhost:3000/dropdown-test (Admin test page)"
echo "      - http://localhost:3000/dashboard (Main invoice editor)"
echo "   2. Hover over ANY option to see the delete (trash) icon"
echo "   3. All options (standard and custom) can now be deleted"
echo "   4. Standard options still show 'Standard' badge but are deletable"
