#!/usr/bin/env python3
"""
API-level test suite for upload functionality.
Tests all upload endpoints with various edge cases.
"""
import requests
import json
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any

class APITestResults:
    """Track API test results"""
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
        print(f"API TEST SUMMARY: {self.passed}/{self.total} passed ({self.failed} failed)")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  • {error}")
        print(f"{'='*60}")

# Global test results
results = APITestResults()

# API Configuration
API_BASE = os.getenv('API_URL', 'http://localhost:8000')
UPLOAD_ENDPOINT = f"{API_BASE}/api/upload"
FOLDER_WATCHER_ENDPOINT = f"{API_BASE}/api/folder-watcher"
INVOICES_ENDPOINT = f"{API_BASE}/api/invoices"

def create_test_pdf_content(size_bytes: int = 1000) -> bytes:
    """Create fake PDF content of specified size"""
    content = b"%PDF-1.4\n"
    padding = b"A" * (size_bytes - len(content) - 10)
    content += padding
    content += b"\n%%EOF\n"
    return content

def test_api_connectivity():
    """Test basic API connectivity"""
    print("\n🌐 Testing API Connectivity")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=10)
        results.add_result("API Health Check", response.status_code == 200)
    except Exception as e:
        results.add_result("API Health Check", False, str(e))
    
    try:
        response = requests.get(f"{FOLDER_WATCHER_ENDPOINT}/status", timeout=10)
        results.add_result("Folder Watcher Status", response.status_code == 200)
    except Exception as e:
        results.add_result("Folder Watcher Status", False, str(e))

