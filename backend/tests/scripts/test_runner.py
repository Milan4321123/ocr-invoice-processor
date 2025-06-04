#!/usr/bin/env python3
"""
Invoice OCR Backend Test Runner - Organized Test Suite
======================================================
Enhanced Python test runner with better organization, error handling, and reporting
"""

import sys
import subprocess
import os
import argparse
import time
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TestType(Enum):
    """Enumeration of available test types"""
    UNIT = "unit"
    INTEGRATION = "integration"
    OCR = "ocr"
    ALL = "all"
    COVERAGE = "coverage"

@dataclass
class TestConfig:
    """Configuration for test execution"""
    test_type: TestType
    verbose: bool = False
    quiet: bool = False
    parallel: bool = False
    backend_root: Path = Path(__file__).parent.parent.parent
    timeout: int = 300  # 5 minutes default timeout

@dataclass
class TestResult:
    """Result of a test execution"""
    name: str
    success: bool
    duration: float
    command: str
    output: Optional[str] = None

class TestRunner:
    """Organized test runner with comprehensive functionality"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results: List[TestResult] = []
        
        # Test categories configuration
        self.test_categories = {
            TestType.UNIT: {
                "path": "tests/unit/",
                "description": "Unit tests with mocked dependencies",
                "emoji": "🔍",
                "requires_credentials": False
            },
            TestType.INTEGRATION: {
                "path": "tests/integration/",
                "description": "Integration tests requiring Supabase",
                "emoji": "🌐",
                "requires_credentials": True
            },
            TestType.OCR: {
                "path": "tests/ocr/",
                "description": "OCR-specific functionality tests",
                "emoji": "🔮",
                "requires_credentials": False
            }
        }
    
    def log_info(self, message: str) -> None:
        """Log informational message"""
        if not self.config.quiet:
            print(f"ℹ️  {message}")
    
    def log_success(self, message: str) -> None:
        """Log success message"""
        if not self.config.quiet:
            print(f"✅ {message}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        print(f"⚠️  {message}")
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        print(f"❌ {message}")
    
    def log_section(self, message: str) -> None:
        """Log section header"""
        if not self.config.quiet:
            print(f"\n{message}")
            print("=" * len(message))
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log_section("🔧 Checking Prerequisites")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.log_error("Python 3.8+ is required")
            return False
        
        # Check if we're in the right directory
        if not (self.config.backend_root / "main.py").exists():
            self.log_error(f"Backend main.py not found in {self.config.backend_root}")
            return False
        
        # Check if requirements.txt exists
        if not (self.config.backend_root / "requirements.txt").exists():
            self.log_error("requirements.txt not found")
            return False
        
        self.log_success("Prerequisites check passed")
        return True
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        self.log_section("📦 Installing Dependencies")
        
        commands = [
            "python -m pip install --upgrade pip",
            "python -m pip install -r requirements.txt",
            "python -m pip install pytest-cov pytest-xdist"  # Additional test tools
        ]
        
        for cmd in commands:
            if not self._run_command(cmd, "Installing dependencies", show_output=False):
                return False
        
        self.log_success("Dependencies installed successfully")
        return True
    
    def check_credentials(self, test_type: TestType) -> bool:
        """Check if required credentials are available"""
        if not self.test_categories[test_type]["requires_credentials"]:
            return True
        
        required_vars = ["SUPA_URL", "SUPA_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self.log_warning(f"Missing environment variables: {', '.join(missing_vars)}")
            self.log_info("Set the following environment variables:")
            for var in missing_vars:
                self.log_info(f"  export {var}='your_value'")
            return False
        
        return True
    
    def _run_command(self, cmd: str, description: str, show_output: bool = True) -> bool:
        """Execute a command and handle the result"""
        start_time = time.time()
        
        if show_output and self.config.verbose:
            self.log_info(f"Running: {cmd}")
        
        try:
            # Prepare command arguments
            pytest_args = []
            if self.config.verbose and "pytest" in cmd:
                pytest_args.append("-v")
            if self.config.parallel and "pytest" in cmd:
                pytest_args.append("-n auto")
            
            # Add pytest arguments to command
            if pytest_args and "pytest" in cmd:
                cmd += " " + " ".join(pytest_args)
            
            # Execute command
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.config.backend_root,
                capture_output=not show_output,
                text=True,
                timeout=self.config.timeout
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Store result
            test_result = TestResult(
                name=description,
                success=success,
                duration=duration,
                command=cmd,
                output=result.stdout if not show_output else None
            )
            self.results.append(test_result)
            
            if success:
                if show_output:
                    self.log_success(f"{description} completed in {duration:.2f}s")
            else:
                self.log_error(f"{description} failed")
                if not show_output and result.stderr:
                    print(result.stderr)
            
            return success
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_error(f"{description} timed out after {duration:.2f}s")
            return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_error(f"{description} failed with error: {e}")
            return False
    
    def run_test_category(self, test_type: TestType) -> bool:
        """Run tests for a specific category"""
        category = self.test_categories[test_type]
        
        # Check if test directory exists
        test_path = self.config.backend_root / category["path"]
        if not test_path.exists():
            self.log_error(f"Test directory not found: {test_path}")
            return False
        
        # Check credentials if required
        if not self.check_credentials(test_type):
            self.log_warning(f"Skipping {test_type.value} tests - credentials not available")
            return False
        
        # Run the tests
        self.log_section(f"{category['emoji']} Running {test_type.value.title()} Tests")
        self.log_info(f"Description: {category['description']}")
        
        cmd = f"python -m pytest {category['path']}"
        return self._run_command(cmd, f"{test_type.value.title()} Tests")
    
    def run_coverage_tests(self) -> bool:
        """Run all tests with coverage analysis"""
        self.log_section("📊 Running Coverage Analysis")
        
        # Collect all available test paths
        test_paths = []
        for test_type in [TestType.UNIT, TestType.OCR]:
            category = self.test_categories[test_type]
            test_path = self.config.backend_root / category["path"]
            if test_path.exists():
                test_paths.append(category["path"])
        
        # Add integration tests if credentials are available
        if self.check_credentials(TestType.INTEGRATION):
            test_paths.append(self.test_categories[TestType.INTEGRATION]["path"])
        
        if not test_paths:
            self.log_error("No test directories found")
            return False
        
        # Run coverage analysis
        test_paths_str = " ".join(test_paths)
        cmd = f"python -m pytest {test_paths_str} --cov=main --cov-report=term-missing --cov-report=html"
        
        if self._run_command(cmd, "Coverage Analysis"):
            self.log_info("HTML coverage report generated in htmlcov/index.html")
            return True
        
        return False
    
    def run_all_tests(self) -> bool:
        """Run all available test categories"""
        self.log_section("🧪 Running All Test Categories")
        
        success = True
        test_order = [TestType.UNIT, TestType.OCR, TestType.INTEGRATION]
        
        for test_type in test_order:
            category = self.test_categories[test_type]
            test_path = self.config.backend_root / category["path"]
            
            if test_path.exists():
                if not self.run_test_category(test_type):
                    success = False
            else:
                self.log_warning(f"Test directory not found: {test_path}")
        
        return success
    
    def print_summary(self) -> None:
        """Print test execution summary"""
        self.log_section("📋 Test Execution Summary")
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results if result.success)
        failed_tests = total_tests - successful_tests
        total_duration = sum(result.duration for result in self.results)
        
        print(f"Total test categories: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Total duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print("\nFailed tests:")
            for result in self.results:
                if not result.success:
                    print(f"  ❌ {result.name} ({result.duration:.2f}s)")
        
        # Print organized test structure info
        print("\n📁 Organized Test Structure:")
        print("   • tests/unit/        - Unit tests with mocked dependencies")
        print("   • tests/integration/ - Integration tests requiring Supabase")
        print("   • tests/ocr/         - OCR-specific functionality tests")
        print("   • tests/scripts/     - Test utility scripts")
    
    def run(self) -> bool:
        """Main execution method"""
        self.log_section("🧪 Invoice OCR Backend Test Runner - Organized Structure")
        self.log_info(f"Backend Root: {self.config.backend_root}")
        self.log_info(f"Test Type: {self.config.test_type.value}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Execute tests based on type
        success = False
        
        if self.config.test_type == TestType.COVERAGE:
            success = self.run_coverage_tests()
        elif self.config.test_type == TestType.ALL:
            success = self.run_all_tests()
        else:
            success = self.run_test_category(self.config.test_type)
        
        # Print summary
        self.print_summary()
        
        # Final message
        if success:
            self.log_success("All tests completed successfully!")
            self.log_info("Test suite is well-organized and comprehensive.")
        else:
            self.log_error("Some tests failed. Please check the output above.")
        
        return success

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Invoice OCR Backend Test Runner - Organized Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Types:
  unit         Run only unit tests
  integration  Run only integration tests  
  ocr          Run only OCR tests
  all          Run all available tests
  coverage     Run all tests with coverage report

Examples:
  python test_runner.py unit
  python test_runner.py --verbose coverage
  python test_runner.py --parallel all
        """
    )
    
    parser.add_argument(
        "test_type",
        nargs="?",
        default="unit",
        choices=[t.value for t in TestType],
        help="Type of tests to run (default: unit)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=300,
        help="Timeout for test execution in seconds (default: 300)"
    )
    
    return parser

def main() -> int:
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfig(
        test_type=TestType(args.test_type),
        verbose=args.verbose,
        quiet=args.quiet,
        parallel=args.parallel,
        timeout=args.timeout
    )
    
    # Create and run test runner
    runner = TestRunner(config)
    success = runner.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
