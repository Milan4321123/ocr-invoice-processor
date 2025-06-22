#!/usr/bin/env python3
"""
Quick test to check folder watcher import and basic functionality
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing folder watcher imports...")
    
    # Test individual imports
    print("1. Testing services.folder_watcher import...")
    from services.folder_watcher import folder_watcher_service
    print("   ✅ services.folder_watcher imported successfully")
    
    print("2. Testing api.routes.folder_watcher import...")
    from api.routes.folder_watcher import router
    print("   ✅ api.routes.folder_watcher imported successfully")
    
    print("3. Testing folder watcher service status...")
    status = folder_watcher_service.get_status()
    print(f"   ✅ Folder watcher status: {status['status']}")
    
    print("4. Testing router endpoints...")
    print(f"   ✅ Router has {len(router.routes)} routes")
    
    print("\n🎉 All imports and basic functionality working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()
