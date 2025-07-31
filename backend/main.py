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

# Configure logging with filter to reduce noise from frequent requests
class QuietPathsFilter(logging.Filter):
    """Filter to reduce logging noise from frequently called endpoints"""
    
    def __init__(self):
        super().__init__()
        # Paths that should have reduced logging (only log errors)
        self.quiet_paths = [
            "/api/folder-watcher/status",
            "/api/folder-watcher/notifications"
        ]
    
    def filter(self, record):
        # For uvicorn access logs, reduce noise from frequent endpoints
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            for quiet_path in self.quiet_paths:
                if quiet_path in message and " 200 " in message:
                    # Only log errors for these paths, skip successful 200 responses
                    return False
        return True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apply quiet filter to uvicorn access logs
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(QuietPathsFilter())

app = FastAPI(
    title="Invoice Management API",
    description="Clean invoice processing without OCR dependencies",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "https://ocr-invoice-frontend.onrender.com",  # Production frontend
        "https://ocr-invoice-backend.onrender.com"   # Production backend
    ],
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
    # email_test,  # Removed - not needed for production
    reports,
    folder_watcher,
    skonto_dashboard,  # Added missing skonto dashboard import
    # multi_layer_approval,  # Removed - using simple single Bauleiter approval only
    auth
)

# Register routes
app.include_router(auth.router, tags=["authentication"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(dropdowns.router, prefix="/api", tags=["dropdowns"])
app.include_router(approval.router, prefix="/api/approval", tags=["approval"])
app.include_router(approval_workflow.router, prefix="/api", tags=["workflow"])
app.include_router(email_workflow.router, prefix="/api", tags=["email"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(skonto_dashboard.router, prefix="/api", tags=["skonto"])  # Added missing skonto dashboard router
app.include_router(folder_watcher.router, prefix="/api/folder-watcher", tags=["folder-watcher"])
# Removed multi_layer_approval.router - using simple single Bauleiter approval only

@app.get("/")
async def root():
    return {
        "message": "Invoice Management API",
        "version": "2.0.0",
        "status": "running",
        "features": ["manual_entry", "searchable_dropdowns", "workflow", "email"]
    }

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Invoice Management API...")
    
    # Initialize authentication system
    try:
        from services.auth_service import auth_service
        result = await auth_service.initialize_default_user()
        if result["success"]:
            logger.info(f"🔐 {result['message']}")
        else:
            logger.error(f"❌ Auth initialization failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        logger.error(f"❌ Auth initialization error: {e}")
    
    # Start Skonto reminder scheduler
    try:
        from services.skonto_scheduler import skonto_scheduler
        import asyncio
        
        # Start the scheduler in the background
        asyncio.create_task(skonto_scheduler.start_scheduler())
        logger.info("📅 Skonto reminder scheduler started")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Skonto scheduler: {e}")
    
    logger.info("✅ Application startup complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)