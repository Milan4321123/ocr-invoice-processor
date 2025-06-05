"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any, Optional
import logging
from supabase import Client

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

@router.get("/invoices")
async def get_invoices():
    """Get all invoices"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        # Mock response when Supabase is not available
        return {
            "invoices": [],
            "total": 0,
            "message": "Demo mode - Supabase not configured"
        }
    
    try:
        # Fetch invoices from Supabase
        response = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
        
        return {
            "invoices": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Get a specific invoice by ID"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        # Mock response when Supabase is not available
        raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
    
    try:
        # Fetch specific invoice from Supabase
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "status": "success",
            "invoice": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoice: {str(e)}")

@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Delete an invoice by ID"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        # Mock response when Supabase is not available
        return {
            "message": "Invoice deleted (Demo mode)",
            "invoice_id": invoice_id,
            "status": "success"
        }
    
    try:
        # First, check if the invoice exists
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = response.data[0]
        
        # Delete from storage if URL exists and it's not a mock URL
        if invoice.get("url") and not invoice.get("url", "").startswith("http://localhost:8000/mock-storage/"):
            try:
                # Extract filename from URL or use filename field
                filename = invoice.get("filename")
                if filename:
                    supabase.storage.from_("invoices").remove([filename])
            except Exception as storage_error:
                logger.warning(f"Failed to delete file from storage: {str(storage_error)}")
                # Continue with database deletion even if storage deletion fails
        
        # Delete from database
        delete_response = supabase.table("invoices").delete().eq("id", invoice_id).execute()
        
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

@router.get("/invoices/{invoice_id}/ocr")
async def get_invoice_ocr(invoice_id: str = Path(..., description="The invoice ID")):
    """Get OCR data for a specific invoice"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        # Mock response when Supabase is not available
        raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
    
    try:
        # Fetch specific invoice from Supabase with OCR fields
        ocr_fields = [
            "id", "filename", "ocr_status", "ocr_text", "ocr_confidence", 
            "ocr_pages", "ocr_processing_time", "ocr_error", "ocr_processed_at",
            "ocr_entities", "ocr_form_fields", "ocr_tables", "line_items",
            "invoice_number", "invoice_date", "due_date", "vendor_name", 
            "vendor_address", "customer_name", "customer_address", "subtotal", 
            "tax_amount", "total_amount", "currency", "payment_terms", "po_number"
        ]
        
        response = supabase.table("invoices").select(",".join(ocr_fields)).eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = response.data[0]
        
        # Structure the OCR response
        ocr_response = {
            "id": invoice_data.get("id"),
            "filename": invoice_data.get("filename"),
            "ocr_status": invoice_data.get("ocr_status"),
            "ocr_confidence": invoice_data.get("ocr_confidence", 0.0),
            "ocr_pages": invoice_data.get("ocr_pages", 0),
            "ocr_processing_time": invoice_data.get("ocr_processing_time", 0.0),
            "ocr_error": invoice_data.get("ocr_error"),
            "ocr_processed_at": invoice_data.get("ocr_processed_at"),
            "raw_text": invoice_data.get("ocr_text", ""),
            "structured_data": {
                "invoice_number": invoice_data.get("invoice_number"),
                "invoice_date": invoice_data.get("invoice_date"),
                "due_date": invoice_data.get("due_date"),
                "vendor_name": invoice_data.get("vendor_name"),
                "vendor_address": invoice_data.get("vendor_address"),
                "customer_name": invoice_data.get("customer_name"),
                "customer_address": invoice_data.get("customer_address"),
                "subtotal": invoice_data.get("subtotal"),
                "tax_amount": invoice_data.get("tax_amount"),
                "total_amount": invoice_data.get("total_amount"),
                "currency": invoice_data.get("currency"),
                "payment_terms": invoice_data.get("payment_terms"),
                "po_number": invoice_data.get("po_number"),
                "line_items": invoice_data.get("line_items", [])
            },
            "entities": invoice_data.get("ocr_entities", []),
            "form_fields": invoice_data.get("ocr_form_fields", []),
            "tables": invoice_data.get("ocr_tables", [])
        }
        
        return ocr_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch OCR data for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch OCR data: {str(e)}")

@router.get("/invoices/{invoice_id}/validate")
async def validate_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Validate if an invoice exists and is accessible"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        # Mock validation for demo
        if invoice_id == "test-123":
            return {"valid": True, "invoice_id": invoice_id}
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Check if invoice exists in Supabase
        response = supabase.table("invoices").select("id, filename").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "valid": True,
            "invoice_id": invoice_id,
            "filename": response.data[0].get("filename")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate invoice: {str(e)}")

