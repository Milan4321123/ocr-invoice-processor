#!/usr/bin/env python3
"""
Start the approval server in the background for testing.
"""
import subprocess
import sys
import os
import time

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting approval server...")
    
    # Change to backend directory
    backend_dir = "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend"
    
    try:
        # Start the server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--port", "8001",
            "--host", "0.0.0.0"
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Directory: {backend_dir}")
        
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully!")
            print("🌐 Server running at: http://localhost:8001")
            print("📖 API docs at: http://localhost:8001/docs")
            print("\n🔗 Test the approval endpoint:")
            print("   1. Check your email for approval links")
            print("   2. Click 'GENEHMIGEN' button")
            print("   3. You should see a confirmation page AND receive confirmation email")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

if __name__ == "__main__":
    process = start_server()
    
    if process:
        try:
            print("\n⏸️  Server is running. Press Ctrl+C to stop...")
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped.")
    else:
        print("❌ Failed to start server.")
        sys.exit(1)
