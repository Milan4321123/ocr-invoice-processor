from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import re
import uuid
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI(title="Invoice OCR API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
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

@app.get("/")
async def root():
    return {"message": "Invoice OCR API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF invoice file"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
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
        
        # Store metadata in database
        invoice_data = {
            "id": invoice_id,
            "filename": file.filename,
            "url": public_url,
            "status": "uploaded",
            "file_size": len(content)
        }
        
        supabase.table("invoices").insert(invoice_data).execute()
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "url": public_url,
            "id": invoice_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/invoices")
async def get_invoices():
    """Get all invoices"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    try:
        response = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
        return {"invoices": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get a specific invoice by ID"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
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
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)