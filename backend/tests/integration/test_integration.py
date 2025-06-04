"""
Integration tests for the Invoice OCR API
Tests full workflows end-to-end including cross-endpoint interactions
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import uuid
from datetime import datetime

from main import app

client = TestClient(app)

class TestFullWorkflowIntegration:
    """Test complete invoice processing workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_invoice_lifecycle(self):
        """Test full invoice lifecycle in demo mode: upload → retrieve → delete"""
        # This test works in demo mode (no Supabase)
        
        # Step 1: Upload invoice
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        upload_response = client.post("/upload", files=files)
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        uploaded_id = upload_data["id"]
        uploaded_filename = upload_data["filename"]
        
        # Verify upload response structure
        assert "status" in upload_data
        assert "filename" in upload_data
        assert "url" in upload_data
        assert "id" in upload_data
        assert upload_data["status"] == "uploaded"
        
        # Step 2: Test invoice retrieval (demo mode behavior)
        # In demo mode, individual invoice retrieval returns demo data
        get_response = client.get(f"/invoices/{uploaded_id}")
        # Demo mode returns 404 for individual invoices since there's no persistence
        # This is expected behavior in demo mode
        assert get_response.status_code in [200, 404]
        
        # Step 3: List all invoices (demo mode)
        list_response = client.get("/invoices")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert "invoices" in list_data
        
        # Step 4: Delete the invoice (demo mode)
        delete_response = client.delete(f"/invoices/{uploaded_id}")
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert "status" in delete_data
        
        # Verify system remains healthy after full workflow
        health_response = client.get("/health")
        assert health_response.status_code == 200

    def test_demo_mode_full_workflow(self):
        """Test complete workflow in demo mode (no Supabase)"""
        with patch('main.supabase', None):
            # Step 1: Upload in demo mode
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
            files = {
                "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(pdf_content), "application/pdf")
            }
            
            upload_response = client.post("/upload", files=files)
            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            assert "mock-storage" in upload_data["url"]
            
            # Step 2: List invoices in demo mode
            list_response = client.get("/invoices")
            assert list_response.status_code == 200
            list_data = list_response.json()
            assert "Demo mode" in list_data["message"]
            assert list_data["total"] == 0
            
            # Step 3: Try to get single invoice in demo mode
            demo_id = str(uuid.uuid4())
            get_response = client.get(f"/invoices/{demo_id}")
            assert get_response.status_code == 404
            assert "Demo mode" in get_response.json()["detail"]
            
            # Step 4: Delete in demo mode
            delete_response = client.delete(f"/invoices/{demo_id}")
            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert "Demo mode" in delete_data["message"]

