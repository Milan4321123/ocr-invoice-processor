#!/usr/bin/env python3

"""
End-to-End Skonto Bericht Page Test
Tests the complete Skonto functionality from API to frontend
"""

import requests
import json
import time
from datetime import datetime

def test_backend_api():
    """Test backend API endpoints directly"""
    print("=== Testing Backend API ===")
    
    # Test backend summary
    try:
        response = requests.get("http://localhost:8000/api/skonto/dashboard/summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Summary: {data['total_opportunities']} opportunities, {data['total_potential_savings']} savings")
        else:
            print(f"❌ Backend Summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Summary error: {e}")
        return False
    
    # Test backend opportunities
    try:
        response = requests.get("http://localhost:8000/api/skonto/dashboard/opportunities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Opportunities: {len(data)} invoices found")
            for invoice in data:
                print(f"   - {invoice['invoice_number']}: {invoice['skonto_decision']} ({invoice['potential_savings']}€)")
        else:
            print(f"❌ Backend Opportunities failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Opportunities error: {e}")
        return False
    
    return True

def test_frontend_api():
    """Test frontend API proxy endpoints"""
    print("\n=== Testing Frontend API Proxy ===")
    
    # Test frontend summary proxy
    try:
        response = requests.get("http://localhost:3000/api/skonto/dashboard/summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Frontend Summary Proxy: {data['total_opportunities']} opportunities")
        else:
            print(f"❌ Frontend Summary Proxy failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Summary Proxy error: {e}")
        return False
    
    # Test frontend opportunities proxy
    try:
        response = requests.get("http://localhost:3000/api/skonto/dashboard/opportunities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Frontend Opportunities Proxy: {len(data)} invoices")
        else:
            print(f"❌ Frontend Opportunities Proxy failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Opportunities Proxy error: {e}")
        return False
    
    return True

def test_frontend_page():
    """Test frontend Skonto page accessibility"""
    print("\n=== Testing Frontend Page ===")
    
    try:
        response = requests.get("http://localhost:3000/prufbericht", timeout=10)
        if response.status_code == 200:
            print("✅ Prüfbericht (Skonto) page is accessible")
            # Check if the page contains Skonto-related content
            if "Skonto" in response.text:
                print("✅ Page contains Skonto-related content")
            return True
        else:
            print(f"❌ Prüfbericht (Skonto) page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prüfbericht (Skonto) page error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"🚀 Starting Skonto End-to-End Test - {datetime.now()}")
    print("=" * 60)
    
    # Test sequence
    backend_ok = test_backend_api()
    frontend_api_ok = test_frontend_api()
    frontend_page_ok = test_frontend_page()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Backend API:       {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   Frontend API:      {'✅ PASS' if frontend_api_ok else '❌ FAIL'}")
    print(f"   Frontend Page:     {'✅ PASS' if frontend_page_ok else '❌ FAIL'}")
    
    if all([backend_ok, frontend_api_ok, frontend_page_ok]):
        print("\n🎉 All Skonto tests PASSED! Skonto Bericht page is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests FAILED. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
