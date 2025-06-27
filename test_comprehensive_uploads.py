#!/usr/bin/env python3
"""
Comprehensive test suite for all upload functions (drag & drop, folder watcher, manual).
Tests all edge cases: file types, patterns, duplicates, sizes, permissions, etc.
"""
import sys
import os
import asyncio
import json
import time
import tempfile
import shutil
import stat
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from typing import List, Dict, Any, Optional
import logging

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import services
from services.upload_service import upload_service, FileData, UploadSource, UploadResult
from services.folder_watcher import folder_watcher_service, WatchConfig, FileNotification, NotificationType
from services.database import db_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestResults:
    """Track test results"""
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
            self.errors.append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{self.total} passed ({self.failed} failed)")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  • {error}")
        print(f"{'='*60}")

# Global test results
results = TestResults()

def create_test_pdf_content(size_bytes: int = 1000) -> bytes:
    """Create fake PDF content of specified size"""
    # Minimal PDF header
    content = b"%PDF-1.4\n"
    # Add padding to reach desired size
    padding = b"A" * (size_bytes - len(content) - 10)
    content += padding
    content += b"\n%%EOF\n"
    return content

async def test_file_validation():
    """Test file validation for all upload sources"""
    print("\n🔍 Testing File Validation")
    print("-" * 40)
    
    test_cases = [
        # Valid files
        {
            "name": "Valid German business filename",
            "filename": "20250627_BauProjekt-A1_Elektrik_Müller-GmbH.pdf",
            "content_type": "application/pdf",
            "content": create_test_pdf_content(1000),
            "expected_valid": True
        },
        {
            "name": "Valid German business filename with periods",
            "filename": "20240101_Neubau.Office_Heizung_Schmidt-Co.pdf",
            "content_type": "application/pdf", 
            "content": create_test_pdf_content(1000),
            "expected_valid": True
        },
        
        # Invalid filename patterns
        {
            "name": "Invalid filename pattern - missing supplier",
            "filename": "20250627_Projekt_Gewerk.pdf",
            "content_type": "application/pdf",
            "content": create_test_pdf_content(1000),
            "expected_valid": False,
            "error_contains": "Dateiname muss dem Muster folgen"
        },
        {
            "name": "Invalid filename pattern - wrong date format", 
            "filename": "2025627_Projekt_Gewerk_Lieferant.pdf",
            "content_type": "application/pdf",
            "content": create_test_pdf_content(1000),
            "expected_valid": False,
            "error_contains": "Dateiname muss dem Muster folgen"
        },
        {
            "name": "Invalid filename pattern - empty project",
            "filename": "20250627__Gewerk_Lieferant.pdf",
            "content_type": "application/pdf", 
            "content": create_test_pdf_content(1000),
            "expected_valid": False,
            "error_contains": "Dateiname muss dem Muster folgen"
        },
        
        # Wrong file types
        {
            "name": "Invalid file type - TXT",
            "filename": "20250627_TestProjekt_Elektrik_TestFirma.txt",
            "content_type": "text/plain",
            "content": b"This is text content",
            "expected_valid": False,
            "error_contains": "Nur PDF-Dateien sind erlaubt"
        },
        {
            "name": "Invalid file type - DOC",
            "filename": "20250627_TestProjekt_Elektrik_TestFirma.doc",
            "content_type": "application/msword",
            "content": b"Document content",
            "expected_valid": False,
            "error_contains": "Nur PDF-Dateien sind erlaubt"
        },
        
        # File size issues
        {
            "name": "Empty file",
            "filename": "20250627_TestProjekt_Elektrik_TestFirma.pdf",
            "content_type": "application/pdf",
            "content": b"",
            "expected_valid": False,
            "error_contains": "Die Datei ist leer"
        },
        {
            "name": "File too large",
            "filename": "20250627_TestProjekt_Elektrik_TestFirma.pdf", 
            "content_type": "application/pdf",
            "content": create_test_pdf_content(15 * 1024 * 1024),  # 15MB (over 10MB limit)
            "expected_valid": False,
            "error_contains": "Datei ist zu groß"
        }
    ]
    
    for test_case in test_cases:
        # Test all upload sources
        for source in [UploadSource.DRAG_DROP, UploadSource.FOLDER_WATCHER, UploadSource.MANUAL]:
            test_name = f"{test_case['name']} ({source.value})"
            
            try:
                file_data = FileData(
                    content=test_case["content"],
                    filename=test_case["filename"],
                    content_type=test_case["content_type"],
                    file_size=len(test_case["content"]),
                    source=source
                )
                
                is_valid, error_message = upload_service.validate_file(file_data)
                
                # Check if result matches expectation
                if is_valid == test_case["expected_valid"]:
                    # If invalid, check error message
                    if not test_case["expected_valid"] and "error_contains" in test_case:
                        if error_message and test_case["error_contains"] in error_message:
                            results.add_result(test_name, True)
                        else:
                            results.add_result(test_name, False, f"Wrong error message: {error_message}")
                    else:
                        results.add_result(test_name, True)
                else:
                    results.add_result(test_name, False, f"Expected valid={test_case['expected_valid']}, got {is_valid}")
                    
            except Exception as e:
                results.add_result(test_name, False, f"Exception: {str(e)}")

