"""
Centralized database service layer for OCR Invoice Processor.
Handles all Supabase database operations for the invoices_clean table.
Single source of truth for all database communication.
"""
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Centralized database service for Supabase operations.
    Works directly with the invoices_clean table schema.
    Single source of truth for all database communication.
    """
    
    def __init__(self):
        self._client: Optional[Client] = None
        self.table_name = "invoices_clean"  # Single table we work with
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client"""
        url = os.getenv("SUPA_URL")
        key = os.getenv("SUPA_KEY")
        
        if url and key:
            try:
                self._client = create_client(url, key)
                logger.info(f"Database service initialized successfully")
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
    
    def _add_timestamps(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Add timestamp fields to data"""
        now = datetime.utcnow().isoformat()
        
        if not is_update:
            data["created_at"] = now
        data["updated_at"] = now
        
        return data
    
    def _add_compatibility_fields(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Add compatibility fields for frontend"""
        # Add URL field for frontend
        if invoice.get("file_path"):
            invoice["url"] = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice['file_path']}"
        
        # Add compatible field names
        if invoice.get("file_name"):
            invoice["filename"] = invoice["file_name"]
        
        # Add English field names for compatibility
        if invoice.get("rechnungsempfaenger"):
            invoice["customer_name"] = invoice["rechnungsempfaenger"]
        if invoice.get("rechnungssteller"):
            invoice["vendor_name"] = invoice["rechnungssteller"]
        if invoice.get("rechnungsbetrag"):
            invoice["total_amount"] = invoice["rechnungsbetrag"]
        if invoice.get("rechnungseingang"):
            invoice["invoice_date"] = invoice["rechnungseingang"]
        if invoice.get("faelligkeit"):
            invoice["due_date"] = invoice["faelligkeit"]
        if invoice.get("projekt"):
            invoice["po_number"] = invoice["projekt"]
        
        return invoice
    
    def _map_input_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map common input field names to database field names"""
        mapped = data.copy()
        
        # Map common field names to database schema
        field_mapping = {
            "filename": "file_name",
            "customer_name": "rechnungsempfaenger",
            "vendor_name": "rechnungssteller",
            "total_amount": "rechnungsbetrag",
            "invoice_date": "rechnungseingang",
            "due_date": "faelligkeit",
            "po_number": "projekt"
        }
        
        for input_field, db_field in field_mapping.items():
            if input_field in mapped:
                mapped[db_field] = mapped.pop(input_field)
        
        return mapped
    
    # ===== CORE INVOICE OPERATIONS =====
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice record in invoices_clean table"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot create invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Map input fields and add timestamps
            data = self._map_input_fields(invoice_data.copy())
            data = self._add_timestamps(data)
            
            # Ensure required fields
            if not data.get("file_name"):
                return {"success": False, "error": "file_name is required"}
            
            # Set default values
            data.setdefault("status", "pending")
            data.setdefault("ocr_status", "pending")
            data.setdefault("kfw_anrechenbare_kosten", False)
            
            response = self._client.table(self.table_name).insert(data).execute()
            
            if response.data:
                invoice = self._add_compatibility_fields(response.data[0])
                logger.info(f"Successfully created invoice: {invoice['id']}")
                return {"success": True, "data": invoice}
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
            response = self._client.table(self.table_name).select("*").eq("id", invoice_id).execute()
            
            if response.data:
                invoice = self._add_compatibility_fields(response.data[0])
                return {"success": True, "data": invoice}
            else:
                return {"success": False, "error": "Invoice not found"}
                
        except Exception as e:
            logger.error(f"Database error when fetching invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def get_invoices(self, limit: int = 100, offset: int = 0, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get invoices with pagination and filtering"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot fetch invoices")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            query = self._client.table(self.table_name).select("*")
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.eq(field, value)
            
            # Apply pagination and ordering
            response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            invoices = []
            if response.data:
                for invoice in response.data:
                    invoices.append(self._add_compatibility_fields(invoice))
            
            return {"success": True, "data": invoices, "total": len(invoices)}
                
        except Exception as e:
            logger.error(f"Database error when fetching invoices: {e}")
            return {"success": False, "error": str(e)}
    
    def update_invoice(self, invoice_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an invoice record"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot update invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Map input fields and add update timestamp
            data = self._map_input_fields(update_data.copy())
            data = self._add_timestamps(data, is_update=True)
            
            response = self._client.table(self.table_name).update(data).eq("id", invoice_id).execute()
            
            if response.data:
                invoice = self._add_compatibility_fields(response.data[0])
                logger.info(f"Successfully updated invoice: {invoice_id}")
                return {"success": True, "data": invoice}
            else:
                logger.warning(f"No invoice found to update: {invoice_id}")
                return {"success": False, "error": "Invoice not found"}
                
        except Exception as e:
            logger.error(f"Database error when updating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Delete an invoice record"""
        if not self.is_available:
            logger.warning("Database unavailable, cannot delete invoice")
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = self._client.table(self.table_name).delete().eq("id", invoice_id).execute()
            
            if response.data:
                logger.info(f"Successfully deleted invoice: {invoice_id}")
                return {"success": True, "data": response.data[0]}
            else:
                logger.warning(f"No invoice found to delete: {invoice_id}")
                return {"success": False, "error": "Invoice not found"}
                
        except Exception as e:
            logger.error(f"Database error when deleting invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def invoice_exists(self, invoice_id: str) -> bool:
        """Check if an invoice exists"""
        if not self.is_available:
            return False
        
        try:
            response = self._client.table(self.table_name).select("id").eq("id", invoice_id).execute()
            return bool(response.data)
                
        except Exception as e:
            logger.error(f"Database error when checking invoice existence: {e}")
            return False
    
    # ===== STORAGE OPERATIONS =====
    
    def delete_storage_file(self, filename: str) -> bool:
        """Delete a file from Supabase storage"""
        if not self.is_available:
            return False
        
        try:
            self._client.storage.from_("invoices").remove([filename])
            logger.info(f"Successfully deleted file from storage: {filename}")
            return True
        except Exception as e:
            logger.error(f"Storage deletion failed for {filename}: {e}")
            return False


# Global database service instance
db_service = DatabaseService()
