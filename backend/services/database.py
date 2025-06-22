"""
Centralized database service layer for OCR Invoice Processor.
Handles all Supabase database operations in one place.
"""
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
import os
import logging
from dotenv import load_dotenv

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
        
        # Create a copy to avoid modifying the original
        mapped = db_record.copy()
        
        # Map database fields to application fields
        if 'file_name' in mapped:
            mapped['filename'] = mapped['file_name']
        
        # Add URL field based on file_path
        if 'file_path' in mapped and mapped['file_path']:
            # Construct the public URL for Supabase storage
            mapped['url'] = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{mapped['file_path']}"
        
        # Map German database fields to English application fields
        field_mappings = {
            'rechnungsempfaenger': 'customer_name',
            'rechnungssteller': 'vendor_name', 
            'rechnungsnummer': 'invoice_number',
            'rechnungsdatum': 'invoice_date',
            'netto_betrag': 'subtotal',
            'brutto_betrag': 'total_amount',
            'projekt': 'project',
            'gewerk': 'trade'
        }
        
        for db_field, app_field in field_mappings.items():
            if db_field in mapped:
                mapped[app_field] = mapped[db_field]
                # Remove the German field name to avoid confusion
                del mapped[db_field]
        
        return mapped
    
    @staticmethod
    def _map_app_to_db(app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map application field names to database column names"""
        if not app_data:
            return app_data
        
        # Create a copy to avoid modifying the original
        mapped = app_data.copy()
        
        # Map application fields to database fields
        if 'filename' in mapped:
            mapped['file_name'] = mapped['filename']
            # Remove the application field to avoid conflicts
            del mapped['filename']
        
        # Remove URL field as it's computed, not stored
        if 'url' in mapped:
            del mapped['url']
        
        # Map English application fields to German database fields
        field_mappings = {
            'customer_name': 'rechnungsempfaenger',
            'vendor_name': 'rechnungssteller',
            'invoice_number': 'rechnungsnummer', 
            'invoice_date': 'rechnungsdatum',
            'subtotal': 'netto_betrag',
            'total_amount': 'brutto_betrag',
            'net_amount': 'netto_betrag',
            'gross_amount': 'brutto_betrag',
            'invoice_recipient': 'rechnungsempfaenger',
            'invoice_issuer': 'rechnungssteller',
            'project': 'projekt',
            'trade': 'gewerk'
        }
        
        for app_field, db_field in field_mappings.items():
            if app_field in mapped:
                mapped[db_field] = mapped[app_field]
                del mapped[app_field]
        
        # Store complex OCR data in raw_ocr_data JSONB field
        ocr_fields = ['ocr_entities', 'ocr_form_fields', 'ocr_tables', 'line_items', 
                      'vendor_address', 'customer_address', 'due_date', 'currency', 
                      'payment_terms', 'po_number', 'tax_amount', 'ocr_text', 
                      'ocr_status', 'ocr_pages', 'ocr_error', 'ocr_processed_at']
        
        raw_ocr_data = {}
        for field in ocr_fields:
            if field in mapped:
                raw_ocr_data[field] = mapped[field]
                del mapped[field]
        
        # Handle processing time conversion (seconds to milliseconds)
        if 'ocr_processing_time' in mapped:
            processing_time = mapped['ocr_processing_time']
            if isinstance(processing_time, (int, float)):
                # Convert seconds to milliseconds and ensure it's an integer
                mapped['ocr_processing_time'] = int(processing_time * 1000)
            else:
                # Store in raw data if not a number
                raw_ocr_data['ocr_processing_time'] = processing_time
                del mapped['ocr_processing_time']
        
        if raw_ocr_data:
            mapped['raw_ocr_data'] = raw_ocr_data
        
        return mapped

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
            
            response = self._client.table("invoices").insert(db_data).execute()
            
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
            response = (self._client.table("invoices")
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
            
            response = (self._client.table("invoices")
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
            query = self._client.table("invoices").select("*")
            
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
            response = (self._client.table("invoices")
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
