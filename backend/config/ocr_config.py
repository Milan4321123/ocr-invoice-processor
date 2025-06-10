"""
OCR Configuration Management
Handles Google Cloud Document AI configuration and credentials
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class OCRConfig(BaseModel):
    """Configuration for Google Document AI OCR service"""
    
    # Google Cloud Project Configuration
    gcp_project_id: str = Field(default="", env="GCP_PROJECT_ID")
    gcp_location: str = Field(default="eu", env="GCP_LOCATION")
    
    # Document AI Processor Configuration
    processor_id: Optional[str] = Field(default=None, env="DOCUMENT_AI_PROCESSOR_ID")
    processor_version: str = Field(default="rc", env="DOCUMENT_AI_PROCESSOR_VERSION")
    
    # Authentication
    google_application_credentials: Optional[str] = Field(
        default=None,
        env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    
    # OCR Processing Settings
    max_file_size_mb: int = Field(default=20, env="OCR_MAX_FILE_SIZE_MB")
    supported_mime_types: list = Field(
        default_factory=lambda: [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/tiff",
            "image/bmp",
            "image/webp"
        ]
    )
    
    # Timeout and Retry Settings
    request_timeout_seconds: int = Field(default=300, env="OCR_REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="OCR_MAX_RETRIES")
    retry_delay_seconds: int = Field(default=2, env="OCR_RETRY_DELAY")
    
    # Feature Flags
    enable_ocr: bool = Field(default=False, env="ENABLE_OCR")
    enable_form_parser: bool = Field(default=True, env="ENABLE_FORM_PARSER")
    enable_layout_parser: bool = Field(default=False, env="ENABLE_LAYOUT_PARSER")
    use_mock_ocr: bool = Field(default=False, env="USE_MOCK_OCR")
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Helper function to safely convert to int
        def safe_int(value, default):
            if not value or value.strip() == "":
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        return cls(
            gcp_project_id=os.getenv("GCP_PROJECT_ID", ""),
            gcp_location=os.getenv("GCP_LOCATION", "eu"),
            processor_id=os.getenv("DOCUMENT_AI_PROCESSOR_ID"),
            processor_version=os.getenv("DOCUMENT_AI_PROCESSOR_VERSION", "rc"),
            google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            max_file_size_mb=safe_int(os.getenv("OCR_MAX_FILE_SIZE_MB"), 20),
            request_timeout_seconds=safe_int(os.getenv("OCR_REQUEST_TIMEOUT"), 300),
            max_retries=safe_int(os.getenv("OCR_MAX_RETRIES"), 3),
            retry_delay_seconds=safe_int(os.getenv("OCR_RETRY_DELAY"), 2),
            enable_ocr=os.getenv("ENABLE_OCR", "false").lower() in ("true", "1", "yes"),
            enable_form_parser=os.getenv("ENABLE_FORM_PARSER", "true").lower() in ("true", "1", "yes"),
            enable_layout_parser=os.getenv("ENABLE_LAYOUT_PARSER", "false").lower() in ("true", "1", "yes"),
            use_mock_ocr=os.getenv("USE_MOCK_OCR", "false").lower() in ("true", "1", "yes")
        )

    def validate_config(self) -> bool:
        """Validate OCR configuration"""
        try:
            if not self.gcp_project_id:
                logger.error("GCP_PROJECT_ID is required for OCR functionality")
                return False
                
            if self.enable_ocr and not self.processor_id:
                logger.warning("DOCUMENT_AI_PROCESSOR_ID not set - OCR will use default processor")
                
            if self.google_application_credentials and not os.path.exists(self.google_application_credentials):
                logger.error(f"Google credentials file not found: {self.google_application_credentials}")
                return False
                
            logger.info("OCR configuration validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"OCR configuration validation failed: {e}")
            return False

    def get_processor_name(self) -> str:
        """Get the full processor resource name"""
        logger.info(f"Constructing processor name - Project: {self.gcp_project_id}, Location: {self.gcp_location}, Processor ID: {self.processor_id}")
        
        if not self.processor_id:
            # Use default form parser processor type
            processor_name = f"projects/{self.gcp_project_id}/locations/{self.gcp_location}/processors"
            logger.info(f"Using default processor path: {processor_name}")
            return processor_name
        
        processor_name = f"projects/{self.gcp_project_id}/locations/{self.gcp_location}/processors/{self.processor_id}"
        logger.info(f"Using specific processor: {processor_name}")
        return processor_name

    def is_supported_file_type(self, mime_type: str) -> bool:
        """Check if file type is supported for OCR"""
        return mime_type.lower() in [mt.lower() for mt in self.supported_mime_types]

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024

# Global OCR configuration instance
ocr_config = OCRConfig.from_env()
