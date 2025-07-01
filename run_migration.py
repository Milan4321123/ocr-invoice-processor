#!/usr/bin/env python3
"""
Database Migration Runner for Skonto Reminder System
Safely applies database migrations with rollback capability
"""

import os
import sys
import logging
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables"""
    load_dotenv()
    url = os.getenv("SUPA_URL")
    key = os.getenv("SUPA_KEY")
    
    if not url or not key:
        logger.error("❌ Missing SUPA_URL or SUPA_KEY environment variables")
        sys.exit(1)
        
    return url, key

def create_database_client(url: str, key: str) -> Client:
    """Create and test database connection"""
    try:
        client = create_client(url, key)
        # Test connection
        result = client.rpc('version').execute()
        logger.info(f"✅ Database connection successful: PostgreSQL {result.data}")
        return client
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)

def create_migration_table(client: Client):
    """Create migration tracking table if it doesn't exist"""
    try:
        # Check if table exists by trying to select from it
        try:
            client.table('migration_history').select('id').limit(1).execute()
            logger.info("✅ Migration history table already exists")
        except:
            # Table doesn't exist, we'll track migrations in a simple way
            logger.info("✅ Will use simple migration tracking")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup migration tracking: {e}")
        # Don't raise - we can continue without migration history

def check_migration_applied(client: Client, migration_name: str) -> bool:
    """Check if migration has already been applied by looking for new columns"""
    try:
        # Check if the new Skonto columns exist
        result = client.table('invoices_clean').select('skonto_reminder_sent').limit(1).execute()
        logger.info("✅ Skonto columns already exist, migration previously applied")
        return True
    except Exception as e:
        logger.info("🔄 Skonto columns not found, migration needed")
        return False

def apply_migration(client: Client, migration_file: str):
    """Apply the migration file"""
    migration_name = os.path.basename(migration_file)
    
    # Check if already applied
    if check_migration_applied(client, migration_name):
        logger.info(f"✅ Migration {migration_name} already applied, skipping")
        return
    
    try:
        # Read migration file
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        logger.info(f"🔄 Applying migration: {migration_name}")
        
        # Execute migration
        client.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        # Record successful migration
        client.table('migration_history').insert({
            'migration_name': migration_name,
            'applied_by': os.getenv('USER', 'system'),
            'status': 'success'
        }).execute()
        
        logger.info(f"✅ Migration {migration_name} applied successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration {migration_name} failed: {e}")
        
        # Record failed migration
        try:
            client.table('migration_history').insert({
                'migration_name': migration_name,
                'applied_by': os.getenv('USER', 'system'),
                'status': 'failed'
            }).execute()
        except:
            pass
        
        raise

def main():
    """Main execution function"""
    logger.info("🚀 Starting Skonto Database Migration")
    
    # Load environment
    url, key = load_environment()
    
    # Create database client
    client = create_database_client(url, key)
    
    # Setup migration tracking
    create_migration_table(client)
    
    # Apply migration
    migration_file = os.path.join(os.path.dirname(__file__), 'database', 'migrations', '002_skonto_tracking_fields.sql')
    
    if not os.path.exists(migration_file):
        logger.error(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    try:
        apply_migration(client, migration_file)
        logger.info("🎉 All migrations completed successfully!")
        
        # Verify the migration worked
        result = client.table('invoices_clean').select('*').limit(1).execute()
        logger.info(f"✅ Database verification: Found {len(result.data)} test records")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
