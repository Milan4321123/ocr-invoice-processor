#!/usr/bin/env python3
"""
Test script to demonstrate the FIXED filename pattern validation:
EINGANGSDATUM_PROJEKT_GEWERK_LIEFERANT.pdf

This shows that the filename must follow this exact structure with exactly 4 parts.
"""

import asyncio
import sys
import os

# Add the backend path to import our upload service
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.upload_service import UploadService, FileData, UploadSource

def create_test_pdf_content(size_bytes=1000):
    """Create mock PDF content for testing"""
    pdf_header = b"%PDF-1.4\n"
    pdf_content = b"Mock PDF content for testing\n"
    padding = b"0" * (size_bytes - len(pdf_header) - len(pdf_content) - 10)
    pdf_footer = b"\n%%EOF"
    return pdf_header + pdf_content + padding + pdf_footer

async def test_fixed_pattern():
    """Test the fixed EINGANGSDATUM_PROJEKT_GEWERK_LIEFERANT pattern"""
    upload_service = UploadService()
    
    print("🔒 FIXED Pattern Test: EINGANGSDATUM_PROJEKT_GEWERK_LIEFERANT.pdf")
    print("=" * 70)
    print()
    
    # Test cases following the FIXED pattern
    test_cases = [
        # ✅ Valid cases (exactly 4 parts)
        ("✅ Valid: Business case", "20250627_BauProjekt_Elektrik_Müller-GmbH.pdf"),
        ("✅ Valid: With periods", "20250627_Neubau.Office_Heizung_Schmidt.Co.pdf"),
        ("✅ Valid: German chars", "20250627_Bürogebäude_Sanitär_Möller-Bäder.pdf"),
        ("✅ Valid: With hyphens", "20250627_Projekt-A1_Test-Gewerk_Supplier-Name.pdf"),
        
        # ❌ Invalid cases 
        ("❌ Invalid: Only 3 parts", "20250627_NurDrei_Teile.pdf"),
        ("❌ Invalid: 5 parts", "20250627_Zu_Viele_Teile_Hier_Extra.pdf"),
        ("❌ Invalid: Wrong date", "InvalidDate_Projekt_Gewerk_Lieferant.pdf"),
        ("❌ Invalid: No extension", "20250627_Projekt_Gewerk_Lieferant"),
        ("❌ Invalid: Wrong extension", "20250627_Projekt_Gewerk_Lieferant.doc"),
        ("❌ Invalid: Underscore in part", "20250627_Pro_jekt_Gewerk_Lieferant.pdf"),
    ]
    
    for description, filename in test_cases:
        file_data = FileData(
            content=create_test_pdf_content(1000),
            filename=filename,
            content_type="application/pdf",
            file_size=1000,
            source=UploadSource.DRAG_DROP
        )
        
        # Test validation
        is_valid, error_message = upload_service.validate_file(file_data)
        
        print(f"{description}")
        print(f"  File: {filename}")
        print(f"  Valid: {is_valid}")
        if not is_valid:
            print(f"  Error: {error_message}")
        print()

if __name__ == "__main__":
    asyncio.run(test_fixed_pattern())
