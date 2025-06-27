# Comprehensive Upload Test Suite Documentation

This document describes the comprehensive test suite created for the OCR Invoice Processor upload functionality. The test suite covers all upload sources, edge cases, and complete workflows.

## Test Files Overview

### 1. `test_comprehensive_uploads.py`
**Purpose**: Comprehensive backend-level tests for upload functionality
**Requirements**: Backend imports (services.upload_service, etc.)
**Coverage**:
- File validation (types, sizes, patterns)
- Duplicate detection
- Storage path generation  
- Filename sanitization
- Folder watcher edge cases
- Rapid file changes
- Large file handling
- Concurrent uploads
- Corrupted file handling
- Notification system
- Error recovery scenarios

### 2. `test_api_uploads.py`  
**Purpose**: API-level tests using HTTP requests
**Requirements**: Running backend server
**Coverage**:
- API connectivity tests
- Valid file uploads via API
- Invalid file rejection
- Duplicate upload detection
- Folder watcher API endpoints
- Folder operations (add/remove/enable/disable)
- Invalid folder operations
- Upload response format validation
- Concurrent API uploads
- API error handling

### 3. `test_e2e_workflow.py`
**Purpose**: End-to-end integration tests
**Requirements**: Running backend and optionally frontend
**Coverage**:
- Complete drag & drop workflow
- Complete folder watcher workflow  
- Complete manual upload workflow
- Invoice editing workflow (save/complete)
- Dropdown management workflow
- Frontend integration tests
- Data consistency across views
- Error scenario testing
- Test data cleanup

### 4. `test_standalone_validation.py`
**Purpose**: Standalone validation tests (no dependencies)
**Requirements**: None (pure Python)
**Coverage**:
- Filename pattern validation
- File type validation
- File size validation
- Combined validation scenarios
- Edge cases and boundary conditions

### 5. `run_comprehensive_tests.sh`
**Purpose**: Master test runner script
**Requirements**: Running backend server
**Coverage**:
- Service availability checks
- Python test suite execution
- Manual API testing with curl
- Folder watcher functionality
- Dashboard and editor testing
- Dropdown functionality
- Performance testing
- Comprehensive reporting

## Upload Sources Tested

### 1. Drag & Drop Upload
- **API Endpoint**: `POST /api/upload`
- **Storage Bucket**: `invoices`
- **Tests**:
  - Valid PDF uploads
  - Invalid filename patterns
  - Wrong file types
  - File size limits
  - Duplicate detection
  - Response format validation

### 2. Folder Watcher Upload
- **API Endpoints**: `/api/folder-watcher/*`
- **Storage Bucket**: `folderwatcher`
- **Tests**:
  - Watch folder management (add/remove/enable/disable)
  - File detection and processing
  - Notification system
  - Rapid file changes
  - Permission issues
  - Non-existent folders
  - Service start/stop

### 3. Manual Upload
- **API Endpoint**: `POST /api/upload` (same as drag & drop)
- **Storage Bucket**: `manual-invoices`
- **Tests**:
  - Direct API usage
  - Data consistency
  - Invoice retrieval

## Validation Rules Tested

### Filename Pattern
- **Required Format**: `YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf`
- **Examples**:
  - ✅ `20250627_INV001_ACME_SERVICE.pdf`
  - ✅ `20240101_123ABC_TEST456_INVOICE99.pdf`
  - ❌ `invalid_filename.pdf`
  - ❌ `20250627_INV001_ACME.pdf` (missing TYPE)

### File Type
- **Allowed**: `application/pdf` only
- **Rejected**: All other MIME types (text/plain, image/*, etc.)

### File Size
- **Maximum**: 10MB
- **Minimum**: > 0 bytes (empty files rejected)

### Duplicate Detection
- **Check**: Filename-based duplicate detection
- **Behavior**: Second upload with same filename should be rejected

## Edge Cases Covered

### File System Edge Cases
- Empty files (0 bytes)
- Very large files (>10MB)
- Corrupted PDF files
- Permission denied scenarios
- Rapid file creation/deletion
- Concurrent file operations

### Folder Watcher Edge Cases
- Non-existent directories
- Permission denied directories
- Files instead of directories
- Service start/stop edge cases
- Notification overflow
- Pending file processing

### API Edge Cases
- Missing file in upload request
- Invalid JSON payloads
- Non-existent invoice IDs
- Concurrent API requests
- Network timeouts
- Service unavailability

## Test Data Management

### Test File Creation
```bash
# Valid PDF structure
%PDF-1.4
[PDF content]
%%EOF
```

### Test File Naming
- `20250627_TEST001_*` - Standard test files
- `20250627_E2E001_*` - End-to-end test files
- `20250627_PERF001_*` - Performance test files
- `20250627_DUP001_*` - Duplicate test files

### Cleanup Strategy
- Automatic cleanup in test scripts
- Test invoice tracking for removal
- Temporary directory cleanup
- Response file cleanup

## Running the Tests

### Prerequisites
```bash
# Start backend server
cd backend && python main.py

# Optional: Start frontend
cd frontend && npm run dev
```

### Run All Tests
```bash
# Master test runner (recommended)
./run_comprehensive_tests.sh

# Individual test files
python3 test_standalone_validation.py
python3 test_api_uploads.py
python3 test_e2e_workflow.py
python3 test_comprehensive_uploads.py
```

### Environment Variables
```bash
export API_URL="http://localhost:8000"
export FRONTEND_URL="http://localhost:3000"
```

## Test Results Interpretation

### Success Criteria
- All validation rules correctly enforced
- All upload sources functional
- Complete workflows working end-to-end
- Error scenarios handled gracefully
- Performance requirements met

### Common Failure Points
1. **Service Unavailability**: Backend not running
2. **Database Issues**: Supabase connectivity problems
3. **Permission Errors**: File system access issues
4. **Timeout Issues**: Slow network or processing
5. **Race Conditions**: Concurrent operation conflicts

## Performance Benchmarks

### Upload Performance
- **Single Upload**: < 2 seconds for 1MB file
- **Concurrent Uploads**: 5 simultaneous uploads should complete
- **Large Files**: 10MB files should upload within 30 seconds

### Folder Watcher Performance
- **File Detection**: < 3 seconds after file creation
- **Processing**: < 5 seconds for validation and upload
- **Notifications**: Real-time notification delivery

## Maintenance and Updates

### Adding New Tests
1. Add test cases to appropriate test file
2. Update documentation
3. Ensure cleanup procedures included
4. Test across all upload sources

### Updating Validation Rules
1. Update validation logic in backend
2. Update test expectations in all test files
3. Update documentation
4. Run full test suite to verify

### Test File Maintenance
- Regular cleanup of test data
- Update test files for new scenarios
- Monitor test execution time
- Update dependencies as needed

## Integration with CI/CD

The test suite is designed to be integrated into CI/CD pipelines:

```bash
# CI/CD command
./run_comprehensive_tests.sh
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "All tests passed - deployment approved"
else
    echo "Tests failed - deployment blocked"
    exit 1
fi
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure backend directory in Python path
2. **Connection Refused**: Verify backend server is running
3. **Permission Denied**: Check file system permissions
4. **Test Timeouts**: Increase timeout values for slow systems

### Debug Mode
Enable verbose logging in test files by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

This comprehensive test suite ensures the OCR Invoice Processor upload functionality is robust, reliable, and handles all edge cases appropriately across all upload sources.
