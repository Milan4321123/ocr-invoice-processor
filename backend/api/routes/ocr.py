"""OCR route handlers"""
from fastapi import APIRouter, HTTPException, Path
import logging
from typing import Dict, Any

# OCR imports
from ocr.workflow import ocr_workflow
from config.ocr_config import ocr_config

# Import database service
from services.database import db_service

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
    if not db_service.client:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    if not ocr_config.enable_ocr:
        raise HTTPException(status_code=503, detail="OCR service is disabled")
    
    try:
        # Get the invoice data using database service
        result = db_service.get_invoice(invoice_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = result.get("data")
        
        # Check if file URL exists
        file_url = invoice.get("url")
        if not file_url:
            raise HTTPException(status_code=400, detail="Invoice file URL not found")
        
        # Update status to processing
        db_service.update_invoice(invoice_id, {"status": "processing"})
        
        # Get the file from Supabase storage
        file_path = invoice.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="Invoice file path not found")
        
        try:
            # Download file from storage
            file_response = db_service.client.storage.from_('invoices').download(file_path)
            
            # Determine MIME type from filename
            filename = invoice.get("filename", "")
            mime_type = "application/pdf"  # Default to PDF
            if filename.lower().endswith('.pdf'):
                mime_type = "application/pdf"
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                mime_type = "image/jpeg"
            elif filename.lower().endswith('.png'):
                mime_type = "image/png"
            
            # Process with OCR workflow
            ocr_result = await ocr_workflow.process_document(
                file_content=file_response,
                mime_type=mime_type,
                filename=filename,
                document_type="invoice"
            )
            
            # Update invoice with OCR results
            if ocr_result.get("success"):
                structured_data = ocr_result.get("structured_data") or {}
                update_data = {
                    "status": "completed",
                    "ocr_processing_time": int(ocr_result.get("processing_time", 0) * 1000),  # Convert to milliseconds
                    "processed_at": "NOW()",
                    "raw_ocr_data": ocr_result,  # Store full OCR result as JSONB
                    "ocr_confidence": ocr_result.get("confidence"),
                    # Map OCR structured data to German database field names
                    "rechnungsnummer": structured_data.get("invoice_number"),
                    "rechnungsdatum": structured_data.get("invoice_date"),
                    "rechnungsempfaenger": structured_data.get("customer_name") or structured_data.get("invoice_recipient"),
                    "rechnungssteller": structured_data.get("vendor_name") or structured_data.get("invoice_issuer"),
                    "projekt": structured_data.get("project"),
                    "gewerk": structured_data.get("trade"),
                    "netto_betrag": structured_data.get("net_amount") or structured_data.get("subtotal"),
                    "brutto_betrag": structured_data.get("gross_amount") or structured_data.get("total_amount")
                }
            else:
                # OCR failed
                update_data = {
                    "status": "error",
                    "error_message": ocr_result.get("error", "Unknown OCR error"),
                    "processed_at": "NOW()",
                    "raw_ocr_data": ocr_result
                }
            
            db_service.update_invoice(invoice_id, update_data)
            
            return {
                "status": "success",
                "message": "OCR processing completed successfully",
                "invoice_id": invoice_id,
                "ocr_result": ocr_result
            }
            
        except Exception as ocr_error:
            # Update status to error
            db_service.update_invoice(invoice_id, {
                "status": "error",
                "ocr_status": "failed",
                "ocr_error": str(ocr_error),
                "ocr_processed_at": "NOW()"
            })
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(ocr_error)}")
        
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
