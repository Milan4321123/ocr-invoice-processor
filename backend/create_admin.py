#!/usr/bin/env python3
"""
Manual Admin User Creation Script
Run this if you need to manually create or reset the admin user
"""

import os
import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.auth_service import auth_service
from services.database import db_service

async def create_admin_user():
    """Create or update admin user manually"""
    
    print("🔐 Manual Admin User Creation")
    print("=" * 40)
    
    # Get credentials from environment or prompt
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD")
    email = os.getenv("ADMIN_EMAIL", "admin@yourcompany.com")
    full_name = os.getenv("ADMIN_FULL_NAME", "System Administrator")
    
    if not password:
        password = input("Enter admin password: ")
        if len(password) < 8:
            print("❌ Password too short (minimum 8 characters)")
            return
    
    print(f"Creating admin user: {username}")
    print(f"Email: {email}")
    print(f"Database: {os.getenv('SUPA_URL', 'Not configured')[:50]}...")
    
    # Check database connection
    if not db_service.is_available:
        print("❌ Database not available!")
        print("Make sure your Supabase credentials are configured in .env")
        return
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_username(username)
    if existing_user:
        print(f"⚠️  User '{username}' already exists!")
        choice = input("Do you want to update the password? (y/N): ").lower().strip()
        if choice != 'y':
            print("Cancelled.")
            return
        
        # Update password (this would require implementing an update method)
        print("❌ Password update not implemented in this script.")
        print("To change password, delete the user from Supabase and re-run this script.")
        return
    
    # Create the user
    result = await auth_service.create_user(
        username=username,
        password=password,
        email=email,
        full_name=full_name
    )
    
    if result["success"]:
        print(f"✅ Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print("You can now login to the application.")
    else:
        print(f"❌ Failed to create user: {result['error']}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())