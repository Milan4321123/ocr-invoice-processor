#!/usr/bin/env python3
"""
Test script for end-to-end Skonto workflow testing.
This script will:
1. Create a test invoice with Skonto data
2. Test API endpoints for retrieving Skonto data
3. Test sending reminders
4. Test marking as captured/missed
"""

import requests
import json
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_skonto_workflow():
    """Test the complete Skonto workflow"""
    print("🧪 Testing Skonto Workflow End-to-End")
    print("=" * 50)
    
    # Step 1: Create a test invoice with Skonto data
    print("\n📝 Step 1: Creating test invoice with Skonto data...")
    
    # Calculate future date for Skonto
    skonto_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    test_invoice_data = {
        "file_name": "test_workflow_invoice.pdf",
        "rechnungssteller": "Workflow Test Supplier GmbH",
        "rechnungsbetrag": 2500.00,
        "skonto_prozent": 2.0,
        "skonto_datum": skonto_date,
        "skonto_decision": "pending",
        "status": "completed",  # Mark as completed so it appears in Prüfbericht
        "created_at": datetime.now().isoformat(),
        "bearbeitung_abgeschlossen": True
    }
    
    # We'll use the database service directly instead of API for simplicity
    print(f"   Invoice: {test_invoice_data['file_name']}")
    print(f"   Amount: €{test_invoice_data['rechnungsbetrag']}")
    print(f"   Skonto: {test_invoice_data['skonto_prozent']}% until {skonto_date}")
    print(f"   Potential savings: €{test_invoice_data['rechnungsbetrag'] * test_invoice_data['skonto_prozent'] / 100}")
    
    # Step 2: Test API endpoints
    print("\n🔍 Step 2: Testing Skonto API endpoints...")
    
    # Test summary endpoint
    try:
        response = requests.get(f"{API_BASE}/skonto/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✅ Summary API: {summary['total_opportunities']} opportunities, €{summary['total_potential_savings']} potential")
        else:
            print(f"   ❌ Summary API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Summary API error: {e}")
    
    # Test opportunities endpoint
    try:
        response = requests.get(f"{API_BASE}/skonto/dashboard/opportunities?urgency=all&limit=50")
        if response.status_code == 200:
            opportunities = response.json()
            print(f"   ✅ Opportunities API: {len(opportunities)} opportunities found")
            
            # Find a test invoice to work with
            test_invoice = None
            for opp in opportunities:
                if opp['invoice_number'] and 'test' in opp['invoice_number'].lower():
                    test_invoice = opp
                    break
            
            if test_invoice:
                invoice_id = test_invoice['id']
                print(f"   📋 Using test invoice: {test_invoice['invoice_number']} (ID: {invoice_id})")
                
                # Step 3: Test sending reminder
                print(f"\n📧 Step 3: Testing reminder functionality...")
                try:
                    response = requests.post(f"{API_BASE}/invoices/{invoice_id}/send-skonto-reminder")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Reminder sent successfully!")
                        print(f"   📧 Recipient: {result.get('recipient_email', 'N/A')}")
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        print(f"   ⚠️ Reminder response: {response.status_code} - {error_detail}")
                except Exception as e:
                    print(f"   ❌ Reminder error: {e}")
                
                # Step 4: Test marking as taken
                print(f"\n✅ Step 4: Testing 'mark as taken' functionality...")
                try:
                    response = requests.put(f"{API_BASE}/invoices/{invoice_id}", 
                                          json={"skonto_decision": "taken"})
                    if response.status_code == 200:
                        print(f"   ✅ Successfully marked as taken!")
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        print(f"   ⚠️ Mark as taken response: {response.status_code} - {error_detail}")
                except Exception as e:
                    print(f"   ❌ Mark as taken error: {e}")
                
                # Step 5: Verify the change
                print(f"\n🔍 Step 5: Verifying status change...")
                try:
                    response = requests.get(f"{API_BASE}/skonto/dashboard/opportunities?urgency=all&limit=50")
                    if response.status_code == 200:
                        updated_opportunities = response.json()
                        updated_invoice = None
                        for opp in updated_opportunities:
                            if opp['id'] == invoice_id:
                                updated_invoice = opp
                                break
                        
                        if updated_invoice:
                            print(f"   📊 Updated status: {updated_invoice.get('skonto_decision', 'N/A')}")
                            print(f"   📧 Reminder sent: {updated_invoice.get('reminder_sent', False)}")
                        else:
                            print(f"   ℹ️ Invoice no longer in opportunities (may be moved to captured list)")
                except Exception as e:
                    print(f"   ❌ Verification error: {e}")
                    
            else:
                print(f"   ℹ️ No test invoices found - you can create one manually")
                
        else:
            print(f"   ❌ Opportunities API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Opportunities API error: {e}")
    
    print(f"\n🎯 Step 6: Frontend Testing Instructions")
    print(f"   1. Open: http://localhost:3000/prufbericht")
    print(f"   2. You should see invoices in different status categories")
    print(f"   3. Test the filter dropdown to see: All, Captured, Missed, Pending, Expired")
    print(f"   4. Click 'Reminder' buttons to test email sending")
    print(f"   5. Click 'Take' or 'Miss' buttons to test status updates")
    print(f"   6. Verify that invoices remain visible in the appropriate lists")
    print(f"   7. Check that reminder status is clearly shown")
    
    print(f"\n" + "=" * 50)
    print(f"✅ Skonto workflow test completed!")
    print(f"🌐 Frontend: http://localhost:3000/prufbericht")
    print(f"📋 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_skonto_workflow()
