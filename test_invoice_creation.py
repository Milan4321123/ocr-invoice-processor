#!/usr/bin/env python3
"""
Test script to create an invoice with Skonto data and verify the workflow.
"""
import os
import sys
import logging
from datetime import datetime, timedelta

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from services.database import db_service
except ImportError:
    print("Error: Could not import database service. Make sure backend is properly set up.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_invoice():
    """Create a test invoice with Skonto data"""
    
    # Calculate Skonto date (tomorrow)
    tomorrow = datetime.now() + timedelta(days=1)
    skonto_date = tomorrow.strftime("%Y-%m-%d")
    
    test_invoice = {
        "file_name": "test_skonto_invoice.pdf",
        "file_path": "test/test_skonto_invoice.pdf",
        "rechnungsempfaenger": "Test Company GmbH",
        "rechnungssteller": "Test Supplier AG",
        "projekt": "Test Project",
        "gewerk": "Elektro",
        "rechnungsbetrag": 1000.00,
        "kfw_anrechenbare_kosten": True,
        "rechnungseingang": datetime.now().strftime("%Y-%m-%d"),
        "faelligkeit": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "skonto_datum": skonto_date,
        "skonto_prozent": 2.5,
        "rechnungsart": "Rechnung",
        "status": "completed",  # Set as completed
        "review_status": "completed_review",
        "skonto_decision": "pending",  # This should make it appear in Prüfbericht
        "editor_email": "incognizant321@gmail.com",
        "editor_name": "Test Editor",
        "edit_completed_at": datetime.now().isoformat()
    }
    
    logger.info("🔧 Creating test invoice with Skonto data...")
    logger.info(f"   - Amount: €{test_invoice['rechnungsbetrag']}")
    logger.info(f"   - Skonto: {test_invoice['skonto_prozent']}%")
    logger.info(f"   - Skonto Date: {test_invoice['skonto_datum']}")
    logger.info(f"   - Status: {test_invoice['status']}")
    logger.info(f"   - Skonto Decision: {test_invoice['skonto_decision']}")
    
    result = db_service.create_invoice(test_invoice)
    
    if result["success"]:
        invoice_id = result["data"]["id"]
        logger.info(f"✅ Test invoice created successfully: {invoice_id}")
        
        # Now test the Skonto queries
        logger.info("\n🔍 Testing Skonto queries...")
        
        # Test get_invoices_with_skonto_due
        skonto_result = db_service.get_invoices_with_skonto_due(days_ahead=7)
        logger.info(f"   - get_invoices_with_skonto_due: {len(skonto_result.get('data', []))} invoices")
        
        # Test get_all_invoices_with_skonto
        all_skonto_result = db_service.get_all_invoices_with_skonto()
        logger.info(f"   - get_all_invoices_with_skonto: {len(all_skonto_result.get('data', []))} invoices")
        
        return invoice_id
    else:
        logger.error(f"❌ Failed to create test invoice: {result.get('error')}")
        return None

def test_backend_endpoints():
    """Test the backend Skonto endpoints"""
    import requests
    
    logger.info("\n🌐 Testing backend endpoints...")
    
    try:
        # Test summary endpoint
        summary_response = requests.get("http://localhost:8000/api/skonto/dashboard/summary")
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            logger.info(f"   - Summary: {summary_data.get('total_opportunities', 0)} opportunities")
        else:
            logger.error(f"   - Summary endpoint failed: {summary_response.status_code}")
        
        # Test opportunities endpoint
        opportunities_response = requests.get("http://localhost:8000/api/skonto/dashboard/opportunities")
        if opportunities_response.status_code == 200:
            opportunities_data = opportunities_response.json()
            logger.info(f"   - Opportunities: {len(opportunities_data)} invoices")
        else:
            logger.error(f"   - Opportunities endpoint failed: {opportunities_response.status_code}")
            
    except Exception as e:
        logger.error(f"   - Backend test failed: {e}")

if __name__ == "__main__":
    logger.info("🧪 Starting invoice workflow test...")
    
    # Check database connection
    if not db_service.is_available:
        logger.error("❌ Database service not available")
        sys.exit(1)
    
    # Create test invoice
    invoice_id = create_test_invoice()
    
    if invoice_id:
        # Test backend endpoints
        test_backend_endpoints()
        
        logger.info(f"\n✅ Test completed! Invoice ID: {invoice_id}")
        logger.info("👉 Now check the Prüfbericht page to see if the invoice appears")
    else:
        logger.error("❌ Test failed - could not create invoice")
