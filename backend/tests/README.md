# Backend Testing Documentation

This document describes the comprehensive test suite for the Invoice OCR Processor backend API.

## Overview

The backend has a comprehensive test suite that includes:
- **Unit Tests**: Test individual functions and endpoints with mocked dependencies
- **Integration Tests**: Test the complete workflow with real Supabase connection
- **Coverage Reports**: Track test coverage to ensure thorough testing

## Test Structure

```
backend/tests/
├── __init__.py
├── test_main.py          # Unit tests with mocked dependencies
└── test_integration.py   # Integration tests with real Supabase
```

## Running Tests

### Quick Start

Use the provided script to run all tests:

```bash
cd backend
./run_tests.sh
```

### Manual Test Execution

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run Unit Tests Only
```bash
python -m pytest tests/test_main.py -v
```

#### Run Integration Tests (requires Supabase)
```bash
# Set environment variables first
export SUPA_URL='your_supabase_project_url'
export SUPA_KEY='your_supabase_anon_key'

python -m pytest tests/test_integration.py -v
```

#### Run All Tests with Coverage
```bash
python -m pytest tests/ --cov=main --cov-report=term-missing -v
```

## Test Categories

### Unit Tests (`test_main.py`)

These tests use mocked dependencies and don't require external services:

1. **Health Endpoints**
   - Root endpoint functionality
   - Health check endpoint

2. **File Upload**
   - Valid PDF upload with proper filename
   - Invalid filename format rejection
   - Non-PDF file rejection
   - Supabase error handling

3. **Invoice Retrieval**
   - Get all invoices
   - Get single invoice by ID
   - Handle non-existent invoices
   - Database error handling

4. **Invoice Deletion**
   - Successful deletion workflow
   - Delete non-existent invoice
   - Storage and database error handling

5. **Filename Validation**
   - Test various filename patterns
   - Ensure proper regex validation

6. **Edge Cases**
   - Empty file upload
   - Invalid UUID formats
   - Oversized filenames
   - Supabase connection failures

**Current Coverage: 92%**

### Integration Tests (`test_integration.py`)

These tests require actual Supabase credentials and test the complete workflow:

1. **Full Upload Workflow**
   - Upload → Verify in list → Retrieve individual → Delete → Verify deletion

2. **Real Supabase Connection**
   - Test Supabase client initialization
   - Basic endpoint functionality

3. **Upload and Immediate Retrieval**
   - Test rapid upload/retrieval cycle

4. **Error Handling**
   - Test real backend error responses

5. **File Storage Persistence**
   - Verify files are stored correctly in Supabase storage

6. **Multiple Files Handling**
   - Test handling of multiple file uploads

## Environment Setup

### For Unit Tests
No special setup required - tests use mocked dependencies.

### For Integration Tests
Create a `.env` file in the backend directory:

```bash
# Copy from .env.example
cp .env.example .env

# Edit with your actual Supabase credentials
SUPA_URL=https://your-project-id.supabase.co
SUPA_KEY=your_supabase_anon_key_here
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Running Specific Test Types

```bash
# Run only unit tests
python -m pytest -m "not integration" -v

# Run only integration tests  
python -m pytest -m integration -v

# Run tests with coverage
python -m pytest --cov=main --cov-report=html
```

## API Endpoints Tested

| Endpoint | Method | Unit Tests | Integration Tests |
|----------|--------|------------|------------------|
| `/` | GET | ✅ | ✅ |
| `/health` | GET | ✅ | ✅ |
| `/upload` | POST | ✅ | ✅ |
| `/invoices` | GET | ✅ | ✅ |
| `/invoices/{id}` | GET | ✅ | ✅ |
| `/invoices/{id}` | DELETE | ✅ | ✅ |

## Test Data

### Valid PDF Content
Tests use minimal valid PDF content for file upload testing:
```python
pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
```

### Filename Patterns
Tests validate the required filename pattern:
```
YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf
```

Examples:
- ✅ `20250529_INV001_ACME_SUPPLY.pdf`
- ✅ `20250529_ORDER123_VENDOR_INVOICE.pdf`
- ❌ `invalid_filename.pdf`
- ❌ `20250529_INV001_ACME.pdf` (missing TYPE)

## Continuous Integration

The test suite is designed to work in CI/CD environments:

1. **Unit tests** run without external dependencies
2. **Integration tests** are skipped when Supabase credentials aren't available
3. **Coverage reports** can be generated in various formats

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    cd backend
    pip install -r requirements.txt
    python -m pytest tests/test_main.py -v
    
- name: Run Integration Tests
  env:
    SUPA_URL: ${{ secrets.SUPA_URL }}
    SUPA_KEY: ${{ secrets.SUPA_KEY }}
  run: |
    cd backend
    python -m pytest tests/test_integration.py -v
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   # Install all dependencies
   pip install -r requirements.txt
   ```

2. **Integration Tests Skipped**
   ```bash
   # Set environment variables
   export SUPA_URL='your_supabase_url'
   export SUPA_KEY='your_supabase_key'
   ```

3. **Coverage Not Working**
   ```bash
   # Install pytest-cov
   pip install pytest-cov
   ```

### Debug Mode
```bash
# Run tests with more verbose output
python -m pytest tests/ -v -s

# Run specific test
python -m pytest tests/test_main.py::TestFileUpload::test_upload_valid_pdf -v -s
```

## Contributing

When adding new features:

1. Add unit tests with mocked dependencies
2. Add integration tests for end-to-end functionality
3. Ensure test coverage remains above 90%
4. Update this documentation

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use descriptive names that explain what is being tested

### Mocking Guidelines
- Mock external dependencies (Supabase, file system)
- Test both success and error scenarios
- Use `unittest.mock.patch` for dependency injection
- Verify mock calls when testing integrations
