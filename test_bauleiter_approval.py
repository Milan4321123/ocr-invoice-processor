#!/usr/bin/env python3
"""
Test Bau-Leiter Approval Email with Secure Approval Links
This tests the Phase 2 workflow with approval/reject buttons
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.services.email_service import EmailService
from datetime import datetime

async def test_bauleiter_approval_email():
    """Test Bau-Leiter approval email with secure links"""
    print("🧪 Testing Bau-Leiter Approval Email (Phase 2)")
    print("=" * 60)
    
    # Initialize email service
    email_service = EmailService()
    
    print(f"📧 Email Provider: {email_service.sendgrid_api_key and 'SendGrid → SMTP' or 'SMTP Only'}")
    print(f"📧 From: {email_service.from_name} <{email_service.from_email}>")
    print(f"🔒 JWT Secret: {'✅ Configured' if email_service.jwt_secret else '❌ Missing'}")
    print(f"🔗 Base URL: {email_service.base_url}")
    print()
    
    # Test data (invoice that was edited)
    test_invoice_data = {
        "id": "test-invoice-bauleiter-456",
        "rechnungsnummer": "INV-2025-BL-001",
        "lieferant": "Elektro Wagner GmbH & Co. KG",
        "rechnungsdatum": "2025-06-22",
        "rechnungsbetrag": "4,275.89",
        "currency": "EUR"
    }
    
    # Changes made by editor
    editor_changes = [
        {
            "field": "Rechnungsbetrag",
            "old_value": "3,850.00",
            "new_value": "4,275.89",
            "timestamp": datetime.now().isoformat()
        },
        {
            "field": "Lieferant",
            "old_value": "Elektro Wagner",
            "new_value": "Elektro Wagner GmbH & Co. KG",
            "timestamp": datetime.now().isoformat()
        },
        {
            "field": "Rechnungsdatum",
            "old_value": "2025-06-20",
            "new_value": "2025-06-22",
            "timestamp": datetime.now().isoformat()
        },
        {
            "field": "Zahlungsbedingungen",
            "old_value": "Netto 30 Tage",
            "new_value": "2% Skonto 10 Tage, netto 30 Tage",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Bau-Leiter email (sending to different email to test)
    bauleiter_email = "incognizatn321@gmail.com"  # Bau-Leiter's email
    editor_name = "Milan Adhikari"
    editor_email = "adhikarimilan4321@gmail.com"  # Editor's email
    
    print(f"📋 Invoice: {test_invoice_data['rechnungsnummer']}")
    print(f"🏢 Vendor: {test_invoice_data['lieferant']}")
    print(f"💰 Amount: {test_invoice_data['rechnungsbetrag']} {test_invoice_data['currency']}")
    print(f"👤 Editor: {editor_name}")
    print(f"👥 Bau-Leiter: {bauleiter_email}")
    print(f"🔄 Changes: {len(editor_changes)} modifications")
    print()
    
    try:
        print("📤 Sending Bau-Leiter approval request...")
        print("   (This will include secure approve/reject buttons)")
        print()
        
        # Send Bau-Leiter approval email
        result = await email_service.send_bauleiter_approval_request(
            invoice_data=test_invoice_data,
            bauleiter_email=bauleiter_email,
            editor_name=editor_name,
            editor_email=editor_email,
            changes_summary=editor_changes
        )
        
        if result["success"]:
            print("🎉 BAU-LEITER APPROVAL EMAIL SENT!")
            print(f"📬 Provider Used: {result.get('provider', 'Unknown')}")
            print(f"📬 Message ID: {result.get('message_id', 'N/A')}")
            print()
            print("🔍 Check your email inbox for the approval request")
            print("📧 Email sent to:", bauleiter_email)
            print()
            print("✅ The email should contain:")
            print("   🔘 Invoice details")
            print("   🔘 Summary of changes made")
            print("   🔘 ✅ APPROVE button (secure link)")
            print("   🔘 ❌ REJECT button (secure link)")
            print("   🔘 Security notice about link expiration")
            print()
            print("🔒 Security Features:")
            print("   • Approval links expire in 7 days")
            print("   • JWT tokens prevent tampering")
            print("   • One-time use tokens")
            print("   • IP tracking for security")
            
        else:
            print("❌ BAU-LEITER EMAIL FAILED!")
            print(f"🚨 Error: {result.get('error', 'Unknown error')}")
            print()
            if "SSL" in str(result.get('error', '')):
                print("🔧 SSL issue - but SMTP fallback should work")
            elif "token" in str(result.get('error', '')).lower():
                print("🔧 Security token generation issue")
            else:
                print("🔧 Check email configuration")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        print()
        print("🔧 This could mean:")
        print("   1. Database table missing (approval_tokens)")
        print("   2. JWT secret issue")
        print("   3. Email provider configuration")
        
        # Show what we would need to implement
        print()
        print("📋 Required for full functionality:")
        print("   • approval_tokens table in database")
        print("   • email_audit_log table in database")
        print("   • JWT token validation endpoints")
        print("   • Approval action handlers")

if __name__ == "__main__":
    asyncio.run(test_bauleiter_approval_email())
