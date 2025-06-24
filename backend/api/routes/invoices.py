"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path, Body
from typing import List, Dict, Any, Optional
import logging

# Import database service and centralized field mapping
from services.database import db_service
from config.field_mappings import map_input_to_database, OCR_TO_DATABASE

router = APIRouter()
logger = logging.getLogger(__name__)

def _get_field_confidence_scores(invoice_data: Dict) -> Dict[str, float]:
    """Extract field-specific confidence scores from OCR form fields"""
    confidence_scores = {}
    ocr_form_fields = invoice_data.get("ocr_form_fields", [])
    ocr_entities = invoice_data.get("ocr_entities", [])
    
    # Default confidence based on overall OCR confidence
    default_confidence = invoice_data.get("ocr_confidence", 0.8)
    
    # ✅ Use centralized field mapping
    field_mapping = OCR_TO_DATABASE
    
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
        query_result = db_service.client.table("invoices_clean").select("*").eq("id", invoice_id).execute()
        
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
                "rechnungsbetrag": invoice_data.get("rechnungsbetrag"),        # ✅ NEW: Clean schema field
                "rechnungseingang": invoice_data.get("rechnungseingang"),      # ✅ NEW: Clean schema field
                "faelligkeit": invoice_data.get("faelligkeit"),
                "skonto_datum": invoice_data.get("skonto_datum"),
                "skonto_prozent": invoice_data.get("skonto_prozent"),
                "rechnungsart": invoice_data.get("rechnungsart"),
                "kfw_anrechenbare_kosten": invoice_data.get("kfw_anrechenbare_kosten"),  # ✅ NEW: Clean schema field
                "rechnungspruefung": invoice_data.get("rechnungspruefung"),              # ✅ NEW: Clean schema field
                "weiter_berechnen_an": invoice_data.get("weiter_berechnen_an")
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
    request_body: dict = Body(...)
):
    """Update invoice with comprehensive error handling and debugging"""
    
    # Enhanced logging for better debugging
    logger.info(f"🔄 INVOICE UPDATE REQUEST - ID: {invoice_id}")
    logger.info(f"📊 Raw request body: {request_body}")
    logger.info(f"📊 Request body type: {type(request_body)}")
    logger.info(f"📊 Request body keys: {list(request_body.keys()) if request_body else 'None'}")
    
    # Validate database availability
    if not db_service.is_available:
        logger.error("❌ Database service not available")
        raise HTTPException(
            status_code=503, 
            detail={
                "error": "DATABASE_UNAVAILABLE",
                "message": "Database service is not available",
                "timestamp": "2025-06-23T11:40:00Z"
            }
        )
    
    # Validate request body
    fields = request_body
    if not fields:
        logger.error("❌ No fields provided in request body")
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "NO_FIELDS_PROVIDED",
                "message": "Request body is empty or invalid",
                "received": request_body
            }
        )
    
    # Validate invoice exists before attempting update
    try:
        logger.info(f"🔍 Checking if invoice {invoice_id} exists...")
        existing_invoice_result = db_service.client.table("invoices_clean").select("id").eq("id", invoice_id).execute()
        if not existing_invoice_result.data:
            logger.error(f"❌ Invoice {invoice_id} not found in database")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "INVOICE_NOT_FOUND", 
                    "message": f"Invoice with ID {invoice_id} does not exist",
                    "invoice_id": invoice_id
                }
            )
        logger.info(f"✅ Invoice {invoice_id} exists")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error checking invoice existence: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "DATABASE_CHECK_FAILED",
                "message": f"Failed to verify invoice existence: {str(e)}"
            }
        )
    
    try:
        # Initialize update data dictionary
        # ✅ Use centralized field mapping instead of local mapping
        logger.info(f"🗺️ Starting field mapping using centralized mapping service...")
        
        # Map input fields to database fields using centralized mapping
        mapped_fields = map_input_to_database(fields)
        
        mapped_count = len(mapped_fields)
        logger.info(f"✅ Mapped {mapped_count} fields successfully using centralized mapping")
        
        # Validate that we have something to update
        if not mapped_fields:
            logger.warning(f"⚠️ No valid fields found for update")
            logger.info(f"📊 Received fields: {list(fields.keys())}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "NO_MAPPABLE_FIELDS",
                    "message": "No valid fields provided for update",
                    "received_fields": list(fields.keys())
                }
            )
        
        logger.info(f"📊 Final update data: {mapped_fields}")
        
        # Enhanced database update with comprehensive error handling
        logger.info(f"💾 Attempting database update...")
        
        try:
            result = db_service.client.table("invoices_clean").update(mapped_fields).eq("id", invoice_id).execute()
            
            # Enhanced result analysis
            if hasattr(result, 'error') and result.error:
                logger.error(f"❌ Supabase error: {result.error}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "SUPABASE_UPDATE_ERROR",
                        "message": f"Database update failed: {result.error}",
                        "attempted_fields": list(mapped_fields.keys())
                    }
                )
            
            if not result.data:
                logger.error(f"❌ No data returned from update - invoice may not exist")
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "UPDATE_NO_EFFECT", 
                        "message": "Update had no effect - invoice may not exist",
                        "invoice_id": invoice_id
                    }
                )
            
            # Success - log the result
            updated_record = result.data[0]
            logger.info(f"✅ Database update successful")
            logger.info(f"📊 Updated record ID: {updated_record.get('id')}")
            logger.info(f"📊 Updated timestamp: {updated_record.get('updated_at')}")
            
            # Verify critical field updates
            verification_log = {}
            for db_field, expected_value in mapped_fields.items():
                actual_value = updated_record.get(db_field)
                verification_log[db_field] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "match": str(expected_value) == str(actual_value)
                }
            
            logger.info(f"🔍 Field verification: {verification_log}")
            
            # Check for any mismatches
            mismatches = [field for field, check in verification_log.items() if not check["match"]]
            if mismatches:
                logger.warning(f"⚠️ Field value mismatches detected: {mismatches}")
            
            return {
                "status": "success", 
                "message": "Invoice updated successfully",
                "invoice_id": invoice_id,
                "updated_fields": list(mapped_fields.keys()),
                "verification": verification_log
            }
            
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"❌ Database update exception: {str(db_error)}")
            logger.error(f"❌ Exception type: {type(db_error).__name__}")
            logger.error(f"❌ Update data: {mapped_fields}")
            
            # Check for specific error types
            error_message = str(db_error).lower()
            if "column" in error_message and "not found" in error_message:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "COLUMN_NOT_FOUND",
                        "message": f"Database column missing: {str(db_error)}",
                        "attempted_fields": list(mapped_fields.keys()),
                        "suggestion": "Database schema may need migration"
                    }
                )
            elif "permission" in error_message or "access" in error_message:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "DATABASE_PERMISSION_ERROR", 
                        "message": f"Database permission error: {str(db_error)}"
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "DATABASE_UPDATE_FAILED",
                        "message": f"Database update failed: {str(db_error)}",
                        "exception_type": type(db_error).__name__
                    }
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")
