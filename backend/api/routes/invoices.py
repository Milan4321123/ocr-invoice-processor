"""Invoice management route handlers - CLEAN VERSION WITHOUT OCR"""
from fastapi import APIRouter, HTTPException, Path, Body
from typing import List, Dict, Any, Optional
import logging
from services.database import db_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/invoices")
async def get_invoices():
    """Get all invoices using the centralized database service"""
    try:
        result = db_service.get_all_invoices()
        
        if result.get("success"):
            return {
                "invoices": result.get("data", []),
                "total": result.get("total", 0)
            }
        else:
            # Handle database unavailable case
            if "unavailable" in result.get("error", "").lower():
                return {
                    "invoices": [],
                    "total": 0,
                    "message": "Demo mode - Database not configured"
                }
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to fetch invoices"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Get a specific invoice by ID using the centralized database service"""
    try:
        result = db_service.get_invoice(invoice_id)
        
        if result.get("success"):
            return {
                "status": "success",
                "invoice": result.get("data")
            }
        else:
            # Handle specific error cases
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            elif "unavailable" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoice: {str(e)}")

@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Delete an invoice by ID using the centralized database service"""
    try:
        result = db_service.delete_invoice(invoice_id)
        
        if result.get("success"):
            return {
                "message": "Invoice deleted successfully",
                "invoice_id": invoice_id,
                "status": "success"
            }
        else:
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            elif "unavailable" in error_msg.lower():
                return {
                    "message": "Invoice deleted (Demo mode)",
                    "invoice_id": invoice_id,
                    "status": "success"
                }
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")



@router.get("/invoices/{invoice_id}/validate")
async def validate_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Validate if an invoice exists and is accessible using the centralized database service"""
    try:
        result = db_service.get_invoice(invoice_id)
        
        if result.get("success"):
            invoice_data = result.get("data")
            return {
                "valid": True,
                "invoice_id": invoice_id,
                "filename": invoice_data.get("file_name")
            }
        else:
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            elif "unavailable" in error_msg.lower():
                # Mock validation for demo
                if invoice_id == "test-123":
                    return {"valid": True, "invoice_id": invoice_id}
                else:
                    raise HTTPException(status_code=404, detail="Invoice not found")
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate invoice: {str(e)}")

@router.get("/invoices/{invoice_id}/editor")
async def get_invoice_editor_data(invoice_id: str = Path(..., description="The invoice ID")):
    """Get invoice data formatted for the editor interface - MANUAL EDITING ONLY"""
    try:
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        invoice_data = result.get("data")
        if not invoice_data:
            raise HTTPException(status_code=404, detail="Invoice data not found")
        
        # Build PDF URL
        pdf_url = invoice_data.get("url", "")
        if not pdf_url and invoice_data.get("file_path"):
            pdf_url = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice_data['file_path']}"
        
        # Simple field mapping - just return database values or empty defaults
        editor_data = {
            "pdfUrl": pdf_url,
            "fields": {
                "rechnungsempfaenger": invoice_data.get("rechnungsempfaenger") or "",
                "rechnungssteller": invoice_data.get("rechnungssteller") or "",
                "projekt": invoice_data.get("projekt") or "",
                "gewerk": invoice_data.get("gewerk") or "",
                "rechnungsbetrag": invoice_data.get("rechnungsbetrag") or 0,
                "rechnungseingang": invoice_data.get("rechnungseingang") or "",
                "faelligkeit": invoice_data.get("faelligkeit") or "",
                "skonto_datum": invoice_data.get("skonto_datum") or "",
                "skonto_prozent": invoice_data.get("skonto_prozent") or 0,
                "rechnungsart": invoice_data.get("rechnungsart") or "rechnung",
                "kfw_anrechenbar": invoice_data.get("kfw_anrechenbare_kosten") or False,
                "rechnungspruefung_email": invoice_data.get("rechnungspruefung") or "",
                "weiter_berechnen_an": invoice_data.get("weiter_berechnen_an") or ""
            },
            "filename": invoice_data.get("file_name") or f"Invoice {invoice_id}"
        }
        
        logger.info(f"✅ Editor data loaded successfully for invoice {invoice_id}")
        return editor_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch editor data for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch editor data: {str(e)}")

@router.put("/invoices/{invoice_id}/editor")
async def update_invoice_editor_data(
    invoice_id: str = Path(..., description="The invoice ID"),
    request_data: Dict[str, Any] = Body(...)
):
    """Update invoice data from the editor interface - MANUAL EDITING ONLY"""
    if not request_data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    fields = request_data.get("fields", {})
    logger.info(f"📝 Updating invoice {invoice_id} with fields: {list(fields.keys())}")
    
    try:
        # Check if invoice exists first
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        # Direct field mapping - frontend field names match database field names
        update_data = {}
        
        field_mapping = {
            "rechnungsempfaenger": "rechnungsempfaenger",
            "rechnungssteller": "rechnungssteller", 
            "projekt": "projekt",
            "gewerk": "gewerk",
            "rechnungsbetrag": "rechnungsbetrag",
            "rechnungseingang": "rechnungseingang",
            "faelligkeit": "faelligkeit",
            "skonto_datum": "skonto_datum",
            "skonto_prozent": "skonto_prozent",
            "rechnungsart": "rechnungsart",
            "kfw_anrechenbar": "kfw_anrechenbare_kosten",
            "rechnungspruefung_email": "rechnungspruefung",
            "weiter_berechnen_an": "weiter_berechnen_an"
        }
        
        # Process each field that was provided
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in fields:
                value = fields[frontend_field]
                
                # Handle different field types
                if db_field in ["rechnungsbetrag", "skonto_prozent"]:
                    # Numeric fields
                    update_data[db_field] = float(value) if value not in [None, ""] else 0.0
                elif db_field == "kfw_anrechenbare_kosten":
                    # Boolean field
                    update_data[db_field] = bool(value) if value is not None else False
                elif db_field in ["rechnungseingang", "faelligkeit", "skonto_datum"]:
                    # Date fields - handle empty strings properly
                    if value and value.strip():
                        update_data[db_field] = value.strip()
                    else:
                        update_data[db_field] = None  # Use None instead of empty string for dates
                else:
                    # Text fields
                    update_data[db_field] = str(value) if value is not None else ""
        
        logger.info(f"💾 Sending to database: {update_data}")
        
        if update_data:
            update_result = db_service.update_invoice(invoice_id, update_data)
            
            if not update_result.get("success"):
                raise HTTPException(status_code=500, detail=update_result.get("error", "Update failed"))
        
        logger.info(f"✅ Invoice {invoice_id} updated successfully")
        return {
            "success": True,
            "message": "Invoice updated successfully",
            "invoice_id": invoice_id,
            "updated_fields": list(update_data.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update editor data for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")
