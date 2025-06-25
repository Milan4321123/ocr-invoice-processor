#!/usr/bin/env python3
"""
Simple server to handle approval clicks - just starts and waits.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Disable problematic imports
os.environ['ENABLE_OCR'] = 'false'
os.environ['USE_MOCK_OCR'] = 'true'

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting approval server on http://localhost:8002")
    print("📧 Email sent to: incognizant321@gmail.com")
    print("📱 Ready to handle approval clicks!")
    print("🔗 When someone clicks approve/reject, it will be processed here")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
