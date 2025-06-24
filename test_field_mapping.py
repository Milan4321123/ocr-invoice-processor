#!/usr/bin/env python3
"""
Test script to verify centralized field mapping works correctly.
"""

import sys
import os

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.field_mappings import (
    map_input_to_database,
    map_database_to_api,
    validate_database_fields,
    DATABASE_FIELDS,
    OCR_TO_DATABASE
)

def test_ocr_mapping():
    """Test OCR field mapping"""
    print("🧪 Testing OCR field mapping...")
    
    ocr_data = {
        "customer_name": "Test Customer GmbH",
        "vendor_name": "Test Vendor AG",
        "total_amount": 1234.56,
        "invoice_date": "2025-06-24",
        "due_date": "2025-07-24",
        "po_number": "PO-2025-001"
    }
    
    mapped = map_input_to_database(ocr_data)
    print(f"📥 Input: {ocr_data}")
    print(f"📤 Mapped: {mapped}")
    
    # Verify expected mappings
    expected = {
        "rechnungsempfaenger": "Test Customer GmbH",
        "rechnungssteller": "Test Vendor AG", 
        "rechnungsbetrag": 1234.56,
        "rechnungseingang": "2025-06-24",
        "faelligkeit": "2025-07-24",
        "projekt": "PO-2025-001"
    }
    
    for field, expected_value in expected.items():
        if mapped.get(field) == expected_value:
            print(f"✅ {field}: {expected_value}")
        else:
            print(f"❌ {field}: expected {expected_value}, got {mapped.get(field)}")
    
    return mapped

def test_api_response_mapping():
    """Test database to API response mapping"""
    print("\n🧪 Testing API response mapping...")
    
    db_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "rechnungsempfaenger": "Test Customer GmbH",
        "rechnungssteller": "Test Vendor AG",
        "rechnungsbetrag": 1234.56,
        "projekt": "PO-2025-001",
        "review_status": "under_review",
        "reviewed_by": "jane.doe@example.com"
    }
    
    api_response = map_database_to_api(db_data, include_english_aliases=True)
    print(f"📥 Database: {db_data}")
    print(f"📤 API Response: {api_response}")
    
    # Check that both German and English fields exist
    expected_german = ["rechnungsempfaenger", "rechnungssteller", "rechnungsbetrag"]
    expected_english = ["customer_name", "vendor_name", "total_amount"]
    
    for field in expected_german:
        if field in api_response:
            print(f"✅ German field '{field}': {api_response[field]}")
        else:
            print(f"❌ Missing German field: {field}")
    
    for field in expected_english:
        if field in api_response:
            print(f"✅ English alias '{field}': {api_response[field]}")
        else:
            print(f"❌ Missing English alias: {field}")

def test_field_validation():
    """Test field validation"""
    print("\n🧪 Testing field validation...")
    
    mixed_data = {
        "rechnungsempfaenger": "Valid Customer",
        "invalid_field": "Should be filtered out",
        "rechnungsbetrag": 999.99,
        "another_invalid": "Also filtered"
    }
    
    validated = validate_database_fields(mixed_data)
    print(f"📥 Mixed input: {mixed_data}")
    print(f"📤 Validated: {validated}")
    
    if "invalid_field" not in validated and "another_invalid" not in validated:
        print("✅ Invalid fields filtered out correctly")
    else:
        print("❌ Invalid fields not filtered properly")

def test_legacy_support():
    """Test legacy field support"""
    print("\n🧪 Testing legacy field support...")
    
    legacy_data = {
        "brutto_betrag": 500.00,  # Legacy field
        "rechnungsdatum": "2025-06-20",  # Legacy field
        "customer_name": "Legacy Customer"  # OCR field
    }
    
    mapped = map_input_to_database(legacy_data)
    print(f"📥 Legacy input: {legacy_data}")
    print(f"📤 Mapped: {mapped}")
    
    # Check that legacy fields map to correct database fields
    expected_mappings = {
        "rechnungsbetrag": 500.00,
        "rechnungseingang": "2025-06-20",
        "rechnungsempfaenger": "Legacy Customer"
    }
    
    for field, expected_value in expected_mappings.items():
        if mapped.get(field) == expected_value:
            print(f"✅ Legacy mapping {field}: {expected_value}")
        else:
            print(f"❌ Legacy mapping failed for {field}")

def main():
    """Run all tests"""
    print("🚀 Testing Centralized Field Mapping System")
    print("=" * 50)
    
    print(f"📊 Total database fields: {len(DATABASE_FIELDS)}")
    print(f"📊 OCR mappings: {len(OCR_TO_DATABASE)}")
    
    try:
        test_ocr_mapping()
        test_api_response_mapping()
        test_field_validation()
        test_legacy_support()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
