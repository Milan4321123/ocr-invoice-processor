"""
Render startup script for OCR Invoice Processor Backend
Runs the server directly with uvicorn to avoid Pydantic import issues
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    port = os.environ.get("PORT", "8000")
    # Run uvicorn directly to bypass any import issues
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0",
        "--port", port,
        "--log-level", "info"
    ])
