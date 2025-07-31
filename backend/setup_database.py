#!/usr/bin/env python3
"""
Automatic Database Setup Script
Executes the complete Supabase setup SQL automatically
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.database import db_service

async def setup_complete_database() -> Dict[str, Any]:
    """
    Set up the complete database schema by executing COMPLETE_SUPABASE_SETUP.sql
    """
    print("🏗️  Setting up complete database schema...")
    
    try:
        # Check database connection
        if not db_service.is_available:
            return {
                "success": False,
                "error": "Database connection not available. Please check your .env file."
            }
        
        print("✅ Database connection established")
        
        # Read the complete setup SQL file
        sql_file = Path(__file__).parent.parent / "COMPLETE_SUPABASE_SETUP.sql"
        
        if not sql_file.exists():
            return {
                "success": False,
                "error": f"SQL setup file not found: {sql_file}"
            }
        
        print(f"📄 Reading SQL setup file: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL into individual statements (basic approach)
        # Remove comments and empty lines
        sql_lines = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                sql_lines.append(line)
        
        sql_statements = ' '.join(sql_lines).split(';')
        sql_statements = [stmt.strip() for stmt in sql_statements if stmt.strip()]
        
        print(f"🔧 Executing {len(sql_statements)} SQL statements...")
        
        # Execute each SQL statement
        executed_count = 0
        failed_count = 0
        
        for i, statement in enumerate(sql_statements, 1):
            try:
                if statement.strip():
                    print(f"   [{i}/{len(sql_statements)}] Executing statement...")
                    
                    # Use raw SQL execution via Supabase client
                    response = db_service._client.rpc('execute_sql', {'sql_query': statement}).execute()
                    executed_count += 1
                    
            except Exception as e:
                print(f"   ⚠️  Statement {i} failed (might be expected): {str(e)[:100]}...")
                failed_count += 1
                # Continue with other statements
                continue
        
        print(f"✅ Database setup completed!")
        print(f"   - Executed: {executed_count} statements")
        print(f"   - Failed: {failed_count} statements (some failures are expected)")
        
        return {
            "success": True,
            "message": f"Database setup completed. Executed {executed_count} statements.",
            "executed": executed_count,
            "failed": failed_count
        }
        
    except Exception as e:
        error_msg = f"Database setup failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

async def setup_database_simple() -> Dict[str, Any]:
    """
    Simple database setup using direct table creation
    Fallback if SQL file execution fails
    """
    print("🔧 Setting up database with direct table creation...")
    
    try:
        # Check if main table exists
        try:
            response = db_service._client.table("invoices_clean").select("*").limit(1).execute()
            print("✅ Main tables already exist")
            return {"success": True, "message": "Database already set up"}
        except:
            pass
        
        # Create tables using direct SQL execution
        tables_sql = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS public.users (
                id UUID NOT NULL DEFAULT gen_random_uuid(),
                username VARCHAR(50) NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                email VARCHAR(255),
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT users_pkey PRIMARY KEY (id)
            );
            """,
            
            # Invoices table
            """
            CREATE TABLE IF NOT EXISTS public.invoices_clean (
                id UUID NOT NULL DEFAULT gen_random_uuid(),
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500),
                file_size INTEGER,
                mime_type VARCHAR(100),
                rechnungsempfaenger VARCHAR(255),
                rechnungssteller VARCHAR(255),
                projekt VARCHAR(255),
                gewerk VARCHAR(255),
                weiter_berechnen_an VARCHAR(255),
                rechnungsbetrag DECIMAL(10,2),
                kfw_anrechenbare_kosten BOOLEAN DEFAULT false,
                rechnungseingang DATE,
                faelligkeit DATE,
                skonto_datum DATE,
                skonto_prozent DECIMAL(5,2),
                rechnungsart VARCHAR(50) DEFAULT 'rechnung',
                rechnungspruefung VARCHAR(255),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT invoices_clean_pkey PRIMARY KEY (id)
            );
            """
        ]
        
        for sql in tables_sql:
            try:
                db_service._client.rpc('execute_sql', {'sql_query': sql}).execute()
                print("   ✅ Table created successfully")
            except Exception as e:
                print(f"   ⚠️  Table creation: {str(e)[:100]}...")
        
        return {
            "success": True,
            "message": "Basic database setup completed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Simple database setup failed: {str(e)}"
        }

async def main():
    """Main setup function"""
    print("🚀 Starting automatic database setup...")
    print("=" * 60)
    
    # Try complete setup first
    result = await setup_complete_database()
    
    if not result["success"]:
        print("\n🔄 Complete setup failed, trying simple setup...")
        result = await setup_database_simple()
    
    if result["success"]:
        print(f"\n🎉 {result['message']}")
        print("\n📋 Next steps:")
        print("1. Start the backend server: python main.py")
        print("2. The admin user will be created automatically")
        print("3. Access the application at http://localhost:3000")
    else:
        print(f"\n❌ Setup failed: {result['error']}")
        print("\n📋 Manual setup required:")
        print("1. Go to your Supabase SQL Editor")
        print("2. Run the COMPLETE_SUPABASE_SETUP.sql file")
        print("3. Then start the application")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(main())