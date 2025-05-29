#!/usr/bin/env python3
"""
Simple test runner for the Invoice OCR Backend
Usage: python test_runner.py [unit|integration|all|coverage]
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print("=" * 50)
    
    result = subprocess.run(cmd, shell=True, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
    else:
        print(f"❌ {description} failed")
        return False
    return True

def main():
    test_type = sys.argv[1] if len(sys.argv) > 1 else "unit"
    
    print(f"🧪 Invoice OCR Backend Test Runner")
    print(f"📋 Running: {test_type} tests")
    
    # Install dependencies
    if not run_command("python -m pip install -r requirements.txt -q", "Installing dependencies"):
        return 1
    
    if test_type == "unit":
        # Run unit tests only
        cmd = "python -m pytest tests/test_main.py -v"
        if not run_command(cmd, "Unit Tests"):
            return 1
            
    elif test_type == "integration":
        # Check for environment variables
        if not os.getenv("SUPA_URL") or not os.getenv("SUPA_KEY"):
            print("\n⚠️  Supabase credentials not found!")
            print("Set SUPA_URL and SUPA_KEY environment variables to run integration tests.")
            return 1
        
        cmd = "python -m pytest tests/test_integration.py -v"
        if not run_command(cmd, "Integration Tests"):
            return 1
            
    elif test_type == "coverage":
        # Run all tests with coverage
        cmd = "python -m pytest tests/ --cov=main --cov-report=term-missing --cov-report=html -v"
        if not run_command(cmd, "All Tests with Coverage"):
            return 1
        print("\n📊 Coverage report generated in htmlcov/")
        
    elif test_type == "all":
        # Run unit tests
        cmd = "python -m pytest tests/test_main.py -v"
        if not run_command(cmd, "Unit Tests"):
            return 1
        
        # Run integration tests if credentials are available
        if os.getenv("SUPA_URL") and os.getenv("SUPA_KEY"):
            cmd = "python -m pytest tests/test_integration.py -v"
            if not run_command(cmd, "Integration Tests"):
                return 1
        else:
            print("\n⚠️  Skipping integration tests (Supabase credentials not found)")
            
    else:
        print(f"\n❌ Unknown test type: {test_type}")
        print("Usage: python test_runner.py [unit|integration|all|coverage]")
        return 1
    
    print(f"\n🎉 All {test_type} tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
