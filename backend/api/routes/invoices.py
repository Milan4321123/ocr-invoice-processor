"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from services.database import db_service
from services.email_service import email_service
from api.dependencies.auth import require_auth

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/invoices")
async def get_invoices():  # Removed authentication for demo
    """Get all invoices"""
    
    if not db_service.is_available:
        # Mock response when database is not available
        return {
            "invoices": [],
            "total": 0,
            "message": "Demo mode - Database not configured"
        }
    
    try:
        # Use centralized database service method
        result = db_service.get_all_invoices(limit=1000)
        
        if result["success"]:
            return {
                "invoices": result["data"],
                "total": len(result["data"])
            }
        else:
            raise Exception(result["error"])
        
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

@router.get("/invoices/pending-approval")
async def get_pending_bauleiter_approvals(bauleiter_email: Optional[str] = None):
    """
    Get invoices pending Bauleiter approval.
    Uses existing database service patterns for filtering.
    """
    try:
        # Use new database method that follows existing patterns
        result = db_service.get_pending_bauleiter_approvals(
            bauleiter_email=bauleiter_email,
            limit=100
        )
        
        if result["success"]:
            return {
                "success": True,
                "pending_approvals": result["data"],
                "total": len(result["data"]),
                "bauleiter_email": bauleiter_email
            }
        else:
            logger.warning(f"Failed to get pending approvals: {result['error']}")
            return {
                "success": True,
                "pending_approvals": [],
                "total": 0,
                "bauleiter_email": bauleiter_email,
                "message": "No pending approvals found"
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to get pending approvals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pending approvals: {str(e)}")

@router.get("/invoices/by-status/{status}")
async def get_invoices_by_status(status: str, limit: int = 100):
    """
    Get invoices filtered by status.
    Uses existing database service patterns.
    """
    try:
        # Use new database method that leverages existing query logic
        result = db_service.get_invoices_by_status(status=status, limit=limit)
        
        if result["success"]:
            return {
                "success": True,
                "invoices": result["data"],
                "total": len(result["data"]),
                "status": status
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to get invoices by status: {result['error']}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get invoices by status {status}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get invoices by status: {str(e)}")

@router.get("/invoices/skonto-due")
async def get_invoices_with_skonto_due(days_ahead: int = 7):
    """
    Get invoices with Skonto expiring within the specified number of days.
    
    Args:
        days_ahead: Number of days ahead to check for Skonto expiry (default: 7)
    """
    try:
        logger.info(f"🔍 Getting invoices with Skonto due within {days_ahead} days")
        
        # Get invoices with Skonto due
        result = db_service.get_invoices_with_skonto_due(days_ahead=days_ahead)
        
        if result["success"]:
            invoices = result["data"]
            logger.info(f"✅ Found {len(invoices)} invoices with Skonto due within {days_ahead} days")
            
            # Calculate additional metadata for each invoice
            for invoice in invoices:
                try:
                    # Calculate days until expiry
                    from datetime import datetime, timedelta
                    skonto_datum = invoice.get("skonto_datum")
                    if skonto_datum:
                        if isinstance(skonto_datum, str):
                            if "." in skonto_datum:
                                skonto_date = datetime.strptime(skonto_datum, "%d.%m.%Y")
                            elif "-" in skonto_datum:
                                skonto_date = datetime.strptime(skonto_datum, "%Y-%m-%d")
                            else:
                                skonto_date = datetime.strptime(skonto_datum, "%Y%m%d")
                        else:
                            skonto_date = skonto_datum
                        
                        invoice["days_until_expiry"] = (skonto_date - datetime.now()).days
                        
                        # Calculate potential savings
                        total_amount = invoice.get("rechnungsbetrag")
                        skonto_prozent = invoice.get("skonto_prozent")
                        if total_amount and skonto_prozent:
                            invoice["potential_savings"] = round(float(total_amount) * float(skonto_prozent) / 100, 2)
                        else:
                            invoice["potential_savings"] = 0
                    else:
                        invoice["days_until_expiry"] = None
                        invoice["potential_savings"] = 0
                        
                except Exception as e:
                    logger.warning(f"Failed to calculate metadata for invoice {invoice.get('id')}: {e}")
                    invoice["days_until_expiry"] = None
                    invoice["potential_savings"] = 0
            
            return {
                "success": True,
                "invoices": invoices,
                "total": len(invoices),
                "days_ahead": days_ahead,
                "retrieved_at": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ Failed to get invoices with Skonto due: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get invoices with Skonto due: {result.get('error')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get invoices with Skonto due: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get invoices with Skonto due: {str(e)}"
        )

@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str = Path(..., description="The invoice ID")):
    """Get a specific invoice by ID"""
    
    if not db_service.is_available:
        # Mock response when database is not available
        raise HTTPException(status_code=404, detail="Invoice not found (Demo mode)")
    
    try:
        # Use centralized database service method
        result = db_service.get_invoice(invoice_id)
        
        if result["success"]:
            return {
                "status": "success",
                "invoice": result["data"]
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
        # Use centralized database service method
        result = db_service.delete_invoice(invoice_id)
        
        if result["success"]:
            return {
                "message": "Invoice deleted successfully",
                "invoice_id": invoice_id,
                "filename": result.get("filename"),
                "status": "success"
            }
        else:
            if "not found" in result["error"].lower():
                raise HTTPException(status_code=404, detail="Invoice not found")
            else:
                raise Exception(result["error"])
        
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
        # Use centralized database service method
        result = db_service.get_invoice(invoice_id)
        
        if result["success"]:
            return {
                "valid": True,
                "invoice_id": invoice_id,
                "filename": result["data"].get("file_name")
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
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
        # Use centralized database service method
        result = db_service.get_invoice(invoice_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = result["data"]
        
        # Construct proper PDF URL from file_path
        file_path = invoice_data.get("file_path", "")
        if file_path:
            # Determine the correct bucket based on file_path prefix
            if file_path.startswith('folder_watcher/'):
                bucket_name = "folderwatcher"
                # Remove the prefix since it's now part of the bucket structure
                file_name = file_path.replace('folder_watcher/', '')
            elif file_path.startswith('manual/'):
                bucket_name = "manual"
                file_name = file_path.replace('manual/', '')
            else:
                # Default for drag-drop uploads
                bucket_name = "invoices"
                file_name = file_path
            
            # Construct full Supabase storage URL with correct bucket
            pdf_url = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/{bucket_name}/{file_name}"
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
        # Update invoice data using centralized database service
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
            "rechnungspruefung": fields.get("rechnungspruefung_email")
        }
        
        # Remove None values but keep empty strings and False values for proper field clearing
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Update invoice fields first
        if update_data:
            field_result = db_service.update_invoice(invoice_id, update_data)
            if not field_result["success"]:
                raise HTTPException(status_code=500, detail=f"Failed to update invoice fields: {field_result['error']}")
        
        # Update status to "in Bearbeitung" stage (edited + under_review)
        status_result = db_service.update_invoice_to_editing_stage(invoice_id)
        if not status_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to update invoice status: {status_result['error']}")
        
        logger.info(f"✅ Invoice {invoice_id} updated and moved to 'in Bearbeitung' stage")
        
        # Send email notification if editor information is provided
        email_sent = False
        if editor_info.get("editor_email") and editor_info.get("editor_name"):
            try:
                # Get updated invoice data for email
                updated_result = db_service.get_invoice(invoice_id)
                if updated_result["success"]:
                    invoice_data = updated_result["data"]
                    
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

@router.put("/invoices/{invoice_id}/complete")
async def complete_invoice(
    invoice_id: str = Path(..., description="The invoice ID"),
    request_data: Dict[str, Any] = None
):
    """Mark invoice as completed with review status and trigger Bauleiter approval email"""
    
    if not request_data:
        raise HTTPException(status_code=400, detail="No completion data provided")
    
    completion_info = request_data.get("completion_info", {})
    
    if not db_service.is_available:
        # Mock success for demo
        if invoice_id == "test-123":
            return {
                "success": True,
                "message": "Invoice marked as completed (demo mode)",
                "invoice_id": invoice_id,
                "completion_status": "completed_review",
                "email_sent": False
            }
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Use centralized database service to complete invoice
        completion_info = request_data.get("completion_info", {})
        
        result = db_service.update_invoice_to_completed_stage(
            invoice_id=invoice_id,
            completed_by=completion_info.get("completed_by"),
            notes=completion_info.get("completion_notes")
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to complete invoice: {result['error']}")
        
        updated_invoice = result["data"]
        
        # No automatic email sending - let user control via dashboard "An Bauleiter senden" button
        logger.info(f"Invoice {invoice_id} marked as completed - ready for manual Bauleiter sending via dashboard")
        
        return {
            "success": True,
            "message": "Invoice marked as completed successfully - ready to send to Bauleiter via dashboard",
            "invoice_id": invoice_id,
            "completion_status": updated_invoice.get("review_status", "completed_review"),
            "completed_at": updated_invoice.get("reviewed_at"),
            "email_sent": False,  # No automatic email - user controls via dashboard
            "email_note": "Use 'An Bauleiter senden' button in dashboard to send approval email"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete invoice: {str(e)}")

@router.post("/invoices/{invoice_id}/send-to-bauleiter")
async def send_invoice_to_bauleiter(
    invoice_id: str = Path(..., description="Invoice ID"),
    request_data: Dict[str, Any] = None
):
    """
    Send completed invoice to Bauleiter for approval.
    Uses existing database service patterns and email service.
    """
    try:
        # Validate request data
        if not request_data:
            raise HTTPException(status_code=400, detail="Request data is required")
        
        bauleiter_email = request_data.get("bauleiter_email")
        if not bauleiter_email:
            raise HTTPException(status_code=400, detail="bauleiter_email is required")
        
        # Get invoice details using existing database service
        invoice_result = db_service.get_invoice(invoice_id)
        if not invoice_result["success"]:
            raise HTTPException(status_code=404, detail=f"Invoice not found: {invoice_result['error']}")
        
        invoice_data = invoice_result["data"]
        
        # Check if invoice is in correct status for sending to Bauleiter
        current_status = invoice_data.get("status")
        if current_status not in ["completed", "edit_completed"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invoice must be completed before sending to Bauleiter. Current status: {current_status}"
            )
        
        # Update invoice status to 'sent to Bauleiter' using new database method
        sent_by = request_data.get("sent_by", "dashboard_user")
        status_result = db_service.update_invoice_sent_to_bauleiter(
            invoice_id=invoice_id,
            bauleiter_email=bauleiter_email,
            sent_by=sent_by
        )
        
        if not status_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to update invoice status: {status_result['error']}")
        
        # Send Bauleiter approval email using existing email service
        email_sent = False
        email_error = None
        
        try:
            # Prepare email data
            editor_name = request_data.get("editor_name", sent_by)
            editor_email = request_data.get("editor_email", f"{sent_by}@company.com")
            changes_summary = request_data.get("changes_summary", [])
            
            # Send approval request email using existing service
            email_result = await email_service.send_bauleiter_approval_request(
                invoice_data=invoice_data,
                bauleiter_email=bauleiter_email,
                editor_name=editor_name,
                editor_email=editor_email,
                changes_summary=changes_summary
            )
            
            if email_result["success"]:
                email_sent = True
                logger.info(f"✅ Invoice {invoice_id} sent to Bauleiter {bauleiter_email} successfully")
            else:
                email_error = email_result.get("error", "Unknown email error")
                logger.warning(f"❌ Failed to send email to Bauleiter: {email_error}")
                
        except Exception as e:
            email_error = str(e)
            logger.error(f"❌ Error sending email to Bauleiter for invoice {invoice_id}: {str(e)}")
        
        updated_invoice = status_result["data"]
        
        return {
            "success": True,
            "message": f"Invoice sent to Bauleiter {bauleiter_email}",
            "invoice_id": invoice_id,
            "status": updated_invoice.get("status"),
            "bauleiter_email": bauleiter_email,
            "sent_at": updated_invoice.get("sent_to_bauleiter_at"),
            "email_sent": email_sent,
            "email_error": email_error
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send invoice {invoice_id} to Bauleiter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send invoice to Bauleiter: {str(e)}")

@router.post("/invoices/{invoice_id}/send-skonto-reminder")
async def send_skonto_reminder(
    invoice_id: str = Path(..., description="Invoice ID"),
    recipient_email: str = Query(None, description="Recipient email address"),
    recipient_name: str = Query(None, description="Recipient name")
):
    """
    Send Skonto reminder email for a specific invoice.
    
    Args:
        invoice_id: The ID of the invoice
        recipient_email: Optional recipient email (defaults to bauleiter_email)
        recipient_name: Optional recipient name
    """
    try:
        logger.info(f"📧 Sending Skonto reminder for invoice {invoice_id}")
        
        # Get invoice data
        invoice_result = db_service.get_invoice_by_id(invoice_id)
        if not invoice_result["success"]:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = invoice_result["data"]
        
        # Validate that invoice has Skonto data
        if not invoice_data.get("skonto_datum") or not invoice_data.get("skonto_prozent"):
            raise HTTPException(
                status_code=400,
                detail="Invoice does not have Skonto data (missing skonto_datum or skonto_prozent)"
            )
        
        # Check if invoice has already been processed
        skonto_decision = invoice_data.get("skonto_decision")
        if skonto_decision in ["taken", "missed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invoice Skonto has already been processed as '{skonto_decision}'"
            )
        
        # Use provided recipient email or fallback to defaults
        if not recipient_email:
            # Default to bauleiter_email or a configured default
            recipient_email = invoice_data.get("bauleiter_email") or "default@company.com"
            logger.info(f"📧 Using default recipient email: {recipient_email}")
        
        # Send Skonto reminder email
        email_result = await email_service.send_skonto_reminder(
            invoice_data=invoice_data,
            recipient_email=recipient_email,
            recipient_name=recipient_name
        )
        
        if email_result["success"]:
            # Update database to mark reminder as sent
            db_service.update_skonto_reminder_sent(invoice_id)
            
            logger.info(f"✅ Skonto reminder sent successfully for invoice {invoice_id}")
            return {
                "success": True,
                "message": f"Skonto reminder sent to {recipient_email}",
                "invoice_id": invoice_id,
                "recipient_email": recipient_email,
                "message_id": email_result.get("message_id"),
                "potential_savings": email_result.get("potential_savings"),
                "days_until_expiry": email_result.get("days_until_expiry"),
                "sent_at": email_result.get("timestamp")
            }
        else:
            logger.error(f"❌ Failed to send Skonto reminder: {email_result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send Skonto reminder: {email_result.get('error')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send Skonto reminder for invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send Skonto reminder: {str(e)}"
        )

@router.put("/invoices/{invoice_id}")
async def update_invoice(
    invoice_id: str = Path(..., description="Invoice ID"),
    update_data: Dict[str, Any] = None
):
    """
    Update invoice fields including Skonto decisions.
    Supports updating any invoice field, with special handling for Skonto decisions.
    """
    try:
        logger.info(f"🔄 Updating invoice {invoice_id} with data: {update_data}")
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Get current invoice data
        current_invoice = db_service.get_invoice_by_id(invoice_id)
        if not current_invoice["success"]:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = current_invoice["data"]
        
        # Special handling for Skonto decisions
        if "skonto_decision" in update_data:
            skonto_decision = update_data["skonto_decision"]
            
            # Validate Skonto decision
            valid_decisions = ["pending", "taken", "missed", "not_applicable"]
            if skonto_decision not in valid_decisions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid skonto_decision. Must be one of: {valid_decisions}"
                )
            
            # If marking as taken, ensure actual_skonto_savings is set
            if skonto_decision == "taken" and "actual_skonto_savings" not in update_data:
                # Calculate potential savings if not provided
                amount = invoice_data.get("rechnungsbetrag", 0)
                percentage = invoice_data.get("skonto_prozent", 0)
                if amount and percentage:
                    update_data["actual_skonto_savings"] = float(amount) * float(percentage) / 100
            
            # If marking as missed, ensure actual_skonto_savings is 0
            if skonto_decision == "missed":
                update_data["actual_skonto_savings"] = 0.0
            
            logger.info(f"📊 Marking Skonto as {skonto_decision} for invoice {invoice_id}")
        
        # Update invoice in database
        result = db_service.update_invoice(invoice_id, update_data)
        
        if result["success"]:
            logger.info(f"✅ Invoice {invoice_id} updated successfully")
            return {
                "success": True,
                "message": "Invoice updated successfully",
                "invoice_id": invoice_id,
                "updated_fields": list(update_data.keys()),
                "data": result["data"],
                "updated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update invoice: {result.get('error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update invoice: {str(e)}"
        )
