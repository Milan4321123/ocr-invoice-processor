"""
Refactored Invoice OCR API main application.
This file now imports route handlers from separate modules for better maintainability.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from dotenv import load_dotenv

# Route imports
from api.routes import health, upload, invoices, ocr, dropdowns, folder_watcher

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

# Initialize database service
from services.database import db_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(    
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Invoice OCR API", version="0.1.0")

# Log database service status
if db_service.is_available:
    logger.info("Database service initialized and connected successfully")
else:
    logger.warning("Database service unavailable - running in offline mode")

# Add request ID middleware for better traceability
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(health.router, tags=["health"])
app.include_router(upload.router, tags=["upload"])
app.include_router(invoices.router, tags=["invoices"])
app.include_router(ocr.router, tags=["ocr"])
app.include_router(dropdowns.router, prefix="/api", tags=["dropdowns"])
app.include_router(folder_watcher.router, prefix="/api/folder-watcher", tags=["folder-watcher"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)