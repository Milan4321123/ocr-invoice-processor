from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
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
        
        # Mock storage - in a real app this would be saved to disk or cloud storage
        invoice_data = {
            "id": invoice_id,
            "filename": file.filename,
            "url": f"http://localhost:8000/mock-storage/{file.filename}",
            "status": "uploaded",
            "file_size": len(content),
            "created_at": "2025-05-29T10:30:00Z"
        }
        
        # Store in mock database
        mock_invoices.append(invoice_data)
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "url": invoice_data["url"],
            "id": invoice_id,
            "file_size": len(content),
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Invoice OCR API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("uvicorn not available, run with: uvicorn main:app --reload")