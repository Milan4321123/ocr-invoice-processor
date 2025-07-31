#!/usr/bin/env python3
"""
Create Demo Invoice with Skonto for Testing Re-send and Re-update Features
"""

import requests
import json
from datetime import datetime, timedelta

def main():
    base_url = "http://localhost:8000"
    
    print("🎭 Creating demo invoice for testing re-send and re-update features...")
    
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj xref 0 4 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000115 00000 n trailer<</Size 4/Root 1 0 R>>startxref 172 %%EOF"
    
    # Use proper filename format for demo
    today = datetime.now()
    filename = f"{today.strftime('%Y%m%d')}_DEMO001_TESTLIEFERANT_RECHNUNG.pdf"
    
    try:
        # 1. Upload the invoice
        print("📤 Uploading demo invoice...")
        files = {'file': (filename, test_pdf_content, 'application/pdf')}
        response = requests.post(f"{base_url}/api/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
            
        upload_data = response.json()
        invoice_id = upload_data.get('id')
        print(f"✅ Invoice uploaded with ID: {invoice_id}")
        
        # 2. Edit the invoice with Skonto data
        print("✏️ Adding Skonto data to invoice...")
        skonto_date = datetime.now() + timedelta(days=14)
        
        edit_data = {
            "fields": {
                "rechnungsnummer": "DEMO-SKONTO-2025",
                "lieferant": "Demo Supplier GmbH", 
                "rechnungsbetrag": 2500.00,
                "rechnungsdatum": datetime.now().strftime('%Y-%m-%d'),
                "skonto_prozent": 3.0,
                "skonto_datum": skonto_date.strftime('%Y-%m-%d'),
                "zahlungsziel": 30,
                "rechnungspruefung_email": "incognizant321@gmail.com",
                "bauleiter_email": "incognizant321@gmail.com",
                "projekt": "DEMO_PROJECT",
                "gewerk": "ELEKTRO",
                "status": "uploaded"
            },
            "editor_info": {
                "editor_email": "incognizant321@gmail.com",
                "editor_name": "Demo User",
                "changes_summary": [{
                    "field": "all_fields",
                    "old_value": "empty",
                    "new_value": "demo_data",
                    "timestamp": datetime.now().isoformat()
                }]
            }
        }
        
        response = requests.put(f"{base_url}/api/invoices/{invoice_id}/editor", json=edit_data)
        
        if response.status_code == 200:
            print("✅ Invoice edited with Skonto data")
        else:
            print(f"❌ Edit failed: {response.status_code} - {response.text}")
            return
            
        # 3. Test the Skonto decision - mark as "taken" first
        print("💰 Setting initial Skonto decision to 'taken'...")
        decision_data = {"skonto_decision": "taken"}
        response = requests.put(f"{base_url}/api/invoices/{invoice_id}", json=decision_data)
        
        if response.status_code == 200:
            print("✅ Skonto decision set to 'taken'")
        else:
            print(f"❌ Decision update failed: {response.status_code} - {response.text}")
            return
            
        # 4. Test sending a reminder (this should work now even with decision made)
        print("📧 Testing reminder sending...")
        reminder_data = {
            "recipient_email": "incognizant321@gmail.com",
            "reminder_type": "skonto_reminder"
        }
        response = requests.post(f"{base_url}/api/invoices/{invoice_id}/send-skonto-reminder", json=reminder_data)
        
        if response.status_code == 200:
            print("✅ Reminder sent successfully (even with decision already made)")
        else:
            print(f"❌ Reminder failed: {response.status_code} - {response.text}")
            
        # 5. Test changing decision to "missed"
        print("🔄 Testing decision change to 'missed'...")
        decision_data = {"skonto_decision": "missed"}
        response = requests.put(f"{base_url}/api/invoices/{invoice_id}", json=decision_data)
        
        if response.status_code == 200:
            print("✅ Skonto decision changed to 'missed' (re-update allowed)")
        else:
            print(f"❌ Decision re-update failed: {response.status_code} - {response.text}")
            
        # 6. Test changing decision back to "taken" 
        print("🔄 Testing decision change back to 'taken'...")
        decision_data = {"skonto_decision": "taken"}
        response = requests.put(f"{base_url}/api/invoices/{invoice_id}", json=decision_data)
        
        if response.status_code == 200:
            print("✅ Skonto decision changed back to 'taken' (multiple updates allowed)")
        else:
            print(f"❌ Decision re-update failed: {response.status_code} - {response.text}")
            
        print("\n" + "="*60)
        print("🎉 DEMO SETUP COMPLETE!")
        print("="*60)
        print(f"📋 Demo Invoice ID: {invoice_id}")
        print(f"💰 Invoice Amount: €2,500.00")
        print(f"📊 Skonto: 3% (€75.00 potential savings)")
        print(f"📅 Skonto Date: {skonto_date.strftime('%Y-%m-%d')}")
        print(f"🎯 Current Status: taken")
        print("\n🚀 FEATURES TO DEMONSTRATE:")
        print("   ✅ Re-send reminder emails (even after decision made)")
        print("   ✅ Change Skonto decisions multiple times")
        print("   ✅ Update from 'taken' → 'missed' → 'taken'")
        print("   ✅ Send multiple reminder emails")
        print(f"\n🌐 Frontend URLs:")
        print(f"   📊 Dashboard: http://localhost:3000/dashboard")
        print(f"   💰 Prüfbericht: http://localhost:3000/prufbericht")
        print(f"   ✏️ Edit Invoice: http://localhost:3000/invoice-editor?id={invoice_id}")
        
    except Exception as e:
        print(f"❌ Demo setup failed: {str(e)}")

if __name__ == "__main__":
    main()
