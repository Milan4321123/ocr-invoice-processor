#!/usr/bin/env python3
"""
Debug test to check template rendering
"""

import asyncio
import sys
import os

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.email_service import EmailService

async def debug_template():
    email_service = EmailService()
    
    # Test context
    context = {
        'rechnungsempfaenger': 'Zimmerei Müller & Co',
        'rechnungssteller': 'Elektro Wagner GmbH',
        'editor_name': 'Test Editor',
        'completion_date': '03.07.2025',
        'timestamp': '2025-07-03T18:30:00'
    }
    
    # Test editor_summary template
    template = email_service.jinja_env.get_template("editor_summary")
    html_content = template.render(**context)
    
    print('🔍 Checking if rechnungsempfaenger value appears:')
    print(f"Looking for: 'Zimmerei Müller & Co'")
    print(f"Found: {'Zimmerei Müller & Co' in html_content}")
    
    if 'Zimmerei Müller & Co' in html_content:
        print('✅ Value found in template')
    else:
        print('❌ Value NOT found in template')
        # Let's check what's actually rendered for rechnungsempfaenger
        lines = html_content.split('\n')
        for i, line in enumerate(lines):
            if 'Rechnungsempfänger' in line:
                print(f'Found line {i}: {line.strip()}')
                if i + 1 < len(lines):
                    print(f'Next line {i+1}: {lines[i+1].strip()}')
                if i + 2 < len(lines):
                    print(f'Next line {i+2}: {lines[i+2].strip()}')

if __name__ == '__main__':
    asyncio.run(debug_template())
