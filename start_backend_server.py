#!/usr/bin/env python3
"""
Simple backend startup script for OCR Invoice Processor
Starts the FastAPI server and monitors for approval clicks
"""
import subprocess
import sys
import os
import time
import requests
import signal

# Configuration
BACKEND_PORT = 8001
BACKEND_HOST = "0.0.0.0"
BACKEND_DIR = "/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend"

def print_status(message, success=True):
    """Print status message"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def kill_existing_process():
    """Kill any existing process on the backend port"""
    try:
        result = subprocess.run(['lsof', '-ti:8001'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid])
                    print_info(f"Killed existing process on port 8001 (PID: {pid})")
            time.sleep(2)
    except Exception as e:
        print_info(f"No existing process to kill: {e}")

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting OCR Invoice Processor Backend")
    print("=" * 50)
    
    # Kill any existing process
    kill_existing_process()
    
    # Change to backend directory
    if not os.path.exists(BACKEND_DIR):
        print_status(f"Backend directory not found: {BACKEND_DIR}", False)
        return None
    
    os.chdir(BACKEND_DIR)
    print_info(f"Working directory: {BACKEND_DIR}")
    
    # Start the server
    try:
        print_info("Starting FastAPI server with uvicorn...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", BACKEND_HOST,
            "--port", str(BACKEND_PORT),
            "--reload"
        ])
        
        # Wait for server to start
        print_info("Waiting for server to start...")
        for i in range(30):
            try:
                response = requests.get(f"http://localhost:{BACKEND_PORT}/health", timeout=2)
                if response.status_code == 200:
                    print_status(f"Backend started successfully!")
                    print_info(f"🌐 Server URL: http://localhost:{BACKEND_PORT}")
                    print_info(f"📚 API Docs: http://localhost:{BACKEND_PORT}/docs")
                    print_info(f"🔍 Health Check: http://localhost:{BACKEND_PORT}/health")
                    return process
            except:
                pass
            time.sleep(1)
            if i % 5 == 0:
                print_info(f"Still waiting... ({i}s)")
        
        print_status("Server failed to start within 30 seconds", False)
        process.terminate()
        return None
        
    except Exception as e:
        print_status(f"Failed to start server: {e}", False)
        return None

def monitor_server(process):
    """Monitor the server and provide user interface"""
    try:
        print("\n" + "=" * 50)
        print("🎯 Backend Server is Running!")
        print("=" * 50)
        print("📧 Email Testing Commands:")
        print("   python test_email_complete.py")
        print("   python test_bauleiter_approval.py")
        print("   python test_confirmation_email_fix.py")
        print("")
        print("🔗 API Endpoints:")
        print(f"   Health: http://localhost:{BACKEND_PORT}/health")
        print(f"   Docs: http://localhost:{BACKEND_PORT}/docs")
        print(f"   Email Test: http://localhost:{BACKEND_PORT}/api/email/test")
        print("")
        print("🧪 Approval Workflow Test:")
        print("   1. Run: python test_bauleiter_approval.py")
        print("   2. Check email: incognizant321@gmail.com")
        print("   3. Click GENEHMIGEN in the email")
        print("   4. You should receive a confirmation email")
        print("")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Monitor server status
        while True:
            time.sleep(5)
            try:
                response = requests.get(f"http://localhost:{BACKEND_PORT}/health", timeout=2)
                if response.status_code != 200:
                    print_warning("Server health check failed")
            except:
                print_warning("Server appears to be down")
                break
                
    except KeyboardInterrupt:
        print_info("\n🛑 Shutting down server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print_status("Server stopped successfully")
    except Exception as e:
        print_status(f"Monitoring error: {e}", False)

def main():
    """Main function"""
    try:
        # Start backend
        process = start_backend()
        if not process:
            print_status("Failed to start backend server", False)
            return 1
        
        # Monitor server
        monitor_server(process)
        return 0
        
    except Exception as e:
        print_status(f"Startup error: {e}", False)
        return 1

if __name__ == "__main__":
    sys.exit(main())
