#!/usr/bin/env python3
"""
Integration test for simplified dropdown system
Tests all API endpoints and verifies expected behavior
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_get_all_dropdowns():
    """Test getting all dropdown options"""
    print("🔍 Testing GET /api/dropdowns...")
    
    response = requests.get(f"{BASE_URL}/dropdowns")
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    # Verify structure
    if not all(key in data for key in ["dropdowns", "field_names"]):
        print("❌ Failed: Missing required keys in response")
        return False
    
    # Verify all expected fields are present
    expected_fields = ["rechnungsempfaenger", "rechnungssteller", "projekt", "gewerk"]
    if set(data["field_names"]) != set(expected_fields):
        print(f"❌ Failed: Expected fields {expected_fields}, got {data['field_names']}")
        return False
    
    # Verify each field has options
    for field in expected_fields:
        if field not in data["dropdowns"] or not data["dropdowns"][field]:
            print(f"❌ Failed: Field '{field}' has no options")
            return False
    
    print(f"✅ SUCCESS: Retrieved {len(data['field_names'])} fields with options")
    return True

def test_get_specific_field():
    """Test getting options for a specific field"""
    print("🔍 Testing GET /api/dropdowns/gewerk...")
    
    response = requests.get(f"{BASE_URL}/dropdowns/gewerk")
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    # Verify structure
    if not all(key in data for key in ["field_name", "options", "total"]):
        print("❌ Failed: Missing required keys in response")
        return False
    
    if data["field_name"] != "gewerk":
        print(f"❌ Failed: Expected field_name 'gewerk', got '{data['field_name']}'")
        return False
    
    if len(data["options"]) != data["total"]:
        print(f"❌ Failed: Options count mismatch: {len(data['options'])} vs {data['total']}")
        return False
    
    print(f"✅ SUCCESS: Retrieved {data['total']} options for gewerk")
    return True

def test_add_custom_option():
    """Test adding a custom option"""
    print("🔍 Testing POST /api/dropdowns/add-option...")
    
    payload = {
        "field_name": "gewerk",
        "value": "test_custom_gewerk",
        "label": "Test Custom Gewerk"
    }
    
    response = requests.post(
        f"{BASE_URL}/dropdowns/add-option",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    if not data.get("success"):
        print(f"❌ Failed: {data}")
        return False
    
    print(f"✅ SUCCESS: Added custom option '{data['option']['label']}'")
    return True

def test_ocr_suggestions():
    """Test OCR suggestion functionality"""
    print("🔍 Testing POST /api/dropdowns/suggest-from-ocr...")
    
    payload = {
        "extracted_values": {
            "gewerk": "Elektro Arbeiten",  # Should match existing "Elektroinstallation" 
            "projekt": "Totally New Project XYZ",  # Should be suggested as new
            "rechnungssteller": "Elektro Wagner"  # Should match existing closely
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/dropdowns/suggest-from-ocr",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    if "suggestions" not in data:
        print(f"❌ Failed: No suggestions in response: {data}")
        return False
    
    suggestions = data["suggestions"]
    print(f"✅ SUCCESS: Got {len(suggestions)} suggestions:")
    
    for suggestion in suggestions:
        status = "NEW" if suggestion["is_new"] else "EXISTING"
        confidence = suggestion["confidence"]
        print(f"   - {suggestion['field_name']}: '{suggestion['suggested_value']}' → {status} (confidence: {confidence:.2f})")
    
    return True

def test_stats():
    """Test stats endpoint"""
    print("🔍 Testing GET /api/dropdowns/stats...")
    
    response = requests.get(f"{BASE_URL}/dropdowns/stats")
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    if not all(key in data for key in ["field_stats", "total_options", "total_fields"]):
        print("❌ Failed: Missing required keys in stats response")
        return False
    
    print(f"✅ SUCCESS: Stats show {data['total_options']} total options across {data['total_fields']} fields")
    
    # Show breakdown
    for field, stats in data["field_stats"].items():
        print(f"   - {field}: {stats['default_options']} default + {stats['custom_options']} custom = {stats['total_options']} total")
    
    return True

def test_delete_custom_option():
    """Test deleting the custom option we added"""
    print("🔍 Testing DELETE /api/dropdowns/gewerk/test_custom_gewerk...")
    
    response = requests.delete(f"{BASE_URL}/dropdowns/gewerk/test_custom_gewerk")
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    if not data.get("success"):
        print(f"❌ Failed: {data}")
        return False
    
    print(f"✅ SUCCESS: Deleted custom option '{data['deleted_option']}'")
    return True

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print("🔍 Testing error handling...")
    
    # Test invalid field name
    response = requests.get(f"{BASE_URL}/dropdowns/invalid_field")
    if response.status_code == 400:
        print("✅ SUCCESS: Invalid field name properly rejected")
    else:
        print(f"❌ Failed: Expected 400 error for invalid field, got {response.status_code}")
        return False
    
    # Test deleting default option (should fail)
    response = requests.delete(f"{BASE_URL}/dropdowns/gewerk/elektroinstallation")
    if response.status_code == 400:
        print("✅ SUCCESS: Deleting default option properly rejected")
    else:
        print(f"❌ Failed: Expected 400 error for deleting default option, got {response.status_code}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Simplified Dropdown System Integration")
    print("=" * 60)
    
    tests = [
        test_get_all_dropdowns,
        test_get_specific_field,
        test_add_custom_option,
        test_ocr_suggestions,
        test_stats,
        test_delete_custom_option,
        test_invalid_requests
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
        
        print("-" * 40)
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Simplified dropdown system is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the backend server and API endpoints.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
