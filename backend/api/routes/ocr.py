"""OCR route handlers"""
from fastapi import APIRouter, HTTPException, Path
import logging
from typing import Dict, Any

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ocr/status")
async def get_ocr_status():
    """Get OCR service status and configuration"""
    try:
        status_data = ocr_workflow.get_ocr_status()
        
        return {
            "status": "success",
            "ocr": status_data
        }
    except Exception as e:
        logger.error(f"Failed to get OCR status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "ocr": {
                "ocr_enabled": False,
                "service_available": False,
                "error": str(e)
            }
        }

@router.post("/ocr/process/{invoice_id}")
async def process_invoice_ocr(invoice_id: str = Path(..., description="The invoice ID to process")):
    """Process OCR for an existing invoice"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    if not ocr_config.enable_ocr:
        raise HTTPException(status_code=503, detail="OCR service is disabled")
    
    try:
        # Get the invoice data
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = response.data[0]
        
        # Check if file URL exists
        file_url = invoice_data.get("url")
        if not file_url:
            raise HTTPException(status_code=400, detail="Invoice file URL not found")
        
        # TODO: Download file from URL and process with OCR
        # This would require implementing file download from Supabase storage
        # and then processing with the OCR workflow
        
        return {
            "status": "success",
            "message": "OCR processing initiated",
            "invoice_id": invoice_id,
            "note": "OCR processing implementation in progress"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process OCR for invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@router.get("/ocr/health")
async def get_ocr_health():
    """Get detailed OCR service health information"""
    try:
        health_data = await ocr_workflow.health_check()
        return {
            "status": "success",
            "health": health_data
        }
    except Exception as e:
        logger.error(f"OCR health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "health": {
                "service": "OCR",
                "status": "unhealthy",
                "error": str(e)
            }
        }
