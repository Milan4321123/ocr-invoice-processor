"""File upload route handlers"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
import re
import uuid
import datetime
import logging
import os
from typing import Dict, Any
from supabase import Client

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

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
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    # Sanitize filename for security
    safe_filename = sanitize_filename(file.filename)
    
    if not supabase:
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
        supabase.storage.from_(bucket_name).upload(storage_path, content)
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
        
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
        invoice_data = {
            "id": invoice_id,
            "filename": safe_filename,
            "url": public_url,
            "status": "uploaded",
            "file_size": len(content)
        }
        
        # Add OCR data if available
        if ocr_result:
            invoice_data.update({
                "ocr_status": "completed" if ocr_result.get("success") else "failed",
                "ocr_text": ocr_result.get("raw_text", ""),
                "ocr_confidence": ocr_result.get("confidence", 0.0),
                "ocr_pages": ocr_result.get("pages", 0),
                "ocr_processing_time": ocr_result.get("processing_time", 0.0),
                "ocr_error": ocr_result.get("error"),
                "ocr_processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "ocr_entities": ocr_result.get("entities", []),
                "ocr_form_fields": ocr_result.get("form_fields", []),
                "ocr_tables": ocr_result.get("tables", [])
            })
            
            # Add structured invoice data if available
            structured_data = ocr_result.get("structured_data")
            if structured_data:
                invoice_data.update({
                    "invoice_number": structured_data.get("invoice_number"),
                    "invoice_date": structured_data.get("invoice_date"),
                    "due_date": structured_data.get("due_date"),
                    "vendor_name": structured_data.get("vendor_name"),
                    "vendor_address": structured_data.get("vendor_address"),
                    "customer_name": structured_data.get("customer_name"),
                    "customer_address": structured_data.get("customer_address"),
                    "subtotal": float(structured_data.get("subtotal")) if structured_data.get("subtotal") else None,
                    "tax_amount": float(structured_data.get("tax_amount")) if structured_data.get("tax_amount") else None,
                    "total_amount": float(structured_data.get("total_amount")) if structured_data.get("total_amount") else None,
                    "currency": structured_data.get("currency"),
                    "payment_terms": structured_data.get("payment_terms"),
                    "po_number": structured_data.get("po_number"),
                    "line_items": structured_data.get("line_items", [])
                })
        else:
            # OCR disabled
            invoice_data.update({
                "ocr_status": "disabled",
                "ocr_text": "",
                "ocr_confidence": 0.0,
                "ocr_pages": 0,
                "ocr_processing_time": 0.0
            })
        
        supabase.table("invoices").insert(invoice_data).execute()
        
        # Prepare response
        response_data = {
            "status": "uploaded",
            "filename": safe_filename,
            "url": public_url,
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
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
