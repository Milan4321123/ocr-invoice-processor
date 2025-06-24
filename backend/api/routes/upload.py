"""File upload route handlers"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
import re
import uuid
import datetime
import logging
import os
from typing import Dict, Any

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config
from services.database import db_service
from config.field_mappings import map_input_to_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Filename pattern validation
FILENAME_PATTERN = r'^\d{8}_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+\.pdf$'

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and XSS attacks
    """
    if not filename:
        return "unknown.pdf"
    
    # Remove path traversal attempts
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    # Keep only alphanumeric, dots, dashes, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Remove multiple dots that could be used for traversal
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Ensure it ends with .pdf
    if not filename.lower().endswith('.pdf'):
        filename = filename + '.pdf'
    
    # Limit length
    if len(filename) > 255:
        name_part = filename[:-4][:250]  # Leave room for .pdf
        filename = name_part + '.pdf'
    
    return filename

@router.get("/mock-storage/{filename}")
async def get_mock_file(filename: str):
    """Serve mock PDF files for demo purposes"""
    
    # Generate a simple PDF response (in real app, this would serve actual files)
    pdf_text = f"Mock PDF: {filename}"
    pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj
4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Arial>>endobj
5 0 obj<</Length {len(pdf_text) + 30}>>stream
BT /F1 12 Tf 100 700 Td ({pdf_text}) Tj ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000267 00000 n 
0000000343 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
500
%%EOF""".encode('utf-8')
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

async def upload_file_mock(file: UploadFile) -> Dict[str, Any]:
    """Mock upload function for when Supabase is not available"""
    content = await file.read()
    
    # Sanitize filename for security
    safe_filename = sanitize_filename(file.filename)
    
    # Generate UUID for mock invoice
    invoice_id = str(uuid.uuid4())
    
    # Mock URL
    mock_url = f"http://localhost:8000/mock-storage/{safe_filename}"
    
    # Process OCR if enabled
    ocr_result = None
    if ocr_config.enable_ocr:
        try:
            # Validate file for OCR processing
            is_valid, validation_error = ocr_workflow.validate_file_for_ocr(len(content), file.content_type)
            
            if is_valid:
                # Process document with OCR
                ocr_result = await ocr_workflow.process_document(
                    content, file.content_type, file.filename, "invoice"
                )
            else:
                # OCR validation failed, but still upload the file
                ocr_result = {
                    "success": False,
                    "error": validation_error,
                    "ocr_enabled": True
                }
        except Exception as e:
            # OCR failed, but still upload the file
            ocr_result = {
                "success": False,
                "error": f"OCR processing failed: {str(e)}",
                "ocr_enabled": True
            }
    
    # Prepare response
    response_data = {
        "status": "uploaded",
        "filename": safe_filename,
        "url": mock_url,
        "id": invoice_id,
        "file_size": len(content),
        "ocr_enabled": ocr_config.enable_ocr
    }
    
    # Include OCR results in response
    if ocr_result:
        response_data["ocr_result"] = {
            "success": ocr_result.get("success", False),
            "confidence": ocr_result.get("confidence", 0.0),
            "pages": ocr_result.get("pages", 0),
            "processing_time": ocr_result.get("processing_time", 0.0),
            "error": ocr_result.get("error"),
            "structured_data_available": bool(ocr_result.get("structured_data"))
        }
    
    return response_data

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF invoice file"""
    # Sanitize filename for security
    safe_filename = sanitize_filename(file.filename)
    
    if not db_service.is_available:
        # For demo purposes, work without Supabase
        # Create a new UploadFile-like object with sanitized filename
        class SanitizedFile:
            def __init__(self, original_file, sanitized_name):
                self.filename = sanitized_name
                self.content_type = original_file.content_type
                self._original_file = original_file
            
            async def read(self):
                return await self._original_file.read()
        
        sanitized_file = SanitizedFile(file, safe_filename)
        return await upload_file_mock(sanitized_file)
    
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate filename pattern (use sanitized filename)
    if not re.match(FILENAME_PATTERN, safe_filename):
        raise HTTPException(
            status_code=400, 
            detail="Filename must follow pattern: YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Check if file is empty
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Upload to Supabase storage
        bucket_name = "invoices"
        storage_path = safe_filename
        
        # Upload file to storage
        db_service.client.storage.from_(bucket_name).upload(storage_path, content)
        
        # Get public URL
        public_url = db_service.client.storage.from_(bucket_name).get_public_url(storage_path)
        
        # Generate UUID for invoice record
        invoice_id = str(uuid.uuid4())
        
        # Process OCR if enabled
        ocr_result = None
        if ocr_config.enable_ocr:
            try:
                # Validate file for OCR processing
                is_valid, validation_error = ocr_workflow.validate_file_for_ocr(len(content), file.content_type)
                
                if is_valid:
                    # Process document with OCR
                    ocr_result = await ocr_workflow.process_document(
                        content, file.content_type, file.filename, "invoice"
                    )
                else:
                    # OCR validation failed, but still upload the file
                    ocr_result = {
                        "success": False,
                        "error": validation_error,
                        "ocr_enabled": True
                    }
            except Exception as e:
                # OCR failed, but still upload the file
                ocr_result = {
                    "success": False,
                    "error": f"OCR processing failed: {str(e)}",
                    "ocr_enabled": True
                }
        
        # Prepare database record with OCR data
        # ✅ Use correct field names for invoices_clean schema
        invoice_data = {
            "id": invoice_id,
            "file_name": safe_filename,  # ✅ Fixed: Use file_name (with underscore)
            "file_path": storage_path,
            "file_size": len(content),
            "mime_type": file.content_type,
            "status": "uploaded"
        }
        
        # Add OCR data if available - only fields that exist in invoices_clean
        if ocr_result:
            invoice_data.update({
                "ocr_status": "completed" if ocr_result.get("success") else "failed",
                "ocr_text": ocr_result.get("raw_text", ""),
                "raw_ocr_data": ocr_result  # Store full OCR result as JSONB
            })
            
            # Add structured invoice data if available
            # ✅ Use centralized field mapping for OCR results
            structured_data = ocr_result.get("structured_data")
            if structured_data:
                # Use English field names that will be mapped to German by our central mapping
                ocr_structured_data = {
                    "invoice_number": structured_data.get("invoice_number"),
                    "invoice_date": structured_data.get("invoice_date"),
                    "due_date": structured_data.get("due_date"),
                    "vendor_name": structured_data.get("vendor_name"),
                    "customer_name": structured_data.get("customer_name"),
                    "total_amount": float(structured_data.get("total_amount")) if structured_data.get("total_amount") else None,
                    "po_number": structured_data.get("po_number")
                }
                
                # ✅ Don't use centralized mapping here - let the database service handle it
                # Add OCR fields directly to invoice_data
                invoice_data.update({
                    "customer_name": structured_data.get("customer_name"),
                    "vendor_name": structured_data.get("vendor_name"),
                    "total_amount": float(structured_data.get("total_amount")) if structured_data.get("total_amount") else None,
                    "invoice_date": structured_data.get("invoice_date"),
                    "due_date": structured_data.get("due_date"),
                    "po_number": structured_data.get("po_number")
                })
        else:
            # OCR disabled - only set basic OCR status
            invoice_data.update({
                "ocr_status": "disabled",
                "ocr_text": ""
            })
        
        # 🔍 Debug: Print the invoice data before database creation
        print(f"🔍 About to create invoice with data: {invoice_data}")
        
        # Create invoice record in database
        create_result = db_service.create_invoice(invoice_data)
        
        # 🔍 Debug: Print the result
        print(f"🔍 Database creation result: {create_result}")
        
        if not create_result.get("success"):
            error_msg = create_result.get('error', 'Unknown error')
            logger.error(f"❌ Failed to save invoice to database: {error_msg}")
            logger.error(f"❌ Invoice data: {invoice_data}")
            # Don't fail the upload, but make the error more visible
        else:
            logger.info(f"✅ Successfully saved invoice to database: {create_result.get('data', {}).get('id')}")
        
        # Prepare response
        response_data = {
            "status": "uploaded",
            "filename": safe_filename,
            "url": public_url,
            "id": invoice_id,
            "file_size": len(content),
            "ocr_enabled": ocr_config.enable_ocr,
            "database_save": create_result.get("success", False),  # 🔍 Debug field
            "database_error": create_result.get("error") if not create_result.get("success") else None  # 🔍 Debug field
        }
        
        # Include OCR results in response
        if ocr_result:
            response_data["ocr_result"] = {
                "success": ocr_result.get("success", False),
                "confidence": ocr_result.get("confidence", 0.0),
                "pages": ocr_result.get("pages", 0),
                "processing_time": ocr_result.get("processing_time", 0.0),
                "error": ocr_result.get("error"),
                "structured_data_available": bool(ocr_result.get("structured_data"))
            }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
