"""Invoice management route handlers"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any, Optional
import logging
from supabase import Client

router = APIRouter()
logger = logging.getLogger(__name__)

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
