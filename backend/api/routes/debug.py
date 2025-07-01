"""Debug endpoint to test database connection"""
from fastapi import APIRouter
from services.database import db_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/debug/database")
async def debug_database():
    """Debug database connection and invoice count"""
    try:
        # Check if database is available
        if not db_service.is_available:
            return {
                "database_available": False,
                "error": "Database service not available",
                "client": str(db_service.client)
            }
        
        # Try to get a count of invoices
        response = db_service._client.table(db_service.table_name).select("*", count="exact").execute()
        
        return {
            "database_available": True,
            "table_name": db_service.table_name,
            "invoice_count": response.count,
            "raw_data": response.data[:5] if response.data else [],  # First 5 invoices
            "supabase_url": db_service._client.supabase_url if db_service._client else None
        }
        
    except Exception as e:
        logger.error(f"Database debug failed: {e}")
        return {
            "database_available": False,
            "error": str(e),
            "table_name": db_service.table_name
        }
