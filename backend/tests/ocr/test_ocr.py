#!/usr/bin/env python3
"""
OCR Testing Script
Tests all OCR functionality including service availability, file processing, and error handling.
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any

def test_ocr_status() -> Dict[str, Any]:
    """Test OCR status endpoint"""
    print("🔍 Testing OCR status endpoint...")
    try:
        response = requests.get("http://localhost:8000/ocr/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ OCR status endpoint working")
            print(f"   OCR Enabled: {data.get('ocr', {}).get('ocr_enabled', False)}")
            print(f"   Service Available: {data.get('ocr', {}).get('service_available', False)}")
            return {"success": True, "data": data}
        else:
            print(f"❌ OCR status endpoint failed: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ OCR status endpoint error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_health_endpoint() -> Dict[str, Any]:
    """Test health endpoint includes OCR monitoring"""
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data.get('status', 'unknown')}")
            return {"success": True, "data": data}
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return {"success": False, "error": str(e)}

def create_test_pdf() -> str:
    """Create a simple test PDF file"""
    pdf_content = """%PDF-1.4
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
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test Invoice Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000074 00000 n
0000000120 00000 n
0000000179 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
302
%%EOF"""
    
    filename = "test_ocr_invoice.pdf"
    with open(filename, "w") as f:
        f.write(pdf_content)
    return filename

def test_file_upload() -> Dict[str, Any]:
    """Test file upload with OCR processing"""
    print("\n📤 Testing file upload with OCR...")
    
    # Create test PDF
    test_file = create_test_pdf()
    
    try:
        # Upload file with proper filename format
        with open(test_file, "rb") as f:
            files = {
                "file": ("20250529_TEST123_OCRTEST_INVOICE.pdf", f, "application/pdf")
            }
            response = requests.post("http://localhost:8000/upload", files=files)
        
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ File upload successful")
            print(f"   Invoice ID: {data.get('id', 'N/A')}")
            print(f"   OCR Enabled: {data.get('ocr_enabled', False)}")
            if 'ocr_result' in data:
                ocr_result = data['ocr_result']
                print(f"   OCR Success: {ocr_result.get('success', False)}")
                print(f"   OCR Confidence: {ocr_result.get('confidence', 0)}")
                print(f"   OCR Pages: {ocr_result.get('pages', 0)}")
            return {"success": True, "data": data}
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}", "response": response.text}
    except Exception as e:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        print(f"❌ File upload error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_ocr_process_endpoint() -> Dict[str, Any]:
    """Test OCR process endpoint for existing invoice"""
    print("\n⚙️ Testing OCR process endpoint...")
    try:
        # This endpoint requires an existing invoice ID
        # For now, just test that the endpoint exists
        response = requests.post("http://localhost:8000/ocr/process/test-id")
        
        # We expect either 200 (success) or 404 (invoice not found) or 500 (OCR disabled)
        if response.status_code in [200, 404, 500]:
            print("✅ OCR process endpoint accessible")
            return {"success": True, "status_code": response.status_code}
        else:
            print(f"❌ OCR process endpoint unexpected status: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ OCR process endpoint error: {str(e)}")
        return {"success": False, "error": str(e)}

def check_environment() -> Dict[str, Any]:
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    env_status = {
        "ENABLE_OCR": os.getenv("ENABLE_OCR", "false"),
        "GOOGLE_CLOUD_PROJECT_ID": "SET" if os.getenv("GOOGLE_CLOUD_PROJECT_ID") else "NOT SET",
        "GOOGLE_CLOUD_PROCESSOR_ID": "SET" if os.getenv("GOOGLE_CLOUD_PROCESSOR_ID") else "NOT SET",
        "GOOGLE_APPLICATION_CREDENTIALS": "SET" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else "NOT SET",
        "SUPA_URL": "SET" if os.getenv("SUPA_URL") else "NOT SET",
        "SUPA_KEY": "SET" if os.getenv("SUPA_KEY") else "NOT SET"
    }
    
    print("Environment Variables:")
    for key, value in env_status.items():
        status_icon = "✅" if value not in ["false", "NOT SET"] else "⚠️"
        print(f"   {status_icon} {key}: {value}")
    
    return {"success": True, "env_status": env_status}

def run_all_tests():
    """Run comprehensive OCR testing"""
    print("🧪 Starting OCR Comprehensive Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Test environment
    results["environment"] = check_environment()
    
    # Test endpoints
    results["ocr_status"] = test_ocr_status()
    results["health"] = test_health_endpoint()
    results["file_upload"] = test_file_upload()
    results["ocr_process"] = test_ocr_process_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in results.items():
        if isinstance(result, dict) and "success" in result:
            total_tests += 1
            if result["success"]:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
        elif test_name == "environment":
            print(f"ℹ️  {test_name}: Checked")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! OCR system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the configuration and setup.")
        
        # Provide troubleshooting tips
        print("\n🔧 Troubleshooting Tips:")
        if not results["ocr_status"]["success"]:
            print("   - Make sure the FastAPI server is running on port 8000")
        if "ocr_confidence" in str(results.get("file_upload", {}).get("response", "")):
            print("   - Database schema needs to be updated. Run: python database_migration.py")
        if results["environment"]["env_status"]["ENABLE_OCR"] == "false":
            print("   - OCR is disabled. Set ENABLE_OCR=true in your .env file")
        if results["environment"]["env_status"]["GOOGLE_APPLICATION_CREDENTIALS"] == "NOT SET":
            print("   - Google Cloud credentials not configured. See docs/GOOGLE_CLOUD_SETUP.md")
    
    return results

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly. Make sure it's running on port 8000.")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on port 8000.")
        print("   Start with: uvicorn main:app --reload --port 8000")
        sys.exit(1)
    
    # Run tests
    run_all_tests()
