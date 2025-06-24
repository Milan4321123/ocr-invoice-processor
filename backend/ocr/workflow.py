"""
OCR Workflow Orchestrator
Coordinates the complete OCR processing pipeline from file upload to structured data extraction
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple, Any
from dataclasses import asdict
import json
import time
from decimal import Decimal

from ocr.document_ai_service import ocr_service, OCRResult
from ocr.invoice_parser import invoice_parser, InvoiceData
from ocr.mock_service import mock_ocr_service
from config.ocr_config import ocr_config

logger = logging.getLogger(__name__)

def serialize_invoice_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Decimal objects to floats for JSON serialization"""
    result = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, list):
            # Handle lists (e.g., line_items)
            result[key] = []
            for item in value:
                if isinstance(item, dict):
                    result[key].append(serialize_invoice_data(item))
                elif isinstance(item, Decimal):
                    result[key].append(float(item))
                else:
                    result[key].append(item)
        elif isinstance(value, dict):
            result[key] = serialize_invoice_data(value)
        else:
            result[key] = value
    return result

class OCRWorkflow:
    """Orchestrates the complete OCR processing workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_document(
        self, 
        file_content: bytes, 
        mime_type: str, 
        filename: str,
        document_type: str = "invoice"
    ) -> Dict:
        """
        Process a document through the complete OCR pipeline
        
        Args:
            file_content: Raw file bytes
            mime_type: MIME type of the file
            filename: Original filename
            document_type: Type of document to process (invoice, receipt, etc.)
            
        Returns:
            Dict containing OCR results and structured data
        """
        workflow_start = time.time()
        
        try:
            self.logger.info(f"Starting OCR workflow for {filename} ({document_type})")
            
            # Check if mock mode is explicitly enabled
            if ocr_config.use_mock_ocr:
                self.logger.info(f"Using mock OCR mode for {filename}")
                mock_result = mock_ocr_service.process_document(file_content, filename)
                
                if mock_result["success"]:
                    structured_data = mock_result["structured_data"]
                    workflow_time = time.time() - workflow_start
                    
                    return {
                        "success": True,
                        "ocr_enabled": True,
                        "mock_mode": True,
                        "processing_time": workflow_time,
                        "ocr_processing_time": mock_result["processing_time"],
                        "raw_text": mock_result["text"],
                        "confidence": mock_result["confidence"],
                        "pages": mock_result["pages"],
                        "document_type": document_type,
                        "structured_data": structured_data,
                        "entities": mock_result["entities"],
                        "form_fields": mock_result["form_fields"],
                        "tables": mock_result["tables"],
                        "error": None
                    }
            
            # Step 1: Check if OCR is available
            if not ocr_service.is_available():
                self.logger.warning(f"Real OCR service not available, using mock service for {filename}")
                # Use mock OCR service
                mock_result = mock_ocr_service.process_document(file_content, filename)
                
                # Convert mock result to match expected format
                if mock_result["success"]:
                    structured_data = mock_result["structured_data"]
                    workflow_time = time.time() - workflow_start
                    
                    return {
                        "success": True,
                        "ocr_enabled": True,
                        "mock_mode": True,
                        "processing_time": workflow_time,
                        "ocr_processing_time": mock_result["processing_time"],
                        "raw_text": mock_result["text"],
                        "confidence": mock_result["confidence"],
                        "pages": mock_result["pages"],
                        "document_type": document_type,
                        "structured_data": structured_data,
                        "entities": mock_result["entities"],
                        "form_fields": mock_result["form_fields"],
                        "tables": mock_result["tables"],
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "error": mock_result.get("error", "Mock OCR service failed"),
                        "mock_mode": True,
                        "ocr_enabled": True,
                        "processing_time": time.time() - workflow_start
                    }
            
            # Step 2: Extract text using Google Document AI
            self.logger.info(f"Extracting text from {filename}")
            ocr_result = await ocr_service.extract_text_from_file(
                file_content, mime_type, filename
            )
            
            if ocr_result.error:
                # Check if it's a billing error and fallback to mock
                if "BILLING_DISABLED" in ocr_result.error or "billing" in ocr_result.error.lower():
                    self.logger.warning(f"Billing disabled, falling back to mock OCR for {filename}")
                    mock_result = mock_ocr_service.process_document(file_content, filename)
                    
                    if mock_result["success"]:
                        structured_data = mock_result["structured_data"]
                        workflow_time = time.time() - workflow_start
                        
                        return {
                            "success": True,
                            "ocr_enabled": True,
                            "mock_mode": True,
                            "processing_time": workflow_time,
                            "ocr_processing_time": mock_result["processing_time"],
                            "raw_text": mock_result["text"],
                            "confidence": mock_result["confidence"],
                            "pages": mock_result["pages"],
                            "document_type": document_type,
                            "structured_data": structured_data,
                            "entities": mock_result["entities"],
                            "form_fields": mock_result["form_fields"],
                            "tables": mock_result["tables"],
                            "error": None,
                            "original_error": ocr_result.error
                        }
                
                return {
                    "success": False,
                    "error": ocr_result.error,
                    "ocr_enabled": True,
                    "processing_time": ocr_result.processing_time
                }
            
            # Step 3: Parse structured data based on document type
            structured_data = None
            if document_type.lower() == "invoice":
                self.logger.info(f"Parsing invoice data from {filename}")
                invoice_data = invoice_parser.parse_invoice(ocr_result)
                # Convert to dict and serialize Decimal objects for JSON compatibility
                structured_data = serialize_invoice_data(asdict(invoice_data))
            
            # Step 4: Compile results
            workflow_time = time.time() - workflow_start
            
            result = {
                "success": True,
                "ocr_enabled": True,
                "processing_time": workflow_time,
                "ocr_processing_time": ocr_result.processing_time,
                "raw_text": ocr_result.text,
                "confidence": ocr_result.confidence,
                "pages": ocr_result.pages,
                "document_type": document_type,
                "structured_data": structured_data,
                "entities": ocr_result.entities,
                "form_fields": ocr_result.form_fields,
                "tables": ocr_result.tables,
                "error": None
            }
            
            self.logger.info(f"OCR workflow completed for {filename} in {workflow_time:.2f}s")
            return result
            
        except Exception as e:
            workflow_time = time.time() - workflow_start
            self.logger.error(f"OCR workflow failed for {filename}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "ocr_enabled": True,
                "processing_time": workflow_time,
                "raw_text": "",
                "confidence": 0.0,
                "pages": 0,
                "document_type": document_type,
                "structured_data": None,
                "entities": [],
                "form_fields": [],
                "tables": []
            }
    
    def get_ocr_status(self) -> Dict:
        """Get current OCR service status"""
        return {
            "ocr_enabled": ocr_config.enable_ocr,
            "service_available": ocr_service.is_available(),
            "processor_name": ocr_service.processor_name,
            "supported_formats": ocr_config.supported_mime_types,
            "max_file_size_mb": ocr_config.max_file_size_mb,
            "form_parser_enabled": ocr_config.enable_form_parser,
            "layout_parser_enabled": ocr_config.enable_layout_parser
        }
    
    def validate_file_for_ocr(self, file_size: int, mime_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if file can be processed with OCR
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not ocr_config.enable_ocr:
            return False, "OCR is disabled"
        
        if not ocr_service.is_available():
            return False, "OCR service not available"
        
        if file_size > ocr_config.get_max_file_size_bytes():
            return False, f"File too large. Maximum size: {ocr_config.max_file_size_mb}MB"
        
        if not ocr_config.is_supported_file_type(mime_type):
            return False, f"Unsupported file type: {mime_type}"
        
        return True, None
    
    async def health_check(self) -> Dict:
        """Perform OCR service health check"""
        health_status = {
            "service": "OCR",
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        try:
            # Check configuration
            config_valid = ocr_config.validate_config()
            health_status["checks"]["configuration"] = {
                "status": "healthy" if config_valid else "unhealthy",
                "details": "Configuration validated" if config_valid else "Configuration invalid"
            }
            
            # Check service availability
            service_available = ocr_service.is_available()
            health_status["checks"]["service_availability"] = {
                "status": "healthy" if service_available else "unhealthy",
                "details": "Service available" if service_available else "Service unavailable"
            }
            
            # Check processor connection (if available)
            if service_available:
                try:
                    # Test with a minimal document (empty will fail, but we can check the error type)
                    test_result = await asyncio.wait_for(
                        ocr_service._process_document_with_retry(b"test", "text/plain"),
                        timeout=10.0
                    )
                    health_status["checks"]["processor_connection"] = {
                        "status": "healthy",
                        "details": "Processor connection verified"
                    }
                except asyncio.TimeoutError:
                    health_status["checks"]["processor_connection"] = {
                        "status": "unhealthy", 
                        "details": "Processor connection timeout"
                    }
                except Exception as e:
                    # Some errors are expected with test data
                    if "mime_type" in str(e).lower() or "content" in str(e).lower():
                        health_status["checks"]["processor_connection"] = {
                            "status": "healthy",
                            "details": "Processor reachable (expected test error)"
                        }
                    else:
                        health_status["checks"]["processor_connection"] = {
                            "status": "unhealthy",
                            "details": f"Processor error: {str(e)}"
                        }
            else:
                health_status["checks"]["processor_connection"] = {
                    "status": "unhealthy",
                    "details": "Service not available"
                }
            
            # Determine overall status
            unhealthy_checks = [
                check for check in health_status["checks"].values() 
                if check["status"] == "unhealthy"
            ]
            
            if unhealthy_checks:
                health_status["status"] = "unhealthy"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status

# Global OCR workflow instance
ocr_workflow = OCRWorkflow()
