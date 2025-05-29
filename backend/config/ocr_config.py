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
    gcp_location: str = Field(default="us", env="GCP_LOCATION")
    
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
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        return cls(
            gcp_project_id=os.getenv("GCP_PROJECT_ID", ""),
            gcp_location=os.getenv("GCP_LOCATION", "us"),
            processor_id=os.getenv("DOCUMENT_AI_PROCESSOR_ID"),
            processor_version=os.getenv("DOCUMENT_AI_PROCESSOR_VERSION", "rc"),
            google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            max_file_size_mb=int(os.getenv("OCR_MAX_FILE_SIZE_MB", "20")),
            request_timeout_seconds=int(os.getenv("OCR_REQUEST_TIMEOUT", "300")),
            max_retries=int(os.getenv("OCR_MAX_RETRIES", "3")),
            retry_delay_seconds=int(os.getenv("OCR_RETRY_DELAY", "2")),
            enable_ocr=os.getenv("ENABLE_OCR", "false").lower() in ("true", "1", "yes"),
            enable_form_parser=os.getenv("ENABLE_FORM_PARSER", "true").lower() in ("true", "1", "yes"),
            enable_layout_parser=os.getenv("ENABLE_LAYOUT_PARSER", "false").lower() in ("true", "1", "yes")
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
        if not self.processor_id:
            # Use default form parser processor type
            return f"projects/{self.gcp_project_id}/locations/{self.gcp_location}/processors"
        
        return f"projects/{self.gcp_project_id}/locations/{self.gcp_location}/processors/{self.processor_id}"

    def is_supported_file_type(self, mime_type: str) -> bool:
        """Check if file type is supported for OCR"""
        return mime_type.lower() in [mt.lower() for mt in self.supported_mime_types]

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024

# Global OCR configuration instance
ocr_config = OCRConfig.from_env()
