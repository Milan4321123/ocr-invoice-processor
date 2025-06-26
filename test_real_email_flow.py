#!/usr/bin/env python3
"""
Test invoice save flow with real email to incognizant321@gmail.com
"""
import requests
import json

def test_invoice_save_with_real_email():
    # Use a real invoice ID from the database
    invoice_id = "3441971d-ecc4-4c41-af0d-3444b36908e9"
    
    # Test data with real email address
    test_data = {
        "fields": {
            "rechnungsempfaenger": "Milan Test Company GmbH",
            "rechnungssteller": "Updated Test Vendor Services",
            "projekt": "Real Email Test Project",
            "gewerk": "Email Testing Work",
            "rechnungsbetrag": 3750.99,
            "rechnungseingang": "2025-06-26",
            "faelligkeit": "2025-07-26",
            "skonto_datum": "2025-07-06",
            "skonto_prozent": 2.5,
            "rechnungsart": "rechnung",
            "kfw_anrechenbar": True,
            "rechnungspruefung_email": "incognizant321@gmail.com",
            "weiter_berechnen_an": "Milan Test Department"
        },
        "editor_info": {
            "editor_email": "incognizant321@gmail.com",
            "editor_name": "Milan Adhokari",
            "changes_summary": [
                {
                    "field": "rechnungsbetrag",
                    "old_value": "2500.75",
                    "new_value": "3750.99",
                    "description": "Updated invoice amount for real email test"
                },
                {
                    "field": "projekt",
                    "old_value": "Test Project Updated", 
                    "new_value": "Real Email Test Project",
                    "description": "Updated project name for real email test"
                },
                {
                    "field": "rechnungsempfaenger",
                    "old_value": "Test Customer GmbH",
                    "new_value": "Milan Test Company GmbH", 
                    "description": "Updated customer name for real email test"
                }
            ]
        }
    }
    
    try:
        print("🧪 Testing invoice save with REAL email to incognizant321@gmail.com...")
        print(f"📧 Email will be sent to: {test_data['editor_info']['editor_email']}")
        print(f"👤 Editor: {test_data['editor_info']['editor_name']}")
        print(f"🆔 Invoice ID: {invoice_id}")
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
                print("🎉 SUCCESS! Email notification sent to incognizant321@gmail.com")
                print("📬 Check your email inbox for the invoice update notification!")
                print()
                print("Email should contain:")
                print("- Invoice details (amount, dates, customer, etc.)")
                print("- Change summary showing what was updated")
                print("- Professional HTML formatting")
                print("- Editor information (Milan Adhokari)")
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
