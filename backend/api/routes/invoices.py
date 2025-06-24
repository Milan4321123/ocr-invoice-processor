"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any, Optional
import logging
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


@router.get("/invoices/{invoice_id}/ocr")
async def get_invoice_ocr(invoice_id: str = Path(..., description="The invoice ID")):
    """Get OCR data for a specific invoice using the centralized database service"""
    try:
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            elif "unavailable" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        invoice_data = result.get("data")
        
        # Structure the OCR response using the invoice data from database service
        ocr_response = {
            "id": invoice_data.get("id"),
            "filename": invoice_data.get("file_name"),  # Use the correct field name from our schema
            "ocr_status": invoice_data.get("ocr_status"),
            "ocr_confidence": invoice_data.get("ocr_confidence", 0.0),
            "ocr_pages": invoice_data.get("ocr_pages", 0),
            "ocr_processing_time": invoice_data.get("ocr_processing_time", 0.0),
            "ocr_error": invoice_data.get("ocr_error"),
            "ocr_processed_at": invoice_data.get("ocr_processed_at"),
            "raw_text": invoice_data.get("ocr_text", ""),
            "structured_data": {
                # Map from our German schema fields back to English OCR fields for API consistency
                "invoice_number": invoice_data.get("rechnungsnummer"),
                "invoice_date": invoice_data.get("rechnungseingang"),
                "due_date": invoice_data.get("faelligkeit"),
                "vendor_name": invoice_data.get("rechnungssteller"),
                "vendor_address": invoice_data.get("vendor_address"),
                "customer_name": invoice_data.get("rechnungsempfaenger"),
                "customer_address": invoice_data.get("customer_address"),
                "subtotal": invoice_data.get("subtotal"),
                "tax_amount": invoice_data.get("tax_amount"),
                "total_amount": invoice_data.get("rechnungsbetrag"),
                "currency": invoice_data.get("currency"),
                "payment_terms": invoice_data.get("payment_terms"),
                "po_number": invoice_data.get("projekt"),
                "line_items": invoice_data.get("line_items", [])
            },
            # Extract from raw_ocr_data if available
            "entities": invoice_data.get("raw_ocr_data", {}).get("entities", []),
            "form_fields": invoice_data.get("raw_ocr_data", {}).get("form_fields", []),
            "tables": invoice_data.get("raw_ocr_data", {}).get("tables", [])
        }
        
        return ocr_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch OCR data for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch OCR data: {str(e)}")

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
    """Get invoice data formatted for the editor interface using the centralized database service"""
    try:
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            elif "unavailable" in error_msg.lower():
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
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        invoice_data = result.get("data")
        
        # Extract OCR entities for field values from raw_ocr_data
        raw_ocr_data = invoice_data.get("raw_ocr_data", {})
        ocr_entities = raw_ocr_data.get("entities", [])
        
        # Helper function to get value with fallback to OCR entities
        def get_field_value(db_field: str, entity_type: str) -> str:
            db_value = invoice_data.get(db_field, "")
            if db_value:
                return str(db_value)
            return _extract_entity_value(ocr_entities, entity_type)
        
        # Format data for editor interface using our German schema fields
        editor_data = {
            "pdfUrl": invoice_data.get("url", ""),
            "fields": {
                "rechnungsempfaenger": invoice_data.get("rechnungsempfaenger", ""),
                "rechnungssteller": invoice_data.get("rechnungssteller", ""),
                "projekt": invoice_data.get("projekt", ""),
                "gewerk": invoice_data.get("gewerk", ""),
                "rechnungsbetrag": invoice_data.get("rechnungsbetrag", 0),
                "rechnungseingang": invoice_data.get("rechnungseingang", ""),
                "faelligkeit": invoice_data.get("faelligkeit", ""),
                "skonto_datum": invoice_data.get("skonto_datum", ""),
                "skonto_prozent": invoice_data.get("skonto_prozent", 0),
                "rechnungsart": invoice_data.get("rechnungsart", "rechnung"),
                "kfw_anrechenbar": invoice_data.get("kfw_anrechenbare_kosten", False),
                "rechnungspruefung_email": invoice_data.get("rechnungspruefung", ""),
                "weiter_berechnen_an": invoice_data.get("weiter_berechnen_an", "")
            },
            "confidenceScores": {
                # Map confidence scores from OCR form fields
                **_get_field_confidence_scores(invoice_data),
                # Add default scores for fields not in OCR data
                "gewerk": 0.0,
                "skonto_datum": 0.0,
                "skonto_prozent": 0.0,
                "rechnungsart": 0.0,
                "kfw_anrechenbar": 0.0,
                "rechnungspruefung_email": 0.0,
                "weiter_berechnen_an": 0.0,
            },
            "filename": invoice_data.get("file_name", f"Invoice {invoice_id}")
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
    """Update invoice data from the editor interface using the centralized database service"""
    if not request_data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    fields = request_data.get("fields", {})
    
    try:
        # Check if invoice exists first
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            elif "unavailable" in error_msg.lower():
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
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        # Map German editor fields directly to our database schema fields
        # Only include fields that are actually present in the request
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
        
        logger.info(f"Received fields to update: {list(fields.keys())}")
        
        # Only update fields that are explicitly provided in the request
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in fields:
                value = fields[frontend_field]
                logger.info(f"Processing field {frontend_field} -> {db_field}: '{value}' (type: {type(value)})")
                
                # Handle all field types consistently
                if db_field in ["rechnungsbetrag", "skonto_prozent"]:
                    # Numeric fields
                    update_data[db_field] = float(value) if value not in [None, ""] else 0.0
                elif db_field == "kfw_anrechenbare_kosten":
                    # Boolean field
                    update_data[db_field] = bool(value) if value not in [None, ""] else False
                else:
                    # Text fields: explicitly allow empty strings to clear fields
                    update_data[db_field] = str(value) if value is not None else ""
        
        logger.info(f"Final update_data being sent to database: {update_data}")
        
        if update_data:
            update_result = db_service.update_invoice(invoice_id, update_data)
            
            if not update_result.get("success"):
                raise HTTPException(status_code=500, detail=update_result.get("error", "Update failed"))
        
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
