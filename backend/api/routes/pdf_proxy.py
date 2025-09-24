"""
PDF Proxy Route - Secure PDF serving with authentication
Handles private Supabase storage buckets with proper access control
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
import httpx
import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.database import db_service
from api.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

@router.get("/view/{invoice_id}")
async def get_pdf(
    invoice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Serve PDF files securely with authentication.
    Generates signed URLs for private Supabase storage buckets.
    """
    try:
        # Get invoice details from database
        invoice = await db_service.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        file_path = invoice.get("file_path")
        if not file_path:
            raise HTTPException(status_code=404, detail="PDF file not found for this invoice")
        
        # Get Supabase client with service role key
        supabase_url = os.getenv("SUPA_URL")
        service_key = os.getenv("SUPA_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            raise HTTPException(status_code=500, detail="Storage configuration missing")
        
        try:
            from supabase import create_client
            client = create_client(supabase_url, service_key)
            
            # Determine bucket name
            if file_path.startswith('folder_watcher/'):
                bucket_name = "folderwatcher"
                file_name = file_path.replace('folder_watcher/', '')
            elif file_path.startswith('manual/'):
                bucket_name = "manual" 
                file_name = file_path.replace('manual/', '')
            else:
                bucket_name = "invoices"
                file_name = file_path
            
            # Generate signed URL
            signed_url_response = client.storage.from_(bucket_name).create_signed_url(file_name, 3600)
            
            if not signed_url_response or 'signedURL' not in signed_url_response:
                raise HTTPException(status_code=404, detail="Could not generate access URL for PDF")
            
            signed_url = signed_url_response['signedURL']
            
            # Fetch the PDF content and stream it
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(signed_url)
                
                if response.status_code != 200:
                    raise HTTPException(status_code=404, detail="PDF file not accessible")
                
                # Stream the PDF content with proper headers
                return StreamingResponse(
                    iter([response.content]),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"inline; filename={os.path.basename(file_path)}",
                        "Cache-Control": "private, max-age=3600"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error accessing PDF {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error accessing PDF: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in PDF service: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/download/{invoice_id}")
async def download_pdf(
    invoice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Download PDF files securely with authentication.
    Forces download instead of inline viewing.
    """
    try:
        # Get invoice details from database
        invoice = await db_service.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        file_path = invoice.get("file_path")
        if not file_path:
            raise HTTPException(status_code=404, detail="PDF file not found for this invoice")
        
        # Get Supabase client with service role key
        supabase_url = os.getenv("SUPA_URL")
        service_key = os.getenv("SUPA_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            raise HTTPException(status_code=500, detail="Storage configuration missing")
        
        try:
            from supabase import create_client
            client = create_client(supabase_url, service_key)
            
            # Determine bucket name  
            if file_path.startswith('folder_watcher/'):
                bucket_name = "folderwatcher"
                file_name = file_path.replace('folder_watcher/', '')
            elif file_path.startswith('manual/'):
                bucket_name = "manual"
                file_name = file_path.replace('manual/', '')
            else:
                bucket_name = "invoices"
                file_name = file_path
            
            # Generate signed URL
            signed_url_response = client.storage.from_(bucket_name).create_signed_url(file_name, 3600)
            
            if not signed_url_response or 'signedURL' not in signed_url_response:
                raise HTTPException(status_code=404, detail="Could not generate download URL for PDF")
            
            signed_url = signed_url_response['signedURL']
            
            # Fetch the PDF content and stream it as download
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(signed_url)
                
                if response.status_code != 200:
                    raise HTTPException(status_code=404, detail="PDF file not accessible")
                
                # Stream the PDF content with download headers
                filename = os.path.basename(file_path)
                return StreamingResponse(
                    iter([response.content]),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}",
                        "Cache-Control": "private, max-age=3600"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error downloading PDF {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in PDF download service: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")