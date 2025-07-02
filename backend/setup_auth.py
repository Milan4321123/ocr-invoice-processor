#!/usr/bin/env python3
"""
Database Setup Script for Authentication
Creates the users table and default admin user
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.database import db_service
from services.auth_service import auth_service

async def setup_database():
    """Set up the database with users table and default admin user"""
    print("🔧 Setting up authentication database...")
    
    try:
        # Check database connection
        if not db_service.is_available:
            print("❌ Database connection not available!")
            print("Please check your .env file and ensure SUPA_URL and SUPA_KEY are set.")
            return False
        
        print("✅ Database connection established")
        
        # Try to create a test user to see if table exists
        print("🔍 Checking if users table exists...")
        
        # Try to query the users table
        try:
            response = db_service.client.table("users").select("*").limit(1).execute()
            print("✅ Users table exists")
            table_exists = True
        except Exception as e:
            print(f"⚠️ Users table does not exist: {e}")
            table_exists = False
        
        if not table_exists:
            print("❌ Users table must be created manually in Supabase.")
            print("\n📋 Please run the following SQL in your Supabase SQL Editor:")
            print("=" * 60)
            
            # Read and display the SQL setup file
            sql_file = backend_dir / "setup_users_table.sql"
            if sql_file.exists():
                with open(sql_file, 'r') as f:
                    print(f.read())
            else:
                # Fallback SQL if file doesn't exist
                print("""
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations for authenticated users" ON users FOR ALL USING (true);

INSERT INTO users (username, hashed_password, email, full_name)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewEVklk.QjuCQ5/6',
    'admin@company.local',
    'System Administrator'
) ON CONFLICT (username) DO NOTHING;
                """)
            
            print("=" * 60)
            print("\n🔗 Access your Supabase SQL Editor at:")
            print("https://supabase.com/dashboard/project/YOUR_PROJECT_ID/sql")
            print("\nAfter creating the table, run this script again.")
            return False
        
        # Initialize default user
        print("🔐 Initializing default admin user...")
        result = await auth_service.initialize_default_user()
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print("\n🎉 Authentication system setup complete!")
            print("\nDefault login credentials:")
            print("Username: admin")
            print("Password: admin123")
            print("\n🌐 You can now access the application at:")
            print("Frontend: http://localhost:3000")
            print("Backend:  http://localhost:8000")
            return True
        else:
            print(f"❌ Failed to create default user: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup function"""
    print("🚀 Invoice Management System - Authentication Setup")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment variables
    if not os.getenv("SUPA_URL") or not os.getenv("SUPA_KEY"):
        print("❌ Missing required environment variables!")
        print("Please ensure SUPA_URL and SUPA_KEY are set in your .env file.")
        return
    
    # Run setup
    success = asyncio.run(setup_database())
    
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup incomplete. Please follow the instructions above.")

if __name__ == "__main__":
    main()
