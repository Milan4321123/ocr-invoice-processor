#!/usr/bin/env python3
"""
Admin Password Change Script
Use this to change the admin password in Supabase database
"""

import os
import asyncio
import sys
import getpass
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.auth_service import auth_service
from services.database import db_service

async def change_admin_password():
    """Change admin user password"""
    
    print("🔐 Admin Password Change Tool")
    print("=" * 40)
    
    # Get username from environment or prompt
    username = os.getenv("ADMIN_USERNAME", "admin")
    print(f"Changing password for user: {username}")
    print(f"Database: {os.getenv('SUPA_URL', 'Not configured')[:50]}...")
    
    # Check database connection
    if not db_service.is_available:
        print("❌ Database not available!")
        print("Make sure your Supabase credentials are configured in .env")
        return
    
    # Check if user exists
    existing_user = await auth_service.get_user_by_username(username)
    if not existing_user:
        print(f"❌ User '{username}' does not exist!")
        print("Run create_admin.py first to create the admin user.")
        return
    
    print(f"✅ Found user: {existing_user['email']}")
    
    # Get new password
    print("\nEnter new password (minimum 8 characters):")
    new_password = getpass.getpass("New password: ")
    
    if len(new_password) < 8:
        print("❌ Password too short (minimum 8 characters)")
        return
    
    # Confirm password
    confirm_password = getpass.getpass("Confirm password: ")
    
    if new_password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    # Hash the new password
    hashed_password = auth_service.get_password_hash(new_password)
    
    # Update in database
    try:
        response = db_service.client.table("users").update({
            "hashed_password": hashed_password
        }).eq("username", username).execute()
        
        if response.data:
            print("✅ Password updated successfully!")
            print("You can now login with the new password.")
            
            # Also update the .env file if requested
            update_env = input("\nUpdate ADMIN_PASSWORD in .env file? (y/N): ").lower().strip()
            if update_env == 'y':
                update_env_file(new_password)
                
        else:
            print("❌ Failed to update password in database")
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")

def update_env_file(new_password):
    """Update the ADMIN_PASSWORD in .env file"""
    env_file = Path(__file__).parent.parent / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found")
        return
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update ADMIN_PASSWORD line
        updated_lines = []
        password_updated = False
        
        for line in lines:
            if line.startswith('ADMIN_PASSWORD='):
                updated_lines.append(f'ADMIN_PASSWORD={new_password}\n')
                password_updated = True
                print(f"✅ Updated ADMIN_PASSWORD in {env_file}")
            else:
                updated_lines.append(line)
        
        # If ADMIN_PASSWORD wasn't found, add it
        if not password_updated:
            updated_lines.append(f'ADMIN_PASSWORD={new_password}\n')
            print(f"✅ Added ADMIN_PASSWORD to {env_file}")
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
            
        print("🔄 Restart your backend server to use the new password.")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    asyncio.run(change_admin_password())