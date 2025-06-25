#!/usr/bin/env python3
"""
Start monitoring server for approval clicks with email confirmations.
"""
import os
import sys
import asyncio
import uvicorn

# Change to backend directory and add to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

# Disable problematic features
os.environ['ENABLE_OCR'] = 'false'
os.environ['USE_MOCK_OCR'] = 'true'

async def start_approval_server():
    """Start the approval server with email confirmations."""
    
    print("=" * 70)
    print("🚀 STARTING ROBUST APPROVAL SERVER")
    print("=" * 70)
    print("📧 Email sent to: incognizant321@gmail.com") 
    print("📱 Enhanced approval workflow active!")
    print("✉️ Email confirmations enabled (no complex web pages)")
    print("🛡️ Robust error handling and retry mechanisms")
    print("=" * 70)
    
    try:
        # Import the app
        from main import app
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8002,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        print(f"✅ Server starting on http://localhost:8002")
        print(f"🔗 Approval endpoint: http://localhost:8002/api/approval/{{token}}")
        print(f"📬 When approval is clicked:")
        print(f"   1. Invoice status updated in Supabase")
        print(f"   2. Confirmation email sent to Bau-Leiter")
        print(f"   3. Notification email sent to Editor")
        print(f"   4. Simple success page shown")
        print(f"=" * 70)
        
        await server.serve()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try installing missing dependencies:")
        print("   pip install google-cloud-documentai watchdog aiosmtplib")

if __name__ == "__main__":
    asyncio.run(start_approval_server())
