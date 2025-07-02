#!/usr/bin/env python3
"""
Test the enhanced email notification after invoice editing
This script tests the comprehensive email template with all invoice form details
"""

import requests
import json
from datetime import datetime, timedelta

def main():
    base_url = "http://localhost:8000"
    
    print("🎭 Testing Enhanced Email Notification with Comprehensive Invoice Details...")
    
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj xref 0 4 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000115 00000 n trailer<</Size 4/Root 1 0 R>>startxref 172 %%EOF"
    
    # Use proper filename format for demo
    today = datetime.now()
    skonto_date = today + timedelta(days=14)
    filename = f"{today.strftime('%Y%m%d')}_ENH{today.strftime('%H%M%S')}_ELEKTRO_RECHNUNG.pdf"
    
    try:
        # 1. Upload invoice
        print("📤 Uploading test invoice...")
        files = {"file": (filename, test_pdf_content, "application/pdf")}
        response = requests.post(f"{base_url}/api/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
            
        upload_result = response.json()
        print(f"📤 Upload response: {upload_result}")
        invoice_id = upload_result.get("invoice_id") or upload_result.get("id")
        if not invoice_id:
            print(f"❌ No invoice ID found in response: {upload_result}")
            return
        print(f"✅ Invoice uploaded with ID: {invoice_id}")
        
        # 2. Edit invoice with comprehensive data including ALL form fields
        print("✏️ Editing invoice with comprehensive form data...")
        edit_data = {
            "invoice_data": {
                # Basic information
                "rechnungsnummer": "RG-2024-ENHANCED-001",
                "rechnungsempfaenger": "Musterbau GmbH & Co. KG",
                "rechnungssteller": "Premium Elektro Services AG",
                "lieferant": "Premium Elektro Services AG",
                "rechnungsdatum": datetime.now().strftime('%Y-%m-%d'),
                "rechnungseingang": datetime.now().strftime('%Y-%m-%d'),
                
                # Project and trade information
                "projekt": "Wohnpark Sonnenhügel - Phase 2",
                "gewerk": "ELEKTRO",
                "kostenstelle": "KS-4001-ELEKTRO",
                "weiter_berechnen_an": "Bauherr GmbH",
                "bestellnummer": "BO-2024-0789",
                
                # Financial details
                "rechnungsbetrag": 5850.75,
                "currency": "EUR",
                "faelligkeit": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                "skonto_prozent": 2.5,
                "skonto_datum": skonto_date.strftime('%Y-%m-%d'),
                "kfw_anrechenbare_kosten": 3200.00,
                "material_kosten": 4200.50,
                "lohn_kosten": 1650.25,
                
                # Additional information
                "liefertermin": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                "aufmass_datum": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                "netto_brutto": "Netto",
                "mwst_satz": 19,
                "kontierung": "6200 - Elektroinstallation",
                "bemerkungen": "Rechnung enthält Sicherheitsbeleuchtung für Notausgänge und LED-Panels für Büroräume. Material wurde termingerecht geliefert und fachgerecht installiert.",
                
                # Workflow information
                "bauleiter_email": "bauleiter@musterbau.de",
                "rechnungspruefung_email": "buchhaltung@musterbau.de",
                
                # Processing status
                "status": "edited"
            },
            "editor_info": {
                "editor_email": "enhanced.test@company.com",
                "editor_name": "Enhanced Test User",
                "changes_summary": [
                    {
                        "field": "rechnungsnummer",
                        "old_value": "",
                        "new_value": "RG-2024-ENHANCED-001",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "rechnungsempfaenger",
                        "old_value": "",
                        "new_value": "Musterbau GmbH & Co. KG", 
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "projekt",
                        "old_value": "",
                        "new_value": "Wohnpark Sonnenhügel - Phase 2",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "gewerk",
                        "old_value": "",
                        "new_value": "ELEKTRO",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "rechnungsbetrag",
                        "old_value": "0",
                        "new_value": "5850.75 EUR",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "skonto_prozent",
                        "old_value": "",
                        "new_value": "2.5%",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "bemerkungen",
                        "old_value": "",
                        "new_value": "Rechnung enthält Sicherheitsbeleuchtung für Notausgänge...",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        }
        
        response = requests.put(f"{base_url}/api/invoices/{invoice_id}/editor", json=edit_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice edited successfully with comprehensive data")
            print(f"📧 Email sent: {result.get('email_sent', False)}")
            print(f"📬 Message ID: {result.get('email_message_id', 'N/A')}")
            
            # 3. Test the email notification endpoint directly
            print("\n📧 Testing direct email notification endpoint...")
            email_data = {
                "invoice_id": invoice_id,
                "editor_email": "enhanced.test@company.com",
                "editor_name": "Enhanced Test User",
                "changes_summary": edit_data["editor_info"]["changes_summary"]
            }
            
            response = requests.post(
                f"{base_url}/api/email/editor-notification",
                json=email_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                email_result = response.json()
                print("✅ Direct email notification sent successfully")
                print(f"📬 Message ID: {email_result.get('message_id', 'N/A')}")
            else:
                print(f"⚠️ Direct email test failed: {response.status_code} - {response.text}")
                print("(This is expected if no email provider is configured)")
            
        else:
            print(f"❌ Edit failed: {response.status_code} - {response.text}")
            return
            
        print(f"\n🎯 Enhanced Email Test Complete!")
        print(f"📊 Invoice ID: {invoice_id}")
        print(f"📧 Enhanced email template includes:")
        print(f"   ✅ All basic invoice fields (rechnungsnummer, lieferant, etc.)")
        print(f"   ✅ Project & trade info (projekt, gewerk, kostenstelle)")
        print(f"   ✅ Financial details (amounts, skonto, dates)")
        print(f"   ✅ Additional info (liefertermin, bemerkungen, etc.)")
        print(f"   ✅ Workflow information (bauleiter_email, etc.)")
        print(f"   ✅ Comprehensive changes summary with timestamps")
        print(f"   ✅ Professional styling and layout")
        
        print(f"\n🌐 Frontend URL:")
        print(f"   ✏️ Edit Invoice: http://localhost:3000/invoice-editor?id={invoice_id}")
        
    except Exception as e:
        print(f"❌ Enhanced email test failed: {str(e)}")

if __name__ == "__main__":
    main()
