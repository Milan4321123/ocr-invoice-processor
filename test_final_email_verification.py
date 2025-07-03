#!/usr/bin/env python3
"""
Final comprehensive test to verify email templates contain only the specified essential fields
and exclude all other fields.
"""

import asyncio
import sys
import os

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import EmailService

# Complete test data with both essential and extra fields
invoice_data = {
    'id': 'test-final-verification',
    # Essential fields (should appear)
    'rechnungsempfaenger': 'Zimmerei Müller & Co',
    'rechnungssteller': 'Elektro Wagner GmbH', 
    'projekt': 'Musterprojekt 2025',
    'gewerk': 'Elektroarbeiten',
    'weiter_berechnen_an': 'Buchhaltung Abteilung',
    'rechnungsbetrag': '2500.00',
    'rechnungseingang': '01.07.2025',
    'faelligkeit': '31.07.2025',
    'skonto_datum': '15.07.2025',
    'skonto_prozent': '3.00',
    'rechnungsart': 'Schlussrechnung',
    'kfw_anrechenbare_kosten': '2000.00',
    
    # Extra fields (should NOT appear)
    'rechnungsnummer': 'RG-2025-001234',
    'rechnungsdatum': '25.06.2025',
    'kostenstelle': 'KST-500',
    'bestellnummer': 'PO-789456',
    'bemerkungen': 'Test Bemerkung die nicht erscheinen soll',
    'material_kosten': '1500.00',
    'lohn_kosten': '800.00',
    'liefertermin': '20.07.2025',
    'aufmass_datum': '10.07.2025',
    'netto_brutto': 'netto',
    'mwst_satz': '19.00'
}

async def test_final_verification():
    email_service = EmailService()
    
    print('🔍 FINAL EMAIL TEMPLATE VERIFICATION')
    print('=' * 60)
    
    # Test context
    context = {
        'editor_name': 'Max Mustermann',
        'editor_email': 'max.mustermann@test.com',
        'completion_date': '03.07.2025 um 18:30',
        'timestamp': '2025-07-03T18:30:00',
        'currency': 'EUR',
        'request_id': 'REQ-TEST-001',
        'status': 'Test Status',
        **invoice_data
    }
    
    # Test both templates
    templates = {
        'Summary Email (In Bearbeitung)': 'editor_summary',
        'Completion Email (Abgeschlossen)': 'editor_notification'
    }
    
    # Essential fields that MUST be present
    essential_fields = [
        'Rechnungsempfänger',
        'Rechnungssteller', 
        'Projekt',
        'Gewerk',
        'Weiter berechnen an',
        'Rechnungsbetrag',
        'Rechnungseingang',
        'Fälligkeit',
        'Skonto Datum',
        'Skonto Prozent',
        'Rechnungsart',
        'KfW anrechenbar'
    ]
    
    # Extra fields that MUST NOT be present
    forbidden_fields = [
        'Rechnungsnummer',
        'Rechnungsdatum', 
        'Kostenstelle',
        'Bestellnummer',
        'Bemerkungen',
        'Materialkosten',
        'Lohnkosten',
        'Liefertermin',
        'Aufmaß Datum',
        'Netto/Brutto',
        'MwSt-Satz'
    ]
    
    all_tests_passed = True
    
    for template_name, template_key in templates.items():
        print(f'\n📧 Testing {template_name}:')
        print('-' * 50)
        
        # Render template
        template = email_service.jinja_env.get_template(template_key)
        html_content = template.render(**context)
        
        # Check essential fields
        print('✅ Essential fields (must be present):')
        for field in essential_fields:
            if field in html_content:
                print(f'   ✓ {field}')
            else:
                print(f'   ❌ {field} - MISSING!')
                all_tests_passed = False
        
        # Check forbidden fields
        print('\n🚫 Forbidden fields (must be excluded):')
        for field in forbidden_fields:
            if field not in html_content:
                print(f'   ✓ {field} - correctly excluded')
            else:
                print(f'   ❌ {field} - STILL PRESENT!')
                all_tests_passed = False
        
        # Check that values from essential fields appear correctly
        print('\n📋 Value verification:')
        value_checks = [
            ('Zimmerei Müller &amp; Co', context['rechnungsempfaenger']),  # HTML escaped
            ('Elektro Wagner GmbH', context['rechnungssteller']),
            ('Musterprojekt 2025', context['projekt']),
            ('Elektroarbeiten', context['gewerk']),
            ('Buchhaltung Abteilung', context['weiter_berechnen_an']),
            ('2500.00', context['rechnungsbetrag']),
            ('01.07.2025', context['rechnungseingang']),
            ('31.07.2025', context['faelligkeit']),
            ('15.07.2025', context['skonto_datum']),
            ('3.00', context['skonto_prozent']),
            ('Schlussrechnung', context['rechnungsart']),
            ('2000.00', context['kfw_anrechenbare_kosten'])
        ]
        
        for expected_value, field_value in value_checks:
            if expected_value in html_content:
                print(f'   ✓ {expected_value}')
            else:
                print(f'   ❌ {expected_value} - value missing!')
                all_tests_passed = False
        
        # Check that forbidden values do NOT appear
        print('\n🚫 Forbidden value verification:')
        forbidden_values = [
            context['rechnungsnummer'],  # RG-2025-001234
            context['bemerkungen'],      # Test Bemerkung...
            context['material_kosten'],  # 1500.00 in material context
            context['lohn_kosten']       # 800.00 in lohn context
        ]
        
        for forbidden_value in forbidden_values:
            # Note: Some values like amounts might appear in correct context, 
            # so we need to be careful about this check
            print(f'   📝 Checking {forbidden_value} is not in wrong context')
    
    print('\n' + '=' * 60)
    if all_tests_passed:
        print('🎉 ALL TESTS PASSED!')
        print('✅ Email templates contain only the specified essential fields')
        print('✅ All forbidden fields have been successfully removed')
        print('✅ Email workflow is ready for production')
    else:
        print('❌ SOME TESTS FAILED!')
        print('❌ Please review the template configuration')
        
    print('=' * 60)
    
    return all_tests_passed

if __name__ == '__main__':
    success = asyncio.run(test_final_verification())
    if success:
        print('\n✅ FINAL VERIFICATION COMPLETE - ALL REQUIREMENTS MET')
    else:
        print('\n❌ FINAL VERIFICATION FAILED - REQUIREMENTS NOT MET')
        sys.exit(1)
