#!/usr/bin/env python3
"""
Quick test to verify email templates are different for completion vs summary.
"""

import asyncio
import sys
import os
import tempfile

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import EmailService

# Test data
invoice_data = {
    'id': 'test-123',
    'rechnungsnummer': 'TEST-001',
    'lieferant': 'Test Supplier',
    'rechnungsbetrag': '1000.00',
    'projekt': 'Test Project',
    'gewerk': 'Elektro'
}

async def test_template_differences():
    email_service = EmailService()
    
    print('🧪 Testing template content differences...')
    
    # Test completion template
    completion_context = {
        'editor_name': 'Test Editor',
        'editor_email': 'incognizant321@gmail.com',
        'completion_date': '15.01.2025 um 10:30',
        'timestamp': '2025-01-15T10:30:00',
        'invoice_number': 'TEST-001',
        'supplier_name': 'Test Supplier',
        'total_amount': '1000.00',
        'status': 'Bearbeitung abgeschlossen',
        **invoice_data
    }
    
    summary_context = {
        **completion_context,
        'status': 'In Bearbeitung'
    }
    
    # Render completion template
    completion_template = email_service.jinja_env.get_template("editor_notification")
    completion_html = completion_template.render(**completion_context)
    
    # Render summary template
    summary_template = email_service.jinja_env.get_template("editor_summary")
    summary_html = summary_template.render(**summary_context)
    
    # Check key differences
    print('📋 Template Analysis:')
    
    if 'erfolgreich abgeschlossen' in completion_html:
        print('✅ Completion template contains "erfolgreich abgeschlossen"')
    else:
        print('❌ Completion template missing "erfolgreich abgeschlossen"')
    
    if 'Zusammenfassung bisher' in summary_html:
        print('✅ Summary template contains "Zusammenfassung bisher"')
    else:
        print('❌ Summary template missing "Zusammenfassung bisher"')
    
    if 'Noch nicht eingegeben' in summary_html:
        print('✅ Summary template shows empty field placeholders')
    else:
        print('❌ Summary template missing empty field placeholders')
    
    # Save to temp files for inspection
    with tempfile.NamedTemporaryFile(mode='w', suffix='_completion.html', delete=False) as f:
        f.write(completion_html)
        completion_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_summary.html', delete=False) as f:
        f.write(summary_html)
        summary_file = f.name
    
    print(f'\n📄 HTML files saved for inspection:')
    print(f'   Completion: {completion_file}')
    print(f'   Summary: {summary_file}')
    
    print('\n🎉 Template test completed!')

if __name__ == '__main__':
    asyncio.run(test_template_differences())
