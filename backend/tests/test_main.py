import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import re
from main import app

client = TestClient(app)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Invoice OCR API is running"
        assert "version" in data

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestFileUpload:
    """Test file upload functionality"""
    
    @patch('main.supabase')
    def test_upload_valid_pdf(self, mock_supabase):
        """Test uploading a valid PDF file"""
        # Mock Supabase responses
        mock_storage = MagicMock()
        mock_table = MagicMock()
        
        mock_supabase.storage.from_.return_value = mock_storage
        mock_supabase.table.return_value = mock_table
        
        mock_storage.upload.return_value = None
        mock_storage.get_public_url.return_value = "https://example.com/test.pdf"
        mock_table.insert.return_value.execute.return_value = None
        
        # Create a valid PDF file mock
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "uploaded"
        assert data["filename"] == "20241201_INV001_ACME_SUPPLY.pdf"
        assert "url" in data
        assert "id" in data

    @patch('main.supabase')
    def test_upload_invalid_filename(self, mock_supabase):
        """Test uploading PDF with invalid filename format"""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        
        files = {
            "file": ("invalid_filename.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Filename must follow pattern" in data["detail"]

    @patch('main.supabase')
    def test_upload_non_pdf_file(self, mock_supabase):
        """Test uploading non-PDF file"""
        txt_content = b"This is not a PDF file"
        
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.txt", io.BytesIO(txt_content), "text/plain")
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Only PDF files are allowed" in data["detail"]

    @patch('main.supabase')
    def test_upload_supabase_error(self, mock_supabase):
        """Test handling Supabase upload errors"""
        mock_storage = MagicMock()
        mock_supabase.storage.from_.return_value = mock_storage
        mock_storage.upload.side_effect = Exception("Supabase error")
        
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 500
        data = response.json()
        assert "Upload failed" in data["detail"]

class TestGetInvoices:
    """Test invoice retrieval functionality"""
    
    @patch('main.supabase')
    def test_get_invoices_success(self, mock_supabase):
        """Test successful invoice retrieval"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "20241201_INV001_ACME_SUPPLY.pdf",
                "url": "https://example.com/test.pdf",
                "status": "uploaded",
                "created_at": "2024-12-01T10:00:00Z"
            }
        ]
        
        mock_table.select.return_value.order.return_value.execute.return_value = mock_response
        
        response = client.get("/invoices")
        
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data
        assert len(data["invoices"]) == 1
        assert data["invoices"][0]["filename"] == "20241201_INV001_ACME_SUPPLY.pdf"

    @patch('main.supabase')
    def test_get_invoices_database_error(self, mock_supabase):
        """Test handling database errors when fetching invoices"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.side_effect = Exception("Database error")
        
        response = client.get("/invoices")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to fetch invoices" in data["detail"]

class TestFilenameValidation:
    """Test filename validation patterns"""
    
    @pytest.mark.parametrize("filename,expected", [
        ("20241201_INV001_ACME_SUPPLY.pdf", True),
        ("20241231_ORDER123_VENDOR_INVOICE.pdf", True),
        ("20240101_A1B2C3_Company_Receipt.pdf", True),
        ("invalid_filename.pdf", False),
        ("20241201_INV001_ACME.pdf", False),  # Missing TYPE
        ("241201_INV001_ACME_SUPPLY.pdf", False),  # Invalid date format
        ("20241201_INV001_ACME_SUPPLY.txt", False),  # Wrong extension
        ("20241201__ACME_SUPPLY.pdf", False),  # Missing identifier
    ])
    def test_filename_patterns(self, filename, expected):
        """Test various filename patterns against regex"""
        import re
        pattern = r'^\d{8}_[A-Z0-9]+_[A-Za-z]+_[A-Za-z]+\.pdf$'
        result = bool(re.match(pattern, filename))
        assert result == expected

class TestGetSingleInvoice:
    """Test single invoice retrieval functionality"""
    
    @patch('main.supabase')
    def test_get_invoice_success(self, mock_supabase):
        """Test successful retrieval of a single invoice"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "20241201_INV001_ACME_SUPPLY.pdf",
                "url": "https://example.com/test.pdf",
                "status": "uploaded",
                "file_size": 2048,
                "created_at": "2024-12-01T10:00:00Z"
            }
        ]
        
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/invoices/{invoice_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "invoice" in data
        assert data["invoice"]["id"] == invoice_id
        assert data["invoice"]["filename"] == "20241201_INV001_ACME_SUPPLY.pdf"
        assert data["status"] == "success"

    @patch('main.supabase')
    def test_get_invoice_not_found(self, mock_supabase):
        """Test handling when invoice is not found"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        mock_response = MagicMock()
        mock_response.data = []  # Empty response
        
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        
        invoice_id = "non-existent-id"
        response = client.get(f"/invoices/{invoice_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "Invoice not found" in data["detail"]

    @patch('main.supabase')
    def test_get_invoice_database_error(self, mock_supabase):
        """Test handling database errors when fetching single invoice"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.side_effect = Exception("Database connection error")
        
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/invoices/{invoice_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to fetch invoice" in data["detail"]

class TestDeleteInvoice:
    """Test invoice deletion functionality"""
    
    @patch('main.supabase')
    def test_delete_invoice_success(self, mock_supabase):
        """Test successful deletion of an invoice"""
        mock_table = MagicMock()
        mock_storage = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_supabase.storage.from_.return_value = mock_storage
        
        # Mock getting the invoice first
        mock_get_response = MagicMock()
        mock_get_response.data = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "20241201_INV001_ACME_SUPPLY.pdf",
                "url": "https://example.com/test.pdf",
                "status": "uploaded"
            }
        ]
        
        # Mock delete operations
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_get_response
        mock_storage.remove.return_value = None
        mock_table.delete.return_value.eq.return_value.execute.return_value = None
        
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/invoices/{invoice_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Invoice deleted successfully"
        assert data["invoice_id"] == invoice_id
        assert data["filename"] == "20241201_INV001_ACME_SUPPLY.pdf"
        assert data["status"] == "success"
        
        # Verify storage remove was called
        mock_storage.remove.assert_called_once_with(["20241201_INV001_ACME_SUPPLY.pdf"])

    @patch('main.supabase')
    def test_delete_invoice_not_found(self, mock_supabase):
        """Test deletion of non-existent invoice"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        mock_response = MagicMock()
        mock_response.data = []  # Empty response
        
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        
        invoice_id = "non-existent-id"
        response = client.delete(f"/invoices/{invoice_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "Invoice not found" in data["detail"]

    @patch('main.supabase')
    def test_delete_invoice_storage_error(self, mock_supabase):
        """Test handling storage errors during deletion"""
        mock_table = MagicMock()
        mock_storage = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_supabase.storage.from_.return_value = mock_storage
        
        # Mock getting the invoice first
        mock_get_response = MagicMock()
        mock_get_response.data = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "20241201_INV001_ACME_SUPPLY.pdf",
                "url": "https://example.com/test.pdf",
                "status": "uploaded"
            }
        ]
        
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_get_response
        mock_storage.remove.side_effect = Exception("Storage deletion failed")
        
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/invoices/{invoice_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to delete invoice" in data["detail"]

    @patch('main.supabase')
    def test_delete_invoice_database_error(self, mock_supabase):
        """Test handling database errors during deletion"""
        mock_table = MagicMock()
        mock_storage = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_supabase.storage.from_.return_value = mock_storage
        
        # Mock getting the invoice first
        mock_get_response = MagicMock()
        mock_get_response.data = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "20241201_INV001_ACME_SUPPLY.pdf",
                "url": "https://example.com/test.pdf",
                "status": "uploaded"
            }
        ]
        
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_get_response
        mock_storage.remove.return_value = None
        mock_table.delete.side_effect = Exception("Database deletion failed")
        
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/invoices/{invoice_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to delete invoice" in data["detail"]

class TestSupabaseConnection:
    """Test Supabase connection handling"""
    
    @patch('main.supabase', None)
    def test_upload_without_supabase(self):
        """Test upload endpoint when Supabase is not configured"""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 500
        data = response.json()
        assert "Supabase not configured" in data["detail"]

    @patch('main.supabase', None)
    def test_get_invoices_without_supabase(self):
        """Test get invoices endpoint when Supabase is not configured"""
        response = client.get("/invoices")
        
        assert response.status_code == 500
        data = response.json()
        assert "Supabase not configured" in data["detail"]

    @patch('main.supabase', None)
    def test_get_single_invoice_without_supabase(self):
        """Test get single invoice endpoint when Supabase is not configured"""
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/invoices/{invoice_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "Supabase not configured" in data["detail"]

    @patch('main.supabase', None)
    def test_delete_invoice_without_supabase(self):
        """Test delete invoice endpoint when Supabase is not configured"""
        invoice_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/invoices/{invoice_id}")
        
        assert response.status_code == 500
        data = response.json()
        assert "Supabase not configured" in data["detail"]

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_upload_empty_file(self):
        """Test uploading an empty file"""
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(b""), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        
        # Should fail validation or processing
        assert response.status_code in [400, 500]

    @pytest.mark.parametrize("invalid_id", [
        "invalid-uuid",
        "123",
        "not-a-uuid-at-all",
        "123e4567-e89b-12d3-a456-42661417400"  # Invalid UUID format
    ])
    @patch('main.supabase')
    def test_get_invoice_invalid_uuid_format(self, mock_supabase, invalid_id):
        """Test handling of invalid UUID formats"""
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        
        response = client.get(f"/invoices/{invalid_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "Invoice not found" in data["detail"]

    def test_upload_oversized_filename(self):
        """Test uploading file with very long filename"""
        long_filename = "20241201_" + "A" * 200 + "_VENDOR_TYPE.pdf"
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        
        files = {
            "file": (long_filename, io.BytesIO(pdf_content), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        
        # Should pass validation since it follows the pattern, even if long
        # The actual behavior depends on Supabase storage limits
        assert response.status_code in [200, 400, 500]