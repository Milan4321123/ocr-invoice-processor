"""
Common upload service for invoice files.
Handles file upload logic shared between drag & drop and folder watcher.
Clean implementation without external processing dependencies.
"""
import os
import re
import uuid
import datetime
import logging
from typing import Dict, Any, Optional, Tuple, Union, BinaryIO
from dataclasses import dataclass
from enum import Enum

from services.database import db_service

logger = logging.getLogger(__name__)

class UploadSource(Enum):
    """Source of the upload"""
    DRAG_DROP = "drag_drop"
    FOLDER_WATCHER = "folder_watcher"
    MANUAL = "manual"

@dataclass
class UploadResult:
    """Result of file upload operation"""
    success: bool
    invoice_id: Optional[str] = None
    filename: Optional[str] = None
    url: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
    source: Optional[UploadSource] = None
    storage_path: Optional[str] = None

@dataclass
class FileData:
    """Container for file data and metadata"""
    content: bytes
    filename: str
    content_type: str
    file_size: int
    source: UploadSource
    source_metadata: Optional[Dict[str, Any]] = None

class UploadService:
    """Centralized upload service for invoice files"""
    
    # Filename pattern validation
    FILENAME_PATTERN = r'^\d{8}_[A-Za-z0-9]+_[A-Za-z0-9]+_[A-Za-z0-9]+\.pdf$'
    
    # Supported content types
    SUPPORTED_CONTENT_TYPES = {"application/pdf"}
    
    # Max file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(self):
        # Use separate buckets for different upload sources
        self.buckets = {
            UploadSource.DRAG_DROP: "invoices",
            UploadSource.FOLDER_WATCHER: "folderwatcher", 
            UploadSource.MANUAL: "manual-invoices"
        }
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and XSS attacks
        """
        if not filename:
            return "unknown.pdf"
        
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        # Keep only alphanumeric, dots, dashes, underscores
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Remove multiple dots that could be used for traversal
        filename = re.sub(r'\.{2,}', '.', filename)
        
        # Ensure it ends with .pdf
        if not filename.lower().endswith('.pdf'):
            filename = filename + '.pdf'
        
        # Limit length
        if len(filename) > 255:
            name_part = filename[:-4][:250]  # Leave room for .pdf
            filename = name_part + '.pdf'
        
        return filename
    
    def validate_file(self, file_data: FileData) -> Tuple[bool, Optional[str]]:
        """
        Validate file content and metadata
        Returns (is_valid, error_message)
        """
        # Check if file is empty
        if file_data.file_size == 0:
            return False, "Die Datei ist leer"
        
        # Check file size
        if file_data.file_size > self.MAX_FILE_SIZE:
            return False, f"Datei ist zu groß. Maximum: {self.MAX_FILE_SIZE // (1024*1024)}MB"
        
        # Validate content type
        if file_data.content_type not in self.SUPPORTED_CONTENT_TYPES:
            return False, "Nur PDF-Dateien sind erlaubt"
        
        # Validate filename pattern for all uploads (unified validation)
        if not re.match(self.FILENAME_PATTERN, file_data.filename):
            return False, "Dateiname muss dem Muster folgen: JJJJMMTT_KENNUNG_LIEFERANT_TYP.pdf"
        
        # Check for duplicate files by filename
        if db_service.is_available:
            try:
                # Query for existing files with the same filename
                response = db_service.client.table("invoices_clean").select("id,file_name").eq("file_name", file_data.filename).execute()
                if response.data and len(response.data) > 0:
                    return False, f"Eine Datei mit dem Namen '{file_data.filename}' existiert bereits"
            except Exception as e:
                logger.warning(f"Could not check for duplicate files: {e}")
                # Don't fail the upload just because we can't check for duplicates
        
        return True, None
    
    def generate_storage_path(self, filename: str, source: UploadSource) -> str:
        """
        Generate storage path based on source and filename
        For database storage, we include bucket prefix to help with PDF URL construction
        """
        if source == UploadSource.FOLDER_WATCHER:
            return f"folder_watcher/{filename}"
        elif source == UploadSource.MANUAL:
            return f"manual/{filename}"
        else:  # DRAG_DROP
            return filename  # No prefix for drag-drop (default)
    async def upload_to_storage(self, file_data: FileData, storage_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload file to Supabase storage using the appropriate bucket
        Returns (success, public_url, error_message)
        """
        if not db_service.is_available:
            # Mock upload for demo mode
            mock_url = f"http://localhost:8000/mock-storage/{file_data.filename}"
            return True, mock_url, None

        try:
            # Get the appropriate bucket for this upload source
            bucket_name = self.buckets[file_data.source]
            
            # Extract just the filename for storage (remove any prefix)
            filename = storage_path.split('/')[-1] if '/' in storage_path else storage_path
            
            # Upload file to the source-specific bucket using just the filename
            db_service.client.storage.from_(bucket_name).upload(filename, file_data.content)
            
            # Get public URL from the specific bucket
            public_url = db_service.client.storage.from_(bucket_name).get_public_url(filename)
            
            return True, public_url, None
            
        except Exception as e:
            logger.error(f"Storage upload failed to bucket '{bucket_name}': {str(e)}")
            return False, None, str(e)
    
    def create_invoice_record(self, file_data: FileData, storage_path: str, 
                            public_url: str, invoice_id: str) -> Tuple[bool, Optional[str]]:
        """
        Create invoice record in database (clean, no OCR dependencies)
        Returns (success, error_message)
        """
        try:
            # Prepare base database record using exact schema field names
            invoice_data = {
                "id": invoice_id,
                "file_name": file_data.filename,
                "file_path": storage_path,
                "file_size": file_data.file_size,
                "mime_type": file_data.content_type,
                "status": "uploaded"
                # Note: upload_source removed as column doesn't exist in current schema
                # created_at and updated_at will be auto-generated by database default
            }
            # Create invoice record in database using clean database service
            if db_service.is_available:
                create_result = db_service.create_invoice(invoice_data)
                if not create_result.get("success"):
                    error_msg = create_result.get("error", "Unknown database error")
                    logger.warning(f"Failed to save invoice to database: {error_msg}")
                    return False, error_msg
                else:
                    logger.info(f"✅ Invoice saved successfully: {invoice_id}")
            else:
                logger.info(f"Database unavailable - invoice record not persisted: {invoice_id}")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Database record creation failed: {str(e)}")
            return False, str(e)
    
    def _process_field_value(self, value: str, data_type: str) -> Any:
        """
        Process field value based on expected data type
        """
        if not value or value == "":
            return None
            
        try:
            if data_type == "numeric":
                # Extract numeric value from strings like "1,234.56 EUR" or "€1,234.56"
                import re
                # Remove currency symbols and extract numbers
                numeric_match = re.search(r'[\d,]+\.?\d*', str(value))
                if numeric_match:
                    numeric_str = numeric_match.group().replace(',', '')
                    return float(numeric_str) if '.' in numeric_str else int(numeric_str)
                return None
                
            elif data_type == "date":
                # Handle various date formats
                if isinstance(value, str):
                    # Try to parse common date formats
                    from datetime import datetime
                    date_formats = [
                        "%Y-%m-%d",
                        "%d.%m.%Y",
                        "%d/%m/%Y",
                        "%m/%d/%Y",
                        "%Y-%m-%d %H:%M:%S"
                    ]
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(value, fmt)
                            return parsed_date.date().isoformat()
                        except ValueError:
                            continue
                    # If no format matches, return as-is
                    return value
                return value
                
            else:  # text or default
                return str(value).strip()
                
        except Exception as e:
            logger.warning(f"Failed to process field value '{value}' as {data_type}: {e}")
            return None
    
    async def upload_file(self, file_data: FileData) -> UploadResult:
        """
        Main upload method that orchestrates the entire upload process
        """
        try:
            # Step 1: Sanitize filename
            safe_filename = self.sanitize_filename(file_data.filename)
            file_data.filename = safe_filename
            
            # Step 2: Validate file
            is_valid, validation_error = self.validate_file(file_data)
            if not is_valid:
                return UploadResult(
                    success=False,
                    error=validation_error,
                    source=file_data.source
                )
            
            # Step 3: Generate storage path
            storage_path = self.generate_storage_path(safe_filename, file_data.source)
            
            # Step 4: Upload to storage
            upload_success, public_url, upload_error = await self.upload_to_storage(file_data, storage_path)
            if not upload_success:
                return UploadResult(
                    success=False,
                    error=f"Storage upload failed: {upload_error}",
                    source=file_data.source
                )
            
            # Step 5: Generate invoice ID
            invoice_id = str(uuid.uuid4())
            
            # Step 6: Create database record
            db_success, db_error = self.create_invoice_record(
                file_data, storage_path, public_url, invoice_id
            )
            if not db_success:
                # Log error but don't fail the upload completely
                logger.warning(f"Database record creation failed: {db_error}")
            
            # Step 7: Return success result
            return UploadResult(
                success=True,
                invoice_id=invoice_id,
                filename=safe_filename,
                url=public_url,
                file_size=file_data.file_size,
                source=file_data.source,
                storage_path=storage_path
            )
            
        except Exception as e:
            logger.error(f"Upload process failed: {str(e)}")
            return UploadResult(
                success=False,
                error=f"Upload failed: {str(e)}",
                source=file_data.source
            )

# Global instance
upload_service = UploadService()