@router.get("/invoices/{invoice_id}/editor")
async def get_invoice_editor_data(invoice_id: str = Path(..., description="The invoice ID")):
    """Get invoice data formatted for the editor interface"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not supabase:
        # Mock data for demo
        if invoice_id == "test-123":
            return {
                "pdfUrl": "/test_invoice_1748551760.pdf",
                "fields": {
                    "rechnungsempfaenger": "ACME Construction GmbH",
                    "rechnungssteller": "Demo Vendor Services",
                    "projekt": "Residential Building Project",
                    "gewerk": "Electrical Installation", 
                    "rechnungsbetrag": 15750.50,
                    "rechnungseingang": "2025-05-30",
                    "faelligkeit": "2025-06-29",
                    "skonto_datum": "2025-06-09",
                    "skonto_prozent": 2.0,
                    "rechnungsart": "rechnung",
                    "kfw_anrechenbar": True,
                    "rechnungspruefung_email": "review@acme-construction.de",
                    "weiter_berechnen_an": "Client Invoice Department"
                },
                "confidenceScores": {
                    "rechnungsempfaenger": 0.95,
                    "rechnungssteller": 0.88,
                    "projekt": 0.75,
                    "gewerk": 0.82,
                    "rechnungsbetrag": 0.98,
                    "rechnungseingang": 0.92,
                    "faelligkeit": 0.89,
                    "skonto_datum": 0.76,
                    "skonto_prozent": 0.85,
                    "rechnungsart": 0.91,
                    "kfw_anrechenbar": 0.68,
                    "rechnungspruefung_email": 0.45,
                    "weiter_berechnen_an": 0.52
                },
                "filename": "test_invoice_1748551760.pdf"
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Fetch invoice data from Supabase
        response = supabase.table("invoices").select("*").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = response.data[0]
        
        # Format data for editor interface
        editor_data = {
            "pdfUrl": invoice_data.get("url", ""),
            "fields": {
                "rechnungsempfaenger": invoice_data.get("customer_name", ""),
                "rechnungssteller": invoice_data.get("vendor_name", ""),
                "projekt": invoice_data.get("po_number", ""),
                "gewerk": "",  # Map from structured data if available
                "rechnungsbetrag": invoice_data.get("total_amount", 0),
                "rechnungseingang": invoice_data.get("invoice_date", ""),  # Use invoice_date, not created_at
                "faelligkeit": invoice_data.get("due_date", ""),
                "skonto_datum": "",
                "skonto_prozent": 0,
                "rechnungsart": "rechnung",
                "kfw_anrechenbar": False,
                "rechnungspruefung_email": "",
                "weiter_berechnen_an": ""
            },
            "confidenceScores": {
                # Map confidence scores from OCR form fields
                **_get_field_confidence_scores(invoice_data),
                # Add default scores for fields not in OCR data
                "gewerk": 0.0,  # Not extracted by OCR
                "skonto_datum": 0.0,  # Not extracted by OCR  
                "skonto_prozent": 0.0,  # Not extracted by OCR
                "rechnungsart": 0.0,  # Not extracted by OCR
                "kfw_anrechenbar": 0.0,  # Not extracted by OCR
                "rechnungspruefung_email": 0.0,  # Not extracted by OCR
                "weiter_berechnen_an": 0.0,  # Not extracted by OCR
            },
            "filename": invoice_data.get("filename", f"Invoice {invoice_id}")
        }
        
        return editor_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch editor data for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch editor data: {str(e)}")

@router.put("/invoices/{invoice_id}/editor")
async def update_invoice_editor_data(
    invoice_id: str = Path(..., description="The invoice ID"),
    request_data: Dict[str, Any] = None
):
    """Update invoice data from the editor interface"""
    # Import here to avoid circular imports
    import main
    supabase = main.supabase
    
    if not request_data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    fields = request_data.get("fields", {})
    
    if not supabase:
        # Mock success for demo
        if invoice_id == "test-123":
            return {
                "success": True,
                "message": "Invoice updated successfully (demo mode)",
                "invoice_id": invoice_id,
                "updated_fields": fields
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Update invoice data in Supabase
        # Map German fields back to database fields
        update_data = {
            "customer_name": fields.get("rechnungsempfaenger", ""),
            "vendor_name": fields.get("rechnungssteller", ""),
            "po_number": fields.get("projekt", ""),
            "total_amount": fields.get("rechnungsbetrag", 0),
            "due_date": fields.get("faelligkeit", ""),
            # Add other mappings as needed
        }
        
        # Remove empty values
        update_data = {k: v for k, v in update_data.items() if v is not None and v != ""}
        
        if update_data:
            response = supabase.table("invoices").update(update_data).eq("id", invoice_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Invoice not found or update failed")
        
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
