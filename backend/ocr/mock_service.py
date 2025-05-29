"""
Mock OCR Service for Testing
Provides realistic mock data when Google Cloud billing is disabled
"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MockOCRService:
    """Mock OCR service that returns realistic test data"""
    
    def __init__(self):
        self.mock_vendors = [
            "ACME Corporation", "Tech Solutions Inc", "Global Services Ltd",
            "Metro Supplies", "Digital Systems", "Premier Solutions"
        ]
        
        self.mock_addresses = [
            "123 Business St, New York, NY 10001",
            "456 Corporate Ave, Los Angeles, CA 90210",
            "789 Commerce Blvd, Chicago, IL 60601",
            "321 Enterprise Dr, Houston, TX 77001"
        ]

    def generate_mock_invoice_data(self, filename: str) -> Dict[str, Any]:
        """Generate realistic mock invoice data"""
        
        # Simulate processing time
        processing_start = time.time()
        time.sleep(0.2)  # Simulate processing delay
        processing_time = time.time() - processing_start
        
        # Extract some data from filename if possible
        vendor_name = "Mock Vendor"
        invoice_number = "INV-2025-001"
        
        try:
            # Try to extract from filename pattern: YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf
            parts = filename.replace('.pdf', '').split('_')
            if len(parts) >= 3:
                invoice_number = parts[1]
                vendor_name = parts[2].replace('-', ' ').title()
        except:
            pass
        
        # Generate random but realistic data
        subtotal = round(random.uniform(100, 5000), 2)
        tax_rate = random.choice([0.0, 0.08, 0.10, 0.12])
        tax_amount = round(subtotal * tax_rate, 2)
        total_amount = subtotal + tax_amount
        
        # Generate dates
        invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
        due_date = invoice_date + timedelta(days=random.randint(15, 60))
        
        # Generate line items
        line_items = []
        num_items = random.randint(1, 5)
        remaining_subtotal = subtotal
        
        for i in range(num_items):
            if i == num_items - 1:
                # Last item gets remaining amount
                item_total = remaining_subtotal
            else:
                item_total = round(remaining_subtotal * random.uniform(0.1, 0.6), 2)
                remaining_subtotal -= item_total
            
            quantity = random.randint(1, 10)
            unit_price = round(item_total / quantity, 2)
            
            line_items.append({
                "description": f"Service Item {i+1}",
                "quantity": quantity,
                "unit_price": unit_price,
                "total": item_total
            })
        
        mock_data = {
            "success": True,
            "confidence": round(random.uniform(0.85, 0.98), 2),
            "pages": 1,
            "processing_time": processing_time,
            "text": f"INVOICE\n\n{vendor_name}\n{random.choice(self.mock_addresses)}\n\nInvoice Number: {invoice_number}\nDate: {invoice_date.strftime('%Y-%m-%d')}\nDue Date: {due_date.strftime('%Y-%m-%d')}\n\nSubtotal: ${subtotal:.2f}\nTax: ${tax_amount:.2f}\nTotal: ${total_amount:.2f}",
            "structured_data_available": True,
            "entities": [
                {
                    "type": "invoice_number",
                    "mention_text": invoice_number,
                    "confidence": 0.95
                },
                {
                    "type": "vendor_name", 
                    "mention_text": vendor_name,
                    "confidence": 0.92
                },
                {
                    "type": "total_amount",
                    "mention_text": f"${total_amount:.2f}",
                    "confidence": 0.98
                }
            ],
            "form_fields": [
                {
                    "field_name": "invoice_number",
                    "field_value": invoice_number,
                    "confidence": 0.95
                },
                {
                    "field_name": "invoice_date",
                    "field_value": invoice_date.strftime('%Y-%m-%d'),
                    "confidence": 0.90
                },
                {
                    "field_name": "total_amount",
                    "field_value": str(total_amount),
                    "confidence": 0.98
                }
            ],
            "tables": [
                {
                    "header_rows": [["Description", "Quantity", "Unit Price", "Total"]],
                    "body_rows": [[item["description"], str(item["quantity"]), f"${item['unit_price']:.2f}", f"${item['total']:.2f}"] for item in line_items]
                }
            ],
            "structured_data": {
                "invoice_number": invoice_number,
                "invoice_date": invoice_date.strftime('%Y-%m-%d'),
                "due_date": due_date.strftime('%Y-%m-%d'),
                "vendor_name": vendor_name,
                "vendor_address": random.choice(self.mock_addresses),
                "customer_name": "Customer Company Inc",
                "customer_address": "999 Client Street, Business City, BC 12345",
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "currency": "USD",
                "payment_terms": random.choice(["Net 30", "Net 15", "Due on Receipt", "Net 60"]),
                "po_number": f"PO-{random.randint(1000, 9999)}",
                "line_items": line_items
            }
        }
        
        logger.info(f"Generated mock OCR data for {filename}")
        return mock_data

    def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process document with mock OCR"""
        try:
            logger.info(f"Processing document with mock OCR: {filename}")
            return self.generate_mock_invoice_data(filename)
        except Exception as e:
            logger.error(f"Mock OCR processing failed: {e}")
            return {
                "success": False,
                "confidence": 0.0,
                "pages": 0,
                "processing_time": 0.1,
                "error": f"Mock OCR processing failed: {str(e)}",
                "structured_data_available": False
            }

# Global mock OCR service instance
mock_ocr_service = MockOCRService()
