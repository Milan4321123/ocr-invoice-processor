#!/usr/bin/env python3
"""
Test script for real Google Document AI OCR functionality
"""

import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_ocr_status():
    """Test OCR status endpoint"""
    print("🔍 Testing OCR status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/ocr/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OCR Status: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ OCR status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OCR status error: {e}")
        return False

def test_health_check():
    """Test system health endpoint"""
    print("\n🔍 Testing system health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Health: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_invoice():
    """Test invoice upload with real OCR processing"""
    print("\n🔍 Testing invoice upload with real OCR...")
    
    # Find test invoice file
    test_files = [
        "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/20250529_INV001_TESTVENDOR_SERVICE.pdf",
        "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend/test_invoice.pdf"
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ No test invoice file found")
        return False
    
    print(f"📄 Using test file: {test_file}")
    
    try:
        # Upload invoice
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/pdf')}
            data = {
                'vendor_name': 'Test Vendor',
                'invoice_number': 'TEST-001',
                'amount': '100.00'
            }
            
            print("⬆️ Uploading invoice...")
            response = requests.post(f"{BASE_URL}/invoices/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful: {json.dumps(result, indent=2)}")
                
                # Get the invoice ID
                invoice_id = result.get('invoice_id')
                if invoice_id:
                    # Test getting OCR data
                    print(f"\n🔍 Getting OCR data for invoice {invoice_id}...")
                    ocr_response = requests.get(f"{BASE_URL}/invoices/{invoice_id}/ocr")
                    
                    if ocr_response.status_code == 200:
                        ocr_data = ocr_response.json()
                        print(f"✅ OCR Data: {json.dumps(ocr_data, indent=2)}")
                        return True
                    else:
                        print(f"❌ OCR data retrieval failed: {ocr_response.status_code}")
                        return False
                else:
                    print("❌ No invoice ID returned")
                    return False
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def main():
    """Run all OCR tests"""
    print("🚀 Starting Real OCR Functionality Tests\n")
    
    # Test OCR status
    status_ok = test_ocr_status()
    
    # Test health check
    health_ok = test_health_check()
    
    # Test upload with OCR
    upload_ok = test_upload_invoice()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"   OCR Status: {'✅ PASS' if status_ok else '❌ FAIL'}")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Upload + OCR: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if all([status_ok, health_ok, upload_ok]):
        print("\n🎉 All tests PASSED! Real OCR is working correctly!")
        return True
    else:
        print("\n⚠️  Some tests FAILED. Check the logs above.")
        return False

if __name__ == "__main__":
    main()
