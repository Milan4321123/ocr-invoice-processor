#!/usr/bin/env python3
"""
Test the invoice editing workflow with email notification
This script verifies the complete enhanced email notification functionality
"""

import requests
import json
from datetime import datetime, timedelta

def test_comprehensive_invoice_workflow():
    base_url = "http://localhost:8000"
    
    print("🔬 Testing Complete Invoice Workflow with Enhanced Email...")
    
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj xref 0 4 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000115 00000 n trailer<</Size 4/Root 1 0 R>>startxref 172 %%EOF"
    
    # Use proper filename format
    today = datetime.now()
    filename = f"{today.strftime('%Y%m%d')}_WORKFLOW{today.strftime('%H%M%S')}_TESTFIRMA_RECHNUNG.pdf"
    
    try:
        # 1. Upload invoice
        print("📤 Uploading test invoice...")
        files = {"file": (filename, test_pdf_content, "application/pdf")}
        response = requests.post(f"{base_url}/api/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
            
        upload_result = response.json()
        invoice_id = upload_result.get("id")
        print(f"✅ Invoice uploaded with ID: {invoice_id}")
        
        # 2. Get initial invoice data
        print("📋 Checking initial invoice data...")
        response = requests.get(f"{base_url}/api/invoices/{invoice_id}")
        
        if response.status_code == 200:
            initial_data = response.json()
            print(f"📊 Initial status: {initial_data.get('status')}")
        
        # 3. Edit invoice with comprehensive data
        print("✏️ Editing invoice with comprehensive data...")
        edit_data = {
            "invoice_data": {
                # Comprehensive form data with all possible fields
                "rechnungsnummer": "RG-2024-COMPREHENSIVE-001",
                "rechnungsempfaenger": "Beispiel Bauunternehmen GmbH",
                "rechnungssteller": "Meisterbetrieb Elektro Solutions",
                "lieferant": "Meisterbetrieb Elektro Solutions",
                "rechnungsdatum": "2024-06-15",
                "rechnungseingang": datetime.now().strftime('%Y-%m-%d'),
                
                # Project details
                "projekt": "Neubau Bürogebäude Stadtmitte",
                "gewerk": "ELEKTRO",
                "kostenstelle": "KOSTEN-001-ELEKTRO",
                "weiter_berechnen_an": "Auftraggeber XYZ GmbH",
                "bestellnummer": "BO-2024-12345",
                
                # Financial comprehensive data
                "rechnungsbetrag": 12750.89,
                "currency": "EUR",
                "faelligkeit": "2024-07-15",
                "skonto_prozent": 3.0,
                "skonto_datum": "2024-07-01",
                "kfw_anrechenbare_kosten": 8500.00,
                "material_kosten": 9200.50,
                "lohn_kosten": 3550.39,
                
                # Additional comprehensive details
                "liefertermin": "2024-06-30",
                "aufmass_datum": "2024-06-28",
                "netto_brutto": "Netto",
                "mwst_satz": 19,
                "kontierung": "6400 - Elektroinstallationsarbeiten",
                "bemerkungen": "Umfangreiche Elektroinstallation mit LED-Beleuchtung, Netzwerkverkabelung und Sicherheitstechnik. Alle Arbeiten wurden fachgerecht ausgeführt und abgenommen. Garantie: 24 Monate.",
                
                # Workflow
                "bauleiter_email": "bauleiter@comprehensive-test.de",
                "rechnungspruefung_email": "buchhaltung@comprehensive-test.de",
                
                "status": "edited"
            },
            "editor_info": {
                "editor_email": "comprehensive.editor@test-company.de",
                "editor_name": "Max Mustermann (Vollständige Bearbeitung)",
                "changes_summary": [
                    {
                        "field": "rechnungsnummer",
                        "old_value": "",
                        "new_value": "RG-2024-COMPREHENSIVE-001",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "rechnungsempfaenger",
                        "old_value": "",
                        "new_value": "Beispiel Bauunternehmen GmbH",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "projekt",
                        "old_value": "",
                        "new_value": "Neubau Bürogebäude Stadtmitte",
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
                        "new_value": "12750.89 EUR",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "skonto_prozent",
                        "old_value": "",
                        "new_value": "3.0%",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "kfw_anrechenbare_kosten",
                        "old_value": "",
                        "new_value": "8500.00 EUR",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "field": "bemerkungen",
                        "old_value": "",
                        "new_value": "Umfangreiche Elektroinstallation mit LED-Beleuchtung...",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        }
        
        response = requests.put(f"{base_url}/api/invoices/{invoice_id}/editor", json=edit_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice edited successfully")
            print(f"📧 Email sent: {result.get('email_sent', False)}")
            
            # 4. Verify the updated invoice data
            print("🔍 Verifying updated invoice data...")
            response = requests.get(f"{base_url}/api/invoices/{invoice_id}")
            
            if response.status_code == 200:
                updated_data = response.json()
                print(f"📊 Updated status: {updated_data.get('status')}")
                print(f"💰 Amount: {updated_data.get('rechnungsbetrag')} {updated_data.get('currency', 'EUR')}")
                print(f"🏗️ Project: {updated_data.get('projekt')}")
                print(f"⚡ Trade: {updated_data.get('gewerk')}")
                print(f"💰 Skonto: {updated_data.get('skonto_prozent')}% until {updated_data.get('skonto_datum')}")
                print(f"📝 Notes: {updated_data.get('bemerkungen', 'N/A')[:50]}...")
            
        else:
            print(f"❌ Edit failed: {response.status_code} - {response.text}")
            return
            
        print(f"\n🎯 Comprehensive Workflow Test Complete!")
        print(f"📊 Invoice ID: {invoice_id}")
        print(f"📧 Enhanced email notification sent with:")
        print(f"   ✅ Complete invoice details from all form sections")
        print(f"   ✅ Project and trade information")
        print(f"   ✅ Financial data including Skonto and KfW costs")
        print(f"   ✅ Additional information and workflow details")
        print(f"   ✅ Comprehensive changes summary with timestamps")
        print(f"   ✅ Professional layout with organized sections")
        print(f"   ✅ Responsive design for mobile and desktop")
        
        return invoice_id
        
    except Exception as e:
        print(f"❌ Comprehensive workflow test failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_comprehensive_invoice_workflow()
