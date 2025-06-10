class TestGetInvoicePdf:
    """Test cases for get_invoice_pdf endpoint"""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        return mock_client, mock_table

    @pytest.mark.asyncio
    async def test_get_invoice_pdf_demo_mode(self):
        """Test PDF retrieval in demo mode (no Supabase)"""
        invoice_id = "test-invoice-123"
        
        with patch('..invoice_editor.supabase', None):
            result = await get_invoice_pdf(invoice_id)
            
            assert isinstance(result, RedirectResponse)
            assert result.url == f"http://localhost:8000/mock-storage/{invoice_id}.pdf"

    @pytest.mark.asyncio
    async def test_get_invoice_pdf_success_with_supabase(self, mock_supabase):
        """Test successful PDF retrieval with real Supabase data"""
        mock_client, mock_table = mock_supabase
        invoice_id = "test-invoice-456"
        expected_url = "https://storage.example.com/invoice.pdf"
        
        # Mock successful database query
        mock_select = Mock()
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value.execute.return_value.data = [
            {"url": expected_url}
        ]
        
        with patch('..invoice_editor.supabase', mock_client):
            result = await get_invoice_pdf(invoice_id)
            
            assert isinstance(result, RedirectResponse)
            assert result.url == expected_url
            mock_table.select.assert_called_once_with("url")
            mock_select.eq.assert_called_once_with("id", invoice_id)

    @pytest.mark.asyncio
    async def test_get_invoice_pdf_not_found(self, mock_supabase):
        """Test PDF retrieval when invoice doesn't exist"""
        mock_client, mock_table = mock_supabase
        invoice_id = "nonexistent-invoice"
        
        # Mock empty database result
        mock_select = Mock()
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value.execute.return_value.data = []
        
        with patch('..invoice_editor.supabase', mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_invoice_pdf(invoice_id)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Invoice not found"

    @pytest.mark.asyncio
    async def test_get_invoice_pdf_database_error(self, mock_supabase):
        """Test PDF retrieval with database connection error"""
        mock_client, mock_table = mock_supabase
        invoice_id = "test-invoice-error"
        
        # Mock database exception
        mock_select = Mock()
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value.execute.side_effect = Exception("Database connection failed")
        
        with patch('..invoice_editor.supabase', mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await get_invoice_pdf(invoice_id)
            
            assert exc_info.value.status_code == 500
            assert "Failed to retrieve PDF: Database connection failed" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_invoice_pdf_supabase_import_error(self):
        """Test PDF retrieval when Supabase import fails"""
        invoice_id = "test-invoice-import-error"
        
        with patch('..invoice_editor.supabase', side_effect=ImportError("Cannot import supabase")):
            with pytest.raises(HTTPException) as exc_info:
                await get_invoice_pdf(invoice_id)
            
            assert exc_info.value.status_code == 500
            assert "Failed to retrieve PDF" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_invoice_pdf_with_special_characters(self, mock_supabase):
        """Test PDF retrieval with special characters in invoice ID"""
        mock_client, mock_table = mock_supabase
        invoice_id = "test-invoice-äöü-123"
        expected_url = "https://storage.example.com/special-chars.pdf"
        
        mock_select = Mock()
        mock_table.select.return_value = mock_select