def test_upload_valid_files():
    """Test uploading valid PDF files"""
    print("\n📤 Testing Valid File Uploads")
    print("-" * 40)
    
    test_files = [
        {
            "name": "Standard valid PDF",
            "filename": "20250627_TEST001_ACME_INVOICE.pdf",
            "content": create_test_pdf_content(1000)
        },
        {
            "name": "Large valid PDF (5MB)",
            "filename": "20250627_TEST002_LARGE_INVOICE.pdf", 
            "content": create_test_pdf_content(5 * 1024 * 1024)
        },
        {
            "name": "Valid PDF with numbers",
            "filename": "20240101_123ABC_TEST456_INVOICE99.pdf",
            "content": create_test_pdf_content(2000)
        }
    ]
    
    for test_file in test_files:
        try:
            files = {
                'file': (test_file['filename'], test_file['content'], 'application/pdf')
            }
            
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = 'id' in data and 'url' in data and data.get('status') == 'under_review'
                results.add_result(test_file['name'], success)
            else:
                results.add_result(test_file['name'], False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            results.add_result(test_file['name'], False, str(e))

def test_upload_invalid_files():
    """Test uploading invalid files"""
    print("\n🚫 Testing Invalid File Uploads")
    print("-" * 40)
    
    invalid_files = [
        {
            "name": "Invalid filename pattern",
            "filename": "invalid_filename.pdf",
            "content": create_test_pdf_content(1000),
            "expected_error": "Dateiname muss dem Muster folgen"
        },
        {
            "name": "Wrong file type (TXT)",
            "filename": "20250627_TEST003_ACME_INVOICE.txt",
            "content": b"This is text content",
            "expected_error": "Nur PDF-Dateien sind erlaubt"
        },
        {
            "name": "File too large (15MB)",
            "filename": "20250627_TEST004_HUGE_INVOICE.pdf",
            "content": create_test_pdf_content(15 * 1024 * 1024),
            "expected_error": "zu groß"
        },
        {
            "name": "Empty file",
            "filename": "20250627_TEST005_EMPTY_INVOICE.pdf",
            "content": b"",
            "expected_error": "leer"
        }
    ]
    
    for test_file in invalid_files:
        try:
            content_type = 'application/pdf' if test_file['filename'].endswith('.pdf') else 'text/plain'
            files = {
                'file': (test_file['filename'], test_file['content'], content_type)
            }
            
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
            
            if response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get('detail', '')
                has_expected_error = test_file['expected_error'].lower() in error_message.lower()
                results.add_result(test_file['name'], has_expected_error)
            else:
                results.add_result(test_file['name'], False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            results.add_result(test_file['name'], False, str(e))

def test_duplicate_uploads():
    """Test duplicate file upload detection"""
    print("\n📋 Testing Duplicate Upload Detection")
    print("-" * 40)
    
    # First upload
    filename = "20250627_DUP001_ACME_DUPLICATE.pdf"
    content = create_test_pdf_content(1000)
    
    try:
        files = {'file': (filename, content, 'application/pdf')}
        
        # First upload should succeed
        response1 = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
        if response1.status_code == 200:
            results.add_result("First duplicate test upload", True)
            
            # Second upload should fail
            response2 = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
            if response2.status_code == 400:
                error_data = response2.json()
                error_message = error_data.get('detail', '')
                has_duplicate_error = 'existiert bereits' in error_message or 'already exists' in error_message
                results.add_result("Duplicate detection", has_duplicate_error)
            else:
                results.add_result("Duplicate detection", False, f"Expected 400, got {response2.status_code}")
        else:
            results.add_result("First duplicate test upload", False, f"HTTP {response1.status_code}")
            
    except Exception as e:
        results.add_result("Duplicate upload test", False, str(e))

def test_folder_watcher_api():
    """Test folder watcher API endpoints"""
    print("\n👁 Testing Folder Watcher API")
    print("-" * 40)
    
    # Test status endpoint
    try:
        response = requests.get(f"{FOLDER_WATCHER_ENDPOINT}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            has_required_fields = all(field in data for field in ['status', 'folders_watched', 'statistics'])
            results.add_result("Folder watcher status", has_required_fields)
        else:
            results.add_result("Folder watcher status", False, f"HTTP {response.status_code}")
    except Exception as e:
        results.add_result("Folder watcher status", False, str(e))
    
    # Test folders endpoint
    try:
        response = requests.get(f"{FOLDER_WATCHER_ENDPOINT}/folders", timeout=10)
        if response.status_code == 200:
            data = response.json()
            is_list = isinstance(data, list)
            results.add_result("Folder watcher folders list", is_list)
        else:
            results.add_result("Folder watcher folders list", False, f"HTTP {response.status_code}")
    except Exception as e:
        results.add_result("Folder watcher folders list", False, str(e))
    
    # Test notifications endpoint
    try:
        response = requests.get(f"{FOLDER_WATCHER_ENDPOINT}/notifications", timeout=10)
        if response.status_code == 200:
            data = response.json()
            has_notifications = 'notifications' in data and isinstance(data['notifications'], list)
            results.add_result("Folder watcher notifications", has_notifications)
        else:
            results.add_result("Folder watcher notifications", False, f"HTTP {response.status_code}")
    except Exception as e:
        results.add_result("Folder watcher notifications", False, str(e))

def test_folder_watcher_operations():
    """Test folder watcher add/remove operations"""
    print("\n🗂 Testing Folder Watcher Operations")
    print("-" * 40)
    
    # Create temporary directory for testing
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test adding watch folder
        try:
            add_data = {
                "folder_path": temp_dir,
                "pattern": "*.pdf",
                "recursive": False,
                "enabled": True
            }
            
            response = requests.post(
                f"{FOLDER_WATCHER_ENDPOINT}/folders",
                json=add_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result_data = response.json()
                config_id = result_data.get('config_id')
                results.add_result("Add watch folder", config_id is not None)
                
                if config_id:
                    # Test removing the folder
                    remove_response = requests.delete(
                        f"{FOLDER_WATCHER_ENDPOINT}/folders/{config_id}",
                        timeout=10
                    )
                    results.add_result("Remove watch folder", remove_response.status_code == 200)
            else:
                results.add_result("Add watch folder", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            results.add_result("Folder watcher operations", False, str(e))

def test_invalid_folder_operations():
    """Test invalid folder watcher operations"""
    print("\n🚨 Testing Invalid Folder Operations")
    print("-" * 40)
    
    # Test adding non-existent folder
    try:
        add_data = {
            "folder_path": "/non/existent/path",
            "pattern": "*.pdf",
            "recursive": False,
            "enabled": True
        }
        
        response = requests.post(
            f"{FOLDER_WATCHER_ENDPOINT}/folders",
            json=add_data,
            timeout=10
        )
        
        results.add_result("Add non-existent folder", response.status_code == 400)
        
    except Exception as e:
        results.add_result("Add non-existent folder", False, str(e))
    
    # Test removing non-existent folder
    try:
        response = requests.delete(
            f"{FOLDER_WATCHER_ENDPOINT}/folders/non-existent-id",
            timeout=10
        )
        
        results.add_result("Remove non-existent folder", response.status_code == 404)
        
    except Exception as e:
        results.add_result("Remove non-existent folder", False, str(e))

def test_upload_response_format():
    """Test upload response format and data"""
    print("\n📄 Testing Upload Response Format")
    print("-" * 40)
    
    try:
        filename = "20250627_FORMAT_TEST_RESPONSE.pdf"
        content = create_test_pdf_content(1500)
        files = {'file': (filename, content, 'application/pdf')}
        
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['id', 'url', 'status', 'filename', 'file_size', 'message']
            has_all_fields = all(field in data for field in required_fields)
            results.add_result("Response has required fields", has_all_fields)
            
            # Check data types and values
            checks = [
                ("ID is string", isinstance(data.get('id'), str) and len(data.get('id')) > 0),
                ("URL is string", isinstance(data.get('url'), str) and data.get('url').startswith('http')),
                ("Status is under_review", data.get('status') == 'under_review'),
                ("Filename matches", data.get('filename') == filename),
                ("File size correct", data.get('file_size') == len(content)),
                ("Message present", isinstance(data.get('message'), str) and len(data.get('message')) > 0)
            ]
            
            for check_name, check_result in checks:
                results.add_result(check_name, check_result)
                
        else:
            results.add_result("Upload response format", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        results.add_result("Upload response format", False, str(e))

def test_concurrent_api_uploads():
    """Test concurrent API uploads"""
    print("\n🔄 Testing Concurrent API Uploads")
    print("-" * 40)
    
    import threading
    import queue
    
    results_queue = queue.Queue()
    
    def upload_worker(worker_id):
        """Worker function for concurrent uploads"""
        try:
            filename = f"20250627_CONC{worker_id:03d}_API_TEST.pdf"
            content = create_test_pdf_content(1000 + worker_id * 100)
            files = {'file': (filename, content, 'application/pdf')}
            
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
            results_queue.put((worker_id, response.status_code == 200, response.text))
            
        except Exception as e:
            results_queue.put((worker_id, False, str(e)))
    
    # Start multiple threads
    threads = []
    num_workers = 5
    
    for i in range(num_workers):
        thread = threading.Thread(target=upload_worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    # Collect results
    successful_uploads = 0
    failed_uploads = 0
    
    while not results_queue.empty():
        worker_id, success, message = results_queue.get()
        if success:
            successful_uploads += 1
        else:
            failed_uploads += 1
            print(f"    Worker {worker_id} failed: {message}")
    
    results.add_result(
        f"Concurrent uploads ({successful_uploads}/{num_workers})",
        successful_uploads >= num_workers - 1  # Allow 1 failure
    )

def test_api_error_handling():
    """Test API error handling"""
    print("\n⚠️ Testing API Error Handling")
    print("-" * 40)
    
    # Test missing file in upload
    try:
        response = requests.post(UPLOAD_ENDPOINT, files={}, timeout=10)
        results.add_result("Missing file error", response.status_code == 422)
    except Exception as e:
        results.add_result("Missing file error", False, str(e))
    
    # Test invalid JSON in folder watcher
    try:
        response = requests.post(
            f"{FOLDER_WATCHER_ENDPOINT}/folders",
            data="invalid json",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        results.add_result("Invalid JSON error", response.status_code == 422)
    except Exception as e:
        results.add_result("Invalid JSON error", False, str(e))
    
    # Test invalid endpoint
    try:
        response = requests.get(f"{API_BASE}/api/nonexistent", timeout=10)
        results.add_result("Invalid endpoint error", response.status_code == 404)
    except Exception as e:
        results.add_result("Invalid endpoint error", False, str(e))

def run_all_api_tests():
    """Run all API tests"""
    print("🚀 Starting Comprehensive API Upload Tests")
    print("=" * 60)
    print(f"Testing API at: {API_BASE}")
    print()
    
    # Run all test categories
    test_api_connectivity()
    test_upload_valid_files()
    test_upload_invalid_files()
    test_duplicate_uploads()
    test_folder_watcher_api()
    test_folder_watcher_operations()
    test_invalid_folder_operations()
    test_upload_response_format()
    test_concurrent_api_uploads()
    test_api_error_handling()
    
    # Print summary
    results.summary()
    
    # Return success status
    return results.failed == 0

if __name__ == "__main__":
    success = run_all_api_tests()
    exit(0 if success else 1)
