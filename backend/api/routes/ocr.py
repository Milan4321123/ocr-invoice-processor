"""OCR route handlers"""
from fastapi import APIRouter, HTTPException, Path
import logging
from typing import Dict, Any
from datetime import datetime, timezone

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
    """Process OCR for an existing invoice with enhanced status tracking"""
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
        
        # Check if already processing
        if invoice.get("ocr_status") == "processing":
            return {
                "status": "already_processing",
                "message": "OCR processing is already in progress for this invoice",
                "invoice_id": invoice_id
            }
        
        # Check if already completed
        if invoice.get("ocr_status") == "completed":
            # Get confidence from raw_ocr_data if available
            raw_data = invoice.get("raw_ocr_data", {})
            confidence = raw_data.get("confidence", 0.0) if raw_data else 0.0
            return {
                "status": "already_processed", 
                "message": "OCR has already been processed for this invoice",
                "invoice_id": invoice_id,
                "ocr_confidence": confidence
            }
        
        # Immediately set status to processing for real-time feedback
        db_service.update_invoice(invoice_id, {
            "ocr_status": "processing"
        })
        
        logger.info(f"Starting OCR processing for invoice {invoice_id}")
        
        # Check if file URL exists
        file_url = invoice.get("url")
        if not file_url:
            raise HTTPException(status_code=400, detail="Invoice file URL not found")
        
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
                    "ocr_status": "completed",
                    "status": "completed",
                    "raw_ocr_data": ocr_result,  # Store full OCR result as JSONB
                    "ocr_text": ocr_result.get("raw_text", ""),
                    # Map OCR structured data to our exact German database field names
                    "rechnungsempfaenger": structured_data.get("customer_name"),
                    "rechnungssteller": structured_data.get("vendor_name"),
                    "rechnungsbetrag": structured_data.get("total_amount"),
                    "rechnungseingang": structured_data.get("invoice_date"),
                    "faelligkeit": structured_data.get("due_date"),
                    "projekt": structured_data.get("po_number")
                }
                
                logger.info(f"OCR processing completed successfully for invoice {invoice_id}")
                logger.info(f"Mapped OCR fields: rechnungssteller={structured_data.get('vendor_name')}, rechnungsbetrag={structured_data.get('total_amount')}")
                
            else:
                # OCR failed
                update_data = {
                    "ocr_status": "failed",
                    "status": "error",
                    "raw_ocr_data": ocr_result
                }
                
                logger.warning(f"OCR processing failed for invoice {invoice_id}: {ocr_result.get('error')}")
            
            # Perform database update and log result
            logger.info(f"Updating invoice {invoice_id} with data: {update_data}")
            update_result = db_service.update_invoice(invoice_id, update_data)
            logger.info(f"Database update result: {update_result}")
            
            return {
                "status": "success",
                "message": f"OCR processing {'completed' if ocr_result.get('success') else 'failed'} for invoice",
                "invoice_id": invoice_id,
                "ocr_result": {
                    "success": ocr_result.get("success", False),
                    "confidence": ocr_result.get("confidence", 0.0),
                    "pages": ocr_result.get("pages", 0),
                    "processing_time": ocr_result.get("processing_time", 0.0),
                    "error": ocr_result.get("error"),
                    "structured_data_available": bool(structured_data) if ocr_result.get("success") else False
                },
                "extracted_data": structured_data if ocr_result.get("success") else None
            }
            
        except Exception as ocr_error:
            # Update status to error
            error_message = str(ocr_error)
            logger.error(f"OCR processing failed for invoice {invoice_id}: {error_message}")
            
            db_service.update_invoice(invoice_id, {
                "ocr_status": "failed",
                "status": "error"
            })
            
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {error_message}")
        
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

@router.get("/invoices/{invoice_id}/ocr-status")
async def get_invoice_ocr_status(invoice_id: str = Path(..., description="The invoice ID")):
    """Get real-time OCR processing status for an invoice (Phase 2 enhancement)"""
    if not db_service.client:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        # Get the invoice data using database service
        result = db_service.get_invoice(invoice_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = result.get("data")
        
        # Extract OCR-related data
        ocr_status = invoice.get("ocr_status", "pending")
        ocr_text = invoice.get("ocr_text", "")
        
        # Get structured data from raw_ocr_data if available
        raw_ocr_data = invoice.get("raw_ocr_data", {})
        structured_data = raw_ocr_data.get("structured_data", {}) if raw_ocr_data else {}
        confidence = raw_ocr_data.get("confidence", 0.0) if raw_ocr_data else 0.0
        processing_time = raw_ocr_data.get("processing_time", 0.0) if raw_ocr_data else 0.0
        error_info = raw_ocr_data.get("error") if raw_ocr_data else None
        
        return {
            "invoice_id": invoice_id,
            "filename": invoice.get("file_name"),  # Use correct field name
            "ocr_status": ocr_status,
            "ocr_confidence": confidence,
            "ocr_processing_time": processing_time,
            "ocr_error": error_info,
            "ocr_processed_at": invoice.get("updated_at"),  # Use updated_at as processed time
            "has_structured_data": bool(structured_data),
            "extracted_data": {
                "invoice_number": structured_data.get("invoice_number"),
                "vendor_name": structured_data.get("vendor_name"),
                "total_amount": structured_data.get("total_amount"),
                "invoice_date": structured_data.get("invoice_date")
            } if structured_data else None,
            "processing_info": {
                "pages": raw_ocr_data.get("pages", 0) if raw_ocr_data else 0,
                "entities_found": len(raw_ocr_data.get("entities", [])) if raw_ocr_data else 0,
                "tables_found": len(raw_ocr_data.get("tables", [])) if raw_ocr_data else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get OCR status for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get OCR status: {str(e)}")
