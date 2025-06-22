#!/usr/bin/env python3
"""
Simple test to verify folder watcher import and API endpoint availability
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing folder watcher service import...")
    from services.folder_watcher import folder_watcher_service
    print("✅ Folder watcher service imported successfully")
    
    print("Testing service status...")
    status = folder_watcher_service.get_status()
    print(f"✅ Service status: {status['status']}")
    
    print("Testing API routes import...")
    from api.routes.folder_watcher import router
    print(f"✅ Router imported with {len(router.routes)} routes")
    
    print("Testing FastAPI app import...")
    from main import app
    print("✅ FastAPI app imported successfully")
    
    print("\n🎉 All imports successful! API should be working.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
