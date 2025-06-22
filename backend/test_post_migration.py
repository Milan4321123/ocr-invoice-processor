#!/usr/bin/env python3
"""
Post-migration test script to verify folder watcher integration works
Run this AFTER executing the database migration in Supabase
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_post_migration():
    """Test folder watcher upload after database migration"""
    print("🔍 POST-MIGRATION TEST: Folder Watcher Integration")
    print("=" * 60)
    
    try:
        from services.upload_service import upload_service, FileData, UploadSource
        from services.database import db_service
        
        print("✅ Imports successful")
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
            filename="post-migration-test.pdf",
            content_type="application/pdf",
            file_size=len(test_content),
            source=UploadSource.FOLDER_WATCHER,
            source_metadata={
                "folder_path": "/tmp/invoice-test-folder",
                "original_path": "/tmp/invoice-test-folder/post-migration-test.pdf",
                "detected_at": "2025-06-23 23:45:00",
                "watch_config_id": "post-migration-test"
            }
        )
        
        print(f"📄 Test file: {file_data.filename}")
        print(f"📦 File size: {file_data.file_size} bytes")
        print(f"🔗 Source: {file_data.source.value}")
        print("🚀 Testing upload service...")
        
        # Test upload
        result = await upload_service.upload_file(file_data)
        
        print(f"✅ Upload success: {result.success}")
        if result.success:
            print(f"✅ Invoice ID: {result.invoice_id}")
            print(f"✅ URL: {result.url}")
            print(f"✅ Filename: {result.filename}")
            print(f"✅ Storage path: {result.storage_path}")
            
            # Test database fetch
            print("\n🔍 Testing database retrieval...")
            invoice_result = db_service.get_invoice(result.invoice_id)
            if invoice_result.get("success"):
                invoice_data = invoice_result.get("data")
                print(f"✅ Database record found")
                print(f"   - ID: {invoice_data.get('id')}")
                print(f"   - Filename: {invoice_data.get('filename')}")
                print(f"   - Source Type: {invoice_data.get('source_type')}")
                print(f"   - OCR Status: {invoice_data.get('ocr_status')}")
                print(f"   - Status: {invoice_data.get('status')}")
                print(f"   - URL: {invoice_data.get('url')}")
                
                # Test invoices list endpoint
                print("\n🔍 Testing invoices list...")
                invoices_result = db_service.get_invoices(limit=5)
                if invoices_result.get("success"):
                    invoices = invoices_result.get("data", [])
                    print(f"✅ Found {len(invoices)} invoices in database")
                    
                    # Look for our test file
                    test_invoice = next((inv for inv in invoices if inv.get('filename') == file_data.filename), None)
                    if test_invoice:
                        print(f"✅ Test invoice found in list!")
                        print(f"   - Listed in dashboard: YES")
                        print(f"   - Source type: {test_invoice.get('source_type')}")
                    else:
                        print(f"❌ Test invoice NOT found in list")
                else:
                    print(f"❌ Failed to fetch invoices list: {invoices_result.get('error')}")
            else:
                print(f"❌ Failed to fetch invoice: {invoice_result.get('error')}")
        else:
            print(f"❌ Upload failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_post_migration())