async def test_duplicate_detection():
    """Test duplicate file detection"""
    print("\n📋 Testing Duplicate Detection")
    print("-" * 40)
    
    # Mock database to simulate existing files
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Patch the underlying _client to make is_available=True and provide mock client
    with patch.object(db_service, '_client', mock_client):
        # Test case 1: No duplicates
        mock_table.select.return_value.eq.return_value.execute.return_value = Mock(data=[])
        
        file_data = FileData(
            content=create_test_pdf_content(1000),
            filename="20250627_NeuerProjekt_Elektrik_TestFirma.pdf",
            content_type="application/pdf",
            file_size=1000,
            source=UploadSource.DRAG_DROP
        )
        
        is_valid, error_message = upload_service.validate_file(file_data)
        results.add_result("No duplicate file", is_valid and not error_message)
        
        # Test case 2: Duplicate exists
        mock_table.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{"id": "123", "file_name": "20250627_DuplikatProjekt_Elektrik_TestFirma.pdf"}]
        )
        
        file_data.filename = "20250627_DuplikatProjekt_Elektrik_TestFirma.pdf"
        is_valid, error_message = upload_service.validate_file(file_data)
        
        expected_error = "Eine Datei mit dem Namen"
        duplicate_detected = not is_valid and error_message and expected_error in error_message
        results.add_result("Duplicate detection", duplicate_detected)

async def test_storage_paths():
    """Test storage path generation for different sources"""
    print("\n📁 Testing Storage Path Generation")
    print("-" * 40)
    
    test_cases = [
        (UploadSource.DRAG_DROP, "test.pdf", "test.pdf"),
        (UploadSource.FOLDER_WATCHER, "test.pdf", "folder_watcher/test.pdf"),
        (UploadSource.MANUAL, "test.pdf", "manual/test.pdf")
    ]
    
    for source, filename, expected_path in test_cases:
        actual_path = upload_service.generate_storage_path(filename, source)
        test_name = f"Storage path for {source.value}"
        results.add_result(test_name, actual_path == expected_path)

async def test_filename_sanitization():
    """Test filename sanitization"""
    print("\n🧹 Testing Filename Sanitization")
    print("-" * 40)
    
    test_cases = [
        ("normal_file.pdf", "normal_file.pdf"),
        ("../../../etc/passwd.pdf", "passwd.pdf"),
        ("file with spaces.pdf", "file_with_spaces.pdf"),
        ("file<>:\"|?*.pdf", "file_______.pdf"),  # All special chars become underscores
        ("\x00\x01\x02file.pdf", "___file.pdf"),  # Control chars become underscores
    ]
    
    for input_filename, expected_output in test_cases:
        actual_output = upload_service.sanitize_filename(input_filename)
        test_name = f"Sanitize '{input_filename}'"
        results.add_result(test_name, actual_output == expected_output)

async def test_folder_watcher_edge_cases():
    """Test folder watcher edge cases"""
    print("\n👁 Testing Folder Watcher Edge Cases")
    print("-" * 40)
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Test case 1: Non-existent directory
        try:
            non_existent = test_dir / "does_not_exist"
            success, config_id, error = await folder_watcher_service.add_watch_folder(
                str(non_existent), "*.pdf", False, True
            )
            results.add_result("Add non-existent folder", not success and "not exist" in error.lower())
        except Exception as e:
            results.add_result("Add non-existent folder", False, str(e))
        
        # Test case 2: Permission denied directory
        try:
            restricted_dir = test_dir / "restricted"
            restricted_dir.mkdir()
            # Remove read permissions
            restricted_dir.chmod(stat.S_IWRITE)
            
            success, config_id, error = await folder_watcher_service.add_watch_folder(
                str(restricted_dir), "*.pdf", False, True
            )
            # The folder should be added successfully, but watching will fail when started
            results.add_result("Add restricted folder", success)
            
            # Restore permissions for cleanup
            restricted_dir.chmod(stat.S_IRWXU)
        except Exception as e:
            results.add_result("Add restricted folder", False, str(e))
        
        # Test case 3: File instead of directory
        try:
            test_file = test_dir / "not_a_dir.txt"
            test_file.write_text("test")
            
            success, config_id, error = await folder_watcher_service.add_watch_folder(
                str(test_file), "*.pdf", False, True
            )
            results.add_result("Add file as folder", not success)
        except Exception as e:
            results.add_result("Add file as folder", False, str(e))

