from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from supabase import create_client, Client
import os
import re
import uuid
import time
import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

# Load environment variables
load_dotenv()

# Debug environment variables
print(f"DEBUG: GCP_PROJECT_ID = {os.getenv('GCP_PROJECT_ID')}")
print(f"DEBUG: GCP_LOCATION = {os.getenv('GCP_LOCATION')}")
print(f"DEBUG: DOCUMENT_AI_PROCESSOR_ID = {os.getenv('DOCUMENT_AI_PROCESSOR_ID')}")
print(f"DEBUG: OCR Config - Project: {ocr_config.gcp_project_id}, Location: {ocr_config.gcp_location}, Processor ID: {ocr_config.processor_id}")

app = FastAPI(title="Invoice OCR API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
url: str = os.environ.get("SUPA_URL", "")
key: str = os.environ.get("SUPA_KEY", "")
supabase: Client = None

if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")

# Filename validation pattern
FILENAME_PATTERN = r'^\d{8}_[A-Z0-9]+_[A-Za-z]+_[A-Za-z]+\.pdf$'

# In-memory storage for demo mode (when Supabase is not configured)
mock_invoices = []

async def upload_file_mock(file: UploadFile):
    """Mock upload function for when Supabase is not configured"""
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate filename pattern
    if not re.match(FILENAME_PATTERN, file.filename):
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
        
        # Mock storage - in a real app this would be saved to disk or cloud storage
        invoice_data = {
            "id": invoice_id,
            "filename": file.filename,
            "url": f"http://localhost:8000/mock-storage/{file.filename}",
            "status": "uploaded",
            "file_size": len(content),
            "created_at": "2025-05-29T10:30:00Z"
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
                "ocr_processed_at": datetime.datetime.utcnow().isoformat(),
                "structured_data": ocr_result.get("structured_data")
            })
        else:
            invoice_data.update({
                "ocr_status": "disabled",
                "ocr_enabled": False
            })
        
        # Store in mock database
        mock_invoices.append(invoice_data)
        
        # Prepare response
        response_data = {
            "status": "uploaded",
            "filename": file.filename,
            "url": invoice_data["url"],
            "id": invoice_id,
            "file_size": len(content),
            "message": "File uploaded successfully",
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
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Invoice OCR API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug/ocr-config")
async def debug_ocr_config():
    """Debug endpoint to show OCR configuration"""
    return {
        "gcp_project_id": ocr_config.gcp_project_id,
        "gcp_location": ocr_config.gcp_location,
        "processor_id": ocr_config.processor_id,
        "processor_name": ocr_config.get_processor_name(),
        "enable_ocr": ocr_config.enable_ocr,
        "env_vars": {
            "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
            "GCP_LOCATION": os.getenv("GCP_LOCATION"),
            "DOCUMENT_AI_PROCESSOR_ID": os.getenv("DOCUMENT_AI_PROCESSOR_ID"),
            "ENABLE_OCR": os.getenv("ENABLE_OCR")
        }
    }

@app.get("/mock-storage/{filename}")
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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF invoice file"""
    if not supabase:
        # For demo purposes, work without Supabase
        return await upload_file_mock(file)
    
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate filename pattern
    if not re.match(FILENAME_PATTERN, file.filename):
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
        storage_path = file.filename
        
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
            "filename": file.filename,
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
                "ocr_processed_at": datetime.datetime.utcnow().isoformat(),
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
            "filename": file.filename,
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
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/invoices")
async def get_invoices():
    """Get all invoices"""
    if not supabase:
        # Return mock data when Supabase is not configured
        return {"invoices": mock_invoices}
    
    try:
        response = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
        return {"invoices": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get a specific invoice by ID"""
    if not supabase:
        # Search in mock data when Supabase is not configured
        invoice = next((inv for inv in mock_invoices if inv["id"] == invoice_id), None)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return {"status": "success", "invoice": invoice}
    
    try:
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "status": "success",
            "invoice": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoice: {str(e)}")

@app.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    """Delete an invoice by ID"""
    if not supabase:
        # Delete from mock data when Supabase is not configured
        global mock_invoices
        invoice = next((inv for inv in mock_invoices if inv["id"] == invoice_id), None)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        mock_invoices = [inv for inv in mock_invoices if inv["id"] != invoice_id]
        
        return {
            "status": "success",
            "message": "Invoice deleted successfully",
            "invoice_id": invoice_id,
            "filename": invoice["filename"]
        }
    
    try:
        # First, get the invoice to retrieve filename
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = response.data[0]
        filename = invoice["filename"]
        
        # Delete from storage
        bucket_name = "invoices"
        supabase.storage.from_(bucket_name).remove([filename])
        
        # Delete from database
        supabase.table("invoices").delete().eq("id", invoice_id).execute()
        
        return {
            "status": "success",
            "message": "Invoice deleted successfully",
            "invoice_id": invoice_id,
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")

@app.get("/system-health")
async def system_health():
    """Comprehensive system health check"""
    health_status = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    # 1. Database Connection Test
    try:
        if supabase:
            start_time = time.time()
            # Test basic query
            response = supabase.table("invoices").select("count", count="exact").execute()
            db_response_time = round((time.time() - start_time) * 1000, 2)
            
            health_status["components"]["database"] = {
                "status": "healthy",
                "response_time_ms": db_response_time,
                "total_invoices": response.count if hasattr(response, 'count') else 0,
                "connection": "supabase"
            }
        else:
            health_status["components"]["database"] = {
                "status": "mock",
                "response_time_ms": 0,
                "total_invoices": len(mock_invoices),
                "connection": "in-memory"
            }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "error",
            "error": str(e),
            "connection": "failed"
        }
        health_status["overall_status"] = "degraded"
    
    # 2. Storage Test
    try:
        if supabase:
            start_time = time.time()
            # Test storage bucket access
            bucket_name = "invoices"
            bucket_info = supabase.storage.get_bucket(bucket_name)
            storage_response_time = round((time.time() - start_time) * 1000, 2)
            
            health_status["components"]["storage"] = {
                "status": "healthy",
                "response_time_ms": storage_response_time,
                "bucket": bucket_name,
                "connection": "supabase"
            }
        else:
            health_status["components"]["storage"] = {
                "status": "mock",
                "response_time_ms": 0,
                "connection": "in-memory"
            }
    except Exception as e:
        health_status["components"]["storage"] = {
            "status": "error", 
            "error": str(e),
            "connection": "failed"
        }
        health_status["overall_status"] = "degraded"
    
    # 3. Environment Configuration Test
    env_status = {
        "supa_url": "configured" if url else "missing",
        "supa_key": "configured" if key else "missing",
        "filename_pattern": "configured",
        "ocr_enabled": ocr_config.enable_ocr,
        "gcp_project_id": "configured" if ocr_config.gcp_project_id else "missing",
        "google_credentials": "configured" if ocr_config.google_application_credentials else "default"
    }
    
    health_status["components"]["environment"] = {
        "status": "healthy" if url and key else "degraded",
        "config": env_status
    }
    
    # 4. OCR Service Test
    try:
        ocr_health = await ocr_workflow.health_check()
        health_status["components"]["ocr"] = ocr_health
        
        if ocr_health["status"] != "healthy":
            health_status["overall_status"] = "degraded"
            
    except Exception as e:
        health_status["components"]["ocr"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # 5. API Endpoints Test
    health_status["components"]["api_endpoints"] = {
        "status": "healthy",
        "available_endpoints": [
            "/health", 
            "/system-health",
            "/upload", 
            "/invoices", 
            "/invoices/{id}",
            "/invoices/{id}/ocr",
            "/ocr/status",
            "/ocr/process/{id}",
            "/mock-storage/{filename}"
        ]
    }
    
    # 6. File System Test
    try:
        # Test if we can write to temp directory
        temp_file = "/tmp/health_check_test.txt"
        with open(temp_file, "w") as f:
            f.write("health check")
        os.remove(temp_file)
        
        health_status["components"]["filesystem"] = {
            "status": "healthy",
            "write_access": True
        }
    except Exception as e:
        health_status["components"]["filesystem"] = {
            "status": "error",
            "error": str(e),
            "write_access": False
        }
        health_status["overall_status"] = "degraded"
    
    return health_status

@app.get("/ocr/status")
async def get_ocr_status():
    """Get OCR service status and configuration"""
    try:
        status = ocr_workflow.get_ocr_status()
        return {"status": "success", "ocr": status}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/ocr/process/{invoice_id}")
async def process_invoice_ocr(invoice_id: str):
    """Process OCR for an existing invoice"""
    if not supabase:
        raise HTTPException(status_code=501, detail="OCR processing requires Supabase configuration")
    
    try:
        # Get invoice from database
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = response.data[0]
        filename = invoice["filename"]
        
        # Download file from storage
        bucket_name = "invoices"
        file_data = supabase.storage.from_(bucket_name).download(filename)
        
        # Determine MIME type from filename
        mime_type = "application/pdf" if filename.lower().endswith('.pdf') else "image/jpeg"
        
        # Process with OCR
        ocr_result = await ocr_workflow.process_document(
            file_data, mime_type, filename, "invoice"
        )
        
        # Update database with OCR results
        update_data = {
            "ocr_status": "completed" if ocr_result.get("success") else "failed",
            "ocr_text": ocr_result.get("raw_text", ""),
            "ocr_confidence": ocr_result.get("confidence", 0.0),
            "ocr_pages": ocr_result.get("pages", 0),
            "ocr_processing_time": ocr_result.get("processing_time", 0.0),
            "ocr_error": ocr_result.get("error"),
            "ocr_processed_at": datetime.datetime.utcnow().isoformat(),
            "ocr_entities": ocr_result.get("entities", []),
            "ocr_form_fields": ocr_result.get("form_fields", []),
            "ocr_tables": ocr_result.get("tables", [])
        }
        
        # Add structured data if available
        structured_data = ocr_result.get("structured_data")
        if structured_data:
            update_data.update({
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
        
        supabase.table("invoices").update(update_data).eq("id", invoice_id).execute()
        
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "ocr_result": {
                "success": ocr_result.get("success", False),
                "confidence": ocr_result.get("confidence", 0.0),
                "pages": ocr_result.get("pages", 0),
                "processing_time": ocr_result.get("processing_time", 0.0),
                "error": ocr_result.get("error"),
                "structured_data_available": bool(structured_data)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.get("/invoices/{invoice_id}/ocr")
async def get_invoice_ocr_data(invoice_id: str):
    """Get OCR data for a specific invoice"""
    if not supabase:
        # Search in mock data
        invoice = next((inv for inv in mock_invoices if inv["id"] == invoice_id), None)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "ocr_data": {
                "ocr_status": invoice.get("ocr_status", "unknown"),
                "ocr_text": invoice.get("ocr_text", ""),
                "ocr_confidence": invoice.get("ocr_confidence", 0.0),
                "ocr_pages": invoice.get("ocr_pages", 0),
                "ocr_processing_time": invoice.get("ocr_processing_time", 0.0),
                "ocr_error": invoice.get("ocr_error"),
                "structured_data": invoice.get("structured_data")
            }
        }
    
    try:
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = response.data[0]
        
        # Compile OCR data
        ocr_data = {
            "ocr_status": invoice.get("ocr_status"),
            "ocr_text": invoice.get("ocr_text"),
            "ocr_confidence": invoice.get("ocr_confidence"),
            "ocr_pages": invoice.get("ocr_pages"),
            "ocr_processing_time": invoice.get("ocr_processing_time"),
            "ocr_error": invoice.get("ocr_error"),
            "ocr_processed_at": invoice.get("ocr_processed_at"),
            "entities": invoice.get("ocr_entities"),
            "form_fields": invoice.get("ocr_form_fields"),
            "tables": invoice.get("ocr_tables"),
            "structured_data": {
                "invoice_number": invoice.get("invoice_number"),
                "invoice_date": invoice.get("invoice_date"),
                "due_date": invoice.get("due_date"),
                "vendor_name": invoice.get("vendor_name"),
                "vendor_address": invoice.get("vendor_address"),
                "customer_name": invoice.get("customer_name"),
                "customer_address": invoice.get("customer_address"),
                "subtotal": invoice.get("subtotal"),
                "tax_amount": invoice.get("tax_amount"),
                "total_amount": invoice.get("total_amount"),
                "currency": invoice.get("currency"),
                "payment_terms": invoice.get("payment_terms"),
                "po_number": invoice.get("po_number"),
                "line_items": invoice.get("line_items")
            }
        }
        
        return {
            "status": "success",
            "invoice_id": invoice_id,
            "ocr_data": ocr_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch OCR data: {str(e)}")

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("uvicorn not available, run with: uvicorn main:app --reload")