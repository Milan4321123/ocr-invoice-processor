#!/usr/bin/env python3
"""
System Health Check Script
Runs comprehensive health checks on the Invoice OCR system
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

def print_status(component: str, status: str, details: str = ""):
    """Print formatted status"""
    icons = {
        "✅": "✅",
        "⚠️": "⚠️", 
        "❌": "❌",
        "🔧": "🔧"
    }
    
    status_colors = {
        "healthy": "✅",
        "degraded": "⚠️",
        "error": "❌",
        "mock": "🔧"
    }
    
    icon = status_colors.get(status.lower(), "❓")
    print(f"{icon} {component:<20} {status.upper():<10} {details}")

def check_backend_health():
    """Check backend system health"""
    print("\n=== BACKEND HEALTH CHECK ===")
    
    try:
        # Basic health check
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print_status("Basic Health", "healthy", "200 OK")
        else:
            print_status("Basic Health", "error", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Basic Health", "error", f"Connection failed: {e}")
        return False
    
    try:
        # Detailed system health
        response = requests.get(f"{BACKEND_URL}/system-health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print_status("System Health", "healthy", "200 OK")
            
            # Print component details
            for component_name, component_data in health_data.get("components", {}).items():
                status = component_data.get("status", "unknown")
                details = ""
                
                if "response_time_ms" in component_data:
                    details += f"{component_data['response_time_ms']}ms "
                if "total_invoices" in component_data:
                    details += f"({component_data['total_invoices']} invoices) "
                if "connection" in component_data:
                    details += f"[{component_data['connection']}] "
                if "error" in component_data:
                    details += f"Error: {component_data['error']}"
                
                print_status(f"  {component_name}", status, details.strip())
                
            return health_data.get("overall_status") == "healthy"
        else:
            print_status("System Health", "error", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("System Health", "error", f"Connection failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print_status("System Health", "error", f"Invalid JSON response: {e}")
        return False

def check_api_endpoints():
    """Check all API endpoints"""
    print("\n=== API ENDPOINTS CHECK ===")
    
    endpoints = [
        ("GET", "/health", "Basic health check"),
        ("GET", "/system-health", "System health details"),
        ("GET", "/invoices", "List invoices"),
        ("GET", "/", "API root"),
    ]
    
    all_healthy = True
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            
            if response.status_code in [200, 201]:
                print_status(f"{method} {endpoint}", "healthy", f"{response.status_code} - {description}")
            else:
                print_status(f"{method} {endpoint}", "error", f"{response.status_code}")
                all_healthy = False
                
        except requests.exceptions.RequestException as e:
            print_status(f"{method} {endpoint}", "error", f"Connection failed: {e}")
            all_healthy = False
    
    return all_healthy

def check_frontend():
    """Check frontend accessibility"""
    print("\n=== FRONTEND CHECK ===")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_status("Frontend Access", "healthy", f"200 OK - {FRONTEND_URL}")
            return True
        else:
            print_status("Frontend Access", "error", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("Frontend Access", "error", f"Connection failed: {e}")
        return False

def check_file_upload():
    """Test file upload functionality"""
    print("\n=== FILE UPLOAD TEST ===")
    
    # Create a test PDF file content
    test_filename = "20250529_TEST001_TESTVENDOR_INVOICE.pdf"
    test_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj
4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Arial>>endobj
5 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Test PDF) Tj ET
endstream
endobj
xref
0 5
trailer<</Size 5/Root 1 0 R>>
startxref
400
%%EOF"""
    
    try:
        files = {"file": (test_filename, test_content, "application/pdf")}
        response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_status("File Upload", "healthy", f"Uploaded {test_filename}")
            
            # Try to clean up the test file if we got an ID
            if "id" in result:
                try:
                    delete_response = requests.delete(f"{BACKEND_URL}/invoices/{result['id']}", timeout=5)
                    if delete_response.status_code == 200:
                        print_status("File Cleanup", "healthy", "Test file deleted")
                    else:
                        print_status("File Cleanup", "degraded", "Could not delete test file")
                except:
                    print_status("File Cleanup", "degraded", "Could not delete test file")
            
            return True
        else:
            print_status("File Upload", "error", f"HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status("File Upload", "error", f"Connection failed: {e}")
        return False

def main():
    """Run all health checks"""
    print(f"🏥 INVOICE OCR SYSTEM HEALTH CHECK")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    checks = [
        ("Backend Health", check_backend_health),
        ("API Endpoints", check_api_endpoints),
        ("Frontend", check_frontend),
        ("File Upload", check_file_upload),
    ]
    
    results = {}
    overall_healthy = True
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
            if not results[check_name]:
                overall_healthy = False
        except Exception as e:
            print_status(check_name, "error", f"Check failed: {e}")
            results[check_name] = False
            overall_healthy = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    for check_name, result in results.items():
        status = "healthy" if result else "error"
        print_status(check_name, status)
    
    print(f"\n🎯 OVERALL SYSTEM STATUS: {'✅ HEALTHY' if overall_healthy else '❌ DEGRADED/ERROR'}")
    
    if not overall_healthy:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        if not results.get("Backend Health", True):
            print("  • Check if backend server is running: uvicorn main:app --reload")
            print("  • Verify backend environment variables (.env file)")
        if not results.get("Frontend", True):
            print("  • Check if frontend server is running: npm run dev")
            print("  • Verify frontend environment variables (.env.local file)")
        if not results.get("File Upload", True):
            print("  • Check Supabase configuration and permissions")
            print("  • Verify storage bucket exists and is accessible")
    
    # Exit with error code if not healthy
    sys.exit(0 if overall_healthy else 1)

if __name__ == "__main__":
    main()