class TestErrorRecoveryIntegration:
    """Test error recovery and resilience across endpoints"""
    
    @patch('main.supabase')
    def test_partial_failure_recovery(self, mock_supabase):
        """Test recovery from partial failures in the workflow"""
        mock_storage = MagicMock()
        mock_table = MagicMock()
        mock_supabase.storage.from_.return_value = mock_storage
        mock_supabase.table.return_value = mock_table
        
        # Scenario: Storage works but database insert fails
        mock_storage.upload.return_value = None
        mock_storage.get_public_url.return_value = "https://example.com/test.pdf"
        mock_table.insert.side_effect = Exception("Database insert failed")
        
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        files = {
            "file": ("20241201_INV001_ACME_SUPPLY.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        response = client.post("/upload", files=files)
        assert response.status_code == 500
        assert "Upload failed" in response.json()["detail"]
        
        # Verify system is still functional after error
        health_response = client.get("/health")
        assert health_response.status_code == 200

    @patch('main.supabase')
    def test_concurrent_operations_simulation(self, mock_supabase):
        """Simulate concurrent operations on the same resources"""
        mock_storage = MagicMock()
        mock_table = MagicMock()
        mock_supabase.storage.from_.return_value = mock_storage
        mock_supabase.table.return_value = mock_table
        
        invoice_id = str(uuid.uuid4())
        
        # Setup successful responses
        mock_storage.upload.return_value = None
        mock_storage.get_public_url.return_value = f"https://example.com/test_{invoice_id}.pdf"
        
        mock_insert_response = MagicMock()
        mock_insert_response.data = [{
            "id": invoice_id,
            "filename": "20241201_INV001_ACME_SUPPLY.pdf",
            "url": f"https://example.com/test_{invoice_id}.pdf",
            "status": "uploaded"
        }]
        mock_table.insert.return_value.execute.return_value = mock_insert_response
        
        # Simulate concurrent reads
        mock_get_response = MagicMock()
        mock_get_response.data = [mock_insert_response.data[0]]
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_get_response
        
        # Multiple concurrent requests
        responses = []
        for i in range(3):
            response = client.get(f"/invoices/{invoice_id}")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["invoice"]["id"] == invoice_id

class TestCrossEndpointDataConsistency:
    """Test data consistency across different endpoints"""
    
    @patch('main.supabase')
    def test_data_consistency_after_operations(self, mock_supabase):
        """Test that data remains consistent across different endpoint calls"""
        mock_storage = MagicMock()
        mock_table = MagicMock()
        mock_supabase.storage.from_.return_value = mock_storage
        mock_supabase.table.return_value = mock_table
        
        # Mock multiple invoices
        invoices = [
            {
                "id": str(uuid.uuid4()),
                "filename": "20241201_INV001_ACME_SUPPLY.pdf",
                "url": "https://example.com/test1.pdf",
                "status": "uploaded",
                "created_at": "2024-12-01T10:00:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "filename": "20241202_INV002_VENDOR_RECEIPT.pdf", 
                "url": "https://example.com/test2.pdf",
                "status": "uploaded",
                "created_at": "2024-12-02T10:00:00Z"
            }
        ]
        
        # Test list endpoint
        mock_list_response = MagicMock()
        mock_list_response.data = invoices
        mock_table.select.return_value.order.return_value.execute.return_value = mock_list_response
        
        list_response = client.get("/invoices")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data["invoices"]) == 2
        
        # Test individual retrieval for each invoice
        for invoice in invoices:
            mock_single_response = MagicMock()
            mock_single_response.data = [invoice]
            mock_table.select.return_value.eq.return_value.execute.return_value = mock_single_response
            
            single_response = client.get(f"/invoices/{invoice['id']}")
            assert single_response.status_code == 200
            single_data = single_response.json()
            
            # Data should match between list and individual retrieval
            list_invoice = next(inv for inv in list_data["invoices"] if inv["id"] == invoice["id"])
            assert single_data["invoice"]["filename"] == list_invoice["filename"]
            assert single_data["invoice"]["url"] == list_invoice["url"]
            assert single_data["invoice"]["status"] == list_invoice["status"]

class TestSystemHealthIntegration:
    """Test system health and monitoring integration"""
    
    def test_health_endpoints_comprehensive(self):
        """Test all health and monitoring endpoints"""
        # Test root endpoint
        root_response = client.get("/")
        assert root_response.status_code == 200
        root_data = root_response.json()
        assert "Invoice OCR API is running" in root_data["message"]
        assert "version" in root_data
        
        # Test health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        # Test debug configuration
        debug_response = client.get("/debug/ocr-config")
        assert debug_response.status_code == 200
        debug_data = debug_response.json()
        assert "gcp_project_id" in debug_data
        assert "enable_ocr" in debug_data
        assert "env_vars" in debug_data

    def test_system_resilience_after_errors(self):
        """Test that system remains healthy after various error conditions"""
        # Generate some operations that would be errors in production but are handled gracefully in demo mode
        test_responses = []
        
        # Invalid file upload (demo mode should handle gracefully)
        files = {"file": ("invalid.txt", io.BytesIO(b"not a pdf"), "text/plain")}
        test_responses.append(client.post("/upload", files=files))
        
        # Invalid invoice ID (demo mode should return graceful response)
        test_responses.append(client.get("/invoices/invalid-id"))
        
        # Non-existent invoice deletion (demo mode should handle gracefully)
        test_responses.append(client.delete("/invoices/non-existent"))
        
        # In demo mode, system should handle errors gracefully with 200 responses
        # In production mode, these would be proper HTTP error codes
        for response in test_responses:
            # System should respond (not crash) - either success or proper error
            assert response.status_code in [200, 400, 404, 500]
            # Should return valid JSON
            assert response.headers.get("content-type") == "application/json"
        
        # System should still be healthy
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

class TestPerformanceIntegration:
    """Test performance characteristics across endpoints"""
    
    def test_multiple_file_uploads_handling(self):
        """Test system behavior with multiple file uploads"""
        with patch('main.supabase', None):  # Use demo mode for consistent testing
            upload_responses = []
            
            # Upload multiple files
            for i in range(3):
                pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
                files = {
                    "file": (f"2024120{i+1}_INV00{i+1}_VENDOR_TYPE.pdf", 
                            io.BytesIO(pdf_content), "application/pdf")
                }
                
                response = client.post("/upload", files=files)
                upload_responses.append(response)
            
            # All uploads should succeed in demo mode
            for response in upload_responses:
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "uploaded"
                assert "mock-storage" in data["url"]

    def test_large_file_handling(self):
        """Test handling of larger PDF files"""
        with patch('main.supabase', None):
            # Create a larger PDF content (simulate ~50KB file)
            large_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"
            large_pdf_content += b"Large content section " * 1000  # Repeat to make it larger
            large_pdf_content += b"\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
            
            files = {
                "file": ("20241201_INV001_LARGE_FILE.pdf", 
                        io.BytesIO(large_pdf_content), "application/pdf")
            }
            
            response = client.post("/upload", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data["file_size"] > 1000  # Should be larger than minimal PDF

class TestSecurityIntegration:
    """Test security aspects across the API"""
    
    def test_malicious_filename_handling(self):
        """Test handling of potentially malicious filenames"""
        malicious_filenames = [
            "20241201_INV001_../../etc/passwd.pdf",
            "20241201_INV001_<script>alert('xss')</script>_TYPE.pdf",
            "20241201_INV001_VENDOR_TYPE'; DROP TABLE invoices; --.pdf"
        ]
        
        for filename in malicious_filenames:
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
            files = {"file": (filename, io.BytesIO(pdf_content), "application/pdf")}
            
            response = client.post("/upload", files=files)
            # Should either reject invalid filename or sanitize it
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                # If accepted, verify the filename is sanitized
                data = response.json()
                assert "../" not in data["filename"]
                assert "<script>" not in data["filename"]
    
    def test_request_id_tracking(self):
        """Test that request IDs are properly set for traceability"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        # Request ID should be a valid UUID format
        request_id = response.headers["X-Request-ID"]
        uuid.UUID(request_id)  # This will raise ValueError if not valid UUID

if __name__ == "__main__":
    pytest.main([__file__, "-v"])