#!/usr/bin/env python3
"""
Test script for enhanced duplicate checking and filename validation 
in the folder watcher system.
"""
import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.folder_watcher import FolderWatcherService
from services.upload_service import UploadService, FileData, UploadSource
from services.database import DatabaseService

async def test_duplicate_checking():
    """Test duplicate checking and filename validation"""
    print("🧪 Testing Enhanced Duplicate Checking and Filename Validation")
    print("=" * 70)
    
    # Initialize services
    folder_watcher = FolderWatcherService()
    upload_service = UploadService()
    db_service = DatabaseService()
    
    print(f"📊 Database available: {db_service.is_available}")
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_folder = Path(temp_dir) / "test_invoices"
        test_folder.mkdir()
        
        print(f"📁 Created test folder: {test_folder}")
        
        # Test cases
        test_files = [
            # Valid filenames
            ("20250704_OMEGA_ELEKTRO_Mueller.pdf", "Valid filename"),
            ("20250705_ALPHA_SANITAER_Schmidt.pdf", "Valid filename"),
            ("20250706_BETA_HEIZUNG_Wagner.pdf", "Valid filename"),
            
            # Invalid filenames
            ("invoice.pdf", "Invalid - no pattern"),
            ("2025070_OMEGA_ELEKTRO_Mueller.pdf", "Invalid - wrong date format"),
            ("20250704_OMEGA_ELEKTRO.pdf", "Invalid - missing lieferant"),
            ("20250704__ELEKTRO_Mueller.pdf", "Invalid - empty projekt"),
            ("20250704_OMEGA__Mueller.pdf", "Invalid - empty gewerk"),
            ("20250704_OMEGA_ELEKTRO_.pdf", "Invalid - empty lieferant"),
            
            # Duplicate test (same as first file)
            ("20250704_OMEGA_ELEKTRO_Mueller.pdf", "Duplicate test"),
            
            # Similar content test
            ("20250707_OMEGA_ELEKTRO_Mueller_GmbH.pdf", "Similar content"),
        ]
        
        # Create test files with dummy PDF content
        dummy_pdf_content = b"""%PDF-1.4
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
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
189
%%EOF"""
        
        print("\n🔍 Testing Filename Validation and Duplicate Detection:")
        print("-" * 50)
        
        processed_files = set()
        
        for filename, description in test_files:
            print(f"\n📄 Testing: {filename}")
            print(f"   Description: {description}")
            
            # Create test file
            test_file_path = test_folder / filename
            with open(test_file_path, 'wb') as f:
                f.write(dummy_pdf_content)
            
            # Create FileData object
            file_data = FileData(
                content=dummy_pdf_content,
                filename=filename,
                content_type="application/pdf",
                file_size=len(dummy_pdf_content),
                source=UploadSource.FOLDER_WATCHER,
                source_metadata={
                    "folder_path": str(test_folder),
                    "original_path": str(test_file_path),
                    "test": True
                }
            )
            
            # Test validation
            is_valid, error_message = upload_service.validate_file(file_data)
            
            if is_valid:
                print(f"   ✅ Validation: PASSED")
                
                # For the first valid file, simulate upload to create a "duplicate"
                if filename not in processed_files:
                    processed_files.add(filename)
                    print(f"   📤 Simulating first upload...")
                    
                    # Note: In a real test, we would actually upload to database
                    # For this test, we're just checking the validation logic
                else:
                    print(f"   🔄 This should be detected as duplicate on next validation")
            else:
                print(f"   ❌ Validation: FAILED")
                print(f"   💬 Error: {error_message}")
        
        print(f"\n📊 Test Summary:")
        print(f"   Test folder: {test_folder}")
        print(f"   Files created: {len(test_files)}")
        print(f"   Validation tests completed")
        
        # Test folder watcher integration
        print(f"\n🔍 Testing Folder Watcher Integration:")
        print("-" * 50)
        
        try:
            # Add watch folder (this should work)
            success, config_id, error = await folder_watcher.add_watch_folder(
                str(test_folder), 
                pattern="*.pdf",
                enabled=True
            )
            
            if success:
                print(f"   ✅ Watch folder added successfully")
                print(f"   📋 Config ID: {config_id}")
                
                # Test scanning existing files
                scan_result = await folder_watcher.scan_existing_files(config_id)
                print(f"   📊 Scan result: {scan_result}")
                
                # Clean up
                await folder_watcher.remove_watch_folder(config_id)
                print(f"   🧹 Watch folder removed")
                
            else:
                print(f"   ❌ Failed to add watch folder: {error}")
                
        except Exception as e:
            print(f"   💥 Error testing folder watcher: {str(e)}")
    
    print(f"\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_duplicate_checking())
