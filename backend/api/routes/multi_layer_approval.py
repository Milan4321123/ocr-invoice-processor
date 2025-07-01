"""
Multi-Layer Approval Management API Routes
Handles creation and management of approval hierarchies for invoices
All database operations go through centralized database service only
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List, Any, Optional
import logging
from pydantic import BaseModel

from services.database import db_service
from services.email_service import EmailService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/multi-approval", tags=["multi-layer-approval"])

# Pydantic models for request validation
class ApprovalLayer(BaseModel):
    layer_order: int
    approver_email: str
    approver_role: str
    layer_name: str
    required: bool = True

class CreateApprovalHierarchy(BaseModel):
    invoice_id: str
    approval_layers: List[ApprovalLayer]
    editor_name: str
    editor_email: str
    auto_send_first_layer: bool = True

class ApprovalLayerResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/create-hierarchy", response_model=ApprovalLayerResponse)
async def create_approval_hierarchy(request: CreateApprovalHierarchy):
    """
    Create a multi-layer approval hierarchy for an invoice.
    All database operations happen through centralized database service only.
    """
    try:
        logger.info(f"🔄 Creating approval hierarchy for invoice {request.invoice_id} with {len(request.approval_layers)} layers")
        
        # Validate invoice exists
        invoice_result = db_service.get_invoice(request.invoice_id)
        if not invoice_result["success"]:
            logger.error(f"❌ Invoice {request.invoice_id} not found")
            raise HTTPException(status_code=404, detail=f"Invoice {request.invoice_id} not found")
        
        invoice_data = invoice_result["data"]
        
        # Convert Pydantic models to dict for database service
        layers_data = []
        for layer in request.approval_layers:
            layers_data.append({
                "layer_order": layer.layer_order,
                "approver_email": layer.approver_email,
                "approver_role": layer.approver_role,
                "layer_name": layer.layer_name,
                "required": layer.required
            })
        
        # Create approval hierarchy through centralized database service
        hierarchy_result = db_service.create_approval_hierarchy(
            invoice_id=request.invoice_id,
            approval_layers=layers_data
        )
        
        if not hierarchy_result["success"]:
            logger.error(f"❌ Failed to create approval hierarchy: {hierarchy_result['error']}")
            raise HTTPException(status_code=500, detail=f"Failed to create approval hierarchy: {hierarchy_result['error']}")
        
        # Optionally send email to first layer approver
        if request.auto_send_first_layer and layers_data:
            first_layer = layers_data[0]
            
            try:
                email_service = EmailService()
                email_result = await email_service.send_multi_layer_approval_request(
                    invoice_data=invoice_data,
                    approval_layer=first_layer,
                    editor_name=request.editor_name,
                    editor_email=request.editor_email
                )
                
                if email_result["success"]:
                    logger.info(f"✅ Sent first layer approval email to {first_layer['approver_email']}")
                else:
                    logger.warning(f"⚠️ Failed to send first layer approval email: {email_result.get('error')}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to send first layer approval email: {e}")
        
        logger.info(f"✅ Successfully created approval hierarchy for invoice {request.invoice_id}")
        
        return ApprovalLayerResponse(
            success=True,
            message=f"Approval hierarchy created with {len(layers_data)} layers",
            data={
                "invoice_id": request.invoice_id,
                "total_layers": len(layers_data),
                "hierarchy": hierarchy_result["data"],
                "first_layer_email_sent": request.auto_send_first_layer
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating approval hierarchy: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/hierarchy/{invoice_id}", response_model=ApprovalLayerResponse)
async def get_approval_hierarchy(invoice_id: str):
    """
    Get the approval hierarchy for a specific invoice.
    All database operations happen through centralized database service only.
    """
    try:
        logger.info(f"📋 Getting approval hierarchy for invoice {invoice_id}")
        
        # Get hierarchy through centralized database service
        hierarchy_result = db_service.get_approval_hierarchy(invoice_id)
        
        if not hierarchy_result["success"]:
            logger.error(f"❌ Failed to get approval hierarchy: {hierarchy_result['error']}")
            raise HTTPException(status_code=500, detail=f"Failed to get approval hierarchy: {hierarchy_result['error']}")
        
        # Get current invoice status
        invoice_result = db_service.get_invoice(invoice_id)
        invoice_data = invoice_result["data"] if invoice_result["success"] else {}
        
        return ApprovalLayerResponse(
            success=True,
            message="Approval hierarchy retrieved successfully",
            data={
                "invoice_id": invoice_id,
                "hierarchy": hierarchy_result["data"],
                "current_layer": invoice_data.get("current_approval_layer"),
                "total_layers": invoice_data.get("total_approval_layers"),
                "status": invoice_data.get("status"),
                "approval_status": invoice_data.get("approval_status")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting approval hierarchy: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/pending/{approver_email}", response_model=ApprovalLayerResponse)
async def get_pending_approvals_for_user(approver_email: str, limit: int = 50):
    """
    Get all pending approvals for a specific user across all layers.
    All database operations happen through centralized database service only.
    """
    try:
        logger.info(f"📋 Getting pending approvals for user {approver_email}")
        
        # Get pending approvals through centralized database service
        approvals_result = db_service.get_pending_approvals_for_user(approver_email, limit)
        
        if not approvals_result["success"]:
            logger.error(f"❌ Failed to get pending approvals: {approvals_result['error']}")
            raise HTTPException(status_code=500, detail=f"Failed to get pending approvals: {approvals_result['error']}")
        
        pending_approvals = approvals_result["data"]
        
        # Enhance data with additional context
        enhanced_approvals = []
        for approval in pending_approvals:
            enhanced_approval = {
                **approval,
                "invoice_summary": {
                    "invoice_number": approval.get("invoices_clean", {}).get("rechnungsnummer"),
                    "supplier": approval.get("invoices_clean", {}).get("lieferant"),
                    "amount": approval.get("invoices_clean", {}).get("rechnungsbetrag"),
                    "project": approval.get("invoices_clean", {}).get("projekt"),
                    "uploaded_at": approval.get("invoices_clean", {}).get("created_at")
                }
            }
            enhanced_approvals.append(enhanced_approval)
        
        return ApprovalLayerResponse(
            success=True,
            message=f"Found {len(pending_approvals)} pending approvals",
            data={
                "approver_email": approver_email,
                "pending_approvals": enhanced_approvals,
                "total_count": len(pending_approvals)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting pending approvals: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/send-layer-email/{invoice_id}/{layer_order}", response_model=ApprovalLayerResponse)
async def send_approval_email_for_layer(invoice_id: str, layer_order: int, editor_name: str, editor_email: str):
    """
    Send approval email for a specific layer.
    All database operations happen through centralized database service only.
    """
    try:
        logger.info(f"📧 Sending approval email for invoice {invoice_id}, layer {layer_order}")
        
        # Get invoice data through centralized database service
        invoice_result = db_service.get_invoice(invoice_id)
        if not invoice_result["success"]:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        
        invoice_data = invoice_result["data"]
        
        # Get approval hierarchy through centralized database service
        hierarchy_result = db_service.get_approval_hierarchy(invoice_id)
        if not hierarchy_result["success"]:
            raise HTTPException(status_code=404, detail=f"No approval hierarchy found for invoice {invoice_id}")
        
        # Find the specific layer
        target_layer = None
        for layer in hierarchy_result["data"]:
            if layer["layer_order"] == layer_order:
                target_layer = layer
                break
        
        if not target_layer:
            raise HTTPException(status_code=404, detail=f"Approval layer {layer_order} not found")
        
        # Send email through email service (no direct DB access)
        email_service = EmailService()
        email_result = await email_service.send_multi_layer_approval_request(
            invoice_data=invoice_data,
            approval_layer=target_layer,
            editor_name=editor_name,
            editor_email=editor_email
        )
        
        if not email_result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to send approval email: {email_result.get('error')}")
        
        return ApprovalLayerResponse(
            success=True,
            message=f"Approval email sent for layer {layer_order}",
            data={
                "invoice_id": invoice_id,
                "layer_order": layer_order,
                "approver_email": target_layer["approver_email"],
                "email_result": email_result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error sending approval email: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{invoice_id}", response_model=ApprovalLayerResponse)
async def get_approval_status(invoice_id: str):
    """
    Get comprehensive approval status for an invoice.
    All database operations happen through centralized database service only.
    """
    try:
        logger.info(f"📊 Getting approval status for invoice {invoice_id}")
        
        # Get invoice data through centralized database service
        invoice_result = db_service.get_invoice(invoice_id)
        if not invoice_result["success"]:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        
        invoice_data = invoice_result["data"]
        
        # Get approval hierarchy through centralized database service
        hierarchy_result = db_service.get_approval_hierarchy(invoice_id)
        
        approval_status = {
            "invoice_id": invoice_id,
            "invoice_status": invoice_data.get("status"),
            "approval_status": invoice_data.get("approval_status"),
            "current_layer": invoice_data.get("current_approval_layer"),
            "total_layers": invoice_data.get("total_approval_layers"),
            "has_multi_layer": hierarchy_result["success"] and len(hierarchy_result["data"]) > 0,
            "hierarchy": hierarchy_result["data"] if hierarchy_result["success"] else [],
            "approval_method": invoice_data.get("approval_method"),
            "approved_at": invoice_data.get("approved_at"),
            "final_approver": invoice_data.get("final_approver")
        }
        
        return ApprovalLayerResponse(
            success=True,
            message="Approval status retrieved successfully",
            data=approval_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting approval status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