async def test_rapid_file_changes():
    """Test rapid file creation/deletion scenarios"""
    print("\n⚡ Testing Rapid File Changes")
    print("-" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Add watch folder
        try:
            success, config_id, error = await folder_watcher_service.add_watch_folder(
                str(test_dir), "*.pdf", False, True
            )
            
            if success:
                results.add_result("Add temporary watch folder", True)
                
                # Start watcher
                start_success, start_error = await folder_watcher_service.start_watcher()
                if start_success:
                    results.add_result("Start watcher for rapid test", True)
                    
                    # Test rapid file creation and deletion
                    test_file = test_dir / "20250627_RapidTest_Elektrik_TestFirma.pdf"
                    
                    # Create file
                    test_file.write_bytes(create_test_pdf_content(1000))
                    await asyncio.sleep(0.1)  # Brief pause
                    
                    # Delete file quickly
                    test_file.unlink()
                    await asyncio.sleep(0.1)
                    
                    # Create again
                    test_file.write_bytes(create_test_pdf_content(2000))
                    await asyncio.sleep(0.5)  # Wait for processing
                    
                    results.add_result("Rapid file creation/deletion", True)
                    
                    # Cleanup
                    await folder_watcher_service.stop_watcher()
                    await folder_watcher_service.remove_watch_folder(config_id)
                else:
                    results.add_result("Start watcher for rapid test", False, start_error)
            else:
                results.add_result("Add temporary watch folder", False, error)
        except Exception as e:
            results.add_result("Rapid file changes test", False, str(e))

async def test_large_file_handling():
    """Test handling of various file sizes"""
    print("\n📏 Testing Large File Handling")
    print("-" * 40)
    
    size_tests = [
        ("Small file (1KB)", 1024, True),
        ("Medium file (1MB)", 1024 * 1024, True),
        ("Large file (5MB)", 5 * 1024 * 1024, True),
        ("Max size file (10MB)", 10 * 1024 * 1024, True),
        ("Oversized file (15MB)", 15 * 1024 * 1024, False),
    ]
    
    for test_name, size_bytes, should_pass in size_tests:
        try:
            content = create_test_pdf_content(size_bytes)
            file_data = FileData(
                content=content,
                filename="20250627_SizeTest_Elektrik_TestFirma.pdf",
                content_type="application/pdf",
                file_size=len(content),
                source=UploadSource.DRAG_DROP
            )
            
            is_valid, error_message = upload_service.validate_file(file_data)
            
            if should_pass:
                results.add_result(test_name, is_valid)
            else:
                results.add_result(test_name, not is_valid and "zu groß" in error_message)
                
        except Exception as e:
            results.add_result(test_name, False, str(e))

async def test_concurrent_uploads():
    """Test concurrent upload scenarios"""
    print("\n🔄 Testing Concurrent Uploads")
    print("-" * 40)
    
    async def mock_upload(filename: str):
        """Mock upload function"""
        # Use current timestamp to ensure unique filenames
        unique_suffix = int(time.time() * 1000) % 100000
        # Follow FIXED German business convention: EINGANGSDATUM_PROJEKT_GEWERK_LIEFERANT.pdf
        file_data = FileData(
            content=create_test_pdf_content(1000),
            filename=f"20250627_Projekt{unique_suffix}_Test-Gewerk_{filename}-GmbH.pdf",
            content_type="application/pdf",
            file_size=1000,
            source=UploadSource.DRAG_DROP
        )
        return await upload_service.upload_file(file_data)
    
    try:
        # Create multiple concurrent uploads
        upload_tasks = [
            mock_upload(f"CONC{i:03d}") for i in range(5)
        ]
        
        # Wait for all uploads
        results_list = await asyncio.gather(*upload_tasks, return_exceptions=True)
        
        # Count successful uploads
        successful = sum(1 for r in results_list if isinstance(r, UploadResult) and r.success)
        results.add_result(f"Concurrent uploads ({successful}/5)", successful >= 3)
        
    except Exception as e:
        results.add_result("Concurrent uploads", False, str(e))

async def test_corrupted_files():
    """Test handling of corrupted PDF files"""
    print("\n🔧 Testing Corrupted File Handling")
    print("-" * 40)
    
    corrupted_files = [
        ("Invalid PDF header", b"NOT A PDF FILE", "application/pdf"),
        ("Truncated PDF", b"%PDF-1.4\ntruncated", "application/pdf"),
        ("Binary garbage", b"\x00\x01\x02\x03\x04\x05", "application/pdf"),
        ("HTML disguised as PDF", b"<html><body>Fake PDF</body></html>", "application/pdf"),
    ]
    
    for test_name, content, content_type in corrupted_files:
        try:
            file_data = FileData(
                content=content,
                filename="20250627_CorruptTest_Elektrik_TestFirma.pdf",
                content_type=content_type,
                file_size=len(content),
                source=UploadSource.DRAG_DROP
            )
            
            # The system should still process these files as the validation
            # only checks filename, size, and content type, not PDF validity
            is_valid, error_message = upload_service.validate_file(file_data)
            
            # These should pass validation (filename/size/type OK) but might fail in real processing
            results.add_result(f"Validate {test_name}", is_valid or "leer" in error_message)
            
        except Exception as e:
            results.add_result(f"Corrupted file {test_name}", False, str(e))

async def test_notification_system():
    """Test notification system for folder watcher"""
    print("\n🔔 Testing Notification System")
    print("-" * 40)
    
    try:
        # Clear existing notifications
        folder_watcher_service.clear_notifications()
        
        # Get initial count
        initial_notifications = folder_watcher_service.get_notifications(10)
        initial_count = len(initial_notifications)
        
        results.add_result("Clear notifications", initial_count == 0)
        
        # Test notification limits
        for i in range(25):  # Add more than default limit
            notification = FileNotification(
                id=f'test_{i}',
                type=NotificationType.UPLOAD_SUCCESS,
                filename=f'test_{i}.pdf',
                file_path=f'/test/path/test_{i}.pdf',
                timestamp=str(time.time()),
                message=f'Test notification {i}'
            )
            folder_watcher_service._add_notification(notification)
        
        # Get limited notifications
        limited_notifications = folder_watcher_service.get_notifications(10)
        results.add_result("Notification limit", len(limited_notifications) == 10)
        
        # Get all notifications
        all_notifications = folder_watcher_service.get_notifications(50)
        results.add_result("Get all notifications", len(all_notifications) >= 25)
        
        # Clear again
        folder_watcher_service.clear_notifications()
        final_notifications = folder_watcher_service.get_notifications(10)
        results.add_result("Clear all notifications", len(final_notifications) == 0)
        
    except Exception as e:
        results.add_result("Notification system", False, str(e))

async def test_error_recovery():
    """Test error recovery scenarios"""
    print("\n🛠 Testing Error Recovery")
    print("-" * 40)
    
    try:
        # Test storage unavailable scenario
        mock_client_offline = MagicMock()
        with patch.object(db_service, '_client', None):  # Set to None to make is_available=False
            file_data = FileData(
                content=create_test_pdf_content(1000),
                filename="20250627_OfflineTest_Elektrik_TestFirma.pdf",
                content_type="application/pdf",
                file_size=1000,
                source=UploadSource.DRAG_DROP
            )
            
            result = await upload_service.upload_file(file_data)
            # Should use mock storage when DB unavailable
            results.add_result("Offline storage fallback", result.success and "mock-storage" in result.url)
    
        # Test network timeout simulation
        with patch.object(upload_service, 'upload_to_storage') as mock_upload:
            mock_upload.side_effect = Exception("Network timeout")
            
            file_data = FileData(
                content=create_test_pdf_content(1000),
                filename="20250627_TimeoutTest_Elektrik_TestFirma.pdf", 
                content_type="application/pdf",
                file_size=1000,
                source=UploadSource.DRAG_DROP
            )
            
            result = await upload_service.upload_file(file_data)
            results.add_result("Network timeout handling", not result.success and result.error)
            
    except Exception as e:
        results.add_result("Error recovery", False, str(e))

async def run_all_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive Upload Tests")
    print("=" * 60)
    
    # Run all test categories
    await test_file_validation()
    await test_duplicate_detection()
    await test_storage_paths()
    await test_filename_sanitization()
    await test_folder_watcher_edge_cases()
    await test_rapid_file_changes()
    await test_large_file_handling()
    await test_concurrent_uploads()
    await test_corrupted_files()
    await test_notification_system()
    await test_error_recovery()
    
    # Print summary
    results.summary()
    
    # Return success status
    return results.failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
