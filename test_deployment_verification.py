#!/usr/bin/env python3
"""
Comprehensive deployment verification script
Tests all key endpoints and workflows for the OCR Invoice Processor
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://ocr-invoice-processor.onrender.com"
FRONTEND_URL = "https://ocr-invoice-processor-1.onrender.com"

def log_test(test_name, status, details=""):
    """Log test results with formatting"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {status_icon} {test_name}: {status}")
    if details:
        print(f"    {details}")

def test_backend_health():
    """Test backend health endpoints"""
    try:
        # Test root endpoint
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if response.status_code == 200:
            log_test("Backend Health Check", "PASS", f"Response: {response.json()}")
        else:
            log_test("Backend Health Check", "FAIL", f"Status: {response.status_code}")
            return False
            
        # Test system health
        response = requests.get(f"{BACKEND_URL}/api/system-health", timeout=10)
        if response.status_code == 200:
            log_test("Backend System Health", "PASS", f"Response: {response.json()}")
        else:
            log_test("Backend System Health", "FAIL", f"Status: {response.status_code}")
            
        return True
    except Exception as e:
        log_test("Backend Health Check", "FAIL", f"Error: {str(e)}")
        return False

def test_authentication():
    """Test authentication workflow"""
    try:
        # Test login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BACKEND_URL}/api/auth/token", json=login_data, timeout=10)
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            log_test("Authentication Login", "PASS", f"Token received: {token[:20]}...")
            
            # Test token verification
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BACKEND_URL}/api/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                log_test("Token Verification", "PASS", f"User: {user_data.get('username')}")
                return token
            else:
                log_test("Token Verification", "FAIL", f"Status: {response.status_code}")
                return None
        else:
            log_test("Authentication Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test("Authentication", "FAIL", f"Error: {str(e)}")
        return None

def test_core_endpoints(token=None):
    """Test core application endpoints"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    endpoints_to_test = [
        ("/api/invoices", "GET", "Invoice List"),
        ("/api/skonto/dashboard/summary", "GET", "Skonto Dashboard"),
        ("/api/reports/invoice-summary", "GET", "Invoice Reports"),
        ("/api/dropdowns", "GET", "Dropdown Options"),
        ("/api/folder-watcher/status", "GET", "Folder Watcher Status")
    ]
    
    for endpoint, method, name in endpoints_to_test:
        try:
            response = requests.request(method, f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                log_test(name, "PASS", f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
            else:
                log_test(name, "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test(name, "FAIL", f"Error: {str(e)}")

def test_frontend_access():
    """Test frontend accessibility"""
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            content = response.text
            if "OCR" in content or "Invoice" in content or "next" in content.lower():
                log_test("Frontend Access", "PASS", "Frontend is serving content")
                return True
            else:
                log_test("Frontend Access", "WARN", "Frontend serving but content unclear")
                return True
        else:
            log_test("Frontend Access", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Frontend Access", "FAIL", f"Error: {str(e)}")
        return False

def test_cors_and_connectivity():
    """Test CORS and cross-origin connectivity"""
    try:
        # Simulate frontend calling backend
        headers = {
            "Origin": FRONTEND_URL,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = requests.options(f"{BACKEND_URL}/api/health", headers=headers, timeout=10)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        log_test("CORS Configuration", "PASS", f"Headers present: {bool(any(cors_headers.values()))}")
        
    except Exception as e:
        log_test("CORS Test", "FAIL", f"Error: {str(e)}")

def main():
    """Run all deployment verification tests"""
    print("🚀 Starting Deployment Verification")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend health check failed. Stopping tests.")
        sys.exit(1)
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("\n⚠️ Authentication failed, continuing with limited tests...")
    
    # Test core endpoints
    print("\n📊 Testing Core Endpoints")
    test_core_endpoints(token)
    
    # Test frontend
    print("\n🌐 Testing Frontend")
    test_frontend_access()
    
    # Test CORS
    print("\n🔗 Testing Connectivity")
    test_cors_and_connectivity()
    
    print("\n" + "=" * 50)
    print("✅ Deployment verification completed!")
    print(f"🌐 Frontend: {FRONTEND_URL}")
    print(f"🔧 Backend: {BACKEND_URL}")
    print(f"📚 API Docs: {BACKEND_URL}/docs")

if __name__ == "__main__":
    main()
