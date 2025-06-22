#!/usr/bin/env python3
"""
Phase 4 Testing: Folder Watcher API Endpoints
Tests the REST API endpoints for folder watcher functionality
"""

import asyncio
import requests
import json
import tempfile
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8001"

def test_api_endpoints():
    """Test all folder watcher API endpoints"""
    print("🧪 PHASE 4 TESTING: Folder Watcher API Endpoints")
    print("=" * 60)
    
    try:
        # Test 1: Get initial status
        print("\n1. Testing GET /api/folder-watcher/status")
        response = requests.get(f"{API_BASE}/api/folder-watcher/status")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Service Status: {status['status']}")
            print(f"   ✅ Folders Watched: {status['folders_watched']}")
        else:
            print(f"   ❌ Error: {response.text}")
            return False
        
        # Test 2: Get watch folders (should be empty initially)
        print("\n2. Testing GET /api/folder-watcher/folders")
        response = requests.get(f"{API_BASE}/api/folder-watcher/folders")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            folders = response.json()
            print(f"   ✅ Found {len(folders)} configured folders")
        else:
            print(f"   ❌ Error: {response.text}")
            return False
        
        # Test 3: Add a watch folder
        print("\n3. Testing POST /api/folder-watcher/folders")
        with tempfile.TemporaryDirectory() as temp_dir:
            folder_data = {
                "folder_path": temp_dir,
                "pattern": "*.pdf",
                "recursive": False,
                "enabled": True
            }
            
            response = requests.post(
                f"{API_BASE}/api/folder-watcher/folders",
                json=folder_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                config_id = result['config_id']
                print(f"   ✅ Added folder: {result['folder_path']}")
                print(f"   ✅ Config ID: {config_id}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 4: Start watcher
            print("\n4. Testing POST /api/folder-watcher/start")
            response = requests.post(f"{API_BASE}/api/folder-watcher/start")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
                print(f"   ✅ Status: {result['status']}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 5: Get statistics
            print("\n5. Testing GET /api/folder-watcher/statistics")
            response = requests.get(f"{API_BASE}/api/folder-watcher/statistics")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"   ✅ Service Status: {stats['status']}")
                print(f"   ✅ Uptime: {stats['uptime_formatted']}")
                print(f"   ✅ Active Folders: {stats['folders']['active']}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 6: Disable folder
            print(f"\n6. Testing POST /api/folder-watcher/folders/{config_id}/disable")
            response = requests.post(f"{API_BASE}/api/folder-watcher/folders/{config_id}/disable")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 7: Enable folder
            print(f"\n7. Testing POST /api/folder-watcher/folders/{config_id}/enable")
            response = requests.post(f"{API_BASE}/api/folder-watcher/folders/{config_id}/enable")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 8: Health check
            print("\n8. Testing GET /api/folder-watcher/health")
            response = requests.get(f"{API_BASE}/api/folder-watcher/health")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                health = response.json()
                print(f"   ✅ Health Status: {health['status']}")
                print(f"   ✅ Watcher Status: {health['watcher_status']}")
                print(f"   ✅ Folders Watching: {health['folders_watching']}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 9: Stop watcher
            print("\n9. Testing POST /api/folder-watcher/stop")
            response = requests.post(f"{API_BASE}/api/folder-watcher/stop")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Error: {response.text}")
                return False
            
            # Test 10: Remove folder
            print(f"\n10. Testing DELETE /api/folder-watcher/folders/{config_id}")
            response = requests.delete(f"{API_BASE}/api/folder-watcher/folders/{config_id}")
            print(f"    Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ {result['message']}")
            else:
                print(f"    ❌ Error: {response.text}")
                return False
        
        print("\n" + "="*60)
        print("🎉 ALL API ENDPOINT TESTS PASSED!")
        print("="*60)
        
        print("\n📊 PHASE 4 API TESTING SUMMARY:")
        print("✅ GET /api/folder-watcher/status - Working")
        print("✅ GET /api/folder-watcher/folders - Working")
        print("✅ POST /api/folder-watcher/folders - Working")
        print("✅ POST /api/folder-watcher/start - Working")
        print("✅ GET /api/folder-watcher/statistics - Working")
        print("✅ POST /api/folder-watcher/folders/{id}/disable - Working")
        print("✅ POST /api/folder-watcher/folders/{id}/enable - Working")
        print("✅ GET /api/folder-watcher/health - Working")
        print("✅ POST /api/folder-watcher/stop - Working")
        print("✅ DELETE /api/folder-watcher/folders/{id} - Working")
        
        print("\n🔧 READY FOR:")
        print("• Frontend integration testing")
        print("• End-to-end workflow testing")
        print("• Production deployment")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running on http://localhost:8001")
        print("Please start the backend server with: python main.py")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run API endpoint tests"""
    print("Starting Phase 4 API Testing...")
    print("Testing Folder Watcher REST API endpoints\n")
    
    success = test_api_endpoints()
    
    if success:
        print("\n🎉 Phase 4 API testing completed successfully!")
        print("All folder watcher endpoints are working correctly.")
    else:
        print("\n❌ Phase 4 API testing failed!")
        print("Please check the errors above and ensure the backend server is running.")
    
    return success

if __name__ == "__main__":
    main()
