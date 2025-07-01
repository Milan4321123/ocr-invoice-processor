#!/usr/bin/env python3
"""
Create a test invoice for Skonto testing
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
import uuid

# Load environment
load_dotenv()

def create_test_invoice():
    """Create a test invoice with Skonto data"""
    url = os.getenv("SUPA_URL")
    key = os.getenv("SUPA_KEY")
    
    if not url or not key:
        print("❌ Missing database credentials")
        return None
    
    try:
        # Create database client
        client = create_client(url, key)
        
        # Create test invoice data
        invoice_data = {
            "id": str(uuid.uuid4()),
            "file_name": "TEST_SKONTO_INVOICE.pdf",
            "file_path": "/test/path/TEST_SKONTO_INVOICE.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "rechnungsempfaenger": "Test Company",
            "rechnungssteller": "Skonto Test Supplier GmbH",
            "projekt": "Skonto Test Project",
            "gewerk": "Electrical",
            "rechnungsbetrag": 2000.50,
            "rechnungseingang": "2025-06-28",
            "faelligkeit": "2025-07-28",
            "skonto_datum": "2025-07-06",  # 5 days from now
            "skonto_prozent": 2.5,
            "rechnungsart": "Rechnung",
            "status": "uploaded",
            "ocr_status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "skonto_reminder_sent": False,
            "skonto_decision": "pending"
        }
        
        # Insert into database
        response = client.table('invoices_clean').insert(invoice_data).execute()
        
        if response.data:
            invoice_id = response.data[0]["id"]
            print(f"✅ Test invoice created successfully!")
            print(f"📄 Invoice ID: {invoice_id}")
            print(f"💰 Amount: {invoice_data['rechnungsbetrag']} EUR")
            print(f"💸 Skonto: {invoice_data['skonto_prozent']}% until {invoice_data['skonto_datum']}")
            return invoice_id
        else:
            print("❌ Failed to create test invoice")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test invoice: {e}")
        return None

if __name__ == "__main__":
    invoice_id = create_test_invoice()
    if invoice_id:
        print(f"\n🧪 Use this invoice ID for testing: {invoice_id}")
    else:
        sys.exit(1)
