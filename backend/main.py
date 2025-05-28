from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
BUCKET = "invoices"  # Define bucket name globally
try:
    supabase = create_client(
        os.getenv("SUPA_URL", ""), 
        os.getenv("SUPA_KEY", "")
    )
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

@app.get("/")
async def root():
    return {"message": "Invoice OCR API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "supabase_connected": supabase is not None
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF file to Supabase storage and create record in invoices table.
    
    Filename must match pattern: YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf
    
    Args:
        file: PDF file to upload
        
    Returns:
        dict: Upload result with URL, status, filename, and ID
        
    Raises:
        HTTPException: If validation fails or upload errors occur
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    # Validate content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    # Validate filename using regex
    filename_pattern = r'^\d{8}_[A-Z0-9]+_[A-Za-z]+_[A-Za-z]+\.pdf$'
    if not re.match(filename_pattern, file.filename):
        raise HTTPException(
            status_code=400,
            detail="Filename must follow pattern: YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        logger.info(f"Uploading file: {file.filename}, size: {file_size} bytes")
        
        # Upload to Supabase storage
        key = file.filename
        upload_response = supabase.storage.from_(BUCKET).upload(
            key, 
            file_content, 
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        url_response = supabase.storage.from_(BUCKET).get_public_url(key)
        public_url = url_response
        
        # Create record in invoices table
        invoice_id = str(uuid.uuid4())
        invoice_data = {
            "id": invoice_id,
            "filename": key,
            "url": public_url,
            "status": "uploaded",
            "file_size": file_size,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        db_response = supabase.table("invoices").insert(invoice_data).execute()
        
        logger.info(f"Successfully uploaded and recorded: {file.filename}")
        
        return {
            "id": invoice_id,
            "url": public_url,
            "status": "uploaded",
            "filename": key,
            "file_size": file_size,
            "message": "File uploaded successfully"
        }
    
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Upload failed: {str(e)}"
        )

@app.get("/invoices")
async def get_invoices():
    """
    Get all invoices from the database, ordered by creation date (newest first)
    
    Returns:
        dict: List of invoices with metadata
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    try:
        response = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
        
        return {
            "invoices": response.data,
            "count": len(response.data),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to fetch invoices: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch invoices: {str(e)}"
        )

@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """
    Get a specific invoice by ID
    
    Args:
        invoice_id: UUID of the invoice
        
    Returns:
        dict: Invoice details
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    # Validate that invoice_id is not empty
    if not invoice_id or invoice_id.strip() == "":
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "invoice": response.data[0],
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch invoice: {str(e)}"
        )

@app.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    """
    Delete an invoice and its associated file
    
    Args:
        invoice_id: UUID of the invoice to delete
        
    Returns:
        dict: Deletion result
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    try:
        # First get the invoice to find the filename
        invoice_response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not invoice_response.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = invoice_response.data[0]
        filename = invoice["filename"]
        
        # Delete from storage
        supabase.storage.from_(BUCKET).remove([filename])
        
        # Delete from database
        supabase.table("invoices").delete().eq("id", invoice_id).execute()
        
        logger.info(f"Successfully deleted invoice: {invoice_id}")
        
        return {
            "message": "Invoice deleted successfully",
            "invoice_id": invoice_id,
            "filename": filename,
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete invoice: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)