#!/usr/bin/env python3
"""
Simple script to create dropdown table using direct SQL execution
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
import requests

def create_table_with_rest_api():
    """Create table using Supabase REST API"""
    
    # Load environment variables from backend/.env
    load_dotenv('backend/.env')
    
    supabase_url = os.getenv('SUPA_URL')
    supabase_key = os.getenv('SUPA_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Supabase credentials not found")
        return False
    
    print(f"🔌 Connecting to Supabase: {supabase_url}")
    
    # SQL to create table
    create_sql = """
    CREATE TABLE IF NOT EXISTS dropdown_options (
        id BIGSERIAL PRIMARY KEY,
        field_name TEXT NOT NULL,
        value TEXT NOT NULL,
        label TEXT NOT NULL,
        is_default BOOLEAN DEFAULT FALSE,
        sort_order INTEGER DEFAULT 1,
        is_active BOOLEAN DEFAULT TRUE,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(field_name, value)
    );
    
    CREATE INDEX IF NOT EXISTS dropdown_options_field_name_idx ON dropdown_options (field_name);
    CREATE INDEX IF NOT EXISTS dropdown_options_is_active_idx ON dropdown_options (is_active);
    """
    
    try:
        # Use the PostgREST API to execute SQL
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        # Try to use RPC function (this might not work, but let's try)
        rpc_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        
        response = requests.post(
            rpc_url,
            headers=headers,
            json={'sql': create_sql}
        )
        
        if response.status_code == 200:
            print("✅ Table created successfully via RPC!")
        else:
            print(f"⚠️  RPC method failed: {response.status_code} - {response.text}")
            
            # Alternative: Just print the SQL for manual execution
            print("\n" + "="*60)
            print("📋 MANUAL SETUP REQUIRED")
            print("="*60)
            print("Please execute this SQL in your Supabase SQL Editor:")
            print("\n" + create_sql)
            print("\n" + "="*60)
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n" + "="*60)
        print("📋 MANUAL SETUP REQUIRED")
        print("="*60)
        print("Please execute this SQL in your Supabase SQL Editor:")
        print("\n" + create_sql)
        print("\n" + "="*60)
        return True

if __name__ == "__main__":
    create_table_with_rest_api()
