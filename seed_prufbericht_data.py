#!/usr/bin/env python3
"""
Seed the database with realistic test data for Prüfbericht testing
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime, timedelta
from services.database import db_service
import uuid

# Sample invoices with realistic data
sample_invoices = [
    {
        "rechnungssteller": "Bauunternehmen Schmidt GmbH",
        "rechnungsempfaenger": "Bauprojekt Alpha AG",
        "projekt": "Neubau Bürogebäude München",
        "gewerk": "Rohbau",
        "rechnungsbetrag": 45000.00,
        "faelligkeit": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),  # Due soon
        "rechnungseingang": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "rechnungsart": "Teilrechnung",
        "status": "pending",
        "ocr_status": "completed",
        "file_name": "20241201_SCHMIDT_BAUUNTERNEHMEN_RECHNUNG.pdf",
        "file_path": "test_invoices/20241201_SCHMIDT_BAUUNTERNEHMEN_RECHNUNG.pdf",
        "kfw_anrechenbare_kosten": True
    },
    {
        "rechnungssteller": "Elektro Wagner",
        "rechnungsempfaenger": "Bauprojekt Alpha AG", 
        "projekt": "Neubau Bürogebäude München",
        "gewerk": "Elektroinstallation",
        "rechnungsbetrag": 12500.75,
        "faelligkeit": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),  # Due in 2 weeks
        "rechnungseingang": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "rechnungsart": "Schlussrechnung",
        "status": "pending",
        "ocr_status": "completed",
        "file_name": "20241202_WAGNER_ELEKTRO_RECHNUNG.pdf",
        "file_path": "test_invoices/20241202_WAGNER_ELEKTRO_RECHNUNG.pdf",
        "kfw_anrechenbare_kosten": False
    },
    {
        "rechnungssteller": "Bauunternehmen Schmidt GmbH",
        "rechnungsempfaenger": "Bauprojekt Beta GmbH",
        "projekt": "Sanierung Altbau Hamburg", 
        "gewerk": "Dacharbeiten",
        "rechnungsbetrag": 28900.50,
        "faelligkeit": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),  # Overdue
        "rechnungseingang": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "rechnungsart": "Abschlagsrechnung",
        "status": "pending",
        "ocr_status": "completed", 
        "file_name": "20241120_SCHMIDT_DACHARBEITEN_RECHNUNG.pdf",
        "file_path": "test_invoices/20241120_SCHMIDT_DACHARBEITEN_RECHNUNG.pdf",
        "kfw_anrechenbare_kosten": True
    },
    {
        "rechnungssteller": "Heizung & Sanitär Müller",
        "rechnungsempfaenger": "Bauprojekt Beta GmbH",
        "projekt": "Sanierung Altbau Hamburg",
        "gewerk": "Sanitär", 
        "rechnungsbetrag": 8750.00,
        "faelligkeit": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),  # Future
        "rechnungseingang": datetime.now().strftime("%Y-%m-%d"),
        "rechnungsart": "Teilrechnung",
        "status": "approved",
        "ocr_status": "completed",
        "file_name": "20241205_MUELLER_SANITAER_RECHNUNG.pdf", 
        "file_path": "test_invoices/20241205_MUELLER_SANITAER_RECHNUNG.pdf",
        "kfw_anrechenbare_kosten": False
    },
    {
        "rechnungssteller": "Malerbetrieb Weiss",
        "rechnungsempfaenger": "Bauprojekt Gamma Ltd.",
        "projekt": "Renovierung Hotel Berlin",
        "gewerk": "Malerarbeiten",
        "rechnungsbetrag": 15200.25,
        "faelligkeit": None,  # Missing due date
        "rechnungseingang": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "rechnungsart": "Schlussrechnung",
        "status": "pending",
        "ocr_status": "failed",  # OCR failed
        "file_name": "20241130_WEISS_MALER_RECHNUNG.pdf",
        "file_path": "test_invoices/20241130_WEISS_MALER_RECHNUNG.pdf",
        "kfw_anrechenbare_kosten": True
    }
]

def create_sample_invoices():
    """Create sample invoices via database service"""
    print("Creating sample invoices for Prüfbericht testing...")
    
    if not db_service.is_available:
        print("❌ Database service not available")
        return
    
    for i, invoice_data in enumerate(sample_invoices):
        try:
            # Add some mock OCR data
            mock_ocr_data = {
                "error": None,
                "pages": 1,
                "success": True,
                "confidence": 0.85 if invoice_data["ocr_status"] == "completed" else 0.0,
                "processing_time": 1.5,
                "structured_data": {
                    "vendor_name": invoice_data["rechnungssteller"],
                    "total_amount": invoice_data["rechnungsbetrag"],
                    "due_date": invoice_data["faelligkeit"],
                    "invoice_date": invoice_data["rechnungseingang"],
                    "extraction_confidence": 0.85 if invoice_data["ocr_status"] == "completed" else 0.0
                }
            }
            
            invoice_data["raw_ocr_data"] = mock_ocr_data
            invoice_data["file_size"] = 125000 + (i * 10000)  # Vary file sizes
            invoice_data["mime_type"] = "application/pdf"
            
            # Don't set created_at manually, let the database handle it
            
            # Create invoice via database service
            result = db_service.create_invoice(invoice_data)
            
            if result.get("success"):
                print(f"✅ Created invoice: {invoice_data['rechnungssteller']} - {invoice_data['projekt']}")
            else:
                print(f"❌ Failed to create invoice: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error creating invoice: {e}")

if __name__ == "__main__":
    create_sample_invoices()
    print("\n✅ Sample data creation complete!")
    
    # Show summary
    invoices_result = db_service.get_all_invoices(limit=20)
    if invoices_result.get("success"):
        print(f"📊 Total invoices in database: {len(invoices_result['data'])}")
    else:
        print("❌ Could not retrieve invoice summary")
