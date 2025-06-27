#!/usr/bin/env python3
"""
Standalone upload validation tests that don't require backend imports.
Tests filename patterns, file types, and API responses directly.
"""
import re
import sys
from typing import Tuple

class StandaloneTestResults:
    """Track test results without dependencies"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_result(self, test_name: str, passed: bool, error: str = None):
        self.total += 1
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            self.errors.append(f"{test_name}: {error or 'Test failed'}")
            print(f"❌ {test_name}: {error or 'Test failed'}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"STANDALONE TEST SUMMARY: {self.passed}/{self.total} passed ({self.failed} failed)")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  • {error}")
        print(f"{'='*60}")

results = StandaloneTestResults()

def validate_filename_pattern(filename: str) -> Tuple[bool, str]:
    """Validate filename against the expected pattern (matches backend exactly)"""
    pattern = r'^\d{8}_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+\.pdf$'
    if re.match(pattern, filename):
        return True, "Valid filename"
    else:
        return False, "Dateiname muss dem Muster folgen: JJJJMMTT_KENNUNG_LIEFERANT_TYP.pdf"

def validate_file_type(filename: str, content_type: str) -> Tuple[bool, str]:
    """Validate file type"""
    if content_type != "application/pdf":
        return False, "Nur PDF-Dateien sind erlaubt"
    if not filename.lower().endswith('.pdf'):
        return False, "Nur PDF-Dateien sind erlaubt"
    return True, "Valid file type"

def validate_file_size(size_bytes: int) -> Tuple[bool, str]:
    """Validate file size"""
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    if size_bytes == 0:
        return False, "Die Datei ist leer"
    if size_bytes > MAX_SIZE:
        return False, f"Datei ist zu groß. Maximum: {MAX_SIZE // (1024*1024)}MB"
    return True, "Valid file size"

def test_filename_validation():
    """Test filename pattern validation"""
    print("\n📝 Testing Filename Validation")
    print("-" * 40)
    
    test_cases = [
        # Valid cases
        ("20250627_INV001_ACME_SERVICE.pdf", True),
        ("20240101_123ABC_TEST456_INVOICE99.pdf", True),
        ("19991231_A1B2C3_VENDOR1_TYPE123.pdf", True),
        
        # Invalid cases - wrong date format
        ("2025627_INV001_ACME_SERVICE.pdf", False),  # 7 digits
        ("202506271_INV001_ACME_SERVICE.pdf", False),  # 9 digits
        ("ABCD0627_INV001_ACME_SERVICE.pdf", False),  # non-numeric
        
        # Invalid cases - missing components
        ("20250627_INV001_ACME.pdf", False),  # missing TYPE
        ("20250627_INV001_.pdf", False),  # empty VENDOR
        ("20250627__.pdf", False),  # multiple missing
        
        # Invalid cases - wrong separators
        ("20250627-INV001-ACME-SERVICE.pdf", False),  # dashes instead of underscores
        ("20250627INV001ACMESERVICE.pdf", False),  # no separators
        ("20250627_INV001_ACME_SERVICE", False),  # missing .pdf
        
        # Invalid cases - wrong extension
        ("20250627_INV001_ACME_SERVICE.txt", False),
        ("20250627_INV001_ACME_SERVICE.doc", False),
        ("20250627_INV001_ACME_SERVICE.PDF", False),  # backend requires lowercase .pdf
        
        # Edge cases
        ("20250627_A_B_C.pdf", True),  # minimal valid
        ("20250627_VERY_LONG_FILENAME_WITH_NUMBERS123.pdf", False),  # backend doesn't allow underscores in parts
    ]
    
    for filename, expected_valid in test_cases:
        is_valid, error_msg = validate_filename_pattern(filename)
        test_name = f"Filename '{filename}'"
        
        if is_valid == expected_valid:
            results.add_result(test_name, True)
        else:
            results.add_result(test_name, False, f"Expected {expected_valid}, got {is_valid}")

def test_file_type_validation():
    """Test file type validation"""
    print("\n📄 Testing File Type Validation")
    print("-" * 40)
    
    test_cases = [
        # Valid cases
        ("test.pdf", "application/pdf", True),
        ("TEST.PDF", "application/pdf", True),
        
        # Invalid cases
        ("test.pdf", "text/plain", False),
        ("test.txt", "application/pdf", False),
        ("test.doc", "application/msword", False),
        ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False),
        ("test.jpg", "image/jpeg", False),
        ("test.png", "image/png", False),
    ]
    
    for filename, content_type, expected_valid in test_cases:
        is_valid, error_msg = validate_file_type(filename, content_type)
        test_name = f"File type '{filename}' ({content_type})"
        
        if is_valid == expected_valid:
            results.add_result(test_name, True)
        else:
            results.add_result(test_name, False, f"Expected {expected_valid}, got {is_valid}")

def test_file_size_validation():
    """Test file size validation"""
    print("\n📏 Testing File Size Validation")
    print("-" * 40)
    
    test_cases = [
        # Valid cases
        (1024, True),  # 1KB
        (100 * 1024, True),  # 100KB
        (1024 * 1024, True),  # 1MB
        (5 * 1024 * 1024, True),  # 5MB
        (10 * 1024 * 1024, True),  # 10MB (max)
        
        # Invalid cases
        (0, False),  # empty file
        (15 * 1024 * 1024, False),  # 15MB (too large)
        (50 * 1024 * 1024, False),  # 50MB (way too large)
    ]
    
    for size_bytes, expected_valid in test_cases:
        is_valid, error_msg = validate_file_size(size_bytes)
        size_mb = size_bytes / (1024 * 1024)
        test_name = f"File size {size_mb:.1f}MB"
        
        if is_valid == expected_valid:
            results.add_result(test_name, True)
        else:
            results.add_result(test_name, False, f"Expected {expected_valid}, got {is_valid}: {error_msg}")

def test_combined_validation():
    """Test combined validation scenarios"""
    print("\n🔄 Testing Combined Validation")
    print("-" * 40)
    
    test_files = [
        # Perfect valid file
        {
            "filename": "20250627_PERFECT_TEST_INVOICE.pdf",
            "content_type": "application/pdf",
            "size": 1024 * 1024,  # 1MB
            "expected_valid": True
        },
        
        # Valid filename, wrong type
        {
            "filename": "20250627_VALID_TEST_INVOICE.pdf",
            "content_type": "text/plain",
            "size": 1024,
            "expected_valid": False
        },
        
        # Valid filename and type, too large
        {
            "filename": "20250627_LARGE_TEST_INVOICE.pdf",
            "content_type": "application/pdf",
            "size": 15 * 1024 * 1024,  # 15MB
            "expected_valid": False
        },
        
        # Invalid filename, valid type and size
        {
            "filename": "invalid_name.pdf",
            "content_type": "application/pdf",
            "size": 1024,
            "expected_valid": False
        },
        
        # Everything wrong
        {
            "filename": "totally_wrong.txt",
            "content_type": "text/plain",
            "size": 0,
            "expected_valid": False
        },
    ]
    
    for test_file in test_files:
        filename = test_file["filename"]
        
        # Run all validations
        filename_valid, filename_error = validate_filename_pattern(filename)
        type_valid, type_error = validate_file_type(filename, test_file["content_type"])
        size_valid, size_error = validate_file_size(test_file["size"])
        
        # Overall validity
        overall_valid = filename_valid and type_valid and size_valid
        test_name = f"Combined validation: {filename}"
        
        if overall_valid == test_file["expected_valid"]:
            results.add_result(test_name, True)
        else:
            errors = []
            if not filename_valid:
                errors.append(filename_error)
            if not type_valid:
                errors.append(type_error)
            if not size_valid:
                errors.append(size_error)
            
            error_summary = "; ".join(errors) if errors else "Validation passed unexpectedly"
            results.add_result(test_name, False, error_summary)

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n🔍 Testing Edge Cases")
    print("-" * 40)
    
    # Test boundary file sizes
    boundary_sizes = [
        (10 * 1024 * 1024 - 1, True, "Just under 10MB"),
        (10 * 1024 * 1024, True, "Exactly 10MB"),
        (10 * 1024 * 1024 + 1, False, "Just over 10MB"),
    ]
    
    for size, expected_valid, description in boundary_sizes:
        is_valid, error_msg = validate_file_size(size)
        results.add_result(description, is_valid == expected_valid)
    
    # Test filename edge cases
    edge_filenames = [
        ("20250627_A_B_C.pdf", True, "Minimal valid filename"),
        ("20250627_A_B_C.PDF", True, "Uppercase extension"),
        ("20250627_123_456_789.pdf", True, "All numeric parts"),
        ("20250627__B_C.pdf", False, "Empty middle part"),
        ("20250627_A__C.pdf", False, "Empty vendor part"),
        ("20250627_A_B_.pdf", False, "Empty type part"),
    ]
    
    for filename, expected_valid, description in edge_filenames:
        is_valid, error_msg = validate_filename_pattern(filename)
        results.add_result(description, is_valid == expected_valid)

def run_standalone_validation_tests():
    """Run all standalone validation tests"""
    print("🧪 OCR Invoice Processor - Standalone Validation Tests")
    print("=" * 60)
    print("Testing upload validation logic without backend dependencies")
    print()
    
    # Run all test categories
    test_filename_validation()
    test_file_type_validation()
    test_file_size_validation()
    test_combined_validation()
    test_edge_cases()
    
    # Print summary
    results.summary()
    
    # Additional info
    print(f"\nTest Details:")
    print(f"• Filename pattern: YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf")
    print(f"• Allowed file type: application/pdf only")
    print(f"• Max file size: 10MB")
    print(f"• Validation rules consistent across all upload sources")
    
    # Return success status
    return results.failed == 0

if __name__ == "__main__":
    success = run_standalone_validation_tests()
    sys.exit(0 if success else 1)
