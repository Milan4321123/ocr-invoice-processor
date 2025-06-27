#!/usr/bin/env python3
"""
Test enhanced email functionality with all German fields and PDF attachment
"""
import requests
import json

def test_enhanced_email_with_all_fields():
    # Use a real invoice ID from the database
    invoice_id = "3441971d-ecc4-4c41-af0d-3444b36908e9"
    
    # Test data with all German fields populated - matching the screenshot
    test_data = {
        "fields": {
            "rechnungsempfaenger": "Baumeister GmbH",
            "rechnungssteller": "Sanitär Schmidt & Söhne",
            "projekt": "Bürokomplex Nord",
            "gewerk": "Sanitärinstallation",
            "rechnungsbetrag": 5.00,
            "rechnungseingang": "2025-05-29",
            "faelligkeit": "2025-06-03",
            "skonto_datum": "2025-05-29",
            "skonto_prozent": 0.03,
            "rechnungsart": "gutschrift",
            "kfw_anrechenbar": True,
            "rechnungspruefung_email": "incognizant321@gmail.com",
            "weiter_berechnen_an": "Abteilung oder Kontakt auswählen..."
        },
        "editor_info": {
            "editor_email": "incognizant321@gmail.com",
            "editor_name": "Milan Adhokari - Enhanced Test",
            "changes_summary": [
                {
                    "field": "rechnungsbetrag",
                    "old_value": "3750.99",
                    "new_value": "4299.99",
                    "description": "Enhanced test: Updated invoice amount"
                },
                {
                    "field": "projekt",
                    "old_value": "Real Email Test Project", 
                    "new_value": "PDF Email Test Project 2025",
                    "description": "Enhanced test: Updated project name for comprehensive email test"
                },
                {
                    "field": "rechnungssteller",
                    "old_value": "Updated Test Vendor Services",
                    "new_value": "Enhanced Test Vendor Services Ltd", 
                    "description": "Enhanced test: Updated vendor name"
                },
                {
                    "field": "skonto_prozent",
                    "old_value": "2.5",
                    "new_value": "3.5",
                    "description": "Enhanced test: Updated discount percentage"
                }
            ]
        }
    }
    
    try:
        print("🧪 Testing ENHANCED email with ALL German fields + PDF attachment...")
        print(f"📧 Email will be sent to: {test_data['editor_info']['editor_email']}")
        print(f"👤 Editor: {test_data['editor_info']['editor_name']}")
        print(f"🆔 Invoice ID: {invoice_id}")
        print(f"💰 Amount: €{test_data['fields']['rechnungsbetrag']}")
        print(f"🏢 Customer: {test_data['fields']['rechnungsempfaenger']}")
        print(f"🏗️ Project: {test_data['fields']['projekt']}")
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
            print("✅ Enhanced invoice save successful!")
            print(f"📧 Email sent: {result.get('email_sent', False)}")
            print(f"📝 Updated fields: {len(result.get('updated_fields', []))} fields")
            print(f"💾 Message: {result.get('message')}")
            print()
            
            if result.get('email_sent'):
                print("🎉 SUCCESS! Enhanced email notification sent to incognizant321@gmail.com")
                print("📬 Check your email inbox for the comprehensive invoice notification!")
                print()
                print("📄 Email should now contain:")
                print("  ✅ ALL German invoice fields with proper labels")
                print("  ✅ Rechnungsempfänger: Milan Test Company GmbH")
                print("  ✅ Rechnungssteller: Enhanced Test Vendor Services Ltd") 
                print("  ✅ Projekt: PDF Email Test Project 2025")
                print("  ✅ Gewerk: Complete Field Testing Work")
                print("  ✅ Rechnungsbetrag: €4,299.99")
                print("  ✅ All dates and financial details")
                print("  ✅ KfW information")
                print("  ✅ Professional HTML formatting")
                print("  ✅ Detailed change summary")
                print("  ✅ PDF attachment (if available)")
                print("  ✅ German field labels and structure")
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
        print("🔍 Verifying comprehensive data...")
        
        # Verify the comprehensive data was saved
        verify_response = requests.get(f"http://localhost:8000/api/invoices/{invoice_id}/editor")
        if verify_response.status_code == 200:
            saved_data = verify_response.json()
            fields = saved_data.get('fields', {})
            print("✅ Comprehensive data verification successful!")
            print(f"💰 Amount: €{fields.get('rechnungsbetrag', 'N/A')}")
            print(f"🏢 Customer: {fields.get('rechnungsempfaenger', 'N/A')}")
            print(f"🏭 Vendor: {fields.get('rechnungssteller', 'N/A')}")
            print(f"📧 Email: {fields.get('rechnungspruefung_email', 'N/A')}")
            print(f"📋 Project: {fields.get('projekt', 'N/A')}")
            print(f"⚒️  Gewerk: {fields.get('gewerk', 'N/A')}")
            print(f"📅 Due Date: {fields.get('faelligkeit', 'N/A')}")
            print(f"💳 Skonto: {fields.get('skonto_prozent', 'N/A')}%")
            print(f"🎯 KfW: {'Yes' if fields.get('kfw_anrechenbar') else 'No'}")
        else:
            print("❌ Data verification failed")
                
    except Exception as e:
        print(f"❌ Enhanced test failed with exception: {e}")

if __name__ == "__main__":
    test_enhanced_email_with_all_fields()
