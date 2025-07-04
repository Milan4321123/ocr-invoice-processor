#!/usr/bin/env python3
"""
Create Test Invoice with Skonto Data
This script creates a test invoice with Skonto expiring soon to test reminder functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.database import db_service
from datetime import datetime, timedelta
import uuid

def create_test_skonto_invoice():
    """Create a test invoice with Skonto data for testing reminders"""
    print("🧪 Creating Test Invoice with Skonto Data")
    print("=" * 50)
    
    if not db_service.is_available:
        print("❌ Database service is not available")
        return False
    
    # Generate test data
    invoice_id = str(uuid.uuid4())
    skonto_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")  # Expires in 2 days
    
    test_invoice_data = {
        "id": invoice_id,
        "file_name": "test_skonto_reminder_invoice.pdf",
        "rechnungssteller": "Test Skonto Supplier GmbH",
        "rechnungsempfaenger": "Test Company AG",
        "projekt": "Skonto Test Project",
        "gewerk": "Test Construction Work",
        "rechnungsbetrag": 5000.00,
        "rechnungseingang": datetime.now().strftime("%Y-%m-%d"),
        "faelligkeit": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "skonto_datum": skonto_date,
        "skonto_prozent": 3.0,  # 3% Skonto
        "skonto_decision": "pending",  # Important: needs to be pending for reminders
        "rechnungsart": "Baurechnung",
        "kfw_anrechenbare_kosten": True,
        "rechnungspruefung": "test@company.com",
        "bauleiter_email": "bauleiter@company.com",  # This will receive the reminder
        "weiter_berechnen_an": "Test Customer",
        "status": "completed",  # Completed processing
        "review_status": "completed_review",
        "created_at": datetime.now().isoformat(),
        "reviewed_at": datetime.now().isoformat(),
        "skonto_reminder_sent": False,  # Important: should be False to trigger reminder
        "file_path": f"invoices/{invoice_id}/test_skonto_reminder_invoice.pdf",
        "mime_type": "application/pdf",
        "file_size": 12345
    }
    
    print(f"📋 Creating invoice with ID: {invoice_id}")
    print(f"   File name: {test_invoice_data['file_name']}")
    print(f"   Amount: €{test_invoice_data['rechnungsbetrag']}")
    print(f"   Skonto: {test_invoice_data['skonto_prozent']}% until {skonto_date}")
    print(f"   Potential savings: €{test_invoice_data['rechnungsbetrag'] * test_invoice_data['skonto_prozent'] / 100}")
    print(f"   Days until expiry: {(datetime.strptime(skonto_date, '%Y-%m-%d') - datetime.now()).days}")
    print(f"   Bauleiter email: {test_invoice_data['bauleiter_email']}")
    
    try:
        # Insert invoice into database
        result = db_service._client.table(db_service.table_name).insert(test_invoice_data).execute()
        
        if result.data:
            print("✅ Test invoice created successfully!")
            print(f"   Invoice ID: {invoice_id}")
            print(f"   This invoice should trigger a Skonto reminder when the scheduler runs")
            print(f"   Run the reminder test script to verify: python test_skonto_reminder_system.py")
            return True
        else:
            print("❌ Failed to create test invoice")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test invoice: {e}")
        return False

def cleanup_test_skonto_invoices():
    """Clean up test invoices created by this script"""
    print("🧹 Cleaning up test Skonto invoices...")
    
    if not db_service.is_available:
        print("❌ Database service is not available")
        return False
    
    try:
        # Delete invoices with test file names
        result = db_service._client.table(db_service.table_name)\
            .delete()\
            .like("file_name", "%test_skonto%")\
            .execute()
        
        print(f"✅ Cleaned up test invoices")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up test invoices: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage test Skonto invoices")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test invoices instead of creating")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_test_skonto_invoices()
    else:
        create_test_skonto_invoice()
