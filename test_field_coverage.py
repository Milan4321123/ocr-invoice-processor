#!/usr/bin/env python3
"""
Test to verify both email templates show comprehensive field information.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import EmailService

def test_field_coverage():
    email_service = EmailService()
    
    # Complete invoice data to test field coverage
    complete_invoice_data = {
        'id': 'test-123',
        'rechnungsnummer': 'INV-2025-001',
        'rechnungsempfaenger': 'Test Company GmbH',
        'rechnungssteller': 'Supplier Company',
        'rechnungsdatum': '2025-01-15',
        'rechnungseingang': '2025-01-16',
        'projekt': 'Test Project',
        'gewerk': 'Elektro',
        'kostenstelle': 'K001',
        'weiter_berechnen_an': 'Customer ABC',
        'bestellnummer': 'PO-12345',
        'total_amount': '1500.00',
        'rechnungsbetrag': '1500.00',
        'faelligkeit': '2025-02-15',
        'skonto_datum': '2025-01-25',
        'skonto_prozent': '2',
        'kfw_anrechenbare_kosten': '800.00',
        'material_kosten': '1000.00',
        'lohn_kosten': '500.00',
        'liefertermin': '2025-01-20',
        'aufmass_datum': '2025-01-22',
        'netto_brutto': 'Netto',
        'mwst_satz': '19',
        'kontierung': 'K-4711',
        'bemerkungen': 'Test invoice with all fields',
        'bauleiter_email': 'incognizant321@gmail.com',
        'rechnungspruefung_email': 'incognizant321@gmail.com',
        'currency': 'EUR'
    }
    
    context = {
        'editor_name': 'Test Editor',
        'editor_email': 'incognizant321@gmail.com',
        'completion_date': '15.01.2025 um 10:30',
        'timestamp': '2025-01-15T10:30:00',
        'request_id': 'test-req-123',
        **complete_invoice_data
    }
    
    print("🧪 Testing field coverage in both templates...")
    
    # Test completion template
    completion_context = {**context, 'status': 'Bearbeitung abgeschlossen'}
    completion_template = email_service.jinja_env.get_template("editor_notification")
    completion_html = completion_template.render(**completion_context)
    
    # Test summary template
    summary_context = {**context, 'status': 'In Bearbeitung'}
    summary_template = email_service.jinja_env.get_template("editor_summary")
    summary_html = summary_template.render(**summary_context)
    
    # Check key fields
    key_fields = [
        'rechnungsnummer', 'rechnungsempfaenger', 'rechnungssteller', 
        'projekt', 'gewerk', 'kostenstelle', 'bestellnummer',
        'total_amount', 'skonto_datum', 'skonto_prozent',
        'kfw_anrechenbare_kosten', 'material_kosten', 'lohn_kosten',
        'liefertermin', 'aufmass_datum', 'mwst_satz', 'bemerkungen'
    ]
    
    print("\n📋 Field Coverage Analysis:")
    
    completion_missing = []
    summary_missing = []
    
    for field in key_fields:
        field_value = complete_invoice_data.get(field, '')
        if field_value and field_value not in completion_html:
            completion_missing.append(field)
        if field_value and field_value not in summary_html:
            summary_missing.append(field)
    
    if completion_missing:
        print(f"❌ Completion template missing fields: {completion_missing}")
    else:
        print("✅ Completion template shows all key fields")
    
    if summary_missing:
        print(f"❌ Summary template missing fields: {summary_missing}")
    else:
        print("✅ Summary template shows all key fields")
    
    # Check template sizes
    print(f"\n📏 Template Sizes:")
    print(f"   Completion: {len(completion_html)} characters")
    print(f"   Summary: {len(summary_html)} characters")
    
    # Check for key differences
    print(f"\n🔍 Key Differences:")
    if 'erfolgreich abgeschlossen' in completion_html:
        print("✅ Completion template has completion message")
    if 'Zusammenfassung bisher' in summary_html:
        print("✅ Summary template has summary message")
    if 'Noch nicht eingegeben' in summary_html:
        print("✅ Summary template shows empty field handling")
    
    print(f"\n🎉 Field coverage test completed!")

if __name__ == '__main__':
    test_field_coverage()
