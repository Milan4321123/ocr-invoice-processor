#!/usr/bin/env python3
"""
Test script to verify upload functionality and OCR data mapping
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from services.upload_service import UploadService, FileData, UploadSource
from services.database import db_service
import json

def test_upload_with_mock_ocr():
    """Test upload with mock OCR data to verify field mapping"""
    
    # Create mock PDF content
    mock_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n178\n%%EOF"
    
    # Create file data with unique filename
    import time
    timestamp = int(time.time())
    file_data = FileData(
        content=mock_pdf_content,
        filename=f"20241223_TEST_{timestamp}_INVOICE.pdf",
        content_type="application/pdf",
        file_size=len(mock_pdf_content),
        source=UploadSource.MANUAL
    )
    
    # Mock OCR result with structured data
    mock_ocr_result = {
        "success": True,
        "raw_text": "Test Invoice\nInvoice Number: INV-123\nCustomer: Acme Corp\nVendor: Test Vendor Inc\nTotal: 1,234.56 EUR\nDue Date: 2024-01-15",
        "structured_data": {
            "customer_name": "Acme Corp",
            "vendor_name": "Test Vendor Inc", 
            "total_amount": "1,234.56 EUR",
            "invoice_date": "2024-01-15",
            "due_date": "2024-01-30",
            "po_number": "PO-789"
        }
    }
    
    upload_service = UploadService()
    
    async def run_test():
        print("🧪 Testing upload with OCR data mapping...")
        print(f"Database available: {db_service.is_available}")
        
        # Upload the file (this will create the invoice record automatically)
        result = await upload_service.upload_file(file_data)
        
        if result.success:
            print(f"✅ Upload successful!")
            print(f"   Invoice ID: {result.invoice_id}")
            print(f"   Filename: {result.filename}")
            print(f"   File size: {result.file_size}")
            
            # Add OCR data to the uploaded invoice
            if db_service.is_available and result.invoice_id:
                # Update the invoice with OCR data
                ocr_update_data = {
                    "ocr_status": "completed",
                    "ocr_text": mock_ocr_result["raw_text"],
                    "raw_ocr_data": mock_ocr_result
                }
                
                # Map structured OCR data
                structured_data = mock_ocr_result.get("structured_data")
                if structured_data:
                    # Process and add business fields
                    ocr_mapping = {
                        "customer_name": ("rechnungsempfaenger", "text"),
                        "vendor_name": ("rechnungssteller", "text"), 
                        "total_amount": ("rechnungsbetrag", "numeric"),
                        "invoice_date": ("rechnungseingang", "date"),
                        "due_date": ("faelligkeit", "date"),
                        "po_number": ("projekt", "text")
                    }
                    
                    for ocr_field, (db_field, data_type) in ocr_mapping.items():
                        value = structured_data.get(ocr_field)
                        if value is not None and value != "":
                            processed_value = upload_service._process_field_value(value, data_type)
                            if processed_value is not None:
                                ocr_update_data[db_field] = processed_value
                
                # Update the invoice with OCR data
                update_result = db_service.update_invoice(result.invoice_id, ocr_update_data)
                
                if update_result.get("success"):
                    print("✅ Invoice updated with OCR data!")
                    
                    # Fetch the record to verify the mapping
                    invoice_record = db_service.get_invoice(result.invoice_id)
                    if invoice_record.get("success"):
                        data = invoice_record["data"]
                        print("\n📋 Stored invoice data:")
                        print(f"   ID: {data.get('id')}")
                        print(f"   Filename: {data.get('file_name')}")
                        print(f"   Status: {data.get('status')}")
                        print(f"   OCR Status: {data.get('ocr_status')}")
                        
                        print("\n🏢 Business fields (German schema):")
                        print(f"   Rechnungsempfänger: {data.get('rechnungsempfaenger')}")
                        print(f"   Rechnungssteller: {data.get('rechnungssteller')}")
                        print(f"   Rechnungsbetrag: {data.get('rechnungsbetrag')}")
                        print(f"   Rechnungseingang: {data.get('rechnungseingang')}")
                        print(f"   Fälligkeit: {data.get('faelligkeit')}")
                        print(f"   Projekt: {data.get('projekt')}")
                        
                        print(f"\n📄 OCR Text: {data.get('ocr_text')[:100] if data.get('ocr_text') else 'None'}...")
                        
                        # Check if OCR data was mapped
                        ocr_fields_mapped = [
                            data.get('rechnungsempfaenger'),
                            data.get('rechnungssteller'),
                            data.get('rechnungsbetrag')
                        ]
                        mapped_count = len([f for f in ocr_fields_mapped if f])
                        print(f"\n✅ OCR fields mapped: {mapped_count}/6")
                        
                    else:
                        print(f"❌ Failed to fetch invoice: {invoice_record.get('error')}")
                else:
                    print(f"❌ OCR update failed: {update_result.get('error')}")
        else:
            print(f"❌ Upload failed: {result.error}")
    
    return asyncio.run(run_test())

if __name__ == "__main__":
    test_upload_with_mock_ocr()
