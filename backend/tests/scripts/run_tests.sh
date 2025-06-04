#!/bin/bash
# Invoice OCR Backend Test Runner - Organized Test Suite
# ======================================================
# Enhanced bash script for running organized test suites with better error handling

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Constants and Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BACKEND_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"  # 2 levels up: scripts -> tests -> backend
readonly VENV_PATH="$BACKEND_ROOT/venv"
readonly REQUIREMENTS_FILE="$BACKEND_ROOT/requirements.txt"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Test categories
readonly UNIT_TESTS="tests/unit/"
readonly INTEGRATION_TESTS="tests/integration/"
readonly OCR_TESTS="tests/ocr/"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_section() {
    echo ""
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [TEST_TYPE]

Test Types:
  unit         Run only unit tests
  integration  Run only integration tests
  ocr          Run only OCR tests
  coverage     Run all tests with coverage report
  all          Run all available tests (default)

Options:
  -h, --help   Show this help message
  -v, --verbose Enable verbose output
  -q, --quiet  Suppress non-essential output

Examples:
  $0                    # Run all tests
  $0 unit              # Run only unit tests
  $0 coverage          # Run all tests with coverage
  $0 -v integration    # Run integration tests with verbose output
EOF
}

# Function to setup environment
setup_environment() {
    log_section "🔧 Environment Setup"
    
    # Navigate to backend root
    cd "$BACKEND_ROOT" || {
        log_error "Failed to navigate to backend directory: $BACKEND_ROOT"
        exit 1
    }
    
    # Setup virtual environment
    if [[ ! -d "$VENV_PATH" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_PATH" || {
            log_error "Failed to create virtual environment"
            exit 1
        }
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$VENV_PATH/bin/activate" || {
        log_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Install/update dependencies
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        log_info "Installing dependencies..."
        pip install -q -r "$REQUIREMENTS_FILE" || {
            log_error "Failed to install dependencies"
            exit 1
        }
        
        # Install coverage tool if needed
        pip install -q pytest-cov || {
            log_warning "Failed to install pytest-cov"
        }
    else
        log_warning "Requirements file not found: $REQUIREMENTS_FILE"
    fi
    
    log_success "Environment setup completed"
}

# Function to run specific test category
run_test_category() {
    local test_path="$1"
    local test_name="$2"
    local emoji="$3"
    local verbose_flag="${4:-}"
    
    if [[ ! -d "$test_path" ]]; then
        log_warning "Test directory not found: $test_path"
        return 1
    fi
    
    log_section "$emoji Running $test_name Tests"
    
    local pytest_cmd="python -m pytest $test_path"
    [[ -n "$verbose_flag" ]] && pytest_cmd="$pytest_cmd -v"
    
    if eval "$pytest_cmd"; then
        log_success "$test_name tests completed successfully"
        return 0
    else
        log_error "$test_name tests failed"
        return 1
    fi
}

# Function to check integration test prerequisites
check_integration_prerequisites() {
    if [[ -n "${SUPA_URL:-}" ]] && [[ -n "${SUPA_KEY:-}" ]]; then
        return 0
    else
        log_warning "Integration tests skipped - Supabase credentials not found"
        log_info "To run integration tests, set environment variables:"
        log_info "  export SUPA_URL='your_supabase_url'"
        log_info "  export SUPA_KEY='your_supabase_anon_key'"
        return 1
    fi
}

# Function to run coverage analysis
run_coverage_tests() {
    log_section "📊 Running All Tests with Coverage Analysis"
    
    local coverage_cmd="python -m pytest $UNIT_TESTS $OCR_TESTS"
    
    # Add integration tests if credentials are available
    if check_integration_prerequisites; then
        coverage_cmd="$coverage_cmd $INTEGRATION_TESTS"
    fi
    
    coverage_cmd="$coverage_cmd --cov=main --cov-report=term-missing --cov-report=html"
    [[ "${VERBOSE:-false}" == "true" ]] && coverage_cmd="$coverage_cmd -v"
    
    if eval "$coverage_cmd"; then
        log_success "Coverage analysis completed"
        log_info "HTML coverage report generated in htmlcov/index.html"
        return 0
    else
        log_error "Coverage analysis failed"
        return 1
    fi
}

# Main execution function
main() {
    local test_type="${1:-all}"
    local verbose_flag=""
    [[ "${VERBOSE:-false}" == "true" ]] && verbose_flag="-v"
    local exit_code=0
    
    # Print header
    log_section "🧪 Invoice OCR Backend Test Suite - Organized Structure"
    log_info "Backend Root: $BACKEND_ROOT"
    log_info "Test Structure:"
    log_info "  • $UNIT_TESTS - Unit tests with mocked dependencies"
    log_info "  • $INTEGRATION_TESTS - Integration tests requiring Supabase"
    log_info "  • $OCR_TESTS - OCR-specific functionality tests"
    
    # Setup environment
    setup_environment
    
    # Execute tests based on type
    case "$test_type" in
        "unit")
            run_test_category "$UNIT_TESTS" "Unit" "🔍" "$verbose_flag" || exit_code=1
            ;;
        "integration")
            if check_integration_prerequisites; then
                run_test_category "$INTEGRATION_TESTS" "Integration" "🌐" "$verbose_flag" || exit_code=1
            else
                exit_code=1
            fi
            ;;
        "ocr")
            run_test_category "$OCR_TESTS" "OCR" "🔮" "$verbose_flag" || exit_code=1
            ;;
        "coverage")
            run_coverage_tests || exit_code=1
            ;;
        "all"|*)
            # Run all test categories
            run_test_category "$UNIT_TESTS" "Unit" "🔍" "$verbose_flag" || exit_code=1
            run_test_category "$OCR_TESTS" "OCR" "🔮" "$verbose_flag" || exit_code=1
            
            if check_integration_prerequisites; then
                run_test_category "$INTEGRATION_TESTS" "Integration" "🌐" "$verbose_flag" || exit_code=1
            fi
            ;;
    esac
    
    # Final summary
    echo ""
    if [[ $exit_code -eq 0 ]]; then
        log_success "All tests completed successfully!"
        log_info "Test suite is well-organized and comprehensive."
    else
        log_error "Some tests failed. Please check the output above."
    fi
    
    exit $exit_code
}

# Parse command line arguments
VERBOSE=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -*)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            TEST_TYPE="$1"
            shift
            ;;
    esac
done

# Run main function
main "${TEST_TYPE:-all}"
