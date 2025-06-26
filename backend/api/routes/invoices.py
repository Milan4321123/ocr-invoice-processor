"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import logging

from services.database import db_service
from services.email_service import email_service

router = APIRouter()
logger = logging.getLogger(__name__)

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
        # Fetch invoices from database using correct table name
        response = db_service.client.table("invoices_clean").select("*").order("created_at", desc=True).execute()
        
        return {
            "invoices": response.data if response.data else [],
            "total": len(response.data) if response.data else 0
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Database query failed (falling back to demo mode): {error_msg}")
        
        # If table doesn't exist, return demo data
        if "does not exist" in error_msg or "relation" in error_msg:
            return {
                "invoices": [
                    {
                        "id": "demo-001",
                        "filename": "20250626_DEMO_INVOICE_001.pdf",
                        "url": "http://localhost:8000/api/mock-storage/demo_invoice_001.pdf",
                        "status": "uploaded",
                        "file_size": 245760,
                        "created_at": "2025-06-26T10:30:00Z",
                        "customer_name": "Demo Customer Ltd",
                        "vendor_name": "Demo Vendor GmbH",
                        "total_amount": 1250.00
                    },
                    {
                        "id": "demo-002", 
                        "filename": "20250625_DEMO_INVOICE_002.pdf",
                        "url": "http://localhost:8000/api/mock-storage/demo_invoice_002.pdf",
                        "status": "uploaded",
                        "file_size": 156432,
                        "created_at": "2025-06-25T14:20:00Z",
                        "customer_name": "Demo Construction AG",
                        "vendor_name": "Demo Electrical Services",
                        "total_amount": 3750.50
                    }
                ],
                "total": 2,
                "message": "Demo mode - Using sample data"
            }
        
        # For other errors, raise exception
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {error_msg}")

@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Get a specific invoice by ID"""
    
    if not db_service.is_available:
        # Mock response when database is not available
        raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
    
    try:
        # Fetch specific invoice from database using correct table name
        response = db_service.client.table("invoices_clean").select("*").eq("id", invoice_id).execute()
        
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
    
    if not db_service.is_available:
        # Mock response when database is not available
        return {
            "message": "Invoice deleted (Demo mode)",
            "invoice_id": invoice_id,
            "status": "success"
        }
    
    try:
        # First, check if the invoice exists using correct table name
        response = db_service.client.table("invoices_clean").select("*").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = response.data[0]
        
        # Delete from storage if URL exists and it's not a mock URL
        if invoice.get("file_path") and not invoice.get("file_path", "").startswith("http://localhost:8000/mock-storage/"):
            try:
                # Extract filename from file_path or use file_name field
                filename = invoice.get("file_name")
                if filename:
                    db_service.client.storage.from_("invoices").remove([filename])
            except Exception as storage_error:
                logger.warning(f"Failed to delete file from storage: {str(storage_error)}")
                # Continue with database deletion even if storage deletion fails
        
        # Delete from database
        delete_response = db_service.client.table("invoices_clean").delete().eq("id", invoice_id).execute()
        
        return {
            "message": "Invoice deleted successfully",
            "invoice_id": invoice_id,
            "filename": invoice.get("file_name"),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")

@router.get("/invoices/{invoice_id}/validate")
async def validate_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Validate if an invoice exists and is accessible"""
    
    if not db_service.is_available:
        # Mock validation for demo
        if invoice_id == "test-123":
            return {"valid": True, "invoice_id": invoice_id}
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Check if invoice exists in database using correct table name
        response = db_service.client.table("invoices_clean").select("id, file_name").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {
            "valid": True,
            "invoice_id": invoice_id,
            "filename": response.data[0].get("file_name")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate invoice: {str(e)}")

@router.get("/invoices/{invoice_id}/editor")
async def get_invoice_editor_data(invoice_id: str = Path(..., description="The invoice ID")):
    """Get invoice data formatted for the editor interface"""
    
    if not db_service.is_available:
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
                "filename": "test_invoice_1748551760.pdf"
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Fetch invoice data from database using correct table name
        response = db_service.client.table("invoices_clean").select("*").eq("id", invoice_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = response.data[0]
        
        # Construct proper PDF URL from file_path
        file_path = invoice_data.get("file_path", "")
        if file_path:
            # Construct full Supabase storage URL
            pdf_url = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{file_path}"
        else:
            pdf_url = ""
        
        # Format data for editor interface using correct field names
        editor_data = {
            "pdfUrl": pdf_url,
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
    """Update invoice data from the editor interface"""
    
    if not request_data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    fields = request_data.get("fields", {})
    editor_info = request_data.get("editor_info", {})
    
    if not db_service.is_available:
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
        # Update invoice data in database using correct table name and field mappings
        update_data = {
            # Basic information - using correct field names from schema
            "rechnungsempfaenger": fields.get("rechnungsempfaenger"),
            "rechnungssteller": fields.get("rechnungssteller"), 
            "projekt": fields.get("projekt"),
            "gewerk": fields.get("gewerk"),
            "weiter_berechnen_an": fields.get("weiter_berechnen_an"),
            
            # Financial information
            "rechnungsbetrag": fields.get("rechnungsbetrag"),
            "rechnungseingang": fields.get("rechnungseingang"),
            "faelligkeit": fields.get("faelligkeit"),
            "skonto_datum": fields.get("skonto_datum"),
            "skonto_prozent": fields.get("skonto_prozent"),
            "rechnungsart": fields.get("rechnungsart"),
            
            # Additional fields
            "kfw_anrechenbare_kosten": fields.get("kfw_anrechenbar"),
            "rechnungspruefung": fields.get("rechnungspruefung_email"),
            
            # Update timestamp
            "updated_at": "now()"
        }
        
        # Remove None values but keep empty strings and False values for proper field clearing
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if update_data:
            response = db_service.client.table("invoices_clean").update(update_data).eq("id", invoice_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Invoice not found or update failed")
        
        # Send email notification if editor information is provided
        email_sent = False
        if editor_info.get("editor_email") and editor_info.get("editor_name"):
            try:
                # Get updated invoice data for email
                invoice_response = db_service.client.table("invoices_clean").select("*").eq("id", invoice_id).execute()
                if invoice_response.data:
                    invoice_data = invoice_response.data[0]
                    
                    # Send editor notification email
                    email_result = await email_service.send_editor_notification(
                        invoice_data=invoice_data,
                        editor_email=editor_info["editor_email"],
                        editor_name=editor_info["editor_name"],
                        changes_summary=editor_info.get("changes_summary", []),
                        request_id=None
                    )
                    
                    if email_result["success"]:
                        email_sent = True
                        logger.info(f"Email notification sent successfully for invoice {invoice_id}")
                    else:
                        logger.warning(f"Email notification failed for invoice {invoice_id}: {email_result.get('error')}")
                        
            except ValueError as ve:
                if "No email provider configured" in str(ve):
                    logger.info(f"Email notification skipped for invoice {invoice_id}: No email provider configured (demo mode)")
                else:
                    logger.warning(f"Email notification error for invoice {invoice_id}: {str(ve)}")
            except Exception as email_error:
                logger.warning(f"Email notification error for invoice {invoice_id}: {str(email_error)}")
                # Continue with successful save response even if email fails
        
        return {
            "success": True,
            "message": "Invoice updated successfully",
            "invoice_id": invoice_id,
            "updated_fields": list(update_data.keys()),
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update editor data for invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")
