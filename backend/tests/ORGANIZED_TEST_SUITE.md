# Invoice OCR Backend - Organized Test Suite Documentation

## Overview

This document describes the newly organized test structure for the Invoice OCR Backend application. The test suite has been reorganized from a scattered structure into a well-organized, maintainable hierarchy with enhanced tooling.

## Test Structure

```
tests/
├── __init__.py                     # Python package initialization
├── README.md                       # Test documentation
├── unit/                          # Unit tests with mocked dependencies
│   ├── __init__.py
│   └── test_main.py              # 33 comprehensive unit tests
├── integration/                   # Integration tests requiring Supabase
│   ├── __init__.py
│   └── test_integration.py       # 11 end-to-end integration tests
├── ocr/                          # OCR-specific functionality tests
│   ├── __init__.py
│   ├── test_ocr.py              # Comprehensive OCR functionality testing
│   └── test_real_ocr.py         # Real Google Cloud Document AI testing
├── scripts/                      # Test utility scripts and runners
│   ├── __init__.py
│   ├── run_tests.sh             # Enhanced bash test runner
│   ├── test_runner.py           # Enhanced Python test runner
│   └── test_ocr_endpoints.sh    # Enhanced OCR endpoint testing
└── utilities/                    # Future test utilities
    └── __init__.py
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- **File**: `test_main.py`
- **Count**: 33 tests
- **Coverage**: 92% of main application code
- **Dependencies**: All external dependencies mocked
- **Runtime**: ~1-2 seconds
- **Purpose**: Test individual functions and components in isolation

**Test Classes**:
- `TestHealthEndpoints` - API health check endpoints
- `TestFileUpload` - File upload functionality
- `TestGetInvoices` - Invoice retrieval operations
- `TestFilenameValidation` - Filename pattern validation
- `TestGetSingleInvoice` - Single invoice retrieval
- `TestDeleteInvoice` - Invoice deletion operations
- `TestSupabaseConnection` - Database connection handling
- `TestEdgeCases` - Edge cases and error conditions

### 2. Integration Tests (`tests/integration/`)
- **File**: `test_integration.py`
- **Count**: 11 tests
- **Dependencies**: Requires Supabase credentials
- **Runtime**: ~5-10 seconds
- **Purpose**: Test complete workflows with real database

**Test Classes**:
- `TestFullWorkflowIntegration` - End-to-end invoice processing
- `TestErrorRecoveryIntegration` - Error handling and recovery
- `TestCrossEndpointDataConsistency` - Data consistency across endpoints
- `TestSystemHealthIntegration` - System health monitoring
- `TestPerformanceIntegration` - Performance and load testing
- `TestSecurityIntegration` - Security and validation testing

### 3. OCR Tests (`tests/ocr/`)
- **Files**: `test_ocr.py`, `test_real_ocr.py`
- **Count**: 7 tests
- **Dependencies**: Optional Google Cloud credentials
- **Runtime**: ~1-5 seconds
- **Purpose**: Test OCR functionality and Google Cloud integration

**Features Tested**:
- OCR service status and health
- Invoice file upload and processing
- Document AI integration
- OCR data extraction and parsing

## Enhanced Test Runners

### 1. Main Test Runner (`run_tests.py`)
Located in backend root directory, provides comprehensive test suite management.

```bash
# Usage examples
python run_tests.py all              # Run all tests
python run_tests.py unit            # Run only unit tests
python run_tests.py integration     # Run only integration tests
python run_tests.py ocr             # Run only OCR tests
python run_tests.py coverage        # Run all tests with coverage
```

**Features**:
- Automatic dependency installation
- Supabase credential checking
- Coverage report generation
- Clear progress indication and summaries
- HTML coverage reports in `htmlcov/`

### 2. Enhanced Bash Runner (`tests/scripts/run_tests.sh`)
Advanced bash script with comprehensive error handling and organization.

```bash
# Usage examples
./tests/scripts/run_tests.sh                    # Run all tests
./tests/scripts/run_tests.sh unit              # Run unit tests only
./tests/scripts/run_tests.sh coverage          # Run with coverage
./tests/scripts/run_tests.sh -v integration    # Verbose integration tests
```

**Features**:
- Bash strict mode (`set -euo pipefail`)
- Colored output and progress indicators
- Comprehensive error handling
- Environment setup and validation
- Modular function design
- Command-line argument parsing

### 3. Enhanced Python Runner (`tests/scripts/test_runner.py`)
Object-oriented Python test runner with advanced features.

```bash
# Usage examples
python tests/scripts/test_runner.py unit --verbose
python tests/scripts/test_runner.py --parallel coverage
python tests/scripts/test_runner.py integration --timeout 600
```

**Features**:
- Object-oriented design with `TestRunner` class
- Parallel test execution support
- Configurable timeouts
- Detailed test result tracking
- Type hints and dataclasses
- Comprehensive argument parsing

### 4. OCR Endpoint Testing (`tests/scripts/test_ocr_endpoints.sh`)
Specialized script for testing OCR API endpoints.

```bash
# Usage examples
./tests/scripts/test_ocr_endpoints.sh                           # Default testing
./tests/scripts/test_ocr_endpoints.sh -u http://localhost:3000  # Custom URL
./tests/scripts/test_ocr_endpoints.sh -f custom.pdf -v         # Custom file with verbose
```

**Features**:
- Server connectivity checking
- API endpoint testing with error handling
- JSON response validation and pretty printing
- Customizable base URL and test files
- Comprehensive endpoint coverage

## Test Execution Examples

### Quick Unit Tests
```bash
# Fastest way to run unit tests
python run_tests.py unit
```

### Full Test Suite
```bash
# Complete test suite with coverage
python run_tests.py coverage
```

### Integration Testing (requires Supabase)
```bash
# Set up credentials first
export SUPA_URL='your_supabase_url'
export SUPA_KEY='your_supabase_anon_key'

