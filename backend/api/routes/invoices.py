"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any, Optional
import logging

# Import database service
from services.database import db_service

router = APIRouter()
logger = logging.getLogger(__name__)

def _get_field_confidence_scores(invoice_data: Dict) -> Dict[str, float]:
    """Extract field-specific confidence scores from OCR form fields"""
    confidence_scores = {}
    ocr_form_fields = invoice_data.get("ocr_form_fields", [])
    ocr_entities = invoice_data.get("ocr_entities", [])
    
    # Default confidence based on overall OCR confidence
    default_confidence = invoice_data.get("ocr_confidence", 0.8)
    
    # Mapping from OCR field names to German field names
    field_mapping = {
        # From form fields
        "invoice_number": "rechnungsnummer",  # Not used in editor but good to know
        "invoice_date": "rechnungseingang",
        "total_amount": "rechnungsbetrag",
        "due_date": "faelligkeit",
        # From database fields  
        "customer_name": "rechnungsempfaenger", 
        "vendor_name": "rechnungssteller",
        "po_number": "projekt",
        # From OCR entities - additional mappings
        "receiver_name": "rechnungsempfaenger",  # Customer name from entities
        "supplier_name": "rechnungssteller",     # Vendor name from entities  
        "purchase_order": "projekt",             # PO number from entities
        "invoice_id": "rechnungsnummer",         # Invoice number from entities
    }
    
    # Extract from form fields
    for field in ocr_form_fields:
        field_name = field.get("field_name", "")
        confidence = field.get("confidence", default_confidence)
        
        if field_name in field_mapping:
            confidence_scores[field_mapping[field_name]] = confidence
    
    # Extract from entities as fallback
    for entity in ocr_entities:
        entity_type = entity.get("type", "")
        confidence = entity.get("confidence", default_confidence)
        
        if entity_type in field_mapping:
            # Only use if not already set from form fields
            if field_mapping[entity_type] not in confidence_scores:
                confidence_scores[field_mapping[entity_type]] = confidence
    
    # Set default confidence for mapped fields that have actual data
    if invoice_data.get("customer_name") and "rechnungsempfaenger" not in confidence_scores:
        confidence_scores["rechnungsempfaenger"] = default_confidence
    if invoice_data.get("vendor_name") and "rechnungssteller" not in confidence_scores:
        confidence_scores["rechnungssteller"] = default_confidence
    if invoice_data.get("po_number") and "projekt" not in confidence_scores:
        confidence_scores["projekt"] = default_confidence
    if invoice_data.get("total_amount") and "rechnungsbetrag" not in confidence_scores:
        confidence_scores["rechnungsbetrag"] = default_confidence
    if invoice_data.get("due_date") and "faelligkeit" not in confidence_scores:
        confidence_scores["faelligkeit"] = default_confidence
    if invoice_data.get("invoice_date") and "rechnungseingang" not in confidence_scores:
        confidence_scores["rechnungseingang"] = default_confidence
    
    # Debug logging
    logger.info(f"Confidence scores mapped: {confidence_scores}")
    
    return confidence_scores

def _extract_entity_value(ocr_entities: List[Dict], entity_type: str) -> str:
    """Extract value from OCR entities by type"""
    for entity in ocr_entities:
        if entity.get("type") == entity_type:
            return entity.get("value", "") or entity.get("normalized_value", "")
    return ""

