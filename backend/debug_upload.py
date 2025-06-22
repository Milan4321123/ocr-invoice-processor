#!/usr/bin/env python3
"""
Debug script to test folder watcher upload integration
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_upload_service():
    """Test the upload service directly"""
    print("🔍 DEBUGGING: Folder Watcher Upload Integration")
    print("=" * 60)
    
    try:
        from services.upload_service import upload_service, FileData, UploadSource
        from services.database import db_service
        
        print("✅ Import successful")
        print(f"✅ Database available: {db_service.is_available}")
        
        # Create a test file
        test_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref 0 4
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000120 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref 180
%%EOF"""
        
        # Create FileData object as folder watcher would
        file_data = FileData(
            content=test_content,
            filename="debug-test.pdf",
            content_type="application/pdf",
            file_size=len(test_content),
            source=UploadSource.FOLDER_WATCHER,
            source_metadata={
                "folder_path": "/tmp/invoice-test-folder",
                "original_path": "/tmp/invoice-test-folder/debug-test.pdf",
                "detected_at": "2025-06-22 23:40:00",
                "watch_config_id": "debug-test"
            }
        )
        
        print(f"📄 Test file created: {file_data.filename}")
        print(f"📦 File size: {file_data.file_size} bytes")
        print(f"🔗 Source: {file_data.source.value}")
        
        # Test upload
        print("\n🚀 Testing upload service...")
        result = await upload_service.upload_file(file_data)
        
        print(f"✅ Upload result: {result.success}")
        
        if result.success:
            print(f"✅ Invoice ID: {result.invoice_id}")
            print(f"✅ URL: {result.url}")
            print(f"✅ Message: {result.message}")
        else:
            print(f"❌ Error: {result.error}")
            return False
        
        # Check if invoice appears in database
        print("\n📊 Checking database...")
        
        # Get recent invoices
        import requests
        try:
            response = requests.get("http://localhost:8001/invoices")
            if response.ok:
                data = response.json()
                invoices = data.get('invoices', [])
                print(f"✅ Total invoices in database: {len(invoices)}")
                
                # Check if our test invoice is there
                test_invoice = None
                for inv in invoices:
                    if inv['filename'] == 'debug-test.pdf':
                        test_invoice = inv
                        break
                
                if test_invoice:
                    print(f"✅ Test invoice found in database!")
                    print(f"   ID: {test_invoice['id']}")
                    print(f"   Created: {test_invoice['created_at']}")
                else:
                    print(f"❌ Test invoice NOT found in database")
                    print("   Recent invoices:")
                    for i, inv in enumerate(invoices[:3]):
                        print(f"   {i+1}. {inv['filename']}")
            else:
                print(f"❌ Failed to get invoices: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error checking database: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_upload_service()
    if success:
        print("\n🎉 Upload service test completed!")
    else:
        print("\n❌ Upload service test failed!")

if __name__ == "__main__":
    asyncio.run(main())
