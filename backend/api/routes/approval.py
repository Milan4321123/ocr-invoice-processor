"""
Approval workflow endpoints for handling Bau-Leiter approve/reject actions.
Handles secure JWT token validation and invoice status updates.

NOTE: The main approval endpoint ({token}) has been moved to email_workflow.py
to avoid routing conflicts. This file now contains only the status endpoint.
"""
from fastapi import APIRouter, HTTPException, Request
import logging
from services.database import db_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["approval"])

@router.get("/status/{invoice_id}")
async def get_approval_status(invoice_id: str):
    """
    Get the current approval status of an invoice.
    Returns the approval status and related metadata.
    """
    try:
        # Get invoice from database
        result = db_service.get_invoice(invoice_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = result.get("data")
        
        # Extract approval-related information
        approval_info = {
            "invoice_id": invoice_id,
            "status": invoice_data.get("status"),
            "approval_status": invoice_data.get("approval_status"),
            "bauleiter_email": invoice_data.get("bauleiter_email"),
            "bauleiter_review_sent_at": invoice_data.get("bauleiter_review_sent_at"),
            "bauleiter_decision": invoice_data.get("bauleiter_decision"),
            "bauleiter_decision_at": invoice_data.get("bauleiter_decision_at"),
            "bauleiter_decision_by": invoice_data.get("bauleiter_decision_by")
        }
        
        return {
            "success": True,
            "data": approval_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting approval status for invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
