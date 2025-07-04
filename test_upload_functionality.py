#!/usr/bin/env python3
"""
Test upload functionality specifically
"""

import requests
import json
import io
from datetime import datetime

BACKEND_URL = "https://ocr-invoice-processor.onrender.com"

def test_upload_functionality():
    """Test file upload endpoint"""
    
    # First authenticate
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BACKEND_URL}/api/auth/token", json=login_data)
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return
        
    token = response.json().get("access_token")
    print(f"✅ Authenticated successfully")
    
    # Create a mock PDF content
    mock_pdf_content = b"""%PDF-1.4
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
100 700 Td
(Test Invoice) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000189 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
285
%%EOF"""
    
    # Prepare file for upload
    files = {
        'file': ('test_invoice.pdf', io.BytesIO(mock_pdf_content), 'application/pdf')
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        print("📤 Testing file upload...")
        response = requests.post(f"{BACKEND_URL}/api/upload", files=files, headers=headers, timeout=30)
        
        print(f"Upload Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"📄 File details: {json.dumps(result, indent=2)}")
            
            # Test retrieving the uploaded invoice
            invoice_id = result.get('id')
            if invoice_id:
                print(f"\n🔍 Testing invoice retrieval...")
                response = requests.get(f"{BACKEND_URL}/api/invoices/{invoice_id}", headers=headers)
                if response.status_code == 200:
                    print(f"✅ Invoice retrieval successful!")
                    invoice_data = response.json()
                    print(f"📋 Invoice status: {invoice_data.get('status')}")
                    print(f"📁 File URL: {invoice_data.get('url')}")
                else:
                    print(f"❌ Invoice retrieval failed: {response.status_code}")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload test error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Upload Functionality")
    print("=" * 40)
    test_upload_functionality()
