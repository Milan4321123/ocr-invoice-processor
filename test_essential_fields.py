#!/usr/bin/env python3
"""
Test to verify email templates show only essential fields.
"""

import asyncio
import sys
import os

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import EmailService

# Test data
invoice_data = {
    'id': 'test-123',
    'rechnungsempfaenger': 'Zimmerei Müller & Co',
    'rechnungssteller': 'Elektro Wagner GmbH', 
    'projekt': 'Test Project',
    'gewerk': 'Elektro',
    'weiter_berechnen_an': 'Buchhaltung',
    'rechnungsbetrag': '1500.00',
    'rechnungseingang': '15.01.2025',
    'faelligkeit': '15.02.2025',
    'skonto_datum': '25.01.2025',
    'skonto_prozent': '2.00',
    'rechnungsart': 'Rechnung',
    'kfw_anrechenbare_kosten': '1200.00'
}

async def test_essential_fields():
    email_service = EmailService()
    
    print('🧪 Testing essential fields in email templates...')
    
    # Test context
    context = {
        'editor_name': 'Test Editor',
        'editor_email': 'incognizant321@gmail.com',
        'completion_date': '15.01.2025 um 10:30',
        'timestamp': '2025-01-15T10:30:00',
        'currency': 'EUR',
        **invoice_data
    }
    
    # Test completion template
    completion_template = email_service.jinja_env.get_template("editor_notification")
    completion_html = completion_template.render(**context)
    
    # Test summary template  
    summary_template = email_service.jinja_env.get_template("editor_summary")
    summary_html = summary_template.render(**context)
    
    # Check essential fields are present
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
    
    print('📋 Completion Template Field Check:')
    for field in essential_fields:
        if field in completion_html:
            print(f'✅ {field}')
        else:
            print(f'❌ {field} - MISSING!')
    
    print('\n📋 Summary Template Field Check:')
    for field in essential_fields:
        if field in summary_html:
            print(f'✅ {field}')
        else:
            print(f'❌ {field} - MISSING!')
    
    # Check that extra fields are NOT present
    extra_fields = [
        'Rechnungsnummer',
        'Rechnungsdatum', 
        'Kostenstelle',
        'Bestellnummer',
        'Bemerkungen',
        'Materialkosten',
        'Lohnkosten'
    ]
    
    print('\n📋 Checking extra fields are excluded:')
    for field in extra_fields:
        if field not in completion_html and field not in summary_html:
            print(f'✅ {field} - correctly excluded')
        else:
            print(f'⚠️ {field} - still present in templates')
    
    print('\n🎉 Essential fields test completed!')

if __name__ == '__main__':
    asyncio.run(test_essential_fields())
