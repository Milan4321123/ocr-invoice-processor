#!/usr/bin/env python3
"""
Test script to create a real invoice with Skonto data for testing the Prüfbericht page.
This will help us verify that the full workflow works correctly.
"""
import sys
import os
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append('/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend')

from services.database import db_service

def create_test_invoice_with_skonto():
    """Create a test invoice with Skonto data"""
    
    # Calculate skonto date (tomorrow - should appear in urgent list)
    tomorrow = datetime.now() + timedelta(days=1)
    skonto_date = tomorrow.strftime("%Y-%m-%d")
    
    test_invoice = {
        "file_name": "test_skonto_invoice.pdf",
        "file_path": "test/test_skonto_invoice.pdf",
        "file_size": 12345,
        "mime_type": "application/pdf",
        "rechnungsempfaenger": "Test Company GmbH",
        "rechnungssteller": "Test Supplier AG",  # This will be the vendor in Prüfbericht
        "projekt": "Test Project",
        "gewerk": "Electrical Work",
        "weiter_berechnen_an": "Test Department",
        "rechnungsbetrag": 10000.00,  # €10,000 invoice amount
        "kfw_anrechenbare_kosten": False,
        "rechnungseingang": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "faelligkeit": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "skonto_datum": skonto_date,  # Skonto due tomorrow
        "skonto_prozent": 2.50,  # 2.5% Skonto
        "rechnungsart": "Standard Invoice",
        "rechnungspruefung": "Pending Review",
        "status": "completed",  # Set as completed so it appears in reports
        "ocr_status": "completed",
        "ocr_text": "Test OCR text content",
        "review_status": "completed_review",
        "reviewed_by": "Test Reviewer",
        "reviewed_at": datetime.now().isoformat(),
        "review_notes": "Test invoice for Skonto functionality",
        "editor_email": "incognizant321@gmail.com",
        "editor_name": "Test Editor",
        "edit_completed_at": datetime.now().isoformat(),
        "approval_status": "approved",
        "approved_at": datetime.now().isoformat(),
        "approval_method": "manual",
        "skonto_reminder_sent": False,
        "skonto_decision": "pending",  # This is important for Prüfbericht display
        "actual_skonto_savings": None  # Will be set when decision is made
    }
    
    print("🔧 Creating test invoice with Skonto data...")
    print(f"📊 Invoice details:")
    print(f"   - Vendor: {test_invoice['rechnungssteller']}")
    print(f"   - Amount: €{test_invoice['rechnungsbetrag']:,.2f}")
    print(f"   - Skonto Rate: {test_invoice['skonto_prozent']}%")
    print(f"   - Skonto Date: {test_invoice['skonto_datum']}")
    print(f"   - Status: {test_invoice['status']}")
    print(f"   - Skonto Decision: {test_invoice['skonto_decision']}")
    
    # Create the invoice
    result = db_service.create_invoice(test_invoice)
    
    if result["success"]:
        invoice_id = result["data"]["id"]
        potential_savings = test_invoice["rechnungsbetrag"] * test_invoice["skonto_prozent"] / 100
        
        print(f"✅ Successfully created test invoice!")
        print(f"📋 Invoice ID: {invoice_id}")
        print(f"💰 Potential Skonto Savings: €{potential_savings:.2f}")
        print(f"📅 Skonto expires: {test_invoice['skonto_datum']} (tomorrow)")
        print("")
        print("🎯 This invoice should now appear in the Prüfbericht page with:")
        print(f"   - Vendor: {test_invoice['rechnungssteller']}")
        print(f"   - Amount: €{test_invoice['rechnungsbetrag']:,.2f}")
        print(f"   - Skonto: {test_invoice['skonto_prozent']}% (€{potential_savings:.2f})")
        print(f"   - Deadline: {test_invoice['skonto_datum']}")
        print(f"   - Status: pending")
        
        return invoice_id
    else:
        print(f"❌ Failed to create test invoice: {result.get('error')}")
        return None

