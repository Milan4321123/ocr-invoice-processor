#!/usr/bin/env python3
"""
Test script to verify unified validation between drag-and-drop and folder watcher
"""
import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Test imports
from services.upload_service import upload_service, FileData, UploadSource

async def test_validation():
    """Test various file validation scenarios"""
    
    print("🧪 Testing Unified Validation Rules")
    print("=" * 50)
    
    # Test cases: (filename, expected_valid, error_contains)
    test_cases = [
        # Valid files
        ("20250627_INV001_ACME_SERVICE.pdf", True, None),
        ("20240101_A1B2C3_TEST_INVOICE.pdf", True, None),
        
        # Invalid filename patterns
        ("invalid_filename.pdf", False, "Dateiname muss dem Muster folgen"),
        ("20250627_INV001_ACME.pdf", False, "Dateiname muss dem Muster folgen"),  # Missing TYPE
        ("2025627_INV001_ACME_SERVICE.pdf", False, "Dateiname muss dem Muster folgen"),  # Wrong date format
        ("20250627INV001_ACME_SERVICE.pdf", False, "Dateiname muss dem Muster folgen"),  # Missing underscore
        
        # Wrong file type
        ("20250627_INV001_ACME_SERVICE.txt", False, "Nur PDF-Dateien sind erlaubt"),
        ("20250627_INV001_ACME_SERVICE.doc", False, "Nur PDF-Dateien sind erlaubt"),
    ]
    
    for filename, expected_valid, error_contains in test_cases:
        print(f"\n📄 Testing: {filename}")
        
        # Test both drag-drop and folder watcher sources
        for source in [UploadSource.DRAG_DROP, UploadSource.FOLDER_WATCHER]:
            print(f"  Source: {source.value}")
            
            # Create test file data
            content_type = "application/pdf" if filename.endswith(".pdf") else "text/plain"
            file_data = FileData(
                content=b"fake pdf content",
                filename=filename,
                content_type=content_type,
                file_size=100,
                source=source
            )
            
            # Test validation
            is_valid, error_message = upload_service.validate_file(file_data)
            
            # Check results
            if is_valid == expected_valid:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            print(f"    {status} - Valid: {is_valid}, Error: {error_message}")
            
            # Check error message if expected
            if not expected_valid and error_contains:
                if error_message and error_contains in error_message:
                    print(f"    ✅ Error message correct")
                else:
                    print(f"    ❌ Error message incorrect. Expected: '{error_contains}', Got: '{error_message}'")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_validation())
