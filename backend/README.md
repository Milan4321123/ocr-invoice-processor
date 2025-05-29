# Invoice OCR Backend

FastAPI backend for the Invoice OCR Processing System with comprehensive Google Cloud Document AI integration.

## ✨ Features

- 📄 **PDF Upload & Storage**: Secure file upload with Supabase integration
- 🔍 **OCR Processing**: Google Cloud Document AI for text extraction
- 📊 **Structured Data**: Intelligent invoice parsing (vendor, amounts, dates)
- 💾 **Database Integration**: Comprehensive schema for OCR results
- 🏥 **Health Monitoring**: System status and OCR service monitoring
- 🔒 **Security**: Environment-based configuration with safe defaults

## 🚀 Quick Start

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Update database schema:**
   ```bash
   python database_migration.py
   # Run the generated SQL in your Supabase SQL editor
   ```

5. **Start the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Test the setup:**
   ```bash
   python test_ocr.py  # Comprehensive test suite
   curl http://localhost:8000/ocr/status  # OCR status check
   ```

## 📚 Documentation

- **[Google Cloud Setup](docs/GOOGLE_CLOUD_SETUP.md)**: Complete guide for enabling OCR
- **[OCR Status Report](docs/OCR_STATUS_REPORT.md)**: Implementation status and testing
- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs (when server is running)

## 🔧 Configuration

### Basic Setup (Works without OCR)
```bash
# Required for basic functionality
SUPA_URL=your_supabase_project_url
SUPA_KEY=your_supabase_anon_key

# OCR disabled by default (safe for initial setup)
ENABLE_OCR=false
```

### Full OCR Setup
```bash
# Enable OCR after Google Cloud setup
ENABLE_OCR=true
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_PROCESSOR_ID=your-processor-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## 🔍 API Endpoints

### Core Endpoints
- `GET /` - API status and version
- `GET /health` - System health including OCR status
- `POST /upload` - Upload PDF invoice with automatic OCR
- `GET /invoices` - List all invoices
- `GET /invoices/{id}` - Get specific invoice
- `DELETE /invoices/{id}` - Delete invoice

### OCR Endpoints
- `GET /ocr/status` - OCR service status and configuration
- `POST /ocr/process/{invoice_id}` - Process OCR for existing invoice
- `GET /invoices/{invoice_id}/ocr` - Get OCR data for invoice

## 🧪 Testing

### Run All Tests
```bash
./run_tests.sh  # Complete test suite
```

### Individual Test Categories
```bash
# Unit tests (no external dependencies)
python -m pytest tests/test_main.py -v

# Integration tests (requires Supabase)
python -m pytest tests/test_integration.py -v

# OCR functionality test
python test_ocr.py
```

### Test Coverage
```bash
python -m pytest tests/ --cov=main --cov-report=term-missing -v
```

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application with OCR integration
├── config/              # Configuration management
│   ├── __init__.py
│   └── ocr_config.py    # OCR settings and validation
├── ocr/                 # OCR processing modules
│   ├── __init__.py
│   ├── document_ai_service.py  # Google Cloud Document AI
│   ├── invoice_parser.py       # Invoice-specific parsing
│   └── workflow.py            # OCR workflow orchestration
├── docs/                # Documentation
│   ├── GOOGLE_CLOUD_SETUP.md
│   └── OCR_STATUS_REPORT.md
├── tests/              # Test suite
├── database_migration.py  # Database schema migration
└── test_ocr.py        # OCR testing script
```

## 🛠 Database Schema

The system includes comprehensive database schema for OCR data:

### OCR Metadata Columns
- `ocr_status` - Processing status (pending, completed, failed, disabled)
- `ocr_confidence` - Overall confidence score (0.0-1.0)
- `ocr_pages` - Number of pages processed
- `ocr_processing_time` - Processing time in seconds
- `ocr_error` - Error details if processing failed

### Structured Invoice Data
- `invoice_number`, `invoice_date`, `due_date`
- `vendor_name`, `vendor_address`
- `customer_name`, `customer_address`  
- `subtotal`, `tax_amount`, `total_amount`
- `currency`, `payment_terms`, `po_number`

### Complex Data (JSON)
- `ocr_entities` - Document AI entities
- `ocr_form_fields` - Form field mappings
- `ocr_tables` - Table structures
- `line_items` - Invoice line items

## 🔒 Security

- **Environment-based configuration** - No hardcoded secrets
- **OCR disabled by default** - Safe initial setup
- **Service account authentication** - Secure Google Cloud access
- **Input validation** - File type and format checking
- **Error handling** - Graceful failures without exposure

## 📈 Performance

- **Async processing** - Non-blocking OCR operations
- **Configurable timeouts** - Prevent hanging requests
- **Retry logic** - Handle transient failures
- **Database indexing** - Optimized OCR data queries
- **File size limits** - Configurable upload restrictions

## 🐛 Troubleshooting

### Common Issues

1. **"Could not find ocr_confidence column"**
   ```bash
   python database_migration.py
   # Apply the SQL in Supabase SQL editor
   ```

2. **"OCR service not available"**
   - Check Google Cloud credentials
   - Verify processor ID and location
   - See `docs/GOOGLE_CLOUD_SETUP.md`

3. **"Module 'distutils' not found"**
   ```bash
   pip install setuptools
   ```

### Debug Commands
```bash
# Check OCR status
curl http://localhost:8000/ocr/status

# Test basic connectivity  
curl http://localhost:8000/health

# Run comprehensive tests
python test_ocr.py
```

## 📄 License

MIT License - see LICENSE file for details.