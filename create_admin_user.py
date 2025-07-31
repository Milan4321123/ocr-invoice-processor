#!/usr/bin/env python3
"""
Create admin user in production Supabase database
"""
import asyncio
import os
from datetime import datetime
from supabase import create_client

# Supabase configuration (use your production values)
SUPABASE_URL = os.getenv("SUPA_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPA_SERVICE_ROLE_KEY")

async def create_admin_user():
    try:
        # Create Supabase client with service role key
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Admin user data
        admin_data = {
            "username": "admin",
            "hashed_password": "$2b$12$H15JMkrTvK9XJpGPahX9fu7BZ/wS6Au69fPRLLBpYksvTAurKspWO",
            "email": os.getenv("ADMIN_EMAIL", "admin@yourcompany.com"),
            "full_name": "Administrator",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Try to insert the user
        result = supabase.table("users").upsert(admin_data).execute()
        
        if result.data:
            print("✅ Admin user created successfully!")
            print(f"Username: admin")
            print(f"Password: admin123")
            print(f"User ID: {result.data[0]['id']}")
        else:
            print("❌ Failed to create admin user")
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    print("Creating admin user in Supabase...")
    asyncio.run(create_admin_user())
