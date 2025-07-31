#!/usr/bin/env python3
"""
PDF URL Service - Centralized PDF URL construction
Handles both mock storage (for development) and Supabase storage (for production)
"""
import os
from typing import Optional

class PDFUrlService:
    """Service for constructing PDF URLs based on environment configuration"""
    
    def __init__(self):
        self.use_mock_storage = os.getenv("USE_MOCK_STORAGE", "false").lower() == "true"
        self.supabase_url = os.getenv("SUPA_URL")
        self.api_base_url = os.getenv("API_BASE_URL", "")
    
    def get_pdf_url(self, file_path: str) -> str:
        """
        Get PDF URL based on file path and environment configuration
        
        Args:
            file_path: The file path stored in database
            
        Returns:
            Complete URL to access the PDF
        """
        if not file_path:
            return ""
        
        if self.use_mock_storage:
            # Use mock storage for development/demo
            file_name = os.path.basename(file_path)
            return f"/api/mock-storage/{file_name}"
        else:
            # Use Supabase storage for production
            return self._construct_supabase_url(file_path)
    
    def _construct_supabase_url(self, file_path: str) -> str:
        """Construct Supabase storage URL with proper bucket logic"""
        # Determine the correct bucket based on file_path prefix
        if file_path.startswith('folder_watcher/'):
            bucket_name = "folderwatcher"
            file_name = file_path.replace('folder_watcher/', '')
        elif file_path.startswith('manual/'):
            bucket_name = "manual"
            file_name = file_path.replace('manual/', '')
        else:
            # Default for drag-drop uploads
            bucket_name = "invoices"
            file_name = file_path
        
        return f"{self.supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"

# Global instance
pdf_url_service = PDFUrlService()