def create_multiple_test_invoices():
    """Create multiple test invoices with different scenarios"""
    
    scenarios = [
        {
            "name": "Urgent Invoice (1 day)",
            "days_offset": 1,
            "amount": 5000.00,
            "skonto_rate": 2.0,
            "vendor": "Urgent Supplier GmbH"
        },
        {
            "name": "Normal Invoice (3 days)",
            "days_offset": 3,
            "amount": 7500.00,
            "skonto_rate": 3.0,
            "vendor": "Normal Supplier AG"
        },
        {
            "name": "Early Invoice (7 days)",
            "days_offset": 7,
            "amount": 12000.00,
            "skonto_rate": 1.5,
            "vendor": "Early Supplier Ltd"
        },
        {
            "name": "Expired Invoice (-2 days)",
            "days_offset": -2,
            "amount": 3000.00,
            "skonto_rate": 2.5,
            "vendor": "Expired Supplier KG"
        }
    ]
    
    created_invoices = []
    
    for i, scenario in enumerate(scenarios):
        skonto_date = (datetime.now() + timedelta(days=scenario["days_offset"])).strftime("%Y-%m-%d")
        
        test_invoice = {
            "file_name": f"test_invoice_{i+1}.pdf",
            "file_path": f"test/test_invoice_{i+1}.pdf",
            "file_size": 12345 + i * 1000,
            "mime_type": "application/pdf",
            "rechnungsempfaenger": "Test Company GmbH",
            "rechnungssteller": scenario["vendor"],
            "projekt": f"Test Project {i+1}",
            "gewerk": "General Work",
            "rechnungsbetrag": scenario["amount"],
            "kfw_anrechenbare_kosten": False,
            "rechnungseingang": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "faelligkeit": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "skonto_datum": skonto_date,
            "skonto_prozent": scenario["skonto_rate"],
            "rechnungsart": "Standard Invoice",
            "status": "completed",
            "ocr_status": "completed",
            "review_status": "completed_review",
            "reviewed_by": "Test Reviewer",
            "reviewed_at": datetime.now().isoformat(),
            "editor_email": "editor@test.com",
            "editor_name": "Test Editor",
            "edit_completed_at": datetime.now().isoformat(),
            "approval_status": "approved",
            "approved_at": datetime.now().isoformat(),
            "skonto_decision": "pending"
        }
        
        print(f"🔧 Creating {scenario['name']}...")
        result = db_service.create_invoice(test_invoice)
        
        if result["success"]:
            invoice_id = result["data"]["id"]
            potential_savings = scenario["amount"] * scenario["skonto_rate"] / 100
            created_invoices.append(invoice_id)
            
            print(f"✅ Created: {scenario['name']}")
            print(f"   - ID: {invoice_id}")
            print(f"   - Vendor: {scenario['vendor']}")
            print(f"   - Amount: €{scenario['amount']:,.2f}")
            print(f"   - Skonto: {scenario['skonto_rate']}% (€{potential_savings:.2f})")
            print(f"   - Due: {skonto_date}")
            print("")
        else:
            print(f"❌ Failed to create {scenario['name']}: {result.get('error')}")
    
    return created_invoices

def test_skonto_queries():
    """Test the Skonto query methods"""
    print("🔍 Testing Skonto query methods...")
    
    # Test get_invoices_with_skonto_due
    print("\n📋 Testing get_invoices_with_skonto_due(7):")
    result = db_service.get_invoices_with_skonto_due(days_ahead=7)
    if result["success"]:
        invoices = result["data"]
        print(f"   Found {len(invoices)} invoices with Skonto due within 7 days")
        for invoice in invoices:
            print(f"   - {invoice.get('rechnungssteller')} | €{invoice.get('rechnungsbetrag', 0):,.2f} | {invoice.get('skonto_datum')} | {invoice.get('skonto_decision')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test get_all_invoices
    print("\n📋 Testing get_all_invoices():")
    result = db_service.get_all_invoices()
    if result["success"]:
        invoices = result["data"]
        skonto_invoices = [inv for inv in invoices if inv.get('skonto_datum')]
        print(f"   Found {len(invoices)} total invoices")
        print(f"   Found {len(skonto_invoices)} invoices with Skonto data")
    else:
        print(f"   ❌ Error: {result.get('error')}")

if __name__ == "__main__":
    print("🧪 Test Invoice Creator for Skonto Functionality")
    print("=" * 50)
    
    if not db_service.is_available:
        print("❌ Database service is not available!")
        print("   Make sure your .env file has correct SUPA_URL and SUPA_KEY")
        sys.exit(1)
    
    print("✅ Database service is available")
    print("")
    
    choice = input("Choose option:\n1. Create single test invoice\n2. Create multiple test scenarios\n3. Test queries only\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        create_test_invoice_with_skonto()
    elif choice == "2":
        create_multiple_test_invoices()
        print("\n" + "=" * 50)
        print("📊 Summary: Created multiple test invoices with different Skonto scenarios")
        print("🎯 Check the Prüfbericht page to see them in the dashboard!")
    elif choice == "3":
        test_skonto_queries()
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🔍 Testing Skonto queries after creation...")
    test_skonto_queries()
    
    print("\n🎯 Next steps:")
    print("1. Open the frontend: http://localhost:3000/prufbericht")
    print("2. Check if the test invoices appear in the Skonto dashboard")
    print("3. Verify the metrics are calculated correctly")
    print("4. Test the filtering and actions")
