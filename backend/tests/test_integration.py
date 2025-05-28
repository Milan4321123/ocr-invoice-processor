import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
import io

# Only run integration tests if environment variables are set
@pytest.mark.skipif(
    not os.getenv("SUPA_URL") or not os.getenv("SUPA_KEY"),
    reason="Supabase credentials not available"
)
class TestIntegration:
    """Integration tests that require actual Supabase connection"""
    
    def test_full_upload_workflow(self):
        """Test complete upload workflow with real Supabase (if configured)"""
        from main import app
        client = TestClient(app)
        
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
        
        files = {
            "file": (f"20241201_TEST{os.getpid()}_INTEGRATION_TEST.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        
        # Upload file
        response = client.post("/upload", files=files)
        assert response.status_code == 200
        
        upload_data = response.json()
        assert upload_data["status"] == "uploaded"
        
        # Verify file appears in invoice list
        response = client.get("/invoices")
        assert response.status_code == 200
        
        invoices_data = response.json()
        uploaded_invoice = next(
            (inv for inv in invoices_data["invoices"] if inv["filename"] == files["file"][0]),
            None
        )
        assert uploaded_invoice is not None
        assert uploaded_invoice["status"] == "uploaded"
        
        # Clean up - delete the test invoice
        invoice_id = uploaded_invoice["id"]
        response = client.delete(f"/invoices/{invoice_id}")
        assert response.status_code == 200