@router.get("/invoices")
async def get_invoices():
    """Get all invoices"""
    if not db_service.is_available:
        # Mock response when database is not available
        return {
            "invoices": [],
            "total": 0,
            "message": "Demo mode - Database not configured"
        }
    
    try:
        # Fetch invoices from database
        result = db_service.get_invoices(limit=100)
        
        if result.get("success"):
            return {
                "invoices": result.get("data", []),
                "total": result.get("count", 0)
            }
        else:
            logger.error(f"Failed to fetch invoices: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Failed to fetch invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Get a specific invoice by ID"""
    if not db_service.is_available:
        # Mock response when database is not available
        raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
    
    try:
        # Fetch specific invoice from database
        result = db_service.get_invoice(invoice_id)
        
        if result.get("success"):
            return {
                "status": "success",
                "invoice": result.get("data")
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoice: {str(e)}")

@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Delete an invoice by ID"""
    if not db_service.is_available:
        # Mock response when database is not available
        return {
            "message": "Invoice deleted (Demo mode)",
            "invoice_id": invoice_id,
            "status": "success"
        }
    
    try:
        # First, check if the invoice exists
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = result.get("data")
        
        # Delete from storage if URL exists and it's not a mock URL
        if invoice.get("url") and not invoice.get("url", "").startswith("http://localhost:8000/mock-storage/"):
            try:
                # Extract filename from URL or use filename field
                filename = invoice.get("filename")
                if filename and db_service.client:
                    db_service.client.storage.from_("invoices").remove([filename])
            except Exception as storage_error:
                logger.warning(f"Failed to delete file from storage: {str(storage_error)}")
                # Continue with database deletion even if storage deletion fails
        
        # Delete from database
        delete_result = db_service.delete_invoice(invoice_id)
        
        if not delete_result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {delete_result.get('error')}")
        
        return {
            "message": "Invoice deleted successfully",
            "invoice_id": invoice_id,
            "filename": invoice.get("filename"),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")

@router.get("/invoices/{invoice_id}/editor")
async def get_invoice_for_editor(invoice_id: str = Path(..., description="The invoice ID")):
    """Get invoice data in German field format for the editing form"""
    if not db_service.is_available:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        # Get the raw invoice data from database without field mapping
        query_result = db_service.client.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not query_result.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = query_result.data[0]
        
        # Create response with German field names for the form
        editor_data = {
            "pdfUrl": f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice_data.get('file_path')}",
            "filename": invoice_data.get("file_name"),
            "fields": {
                "rechnungsempfaenger": invoice_data.get("rechnungsempfaenger"),
                "rechnungssteller": invoice_data.get("rechnungssteller"),
                "projekt": invoice_data.get("projekt"),
                "gewerk": invoice_data.get("gewerk"),
                "rechnungsbetrag": invoice_data.get("brutto_betrag"),
                "rechnungseingang": invoice_data.get("rechnungsdatum"),
                "faelligkeit": None,  # Add if you have this field
                "skonto_datum": None,  # Add if you have this field
                "skonto_prozent": None,  # Add if you have this field
                "rechnungsart": None,  # Add if you have this field
                "kfw_anrechenbar": None,  # Add if you have this field
                "rechnungspruefung_email": None,  # Add if you have this field
                "weiter_berechnen_an": None  # Add if you have this field
            },
            "confidenceScores": {
                "rechnungsempfaenger": invoice_data.get("ocr_confidence", 0),
                "rechnungssteller": invoice_data.get("ocr_confidence", 0),
                "projekt": invoice_data.get("ocr_confidence", 0),
                "gewerk": invoice_data.get("ocr_confidence", 0),
                "rechnungsbetrag": invoice_data.get("ocr_confidence", 0)
            }
        }
        
        return editor_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invoice for editor {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get invoice for editor: {str(e)}")

@router.put("/invoices/{invoice_id}/editor")
async def update_invoice_from_editor(
    invoice_id: str = Path(..., description="The invoice ID"),
    fields: dict = None
):
    """Update invoice with German field data from the editing form"""
    if not db_service.is_available:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    try:
        # Convert form data to database field names  
        update_data = {}
        
        # Map form fields to database columns
        if "rechnungsempfaenger" in fields:
            update_data["rechnungsempfaenger"] = fields["rechnungsempfaenger"]
        if "rechnungssteller" in fields:
            update_data["rechnungssteller"] = fields["rechnungssteller"]
        if "projekt" in fields:
            update_data["projekt"] = fields["projekt"]
        if "gewerk" in fields:
            update_data["gewerk"] = fields["gewerk"]
        if "rechnungsbetrag" in fields:
            update_data["brutto_betrag"] = fields["rechnungsbetrag"]
        if "rechnungseingang" in fields:
            update_data["rechnungsdatum"] = fields["rechnungseingang"]
        
        # Add timestamp for updates
        update_data["updated_at"] = "NOW()"
        
        # Update using database service (but bypass field mapping since we want German names)
        result = db_service.client.table("invoices").update(update_data).eq("id", invoice_id).execute()
        
        if result.data:
            return {
                "status": "success",
                "message": "Invoice updated successfully",
                "invoice_id": invoice_id
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")
