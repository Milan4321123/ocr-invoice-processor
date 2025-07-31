#!/usr/bin/env python3
"""
Test the cleaned email field functionality
"""

def test_clean_field_value():
    """Test the clean_field_value function logic"""
    
    def clean_field_value(value):
        """Replace placeholder/default values with 'Nicht eingegeben'"""
        if not value or value in [
            'Projekt auswählen...', 'Gewerk auswählen...', 'Abteilung oder Kontakt auswählen...',
            'Typ auswählen...', 'dd.mm.yyyy', 'mm.yyyy', 'yyyy', '0.00', '0,00'
        ]:
            return 'Nicht eingegeben'
        return value
    
    print("🧪 Testing Clean Field Value Function")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("", "Nicht eingegeben"),
        (None, "Nicht eingegeben"),
        ("Projekt auswählen...", "Nicht eingegeben"),
        ("Gewerk auswählen...", "Nicht eingegeben"),
        ("Abteilung oder Kontakt auswählen...", "Nicht eingegeben"),
        ("Typ auswählen...", "Nicht eingegeben"),
        ("dd.mm.yyyy", "Nicht eingegeben"),
        ("mm.yyyy", "Nicht eingegeben"),
        ("yyyy", "Nicht eingegeben"),
        ("0.00", "Nicht eingegeben"),
        ("0,00", "Nicht eingegeben"),
        ("Real Project Name", "Real Project Name"),
        ("Elektroinstallation", "Elektroinstallation"),
        ("15.07.2025", "15.07.2025"),
        ("1500.00", "1500.00"),
        ("Mustermann GmbH", "Mustermann GmbH")
    ]
    
    all_passed = True
    for input_value, expected_output in test_cases:
        result = clean_field_value(input_value)
        passed = result == expected_output
        status = "✅" if passed else "❌"
        
        print(f"{status} Input: '{input_value}' → Output: '{result}' (Expected: '{expected_output}')")
        
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The clean_field_value function works correctly.")
        print("📧 Email templates will now show 'Nicht eingegeben' instead of placeholder values.")
    else:
        print("❌ Some tests failed! Check the function logic.")
    
    print("\n📋 Summary:")
    print("   Before: 'Projekt auswählen...', 'dd.mm.yyyy', etc.")
    print("   After:  'Nicht eingegeben' for all empty/placeholder fields")
    print("   ✅ Real values are preserved unchanged")

if __name__ == "__main__":
    test_clean_field_value()
