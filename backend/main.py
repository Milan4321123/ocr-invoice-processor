"""
Refactored Invoice OCR API main application.
This file now imports route handlers from separate modules for better maintainability.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import uuid
import logging
from dotenv import load_dotenv
from typing import Optional

# Route imports
from api.routes import health, upload, invoices, ocr

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

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

# Initialize Supabase client
supabase: Optional[Client] = None

# Supabase configuration - check both naming conventions
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("SUPA_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPA_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"Supabase client initialized successfully with URL: {SUPABASE_URL[:50]}...")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase = None
else:
    logger.warning("Supabase configuration not found. Running in demo mode.")

# Include route modules
app.include_router(health.router, tags=["health"])
app.include_router(upload.router, tags=["upload"])
app.include_router(invoices.router, tags=["invoices"])
app.include_router(ocr.router, tags=["ocr"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)