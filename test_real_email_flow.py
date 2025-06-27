#!/usr/bin/env python3
"""
Test invoice save flow with real email to incognizant321@gmail.com
"""
import requests
import json

def test_invoice_save_with_real_email():
    # Use a real invoice ID from the database
    invoice_id = "3441971d-ecc4-4c41-af0d-3444b36908e9"
    
    # Test data with realistic construction project data for Bauleiter control
    test_data = {
        "fields": {
            "rechnungsempfaenger": "Bauunternehmen Milan GmbH",
            "rechnungssteller": "Elektro Müller & Söhne GmbH",
            "projekt": "Wohnkomplex Musterstraße 15-17",
            "gewerk": "Elektroinstallation Phase 2",
            "rechnungsbetrag": 15750.85,
            "rechnungseingang": "2025-06-26",
            "faelligkeit": "2025-07-26", 
            "skonto_datum": "2025-07-06",
            "skonto_prozent": 2.0,
            "rechnungsart": "rechnung",
            "kfw_anrechenbar": True,
            "rechnungspruefung_email": "incognizant321@gmail.com",
            "weiter_berechnen_an": "Controlling Abteilung"
        },
        "editor_info": {
            "editor_email": "incognizant321@gmail.com",  # Bauleiter email
            "editor_name": "Milan Adhokari (Bauleiter)",
            "changes_summary": [
                {
                    "field": "rechnungsbetrag",
                    "old_value": "3750.99",
                    "new_value": "15750.85",
                    "description": "Rechnungsbetrag nach Materialprüfung angepasst"
                },
                {
                    "field": "projekt",
                    "old_value": "Real Email Test Project", 
                    "new_value": "Wohnkomplex Musterstraße 15-17",
                    "description": "Korrektes Projekt zugeordnet"
                },
                {
                    "field": "gewerk",
                    "old_value": "Email Testing Work",
                    "new_value": "Elektroinstallation Phase 2",
                    "description": "Spezifizierung der Arbeitsphase"
                },
                {
                    "field": "kfw_anrechenbar",
                    "old_value": "false",
                    "new_value": "true",
                    "description": "KfW-Anrechenbarkeit nach Prüfung bestätigt"
                }
            ]
        }
    }
    
    try:
        print("🧪 Testing Bauleiter control email with BEAUTIFUL HTML format...")
        print(f"📧 Control email will be sent to Bauleiter: {test_data['editor_info']['editor_email']}")
        print(f"👤 Bearbeiter: {test_data['editor_info']['editor_name']}")
        print(f"🆔 Invoice ID: {invoice_id}")
        print(f"🏗️  Project: {test_data['fields']['projekt']}")
        print(f"💰 Amount: €{test_data['fields']['rechnungsbetrag']}")
        print()
        
        # Make the request
        response = requests.put(
            f"http://localhost:8000/api/invoices/{invoice_id}/editor",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice save successful!")
            print(f"📧 Email sent: {result.get('email_sent', False)}")
            print(f"📝 Updated fields: {len(result.get('updated_fields', []))} fields")
            print(f"💾 Message: {result.get('message')}")
            print()
            
            if result.get('email_sent'):
                print("🎉 SUCCESS! Beautiful Bauleiter control email sent to incognizant321@gmail.com")
                print("📬 Check your email inbox for the detailed invoice control notification!")
                print()
                print("Email contains BEAUTIFUL HTML with:")
                print("- 📋 Complete invoice form fields in organized sections")
                print("- 💰 Financial details with formatting")
                print("- 📅 All dates and deadlines")
                print("- ✅ Checkbox fields (KfW status)")
                print("- 📝 Change summary with highlights")
                print("- 🎨 Professional responsive design")
                print("- 🔍 Ready for Bauleiter control and review")
            else:
                print("⚠️  No email was sent (check email configuration)")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
        
        print()
        print("🔍 Verifying saved data...")
        
        # Verify the data was saved
        verify_response = requests.get(f"http://localhost:8000/api/invoices/{invoice_id}/editor")
        if verify_response.status_code == 200:
            saved_data = verify_response.json()
            fields = saved_data.get('fields', {})
            print("✅ Data verification successful!")
            print(f"💰 Amount: €{fields.get('rechnungsbetrag', 'N/A')}")
            print(f"🏢 Customer: {fields.get('rechnungsempfaenger', 'N/A')}")
            print(f"📧 Email: {fields.get('rechnungspruefung_email', 'N/A')}")
            print(f"📋 Project: {fields.get('projekt', 'N/A')}")
        else:
            print("❌ Data verification failed")
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_invoice_save_with_real_email()
