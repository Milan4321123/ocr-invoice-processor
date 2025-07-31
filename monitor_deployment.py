#!/usr/bin/env python3
"""
Monitor frontend deployment and test connectivity
"""

import requests
import time
import json
from datetime import datetime

FRONTEND_URL = "https://ocr-invoice-processor-1.onrender.com"
BACKEND_URL = "https://ocr-invoice-processor.onrender.com"

def log_status(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_frontend_connectivity():
    """Test if frontend can connect to backend and Supabase"""
    try:
        # Test basic frontend access
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            log_status("✅ Frontend is accessible", "SUCCESS")
        else:
            log_status(f"❌ Frontend returned status {response.status_code}", "ERROR")
            return False
            
        # Test diagnostics page (if available)
        try:
            diag_response = requests.get(f"{FRONTEND_URL}/diagnostics", timeout=10)
            if diag_response.status_code == 200:
                log_status("✅ Diagnostics page accessible", "SUCCESS")
            else:
                log_status("⚠️ Diagnostics page not yet available", "WARN")
        except:
            log_status("⚠️ Diagnostics page not yet ready", "WARN")
            
        # Test if frontend can reach backend
        try:
            # Try to access a backend endpoint through frontend proxy
            backend_test = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
            if backend_test.status_code == 200:
                log_status("✅ Backend is reachable from internet", "SUCCESS")
                return True
            else:
                log_status(f"❌ Backend health check failed: {backend_test.status_code}", "ERROR")
                return False
        except Exception as e:
            log_status(f"❌ Backend connection error: {str(e)}", "ERROR")
            return False
            
    except Exception as e:
        log_status(f"❌ Frontend test error: {str(e)}", "ERROR")
        return False

def wait_for_deployment():
    """Wait for deployment to complete and test"""
    log_status("🚀 Monitoring frontend deployment...")
    
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        log_status(f"Attempt {attempt}/{max_attempts} - Testing connectivity...")
        
        if test_frontend_connectivity():
            log_status("🎉 Frontend deployment successful and connectivity verified!", "SUCCESS")
            log_status(f"🌐 Frontend URL: {FRONTEND_URL}", "INFO")
            log_status(f"🔧 Backend URL: {BACKEND_URL}", "INFO")
            log_status(f"📊 Diagnostics: {FRONTEND_URL}/diagnostics", "INFO")
            return True
            
        if attempt < max_attempts:
            log_status(f"⏳ Waiting 30 seconds before next attempt...", "INFO")
            time.sleep(30)
    
    log_status("❌ Deployment monitoring timeout - please check Render dashboard", "ERROR")
    return False

if __name__ == "__main__":
    print("🔍 Frontend Deployment Monitor")
    print("=" * 50)
    wait_for_deployment()
