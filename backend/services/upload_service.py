"""
Common upload service for invoice files.
Handles file upload logic shared between drag & drop and folder watcher.
OCR processing is now separated and triggered manually.
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
        self.storage_bucket = "invoices"
    
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
            return False, "File is empty"
        
        # Check file size
        if file_data.file_size > self.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE // (1024*1024)}MB"
        
        # Validate content type
        if file_data.content_type not in self.SUPPORTED_CONTENT_TYPES:
            return False, f"Unsupported file type. Only {', '.join(self.SUPPORTED_CONTENT_TYPES)} are allowed"
        
        # Validate filename pattern (only for drag & drop uploads)
        if file_data.source == UploadSource.DRAG_DROP:
            if not re.match(self.FILENAME_PATTERN, file_data.filename):
                return False, "Filename must follow pattern: YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf"
        
        return True, None
    
    def generate_storage_path(self, filename: str, source: UploadSource) -> str:
        """
        Generate storage path based on source and filename
        """
        # Add source prefix for organization
        if source == UploadSource.FOLDER_WATCHER:
            return f"folder_watcher/{filename}"
        elif source == UploadSource.MANUAL:
            return f"manual/{filename}"
        else:
            return filename  # Default path for drag & drop
    
    async def upload_to_storage(self, file_data: FileData, storage_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload file to Supabase storage
        Returns (success, public_url, error_message)
        """
        if not db_service.is_available:
            # Mock upload for demo mode
            mock_url = f"http://localhost:8000/mock-storage/{file_data.filename}"
            return True, mock_url, None
        
        try:
            # Upload file to storage
            db_service.client.storage.from_(self.storage_bucket).upload(storage_path, file_data.content)
            
            # Get public URL
            public_url = db_service.client.storage.from_(self.storage_bucket).get_public_url(storage_path)
            
            return True, public_url, None
            
        except Exception as e:
            logger.error(f"Storage upload failed: {str(e)}")
            return False, None, str(e)
    
    def create_invoice_record(self, file_data: FileData, storage_path: str, 
                            public_url: str, invoice_id: str, 
                            ocr_result: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """
        Create invoice record in database with OCR data mapped to your schema fields
        Returns (success, error_message)
        """
        try:
            # Prepare base database record using your exact schema field names
            invoice_data = {
                "id": invoice_id,
                "file_name": file_data.filename,  # Your exact field name
                "file_path": storage_path,
                "file_size": file_data.file_size,
                "mime_type": file_data.content_type,
                "status": "uploaded"
                # created_at will be auto-generated by database default
            }
            
            # Add OCR data if available
            if ocr_result:
                invoice_data.update({
                    "ocr_status": "completed" if ocr_result.get("success") else "failed",
                    "ocr_text": ocr_result.get("raw_text", ""),
                    "raw_ocr_data": ocr_result  # Store complete OCR result
                })
                
                # Map OCR structured data to your German business fields
                structured_data = ocr_result.get("structured_data")
                if structured_data:
                    # Map English OCR fields to your German schema fields with proper data type handling
                    ocr_mapping = {
                        "customer_name": ("rechnungsempfaenger", "text"),
                        "vendor_name": ("rechnungssteller", "text"), 
                        "total_amount": ("rechnungsbetrag", "numeric"),
                        "invoice_date": ("rechnungseingang", "date"),
                        "due_date": ("faelligkeit", "date"),
                        "po_number": ("projekt", "text")  # Map PO number to project
                    }
                    
                    for ocr_field, (db_field, data_type) in ocr_mapping.items():
                        value = structured_data.get(ocr_field)
                        if value is not None and value != "":
                            # Process the value based on data type
                            processed_value = self._process_field_value(value, data_type)
                            if processed_value is not None:
                                invoice_data[db_field] = processed_value
                            
                    logger.info(f"Mapped OCR data: {len([k for k, _ in ocr_mapping.values() if k in invoice_data])} fields populated")
            else:
                # OCR disabled or not processed
                invoice_data.update({
                    "ocr_status": "disabled",
                    "ocr_text": ""
                })
            
            # Create invoice record in database using your clean database service
            if db_service.is_available:
                create_result = db_service.create_invoice(invoice_data)
                if not create_result.get("success"):
                    error_msg = create_result.get("error", "Unknown database error")
                    logger.warning(f"Failed to save invoice to database: {error_msg}")
                    return False, error_msg
                else:
                    logger.info(f"✅ Invoice saved with OCR data: {invoice_id}")
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
