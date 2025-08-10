"""
Render startup script for OCR Invoice Processor Backend (Root Directory)
Runs the server from the backend directory
"""
import os
import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Add backend to Python path
    sys.path.insert(0, str(backend_dir))
    
    port = os.environ.get("PORT", "8000")
    
    # Run uvicorn from backend directory
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0",
        "--port", port,
        "--log-level", "info"
    ])
