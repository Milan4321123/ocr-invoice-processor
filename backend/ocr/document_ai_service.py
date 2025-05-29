"""
Google Document AI OCR Service
Handles text extraction from invoices and documents using Google Cloud Document AI
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from google.cloud import documentai
from google.api_core import exceptions as gcloud_exceptions
import time

from config.ocr_config import ocr_config

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Container for OCR extraction results"""
    text: str
    confidence: float
    pages: int
    processing_time: float
    entities: List[Dict]
    form_fields: List[Dict]
    tables: List[Dict]
    error: Optional[str] = None

class DocumentAIOCRService:
    """Google Document AI OCR service implementation"""
    
    def __init__(self):
        self.client = None
        self.processor_name = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Document AI client"""
        try:
            if not ocr_config.validate_config():
                raise ValueError("Invalid OCR configuration")
            
            self.client = documentai.DocumentProcessorServiceClient()
            self.processor_name = ocr_config.get_processor_name()
            
            logger.info(f"Document AI client initialized with processor: {self.processor_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Document AI client: {e}")
            self.client = None
            self.processor_name = None
    
    def is_available(self) -> bool:
        """Check if OCR service is available"""
        return self.client is not None and ocr_config.enable_ocr
    
    async def extract_text_from_file(
        self, 
        file_content: bytes, 
        mime_type: str,
        filename: str = "document"
    ) -> OCRResult:
        """
        Extract text from document using Google Document AI
        
        Args:
            file_content: Raw file bytes
            mime_type: MIME type of the file
            filename: Original filename for logging
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not self.is_available():
                return OCRResult(
                    text="",
                    confidence=0.0,
                    pages=0,
                    processing_time=0.0,
                    entities=[],
                    form_fields=[],
                    tables=[],
                    error="OCR service not available"
                )
            
            if not ocr_config.is_supported_file_type(mime_type):
                return OCRResult(
                    text="",
                    confidence=0.0,
                    pages=0,
                    processing_time=0.0,
                    entities=[],
                    form_fields=[],
                    tables=[],
                    error=f"Unsupported file type: {mime_type}"
                )
            
            if len(file_content) > ocr_config.get_max_file_size_bytes():
                return OCRResult(
                    text="",
                    confidence=0.0,
                    pages=0,
                    processing_time=0.0,
                    entities=[],
                    form_fields=[],
                    tables=[],
                    error=f"File too large. Maximum size: {ocr_config.max_file_size_mb}MB"
                )
            
            logger.info(f"Processing document: {filename} ({mime_type}, {len(file_content)} bytes)")
            
            # Process document with retry logic
            document = await self._process_document_with_retry(file_content, mime_type)
            
            # Extract information from processed document
            result = self._extract_document_info(document)
            result.processing_time = time.time() - start_time
            
            logger.info(f"OCR completed for {filename} in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OCR extraction failed for {filename}: {e}")
            
            return OCRResult(
                text="",
                confidence=0.0,
                pages=0,
                processing_time=processing_time,
                entities=[],
                form_fields=[],
                tables=[],
                error=str(e)
            )
    
    async def _process_document_with_retry(
        self, 
        file_content: bytes, 
        mime_type: str
    ) -> documentai.Document:
        """Process document with retry logic for transient failures"""
        
        for attempt in range(ocr_config.max_retries):
            try:
                # Create the request
                request = documentai.ProcessRequest(
                    name=self.processor_name,
                    raw_document=documentai.RawDocument(
                        content=file_content,
                        mime_type=mime_type
                    )
                )
                
                # Process the document
                response = self.client.process_document(
                    request=request,
                    timeout=ocr_config.request_timeout_seconds
                )
                
                return response.document
                
            except gcloud_exceptions.RetryError as e:
                logger.warning(f"Retry error on attempt {attempt + 1}: {e}")
                if attempt == ocr_config.max_retries - 1:
                    raise
                await asyncio.sleep(ocr_config.retry_delay_seconds * (attempt + 1))
                
            except gcloud_exceptions.ServiceUnavailable as e:
                logger.warning(f"Service unavailable on attempt {attempt + 1}: {e}")
                if attempt == ocr_config.max_retries - 1:
                    raise
                await asyncio.sleep(ocr_config.retry_delay_seconds * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Unexpected error during document processing: {e}")
                raise
    
    def _extract_document_info(self, document: documentai.Document) -> OCRResult:
        """Extract structured information from processed document"""
        
        # Extract main text
        text = document.text
        
        # Calculate average confidence
        confidence = 0.0
        if document.pages:
            confidences = []
            for page in document.pages:
                for paragraph in page.paragraphs:
                    if paragraph.layout and paragraph.layout.confidence:
                        confidences.append(paragraph.layout.confidence)
            
            confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Extract entities (for form parser)
        entities = []
        if ocr_config.enable_form_parser and document.entities:
            for entity in document.entities:
                entities.append({
                    "type": entity.type_,
                    "value": entity.mention_text,
                    "confidence": entity.confidence,
                    "normalized_value": getattr(entity.normalized_value, 'text', '') if entity.normalized_value else ''
                })
        
        # Extract form fields
        form_fields = []
        if document.pages:
            for page in document.pages:
                if page.form_fields:
                    for field in page.form_fields:
                        field_name = self._get_text_from_layout(document.text, field.field_name)
                        field_value = self._get_text_from_layout(document.text, field.field_value)
                        
                        form_fields.append({
                            "name": field_name.strip(),
                            "value": field_value.strip(),
                            "confidence": field.field_value.confidence if field.field_value else 0.0
                        })
        
        # Extract tables
        tables = []
        if document.pages:
            for page in document.pages:
                if page.tables:
                    for table in page.tables:
                        table_data = self._extract_table_data(document.text, table)
                        if table_data:
                            tables.append(table_data)
        
        return OCRResult(
            text=text,
            confidence=confidence,
            pages=len(document.pages),
            entities=entities,
            form_fields=form_fields,
            tables=tables,
            processing_time=0.0  # Will be set by caller
        )
    
    def _get_text_from_layout(self, document_text: str, layout) -> str:
        """Extract text from layout element"""
        if not layout or not layout.text_anchor:
            return ""
        
        text_segments = []
        for segment in layout.text_anchor.text_segments:
            start_index = int(segment.start_index) if segment.start_index else 0
            end_index = int(segment.end_index) if segment.end_index else len(document_text)
            text_segments.append(document_text[start_index:end_index])
        
        return "".join(text_segments)
    
    def _extract_table_data(self, document_text: str, table) -> Dict:
        """Extract structured data from table"""
        if not table.header_rows and not table.body_rows:
            return {}
        
        headers = []
        rows = []
        
        # Extract headers
        for header_row in table.header_rows:
            header_cells = []
            for cell in header_row.cells:
                cell_text = self._get_text_from_layout(document_text, cell.layout)
                header_cells.append(cell_text.strip())
            headers.append(header_cells)
        
        # Extract body rows
        for body_row in table.body_rows:
            row_cells = []
            for cell in body_row.cells:
                cell_text = self._get_text_from_layout(document_text, cell.layout)
                row_cells.append(cell_text.strip())
            rows.append(row_cells)
        
        return {
            "headers": headers,
            "rows": rows,
            "row_count": len(rows),
            "column_count": len(headers[0]) if headers else (len(rows[0]) if rows else 0)
        }

# Global OCR service instance
ocr_service = DocumentAIOCRService()
