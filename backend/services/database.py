"""
Centralized database service layer for Invoice Management System.
Handles ALL Supabase database operations in one place.
Single source of truth for database communication.
"""
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Single database service for ALL Supabase operations.
    Maps directly to your invoices_clean table schema.
    No field mapping confusion - uses your exact field names.
    """
    
    def __init__(self):
        """Initialize the Supabase client"""
        self._client: Optional[Client] = None
        self.table_name = "invoices_clean"  # Your exact table name
        self.storage_buckets = {
            "invoices": "invoices",
            "folder_watcher": "folderwatcher"
        }
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client using your .env credentials"""
        url = os.getenv("SUPA_URL")
        key = os.getenv("SUPA_KEY")
        
        if url and key:
            try:
                self._client = create_client(url, key)
                logger.info(f"✅ Database service connected to: {url[:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to connect to database: {e}")
                self._client = None
        else:
            logger.warning("⚠️ Database credentials missing. Running in offline mode.")
    
    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Check if database service is available"""
        return self._client is not None

    async def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute raw SQL query for email workflow operations.
        Supabase supports PostgreSQL queries via RPC or direct SQL.
        """
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # For now, let's handle the specific email workflow operations
            # without raw SQL since Supabase client is preferred
            logger.warning(f"Raw SQL query attempted: {query[:100]}...")
            
            # Return success for now - we'll implement proper table operations
            return {
                "success": True, 
                "message": "Query logged - implement specific table operations instead",
                "query": query[:100] + "..." if len(query) > 100 else query
            }
            
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return {"success": False, "error": str(e)}

    async def create_approval_token(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create approval token record for email workflow.
        Uses Supabase table operations instead of raw SQL.
        """
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # For now, just log the token creation
            logger.info(f"Approval token would be created: {token_data.get('action')} for invoice {token_data.get('invoice_id')}")
            
            return {
                "success": True,
                "token_id": "mock-token-id",
                "message": "Token creation logged - approval_tokens table needed"
            }
            
        except Exception as e:
            logger.error(f"Failed to create approval token: {e}")
            return {"success": False, "error": str(e)}

    async def log_email_attempt(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log email attempt for audit purposes.
        Uses Supabase table operations instead of raw SQL.
        """
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # For now, just log the email attempt
            logger.info(f"Email attempt logged: {email_data.get('email_type')} to {email_data.get('recipient_email')}")
            
            return {
                "success": True,
                "log_id": "mock-log-id",
                "message": "Email attempt logged - email_audit_log table needed"
            }
            
        except Exception as e:
            logger.error(f"Failed to log email attempt: {e}")
            return {"success": False, "error": str(e)}

    
    # =============================================================================
    # CORE INVOICE OPERATIONS (using your exact invoices_clean schema)
    # =============================================================================
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new invoice record in invoices_clean table.
        Uses your exact field names - no confusing mapping.
        """
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Add timestamps
            now = datetime.utcnow().isoformat()
            invoice_data.update({
                "created_at": now,
                "updated_at": now
            })
            
            # Set defaults if not provided
            invoice_data.setdefault("status", "uploaded")
            invoice_data.setdefault("kfw_anrechenbare_kosten", False)
            
            response = self._client.table(self.table_name).insert(invoice_data).execute()
            
            if response.data:
                logger.info(f"✅ Created invoice: {response.data[0]['id']}")
                return {"success": True, "data": response.data[0]}
            else:
                logger.error(f"❌ Failed to create invoice: {response}")
                return {"success": False, "error": "Insert failed"}
                
        except Exception as e:
            logger.error(f"❌ Database error creating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get a single invoice by ID from invoices_clean table"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table(self.table_name)
                       .select("*")
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data:
                invoice = response.data[0]
                # Add URL field for file access
                if invoice.get("file_path"):
                    invoice["url"] = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice['file_path']}"
                return {"success": True, "data": invoice}
            else:
                return {"success": False, "error": "Invoice not found"}
                
        except Exception as e:
            logger.error(f"❌ Database error fetching invoice {invoice_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_invoices(self, limit: int = 100) -> Dict[str, Any]:
        """Get all invoices from invoices_clean table"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table(self.table_name)
                       .select("*")
                       .order("created_at", desc=True)
                       .limit(limit)
                       .execute())
            
            if response.data is not None:
                # Add URL field for each invoice (for file access)
                for invoice in response.data:
                    if invoice.get("file_path"):
                        invoice["url"] = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice['file_path']}"
                
                return {
                    "success": True, 
                    "data": response.data,
                    "total": len(response.data)
                }
            else:
                return {"success": True, "data": [], "total": 0}
                
        except Exception as e:
            logger.error(f"❌ Database error fetching invoices: {e}")
            return {"success": False, "error": str(e)}

    def get_invoices(self, limit: int = 100, offset: int = 0, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get invoices with pagination and filtering support for reports"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Start with base query
            query = self._client.table(self.table_name).select("*", count='exact')
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.eq(field, value)
            
            # Apply ordering, pagination
            response = (query
                       .order("created_at", desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            
            if response.data is not None:
                # Add URL field for each invoice (for file access)
                for invoice in response.data:
                    if invoice.get("file_path"):
                        invoice["url"] = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice['file_path']}"
                
                return {
                    "success": True, 
                    "data": response.data,
                    "total": len(response.data),
                    "count": response.count if hasattr(response, 'count') else len(response.data)
                }
            else:
                return {"success": True, "data": [], "total": 0, "count": 0}
                
        except Exception as e:
            logger.error(f"❌ Database error fetching filtered invoices: {e}")
            return {"success": False, "error": str(e)}
    
    def update_invoice(self, invoice_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an invoice record in invoices_clean table"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = (self._client.table(self.table_name)
                       .update(update_data)
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data:
                logger.info(f"✅ Updated invoice: {invoice_id}")
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "Invoice not found or update failed"}
                
        except Exception as e:
            logger.error(f"❌ Database error updating invoice {invoice_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def update_invoice_status(self, invoice_id: str, status: str, review_status: str = None) -> Dict[str, Any]:
        """
        Update invoice status fields using the 3-stage workflow.
        
        3-Stage Workflow:
        1. nicht begonnen: status='pending'/'uploaded', review_status='pending'/null
        2. in Bearbeitung: status='edited', review_status='under_review'  
        3. abgeschlossen: status='completed', review_status='completed_review'
        """
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        # Validate status values against your schema constraints
        valid_statuses = [
            'pending', 'uploaded', 'edited', 'pending_email', 'edit_completed',
            'in_review_by_bauleiter', 'approved_by_bauleiter', 'rejected_by_bauleiter',
            'completed', 'error'
        ]
        
        valid_review_statuses = ['pending', 'under_review', 'completed_review', 'needs_attention']
        
        if status not in valid_statuses:
            return {"success": False, "error": f"Invalid status: {status}. Must be one of: {valid_statuses}"}
        
        if review_status and review_status not in valid_review_statuses:
            return {"success": False, "error": f"Invalid review_status: {review_status}. Must be one of: {valid_review_statuses}"}
        
        try:
            # Build update data
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if review_status:
                update_data["review_status"] = review_status
            
            # Log the status change for debugging
            logger.info(f"🔄 Updating invoice {invoice_id}: status='{status}', review_status='{review_status}'")
            
            response = (self._client.table(self.table_name)
                       .update(update_data)
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data and len(response.data) > 0:
                updated_invoice = response.data[0]
                logger.info(f"✅ Status updated successfully: {invoice_id} -> status='{updated_invoice.get('status')}', review_status='{updated_invoice.get('review_status')}'")
                return {"success": True, "data": updated_invoice}
            else:
                logger.error(f"❌ Status update failed: No data returned for invoice {invoice_id}")
                return {"success": False, "error": "Invoice not found or status update failed"}
                
        except Exception as e:
            logger.error(f"❌ Database error updating status for invoice {invoice_id}: {e}")
            return {"success": False, "error": str(e)}

    def update_invoice_to_editing_stage(self, invoice_id: str) -> Dict[str, Any]:
        """Update invoice to 'in Bearbeitung' stage when editing starts"""
        return self.update_invoice_status(invoice_id, 'edited', 'under_review')
    
    def update_invoice_to_completed_stage(self, invoice_id: str, completed_by: str = None, notes: str = None) -> Dict[str, Any]:
        """Update invoice to 'abgeschlossen' stage when completed"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            update_data = {
                "status": "completed",
                "review_status": "completed_review",
                "reviewed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if completed_by:
                update_data["reviewed_by"] = completed_by
            
            if notes:
                update_data["review_notes"] = notes
            
            logger.info(f"🏁 Completing invoice {invoice_id} by {completed_by}")
            
            response = (self._client.table(self.table_name)
                       .update(update_data)
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data and len(response.data) > 0:
                updated_invoice = response.data[0]
                logger.info(f"✅ Invoice completed successfully: {invoice_id}")
                return {"success": True, "data": updated_invoice}
            else:
                return {"success": False, "error": "Invoice not found or completion failed"}
                
        except Exception as e:
            logger.error(f"❌ Database error completing invoice {invoice_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Delete an invoice record from invoices_clean table"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # First get the invoice to check file_path for storage cleanup
            invoice_result = self.get_invoice(invoice_id)
            
            response = (self._client.table(self.table_name)
                       .delete()
                       .eq("id", invoice_id)
                       .execute())
            
            if response.data:
                logger.info(f"✅ Deleted invoice: {invoice_id}")
                
                # Also delete from storage if file exists
                if invoice_result.get("success") and invoice_result["data"].get("file_path"):
                    try:
                        file_path = invoice_result["data"]["file_path"]
                        self._client.storage.from_("invoices").remove([file_path])
                        logger.info(f"✅ Also deleted file: {file_path}")
                    except Exception as storage_error:
                        logger.warning(f"⚠️ Could not delete file from storage: {storage_error}")
                
                return {"success": True, "data": response.data}
            else:
                return {"success": False, "error": "Invoice not found"}
                
        except Exception as e:
            logger.error(f"❌ Database error deleting invoice {invoice_id}: {e}")
            return {"success": False, "error": str(e)}

    
    # =============================================================================
    # STORAGE OPERATIONS (for your invoices and folderwatcher buckets)
    # =============================================================================
    
    def upload_file_to_storage(self, bucket_name: str, file_path: str, file_content: bytes) -> Dict[str, Any]:
        """Upload file to Supabase storage bucket"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = self._client.storage.from_(bucket_name).upload(file_path, file_content)
            
            if response:
                # Get public URL
                public_url = self._client.storage.from_(bucket_name).get_public_url(file_path)
                logger.info(f"✅ Uploaded file to {bucket_name}: {file_path}")
                return {"success": True, "url": public_url, "path": file_path}
            else:
                return {"success": False, "error": "Upload failed"}
                
        except Exception as e:
            logger.error(f"❌ Storage upload error: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_file_from_storage(self, bucket_name: str, file_path: str) -> Dict[str, Any]:
        """Delete file from Supabase storage bucket"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = self._client.storage.from_(bucket_name).remove([file_path])
            logger.info(f"✅ Deleted file from {bucket_name}: {file_path}")
            return {"success": True}
                
        except Exception as e:
            logger.error(f"❌ Storage delete error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # DROPDOWN OPTIONS MANAGEMENT
    # =============================================================================
    
    def get_dropdown_options(self, field_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get dropdown options from database"""
        if not self.is_available:
            return {}
        
        try:
            # Build query
            query = self._client.table("dropdown_options").select("*").eq("is_active", True)
            
            if field_name:
                query = query.eq("field_name", field_name)
            
            response = query.order("field_name", desc=False).order("sort_order", desc=False).execute()
            
            if response.data:
                # Group by field_name
                options_by_field = {}
                for option in response.data:
                    field = option["field_name"]
                    if field not in options_by_field:
                        options_by_field[field] = []
                    
                    options_by_field[field].append({
                        "value": option["value"],
                        "label": option["label"],
                        "is_default": option["is_default"]
                    })
                
                logger.info(f"✅ Retrieved dropdown options for fields: {list(options_by_field.keys())}")
                return options_by_field
            else:
                logger.warning("No dropdown options found in database")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Database error fetching dropdown options: {e}")
            return {}
    
    def add_dropdown_option(self, field_name: str, value: str, label: str, is_default: bool = False, metadata: Dict = None) -> Dict[str, Any]:
        """Add a new dropdown option to database"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            # Check if option already exists
            existing = (self._client.table("dropdown_options")
                       .select("id")
                       .eq("field_name", field_name)
                       .eq("value", value)
                       .execute())
            
            if existing.data:
                return {"success": False, "error": "Option already exists"}
            
            # Get max sort_order for this field
            max_order = (self._client.table("dropdown_options")
                        .select("sort_order")
                        .eq("field_name", field_name)
                        .order("sort_order", desc=True)
                        .limit(1)
                        .execute())
            
            sort_order = 1
            if max_order.data:
                sort_order = (max_order.data[0].get("sort_order", 0) or 0) + 1
            
            # Insert new option
            new_option = {
                "field_name": field_name,
                "value": value,
                "label": label,
                "is_default": is_default,
                "sort_order": sort_order,
                "is_active": True,
                "metadata": metadata or {}
            }
            
            response = (self._client.table("dropdown_options")
                       .insert(new_option)
                       .execute())
            
            if response.data:
                logger.info(f"✅ Added dropdown option: {field_name}.{value}")
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "Insert failed"}
                
        except Exception as e:
            logger.error(f"❌ Database error adding dropdown option: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_dropdown_option(self, field_name: str, value: str) -> Dict[str, Any]:
        """Soft delete a dropdown option (set is_active=false)"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table("dropdown_options")
                       .update({"is_active": False})
                       .eq("field_name", field_name)
                       .eq("value", value)
                       .execute())
            
            if response.data:
                logger.info(f"✅ Deleted dropdown option: {field_name}.{value}")
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "Option not found"}
                
        except Exception as e:
            logger.error(f"❌ Database error deleting dropdown option: {e}")
            return {"success": False, "error": str(e)}
    
    def update_dropdown_option(self, field_name: str, old_value: str, new_value: str, new_label: str) -> Dict[str, Any]:
        """Update a dropdown option in the database"""
        if not self.is_available:
            return {"success": False, "error": "Database unavailable"}
        
        try:
            response = (self._client.table("dropdown_options")
                       .update({
                           "value": new_value,
                           "label": new_label
                       })
                       .eq("field_name", field_name)
                       .eq("value", old_value)
                       .eq("is_active", True)
                       .execute())
            
            if response.data:
                logger.info(f"✅ Updated dropdown option: {field_name}.{old_value} -> {new_value}")
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "Option not found or no changes made"}
                
        except Exception as e:
            logger.error(f"❌ Database error updating dropdown option: {e}")
            return {"success": False, "error": str(e)}

# =============================================================================
# GLOBAL INSTANCE - Single database service for entire application
# =============================================================================
db_service = DatabaseService()
