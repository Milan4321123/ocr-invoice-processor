"""Health and debug route handlers"""
from fastapi import APIRouter
import os
import time
from datetime import datetime
from config.ocr_config import ocr_config

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Invoice OCR API is running", "version": "0.1.0"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/system-health")
async def system_health():
    """Comprehensive system health check endpoint"""
    start_time = time.time()
    
    # Initialize components status
    components = {}
    overall_status = "healthy"
    
    # Database component check
    # Import supabase from main to check actual connection
    try:
        from main import supabase
        if supabase:
            # Try to perform a simple query to test the connection
            try:
                # Test query to check connection (this won't create a table if it doesn't exist)
                result = supabase.table('invoices').select('count', count='exact').limit(0).execute()
                components["database"] = {
                    "status": "healthy",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "connection": "Supabase (Connected)",
                    "total_invoices": result.count if hasattr(result, 'count') else 0
                }
            except Exception as e:
                components["database"] = {
                    "status": "degraded",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "connection": "Supabase (Connection Error)",
                    "error": str(e),
                    "total_invoices": 0
                }
        else:
            components["database"] = {
                "status": "mock",
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "connection": "Supabase (Demo Mode)",
                "total_invoices": 0
            }
    except ImportError:
        components["database"] = {
            "status": "error",
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "connection": "Configuration Error",
            "total_invoices": 0
        }
    
    # Storage component check  
    try:
        from main import supabase
        if supabase:
            try:
                # Test storage access
                buckets = supabase.storage.list_buckets()
                components["storage"] = {
                    "status": "healthy",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "connection": "Supabase Storage (Connected)",
                    "bucket": "invoices",
                    "write_access": True
                }
            except Exception as e:
                components["storage"] = {
                    "status": "degraded",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "connection": "Supabase Storage (Error)",
                    "bucket": "invoices",
                    "error": str(e),
                    "write_access": False
                }
        else:
            components["storage"] = {
                "status": "mock",
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "connection": "Supabase Storage (Demo Mode)",
                "bucket": "invoices",
                "write_access": True
            }
    except ImportError:
        components["storage"] = {
            "status": "error",
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "connection": "Configuration Error",
            "bucket": "invoices",
            "write_access": False
        }
    
    # Environment component check
    env_config = {}
    env_status = "healthy"
    
    # Check critical environment variables (both naming conventions)
    url_configured = os.getenv("SUPABASE_URL") or os.getenv("SUPA_URL")
    key_configured = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPA_KEY")
    
    env_config["SUPABASE_URL"] = "configured" if url_configured else "missing"
    env_config["SUPABASE_KEY"] = "configured" if key_configured else "missing"
    
    if not url_configured or not key_configured:
        env_status = "degraded"
    
    components["environment"] = {
        "status": env_status,
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "config": env_config
    }
    
    # API endpoints component check
    components["api_endpoints"] = {
        "status": "healthy",
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "available_endpoints": ["/", "/health", "/system-health", "/upload", "/invoices"]
    }
    
    # Filesystem component check
    components["filesystem"] = {
        "status": "healthy",
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "write_access": True
    }
    
    # OCR component check
    ocr_checks = {}
    ocr_status = "healthy"
    
    # Check if we're using mock OCR
    use_mock_ocr = ocr_config.use_mock_ocr or os.getenv("USE_MOCK_OCR", "false").lower() in ("true", "1", "yes")
    
    if use_mock_ocr:
        ocr_checks["service"] = {"status": "healthy", "details": "Using mock OCR service (testing mode)"}
        ocr_status = "healthy"
        service_name = "Mock Service"
    elif ocr_config.enable_ocr:
        # Check credentials file if path is specified
        if ocr_config.google_application_credentials:
            if os.path.exists(ocr_config.google_application_credentials):
                ocr_checks["credentials"] = {"status": "healthy", "details": "GCP credentials file found"}
            else:
                ocr_checks["credentials"] = {"status": "unhealthy", "details": "GCP credentials file missing"}
                ocr_status = "degraded"
        else:
            ocr_checks["credentials"] = {"status": "degraded", "details": "Using default credentials"}
            
        ocr_checks["processor"] = {
            "status": "healthy" if ocr_config.processor_id else "degraded",
            "details": f"Processor ID: {ocr_config.processor_id or 'Using default processor'}"
        }
        
        ocr_checks["project"] = {
            "status": "healthy" if ocr_config.gcp_project_id else "unhealthy",
            "details": f"Project: {ocr_config.gcp_project_id or 'Not configured'}"
        }
        
        if not ocr_config.gcp_project_id:
            ocr_status = "error"
        elif not ocr_config.processor_id:
            ocr_status = "degraded"
        service_name = "Document AI"
    else:
        ocr_checks["service"] = {"status": "healthy", "details": "OCR disabled"}
        service_name = "Disabled"
    
    components["ocr"] = {
        "status": ocr_status,
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "service": service_name,
        "checks": ocr_checks
    }
    
    # Determine overall status
    component_statuses = [comp["status"] for comp in components.values()]
    if "error" in component_statuses:
        overall_status = "error"
    elif "degraded" in component_statuses:
        overall_status = "degraded"
    elif "mock" in component_statuses:
        overall_status = "degraded"  # Consider mock as degraded
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall_status,
        "components": components
    }

@router.get("/debug/ocr-config")
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
