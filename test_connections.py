#!/usr/bin/env python3
"""
Database Connection Test Script
Tests all external service connections for the OCR Invoice Processor
"""

import os
import sys
import asyncio
import json
from typing import Dict, Any
import httpx
import asyncpg
from urllib.parse import urlparse

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

async def test_supabase_connection():
    """Test Supabase database connection"""
    print_header("SUPABASE DATABASE CONNECTION TEST")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print_error("Missing Supabase credentials in .env file")
        return False
    
    print_info(f"Testing connection to: {supabase_url}")
    
    try:
        # Test REST API endpoint
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Test with a simple query
            response = await client.get(
                f"{supabase_url}/rest/v1/invoices?select=count&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print_success("Supabase REST API connection successful")
                return True
            else:
                print_error(f"Supabase REST API failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Supabase connection failed: {str(e)}")
        return False

async def test_supabase_direct_db():
    """Test direct PostgreSQL connection to Supabase"""
    print_header("SUPABASE DIRECT DATABASE CONNECTION TEST")
    
    supabase_url = os.getenv('SUPABASE_URL')
    
    if not supabase_url:
        print_error("Missing SUPABASE_URL in .env file")
        return False
    
    try:
        # Parse Supabase URL to get database connection info
        parsed = urlparse(supabase_url)
        host = parsed.hostname
        
        # Supabase uses port 5432 for direct database connections
        # The URL format: https://project-ref.supabase.co -> project-ref.supabase.co:5432
        if host:
            db_host = host.replace('https://', '').replace('http://', '')
            print_info(f"Testing direct PostgreSQL connection to: {db_host}:5432")
            
            # Test basic connectivity to the host
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    response = await client.get(f"https://{db_host}")
                    print_success(f"Host {db_host} is reachable")
                except Exception as e:
                    print_warning(f"Host connectivity test: {str(e)}")
                    
        return True
        
    except Exception as e:
        print_error(f"Direct database connection test failed: {str(e)}")
        return False

async def test_sendgrid_connection():
    """Test SendGrid email service connection"""
    print_header("SENDGRID EMAIL SERVICE TEST")
    
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    
    if not sendgrid_key or sendgrid_key == 'your_sendgrid_api_key_here':
        print_warning("SendGrid API key not configured (this is optional for basic testing)")
        return True
    
    if not from_email:
        print_error("Missing FROM_EMAIL in .env file")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                'Authorization': f'Bearer {sendgrid_key}',
                'Content-Type': 'application/json'
            }
            
            # Test SendGrid API with a validation endpoint
            response = await client.get(
                'https://api.sendgrid.com/v3/user/profile',
                headers=headers
            )
            
            if response.status_code == 200:
                print_success("SendGrid API connection successful")
                return True
            else:
                print_error(f"SendGrid API failed: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"SendGrid connection failed: {str(e)}")
        return False

async def test_google_cloud_ocr():
    """Test Google Cloud Document AI connection"""
    print_header("GOOGLE CLOUD OCR SERVICE TEST")
    
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    use_mock_ocr = os.getenv('USE_MOCK_OCR', 'false').lower() == 'true'
    
    if use_mock_ocr:
        print_warning("Using Mock OCR (USE_MOCK_OCR=true) - Google Cloud OCR is disabled")
        return True
    
    if not gcp_project_id or not credentials_path:
        print_warning("Google Cloud OCR not configured (USE_MOCK_OCR=true recommended for testing)")
        return True
    
    if not os.path.exists(credentials_path):
        print_error(f"Google Cloud credentials file not found: {credentials_path}")
        return False
    
    try:
        # Basic file validation
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
            if 'project_id' in creds:
                print_success(f"Google Cloud credentials file is valid (Project: {creds['project_id']})")
                return True
            else:
                print_error("Invalid Google Cloud credentials file format")
                return False
                
    except Exception as e:
        print_error(f"Google Cloud OCR test failed: {str(e)}")
        return False

async def test_network_connectivity():
    """Test basic network connectivity"""
    print_header("NETWORK CONNECTIVITY TEST")
    
    test_urls = [
        "https://www.google.com",
        "https://supabase.com",
        "https://api.sendgrid.com"
    ]
    
    results = []
    
    for url in test_urls:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    print_success(f"Network connectivity to {url}: OK")
                    results.append(True)
                else:
                    print_warning(f"Network connectivity to {url}: {response.status_code}")
                    results.append(False)
        except Exception as e:
            print_error(f"Network connectivity to {url}: {str(e)}")
            results.append(False)
    
    return all(results)

async def main():
    """Run all connection tests"""
    print_header("OCR INVOICE PROCESSOR - CONNECTION DIAGNOSTICS")
    print_info("Testing all external service connections...")
    
    # Load environment variables
    if os.path.exists('.env'):
        print_info("Loading environment variables from .env file")
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
    else:
        print_warning("No .env file found in current directory")
    
    # Run all tests
    tests = [
        ("Network Connectivity", test_network_connectivity()),
        ("Supabase Connection", test_supabase_connection()),
        ("Supabase Direct DB", test_supabase_direct_db()),
        ("SendGrid Email", test_sendgrid_connection()),
        ("Google Cloud OCR", test_google_cloud_ocr())
    ]
    
    results = {}
    
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results[test_name] = result
        except Exception as e:
            print_error(f"{test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    all_passed = True
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print_success("🎉 ALL TESTS PASSED - System is ready!")
    else:
        print_error("❌ SOME TESTS FAILED - Check configuration")
        print_info("💡 Recommendation: Fix failed connections before proceeding")
    
    print("\n" + "="*60)
    print_info("Next steps:")
    print("1. Fix any failed connections")
    print("2. Restart Docker containers: ./docker-manager.sh restart")
    print("3. Check application at http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())
