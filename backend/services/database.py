"""
Centralized database service layer for OCR Invoice Processor.
Handles all Supabase database operations in one place.
"""
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
import os
import logging
from dotenv import load_dotenv
from config.field_mappings import (
    map_input_to_database, 
    map_database_to_api, 
    validate_database_fields,
    DATABASE_FIELDS
)

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseService:
    """Centralized database service for Supabase operations"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client"""
        # Check both naming conventions for backward compatibility
        url = os.getenv("SUPABASE_URL") or os.getenv("SUPA_URL")
        key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPA_KEY")
        
        if url and key:
            try:
                self._client = create_client(url, key)
                logger.info(f"Database service initialized successfully with URL: {url[:50]}...")
            except Exception as e:
                logger.error(f"Failed to initialize database client: {e}")
                self._client = None
        else:
            logger.warning("Database configuration not found. Service running in offline mode.")
    
    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Check if database service is available"""
        return self._client is not None
    
    # Field mapping between database columns and application fields
    @staticmethod
    def _map_db_to_app(db_record: Dict[str, Any]) -> Dict[str, Any]:
        """Map database column names to application field names"""
        if not db_record:
            return db_record
        
        # ✅ Use centralized field mapping
        mapped = map_database_to_api(db_record, include_english_aliases=True)
        
        # Add URL field based on file_path
        if 'file_path' in mapped and mapped['file_path']:
            # Construct the public URL for Supabase storage
            mapped['url'] = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{mapped['file_path']}"
        
        # Map file_name to filename for legacy compatibility
        if 'file_name' in mapped:
            mapped['filename'] = mapped['file_name']
        
        return mapped
    
    def _map_app_to_db(self, data: dict) -> dict:
        """Map application data to database schema using centralized mapping"""
        
        # ✅ Use centralized field mapping
        mapped_data = map_input_to_database(data)
        
        # Validate that only database fields are included
        validated_data = validate_database_fields(mapped_data)
                
        return validated_data

    # Dropdown Operations
    def get_dropdown_options(self, field_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get dropdown options from database"""
        if not self.is_available:
            logger.warning("Database unavailable for dropdown options query")
            return {}
        
        try:
            query = self._client.table("dropdown_options").select("*")
            if field_name:
                query = query.eq("field_name", field_name)
            
            response = query.eq("is_active", True).order("field_name, label").execute()
            
            if not response.data:
                logger.warning(f"No dropdown options found for field: {field_name or 'all fields'}")
                return {}
            
            # Group by field_name
            grouped_options = {}
            for row in response.data:
                field = row["field_name"]
                if field not in grouped_options:
                    grouped_options[field] = []
                
                option = {
                    "value": row["value"],
                    "label": row["label"],
                    "is_default": row["is_default"],
                    "id": row["id"],
                    "metadata": row.get("metadata", {})
                }
                grouped_options[field].append(option)
            
            return grouped_options
            
        except Exception as e:
            logger.error(f"Database error when fetching dropdown options: {e}")
            return {}
    
    def add_dropdown_option(self, field_name: str, value: str, label: str, 
                          is_default: bool = False, metadata: Dict = None) -> Dict[str, Any]:
        """Add a new dropdown option to database"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot persist new option")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            new_option = {
                "field_name": field_name,
                "value": value,
                "label": label,
                "is_default": is_default,
                "metadata": metadata or {}
            }
            
            response = self._client.table("dropdown_options").insert(new_option).execute()
            
            if response.data:
                logger.info(f"Successfully added dropdown option: {field_name} - {label}")
                return {"success": True, "data": response.data[0]}
            else:
                logger.error(f"Failed to add dropdown option: {response}")
                return {"success": False, "error": "Insert failed"}
                
        except Exception as e:
            logger.error(f"Database error when adding dropdown option: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_dropdown_option(self, field_name: str, value: str) -> Dict[str, Any]:
        """Delete a dropdown option from database (soft delete)"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot delete option")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table("dropdown_options")
                       .update({"is_active": False})
                       .eq("field_name", field_name)
                       .eq("value", value)
                       .execute())
            
            if response.data:
                logger.info(f"Successfully deleted dropdown option: {field_name} - {value}")
                return {"success": True, "data": response.data}
            else:
                logger.error(f"Failed to delete dropdown option: {response}")
                return {"success": False, "error": "Delete failed"}
                
        except Exception as e:
            logger.error(f"Database error when deleting dropdown option: {e}")
            return {"success": False, "error": str(e)}
    
    # Invoice Operations
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice record"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot create invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Map application fields to database fields
            db_data = self._map_app_to_db(invoice_data)
            
            response = self._client.table("invoices_clean").insert(db_data).execute()
            
            if response.data:
                # Map response back to application fields
                mapped_data = self._map_db_to_app(response.data[0])
                logger.info(f"Successfully created invoice: {mapped_data['id']}")
                return {"success": True, "data": mapped_data}
            else:
                logger.error(f"Failed to create invoice: {response}")
                return {"success": False, "error": "Insert failed"}
                
        except Exception as e:
            logger.error(f"Database error when creating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get an invoice by ID"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot fetch invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table("invoices_clean")
                       .select("*")
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data:
                # Map database fields to application fields
                mapped_data = self._map_db_to_app(response.data[0])
                return {"success": True, "data": mapped_data}
            else:
                return {"success": False, "error": "Invoice not found"}
                
        except Exception as e:
            logger.error(f"Database error when fetching invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def update_invoice(self, invoice_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an invoice record"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot update invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Map application fields to database fields
            db_data = self._map_app_to_db(update_data)
            
            response = (self._client.table("invoices_clean")
                       .update(db_data)
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data:
                # Map response back to application fields
                mapped_data = self._map_db_to_app(response.data[0])
                logger.info(f"Successfully updated invoice: {invoice_id}")
                return {"success": True, "data": mapped_data}
            else:
                logger.error(f"Failed to update invoice: {response}")
                return {"success": False, "error": "Update failed"}
                
        except Exception as e:
            logger.error(f"Database error when updating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def get_invoices(self, limit: int = 50, offset: int = 0, 
                     filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get invoices with pagination and filtering"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot fetch invoices")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            query = self._client.table("invoices_clean").select("*")
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if value:
                        query = query.eq(field, value)
            
            # Apply pagination and ordering
            response = (query.order("created_at", desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            
            if response.data is not None:
                # Map all invoice records from database to application fields
                mapped_data = [self._map_db_to_app(invoice) for invoice in response.data]
                return {"success": True, "data": mapped_data, "count": len(mapped_data)}
            else:
                return {"success": True, "data": [], "count": 0}
                
        except Exception as e:
            logger.error(f"Database error when fetching invoices: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Delete an invoice record"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot delete invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table("invoices_clean")
                       .delete()
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data:
                logger.info(f"Successfully deleted invoice: {invoice_id}")
                return {"success": True, "data": response.data}
            else:
                logger.error(f"Failed to delete invoice: {response}")
                return {"success": False, "error": "Delete failed"}
                
        except Exception as e:
            logger.error(f"Database error when deleting invoice: {e}")
            return {"success": False, "error": str(e)}


# Global database service instance
db_service = DatabaseService()