# Run integration tests
python run_tests.py integration
```

### OCR Endpoint Testing (requires running server)
```bash
# Start the server first
python main.py

# In another terminal, test endpoints
./tests/scripts/test_ocr_endpoints.sh
```

## Coverage Reports

The test suite maintains high coverage (92%+) with detailed reporting:

- **Terminal**: Real-time coverage statistics
- **HTML**: Comprehensive reports in `htmlcov/index.html`
- **Missing Lines**: Detailed coverage gaps identification

## Environment Requirements

### Required
- Python 3.8+
- pytest and dependencies (automatically installed)
- FastAPI application dependencies

### Optional (for full testing)
- Supabase credentials (for integration tests)
- Google Cloud credentials (for real OCR testing)
- Running backend server (for endpoint testing)

## Best Practices

### Running Tests During Development
1. **Quick feedback**: `python run_tests.py unit`
2. **Before commits**: `python run_tests.py coverage`
3. **Integration validation**: `python run_tests.py integration`

### Continuous Integration
```bash
# Recommended CI pipeline
./tests/scripts/run_tests.sh coverage
```

### Test File Organization
- **Unit tests**: Mock all external dependencies
- **Integration tests**: Use real database connections
- **OCR tests**: Can work with mocked or real OCR services
- **Scripts**: Provide different interfaces for different use cases

## Migration Notes

The test reorganization maintains 100% backward compatibility:
- All existing tests preserved and working
- Test coverage maintained at 92%+
- Same test execution time
- Enhanced organization and tooling
- Better maintainability and scalability

## Future Enhancements

### Planned Additions
- Performance benchmarking tests in `tests/performance/`
- Security testing suite in `tests/security/`
- Load testing utilities in `tests/load/`
- Mock data generators in `tests/utilities/`

### Recommended Workflow
1. Write unit tests first for new features
2. Add integration tests for workflow validation
3. Run coverage analysis to identify gaps
4. Use endpoint testing for API validation
5. Regular cleanup of outdated test utilities

## Troubleshooting

### Common Issues
1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Integration test failures**: Check Supabase credentials
3. **OCR test failures**: Verify Google Cloud setup
4. **Endpoint test failures**: Ensure backend server is running

### Debug Mode
```bash
# Run with maximum verbosity
python tests/scripts/test_runner.py unit --verbose
./tests/scripts/run_tests.sh -v unit
```

This organized test structure provides a solid foundation for maintaining high code quality while supporting rapid development and deployment cycles.
