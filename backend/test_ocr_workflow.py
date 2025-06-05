#!/usr/bin/env python3
"""
Direct OCR Workflow Test
Tests the OCR workflow directly with a test invoice file
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import OCR components
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

async def test_ocr_with_file(file_path: str):
    """Test OCR processing with a specific file"""
    print(f"🔍 Testing OCR workflow with file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        return False
    
    try:
        # Read the file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Determine MIME type based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        mime_type_map = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        
        mime_type = mime_type_map.get(file_ext, 'application/pdf')
        filename = os.path.basename(file_path)
        
        print(f"   File size: {len(file_content)} bytes")
        print(f"   MIME type: {mime_type}")
        print(f"   OCR enabled: {ocr_config.enable_ocr}")
        print(f"   Mock OCR: {ocr_config.use_mock_ocr}")
        
        # Process the document
        result = await ocr_workflow.process_document(
            file_content=file_content,
            mime_type=mime_type,
            filename=filename,
            document_type="invoice"
        )
        
        print(f"\n✅ OCR processing completed!")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Mock mode: {result.get('mock_mode', False)}")
        print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        
        if result.get('structured_data'):
            structured = result['structured_data']
            print(f"\n📊 Extracted Invoice Data:")
            print(f"   Invoice Number: {structured.get('invoice_number', 'N/A')}")
            print(f"   Date: {structured.get('date', 'N/A')}")
            print(f"   Total Amount: {structured.get('total_amount', 'N/A')}")
            print(f"   Vendor: {structured.get('vendor_name', 'N/A')}")
            print(f"   Currency: {structured.get('currency', 'N/A')}")
        
        if result.get('raw_text'):
            print(f"\n📄 Raw Text (first 200 chars):")
            print(f"   {result['raw_text'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_ocr_status():
    """Test OCR status functionality"""
    print("🔍 Testing OCR status...")
    
    try:
        status = ocr_workflow.get_ocr_status()
        print(f"✅ OCR Status retrieved successfully:")
        print(f"   OCR Enabled: {status.get('ocr_enabled', False)}")
        print(f"   Service Available: {status.get('service_available', False)}")
        print(f"   Processor: {status.get('processor_name', 'N/A')}")
        print(f"   Supported formats: {', '.join(status.get('supported_formats', []))}")
        return True
    except Exception as e:
        print(f"❌ OCR status check failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting OCR Workflow Test\n")
    
    # Test OCR status
    await test_ocr_status()
    print()
    
    # Test with available invoice files
    test_files = [
        "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend/test_invoice.pdf",
        "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/test_invoice_1748551760.pdf",
        "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/20250605_TEST001_TESTVENDOR_SERVICE.pdf"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = await test_ocr_with_file(test_file)
            if success:
                print(f"\n🎉 Successfully tested OCR with {os.path.basename(test_file)}")
                break
            else:
                print(f"\n⚠️  Failed to test OCR with {os.path.basename(test_file)}")
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print("\n✨ OCR workflow test completed!")

if __name__ == "__main__":
    asyncio.run(main())
