"""
Clean Invoice Management API
Handles upload, storage, editing, and workflow without OCR dependencies.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Invoice Management API",
    description="Clean invoice processing without OCR dependencies",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Import routes
from api.routes import (
    health, 
    upload, 
    invoices, 
    dropdowns, 
    approval, 
    approval_workflow,
    email_workflow,
    reports,
    folder_watcher
)

# Register routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(dropdowns.router, prefix="/api", tags=["dropdowns"])
app.include_router(approval.router, prefix="/api", tags=["approval"])
app.include_router(approval_workflow.router, prefix="/api", tags=["workflow"])
app.include_router(email_workflow.router, prefix="/api", tags=["email"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(folder_watcher.router, prefix="/api", tags=["folder-watcher"])

@app.get("/")
async def root():
    return {
        "message": "Invoice Management API",
        "version": "2.0.0",
        "status": "running",
        "features": ["manual_entry", "searchable_dropdowns", "workflow", "email"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)