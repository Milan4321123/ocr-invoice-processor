#!/usr/bin/env python3
"""
Migration runner for Render deployment (Root Directory)
Ensures database schema is set up before starting the application
"""
import asyncio
import sys
import os
from pathlib import Path

# Change to backend directory and add to path
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from setup_database import setup_complete_database

async def main():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    result = await setup_complete_database()
    
    if result["success"]:
        print(f"✅ {result['message']}")
        return 0
    else:
        print(f"❌ Migration failed: {result['error']}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
