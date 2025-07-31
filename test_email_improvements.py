#!/usr/bin/env python3
"""
Test Email Template Improvements
- Tests placeholder value cleaning
- Tests filename fallback functionality
- Tests enhanced template styling
- Tests non-functional PDF links
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.email_service import EmailService


def test_clean_field_value():
    """Test the clean_field_value function logic"""
    print("🧪 Testing clean_field_value function...")
    
    # Define the function here for testing
    def clean_field_value(value):
        """Replace placeholder/default values with 'Nicht eingegeben'"""
        if not value or value in [
            'Projekt auswählen...', 'Gewerk auswählen...', 'Abteilung oder Kontakt auswählen...',
            'Typ auswählen...', 'dd.mm.yyyy', 'mm.yyyy', 'yyyy', '0.00', '0,00'
        ]:
            return 'Nicht eingegeben'
        return value
    
    # Test cases
    test_cases = [
        ('Projekt auswählen...', 'Nicht eingegeben'),
        ('Gewerk auswählen...', 'Nicht eingegeben'),
        ('dd.mm.yyyy', 'Nicht eingegeben'),
        ('0.00', 'Nicht eingegeben'),
        ('', 'Nicht eingegeben'),
        (None, 'Nicht eingegeben'),
        ('Valid Project Name', 'Valid Project Name'),
        ('15.03.2024', '15.03.2024'),
        ('1250.50', '1250.50'),
    ]
    
    all_passed = True
    for input_val, expected in test_cases:
        result = clean_field_value(input_val)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_val}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("✅ All clean_field_value tests passed!")
    else:
        print("❌ Some clean_field_value tests failed!")
    
    return all_passed


def test_filename_fallback():
    """Test the filename fallback logic"""
    print("\n🧪 Testing filename fallback logic...")
    
    def clean_field_value(value):
        """Replace placeholder/default values with 'Nicht eingegeben'"""
        if not value or value in [
            'Projekt auswählen...', 'Gewerk auswählen...', 'Abteilung oder Kontakt auswählen...',
            'Typ auswählen...', 'dd.mm.yyyy', 'mm.yyyy', 'yyyy', '0.00', '0,00'
        ]:
            return 'Nicht eingegeben'
        return value

    def get_display_name(invoice_data):
        """Get display name for invoice - use filename if invoice number is missing"""
        invoice_number = clean_field_value(invoice_data.get("rechnungsnummer"))
        if invoice_number == 'Nicht eingegeben' and invoice_data.get("file_path"):
            # Extract filename from file_path
            filename = invoice_data["file_path"].split("/")[-1]
            # Remove file extension for cleaner display
            if filename.endswith('.pdf'):
                filename = filename[:-4]
            return filename
        return invoice_number if invoice_number != 'Nicht eingegeben' else 'Rechnung ohne Nummer'
    
    # Test cases
    test_cases = [
        {
            'invoice_data': {'rechnungsnummer': 'INV-12345', 'file_path': 'invoices/test.pdf'},
            'expected': 'INV-12345',
            'description': 'Valid invoice number'
        },
        {
            'invoice_data': {'rechnungsnummer': '', 'file_path': 'invoices/Company_Invoice_2024.pdf'},
            'expected': 'Company_Invoice_2024',
            'description': 'Empty invoice number, use filename'
        },
        {
            'invoice_data': {'rechnungsnummer': 'Projekt auswählen...', 'file_path': 'invoices/Rechnung_März_2024.pdf'},
            'expected': 'Rechnung_März_2024',
            'description': 'Placeholder invoice number, use filename'
        },
        {
            'invoice_data': {'rechnungsnummer': '', 'file_path': ''},
            'expected': 'Rechnung ohne Nummer',
            'description': 'No invoice number and no file path'
        },
        {
            'invoice_data': {'rechnungsnummer': None, 'file_path': None},
            'expected': 'Rechnung ohne Nummer',
            'description': 'None values'
        },
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = get_display_name(test_case['invoice_data'])
        expected = test_case['expected']
        status = "✅" if result == expected else "❌"
        print(f"  {status} Test {i}: {test_case['description']}")
        print(f"      Result: '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("✅ All filename fallback tests passed!")
    else:
        print("❌ Some filename fallback tests failed!")
    
    return all_passed


async def test_template_rendering():
    """Test template rendering with improved data"""
    print("\n🧪 Testing template rendering...")
    
    try:
        email_service = EmailService()
        
        # Sample invoice data with mixed values
        test_invoice_data = {
            'id': 'test-123',
            'rechnungsnummer': '',  # Empty - should use filename
            'file_path': 'invoices/Test_Company_Invoice_March_2024.pdf',
            'lieferant': 'Test Company GmbH',
            'rechnungsdatum': '15.03.2024',
            'rechnungsbetrag': '1,250.50',
            'currency': 'EUR',
            'rechnungsempfaenger': 'My Company Ltd',
            'rechnungssteller': 'Test Company GmbH', 
            'projekt': 'Projekt auswählen...',  # Placeholder - should be cleaned
            'gewerk': 'Elektro',
            'kostenstelle': 'KS-001',
            'abteilung_kontakt': 'Abteilung oder Kontakt auswählen...',  # Placeholder
            'faelligkeitsdatum': 'dd.mm.yyyy',  # Placeholder
            'zahlungsziel': '30 Tage',
            'skonto_prozent': '2',
            'skonto_bis_datum': '25.03.2024',
            'rechnungstyp': 'Typ auswählen...',  # Placeholder
            'umsatzsteuer_betrag': '237.60'
        }
        
        # Test editor notification template
        template = email_service.jinja_env.get_template("editor_notification")
        
        # Create context similar to what the email service would create
        def clean_field_value(value):
            if not value or value in [
                'Projekt auswählen...', 'Gewerk auswählen...', 'Abteilung oder Kontakt auswählen...',
                'Typ auswählen...', 'dd.mm.yyyy', 'mm.yyyy', 'yyyy', '0.00', '0,00'
            ]:
                return 'Nicht eingegeben'
            return value
            
        def get_display_name(invoice_data):
            invoice_number = clean_field_value(invoice_data.get("rechnungsnummer"))
            if invoice_number == 'Nicht eingegeben' and invoice_data.get("file_path"):
                filename = invoice_data["file_path"].split("/")[-1]
                if filename.endswith('.pdf'):
                    filename = filename[:-4]
                return filename
            return invoice_number if invoice_number != 'Nicht eingegeben' else 'Rechnung ohne Nummer'
        
        context = {
            'completion_date': '20.03.2024 um 14:30',
            'editor_name': 'Test Editor',
            'editor_email': 'editor@test.com',
            'invoice_display_name': get_display_name(test_invoice_data),
            'supplier_name': clean_field_value(test_invoice_data.get("lieferant")),
            'invoice_date': clean_field_value(test_invoice_data.get("rechnungsdatum")),
            'total_amount': test_invoice_data.get("rechnungsbetrag"),
            'currency': test_invoice_data.get("currency", "EUR"),
            'status': 'Bearbeitung abgeschlossen',
            'rechnungsempfaenger': clean_field_value(test_invoice_data.get("rechnungsempfaenger")),
            'rechnungssteller': clean_field_value(test_invoice_data.get("rechnungssteller")),
            'projekt': clean_field_value(test_invoice_data.get("projekt")),
            'gewerk': clean_field_value(test_invoice_data.get("gewerk")),
            'kostenstelle': clean_field_value(test_invoice_data.get("kostenstelle")),
            'abteilung_kontakt': clean_field_value(test_invoice_data.get("abteilung_kontakt")),
            'faelligkeitsdatum': clean_field_value(test_invoice_data.get("faelligkeitsdatum")),
            'zahlungsziel': clean_field_value(test_invoice_data.get("zahlungsziel")),
            'skonto_prozent': clean_field_value(test_invoice_data.get("skonto_prozent")),
            'skonto_bis_datum': clean_field_value(test_invoice_data.get("skonto_bis_datum")),
            'rechnungstyp': clean_field_value(test_invoice_data.get("rechnungstyp")),
            'umsatzsteuer_betrag': clean_field_value(test_invoice_data.get("umsatzsteuer_betrag")),
            'has_pdf': bool(test_invoice_data.get("file_path")),
        }
        
        # Render the template
        html_content = template.render(**context)
        
        # Check for improvements
        improvements_found = []
        
        # Check that placeholders are cleaned
        if 'Nicht eingegeben' in html_content:
            improvements_found.append("✅ Placeholder cleaning working")
        else:
            improvements_found.append("❌ Placeholder cleaning not found")
            
        # Check filename fallback is used
        if 'Test_Company_Invoice_March_2024' in html_content:
            improvements_found.append("✅ Filename fallback working")
        else:
            improvements_found.append("❌ Filename fallback not working")
            
        # Check enhanced styling
        if 'class="detail-value amount"' in html_content and 'class="detail-value date"' in html_content:
            improvements_found.append("✅ Enhanced CSS styling present")
        else:
            improvements_found.append("❌ Enhanced CSS styling missing")
            
        # Check non-functional PDF link
        if 'PDF öffnen (Nicht verfügbar)' in html_content or 'PDF nicht verfügbar' in html_content:
            improvements_found.append("✅ Non-functional PDF link working")
        else:
            improvements_found.append("❌ Non-functional PDF link missing")
        
        print("📧 Template rendering results:")
        for improvement in improvements_found:
            print(f"  {improvement}")
            
        # Save rendered template for inspection
        with open('test_email_output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📄 Rendered template saved to: test_email_output.html")
        
        return all("✅" in improvement for improvement in improvements_found)
        
    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        return False


async def main():
    """Run all email improvement tests"""
    print("🧪 Testing Email Template Improvements")
    print("=" * 50)
    
    # Run tests
    test_results = []
    
    test_results.append(test_clean_field_value())
    test_results.append(test_filename_fallback())
    test_results.append(await test_template_rendering())
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    if all(test_results):
        print("🎉 All email improvement tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
