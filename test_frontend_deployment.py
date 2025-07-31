#!/usr/bin/env python3
"""
Test the deployed frontend diagnostics page
"""

import requests
import time
import json

FRONTEND_URL = "https://ocr-invoice-processor-1.onrender.com"

def test_frontend_diagnostics():
    """Test the diagnostics page on the deployed frontend"""
    
    print("🔍 Testing Frontend Diagnostics Page")
    print("=" * 50)
    
    try:
        # Test if diagnostics page is accessible
        print("📡 Checking diagnostics page accessibility...")
        response = requests.get(f"{FRONTEND_URL}/diagnostics", timeout=30)
        
        if response.status_code == 200:
            print("✅ Diagnostics page is accessible")
            
            # Check if the page contains environment variable indicators
            content = response.text
            
            indicators = [
                "Environment Variables",
                "NEXT_PUBLIC_API_URL",
                "NEXT_PUBLIC_SUPABASE_URL",
                "Backend API Test",
                "Supabase Connection Test"
            ]
            
            found_indicators = []
            for indicator in indicators:
                if indicator in content:
                    found_indicators.append(indicator)
            
            print(f"📊 Found diagnostic indicators: {len(found_indicators)}/{len(indicators)}")
            for indicator in found_indicators:
                print(f"   ✅ {indicator}")
            
            missing = [i for i in indicators if i not in found_indicators]
            for indicator in missing:
                print(f"   ❌ {indicator}")
                
            if len(found_indicators) >= 3:
                print("\n🎉 Diagnostics page looks good!")
                return True
            else:
                print("\n⚠️ Diagnostics page may not be fully functional")
                return False
                
        else:
            print(f"❌ Diagnostics page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing diagnostics: {str(e)}")
        return False

def wait_for_deployment():
    """Wait for Render deployment to complete"""
    print("⏳ Waiting for Render deployment to complete...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                print(f"✅ Frontend is responding (attempt {attempt + 1})")
                return True
        except:
            pass
        
        print(f"⏳ Attempt {attempt + 1}/{max_attempts} - waiting 30s...")
        time.sleep(30)
    
    print("❌ Deployment seems to be taking longer than expected")
    return False

if __name__ == "__main__":
    print("🚀 Testing Frontend Deployment")
    print("=" * 50)
    
    if wait_for_deployment():
        # Give it a bit more time for the new build to be fully ready
        print("⏳ Giving deployment 60 seconds to fully initialize...")
        time.sleep(60)
        
        test_frontend_diagnostics()
    else:
        print("❌ Could not verify deployment status")
