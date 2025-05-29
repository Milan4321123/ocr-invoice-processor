"""
Invoice-specific OCR Parser
Specialized parsing logic for invoice documents using Google Document AI
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from ocr.document_ai_service import OCRResult

logger = logging.getLogger(__name__)

@dataclass
class InvoiceData:
    """Structured invoice data extracted from OCR"""
    # Basic invoice information
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    
    # Vendor information
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    vendor_email: Optional[str] = None
    vendor_phone: Optional[str] = None
    
    # Customer information
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_tax_id: Optional[str] = None
    
    # Financial information
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    
    # Line items
    line_items: List[Dict] = None
    
    # Additional fields
    payment_terms: Optional[str] = None
    po_number: Optional[str] = None
    
    # Confidence and metadata
    extraction_confidence: float = 0.0
    raw_text: str = ""
    
    def __post_init__(self):
        if self.line_items is None:
            self.line_items = []

class InvoiceParser:
    """Parser for extracting structured invoice data from OCR results"""
    
    # Common invoice field patterns
    INVOICE_NUMBER_PATTERNS = [
        r'invoice\s*#?\s*:?\s*([A-Za-z0-9\-]+)',
        r'inv\s*#?\s*:?\s*([A-Za-z0-9\-]+)',
        r'number\s*:?\s*([A-Za-z0-9\-]+)',
        r'#\s*([A-Za-z0-9\-]+)',
    ]
    
    DATE_PATTERNS = [
        r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'(\d{2,4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})',
        r'(\w+\s+\d{1,2},?\s+\d{2,4})',
        r'(\d{1,2}\s+\w+\s+\d{2,4})',
    ]
    
    AMOUNT_PATTERNS = [
        r'[\$€£¥]\s*([0-9,]+\.?\d{0,2})',
        r'([0-9,]+\.?\d{0,2})\s*[\$€£¥]',
        r'total\s*:?\s*[\$€£¥]?\s*([0-9,]+\.?\d{0,2})',
        r'amount\s*:?\s*[\$€£¥]?\s*([0-9,]+\.?\d{0,2})',
    ]
    
    TAX_PATTERNS = [
        r'tax\s*:?\s*[\$€£¥]?\s*([0-9,]+\.?\d{0,2})',
        r'vat\s*:?\s*[\$€£¥]?\s*([0-9,]+\.?\d{0,2})',
        r'sales\s*tax\s*:?\s*[\$€£¥]?\s*([0-9,]+\.?\d{0,2})',
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_invoice(self, ocr_result: OCRResult) -> InvoiceData:
        """
        Parse OCR result into structured invoice data
        
        Args:
            ocr_result: Result from OCR processing
            
        Returns:
            InvoiceData with extracted invoice information
        """
        invoice_data = InvoiceData()
        invoice_data.raw_text = ocr_result.text
        invoice_data.extraction_confidence = ocr_result.confidence
        
        try:
            # Parse using form fields first (more accurate)
            if ocr_result.form_fields:
                self._parse_from_form_fields(invoice_data, ocr_result.form_fields)
            
            # Parse using entities (Document AI structured extraction)
            if ocr_result.entities:
                self._parse_from_entities(invoice_data, ocr_result.entities)
            
            # Parse using pattern matching on raw text (fallback)
            self._parse_from_text_patterns(invoice_data, ocr_result.text)
            
            # Parse table data for line items
            if ocr_result.tables:
                self._parse_line_items_from_tables(invoice_data, ocr_result.tables)
            
            # Validate and clean extracted data
            self._validate_and_clean_data(invoice_data)
            
            self.logger.info(f"Invoice parsing completed with confidence: {invoice_data.extraction_confidence:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error parsing invoice data: {e}")
            invoice_data.extraction_confidence = 0.0
        
        return invoice_data
    
    def _parse_from_form_fields(self, invoice_data: InvoiceData, form_fields: List[Dict]):
        """Parse invoice data from Document AI form fields"""
        for field in form_fields:
            field_name = field.get('name', '').lower()
            field_value = field.get('value', '').strip()
            
            if not field_value:
                continue
            
            # Map form fields to invoice data
            if 'invoice' in field_name and ('number' in field_name or '#' in field_name):
                invoice_data.invoice_number = field_value
            elif 'date' in field_name and 'invoice' in field_name:
                invoice_data.invoice_date = self._parse_date(field_value)
            elif 'due' in field_name and 'date' in field_name:
                invoice_data.due_date = self._parse_date(field_value)
            elif 'vendor' in field_name or 'supplier' in field_name:
                if 'name' in field_name:
                    invoice_data.vendor_name = field_value
                elif 'address' in field_name:
                    invoice_data.vendor_address = field_value
            elif 'customer' in field_name or 'client' in field_name:
                if 'name' in field_name:
                    invoice_data.customer_name = field_value
                elif 'address' in field_name:
                    invoice_data.customer_address = field_value
            elif 'total' in field_name:
                invoice_data.total_amount = self._parse_amount(field_value)
            elif 'tax' in field_name:
                invoice_data.tax_amount = self._parse_amount(field_value)
            elif 'subtotal' in field_name:
                invoice_data.subtotal = self._parse_amount(field_value)
    
    def _parse_from_entities(self, invoice_data: InvoiceData, entities: List[Dict]):
        """Parse invoice data from Document AI entities"""
        for entity in entities:
            entity_type = entity.get('type', '').lower()
            entity_value = entity.get('value', '').strip()
            normalized_value = entity.get('normalized_value', '').strip()
            
            # Use normalized value if available, otherwise use raw value
            value = normalized_value if normalized_value else entity_value
            
            if not value:
                continue
            
            # Map entity types to invoice fields
            if entity_type in ['invoice_number', 'invoice_id']:
                invoice_data.invoice_number = value
            elif entity_type in ['invoice_date', 'date']:
                invoice_data.invoice_date = self._parse_date(value)
            elif entity_type in ['due_date', 'payment_due_date']:
                invoice_data.due_date = self._parse_date(value)
            elif entity_type in ['supplier_name', 'vendor_name']:
                invoice_data.vendor_name = value
            elif entity_type in ['supplier_address', 'vendor_address']:
                invoice_data.vendor_address = value
            elif entity_type in ['customer_name', 'client_name']:
                invoice_data.customer_name = value
            elif entity_type in ['total_amount', 'grand_total']:
                invoice_data.total_amount = self._parse_amount(value)
            elif entity_type in ['tax_amount', 'vat_amount']:
                invoice_data.tax_amount = self._parse_amount(value)
            elif entity_type in ['subtotal', 'net_amount']:
                invoice_data.subtotal = self._parse_amount(value)
            elif entity_type in ['currency']:
                invoice_data.currency = value
    
    def _parse_from_text_patterns(self, invoice_data: InvoiceData, text: str):
        """Parse invoice data using regex patterns on raw text"""
        text_lower = text.lower()
        
        # Extract invoice number
        if not invoice_data.invoice_number:
            for pattern in self.INVOICE_NUMBER_PATTERNS:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    invoice_data.invoice_number = match.group(1).strip()
                    break
        
        # Extract dates
        if not invoice_data.invoice_date:
            # Look for date near "invoice" or "date"
            date_context_pattern = r'(?:invoice|date)[:\s]*([^\n\r]{0,20}(?:' + '|'.join(self.DATE_PATTERNS) + r')[^\n\r]{0,20})'
            match = re.search(date_context_pattern, text_lower, re.IGNORECASE)
            if match:
                date_text = match.group(1)
                for date_pattern in self.DATE_PATTERNS:
                    date_match = re.search(date_pattern, date_text, re.IGNORECASE)
                    if date_match:
                        invoice_data.invoice_date = self._parse_date(date_match.group(1))
                        break
        
        # Extract amounts
        if not invoice_data.total_amount:
            for pattern in self.AMOUNT_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    invoice_data.total_amount = self._parse_amount(match.group(1))
                    break
        
        # Extract tax amount
        if not invoice_data.tax_amount:
            for pattern in self.TAX_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    invoice_data.tax_amount = self._parse_amount(match.group(1))
                    break
    
    def _parse_line_items_from_tables(self, invoice_data: InvoiceData, tables: List[Dict]):
        """Extract line items from table data"""
        for table in tables:
            headers = table.get('headers', [])
            rows = table.get('rows', [])
            
            if not headers or not rows:
                continue
            
            # Find relevant columns
            header_row = headers[0] if headers else []
            description_col = self._find_column_index(header_row, ['description', 'item', 'product', 'service'])
            quantity_col = self._find_column_index(header_row, ['qty', 'quantity', 'units'])
            price_col = self._find_column_index(header_row, ['price', 'rate', 'unit price', 'cost'])
            amount_col = self._find_column_index(header_row, ['amount', 'total', 'line total'])
            
            # Extract line items
            for row in rows:
                if len(row) > max(description_col or 0, quantity_col or 0, price_col or 0, amount_col or 0):
                    line_item = {}
                    
                    if description_col is not None and description_col < len(row):
                        line_item['description'] = row[description_col].strip()
                    
                    if quantity_col is not None and quantity_col < len(row):
                        line_item['quantity'] = self._parse_number(row[quantity_col])
                    
                    if price_col is not None and price_col < len(row):
                        line_item['unit_price'] = self._parse_amount(row[price_col])
                    
                    if amount_col is not None and amount_col < len(row):
                        line_item['total_amount'] = self._parse_amount(row[amount_col])
                    
                    # Only add if we have meaningful data
                    if line_item.get('description') or line_item.get('total_amount'):
                        invoice_data.line_items.append(line_item)
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index by matching keywords"""
        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            for keyword in keywords:
                if keyword.lower() in header_lower:
                    return i
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string into standardized format"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            date_formats = [
                '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
                '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d',
                '%m.%d.%Y', '%d.%m.%Y', '%Y.%m.%d',
                '%B %d, %Y', '%d %B %Y',
                '%b %d, %Y', '%d %b %Y',
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return the original string
            return date_str.strip()
            
        except Exception as e:
            self.logger.warning(f"Could not parse date '{date_str}': {e}")
            return date_str.strip()
    
    def _parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string into Decimal"""
        if not amount_str:
            return None
        
        try:
            # Clean the amount string
            cleaned = re.sub(r'[^\d.,\-]', '', amount_str.strip())
            
            # Handle different decimal separators
            if ',' in cleaned and '.' in cleaned:
                # Assume comma is thousands separator if it comes before period
                if cleaned.rfind(',') < cleaned.rfind('.'):
                    cleaned = cleaned.replace(',', '')
                else:
                    # Assume period is thousands separator if it comes before comma
                    cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Check if comma is likely decimal separator (two digits after)
                if re.match(r'.*,\d{2}$', cleaned):
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            
            return Decimal(cleaned)
            
        except (InvalidOperation, ValueError) as e:
            self.logger.warning(f"Could not parse amount '{amount_str}': {e}")
            return None
    
    def _parse_number(self, number_str: str) -> Optional[float]:
        """Parse number string into float"""
        if not number_str:
            return None
        
        try:
            # Clean the number string
            cleaned = re.sub(r'[^\d.,\-]', '', number_str.strip())
            
            # Handle decimal separators
            if ',' in cleaned and '.' in cleaned:
                if cleaned.rfind(',') < cleaned.rfind('.'):
                    cleaned = cleaned.replace(',', '')
                else:
                    cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned and re.match(r'.*,\d{1,2}$', cleaned):
                cleaned = cleaned.replace(',', '.')
            
            return float(cleaned)
            
        except ValueError as e:
            self.logger.warning(f"Could not parse number '{number_str}': {e}")
            return None
    
    def _validate_and_clean_data(self, invoice_data: InvoiceData):
        """Validate and clean extracted invoice data"""
        # Clean text fields
        if invoice_data.vendor_name:
            invoice_data.vendor_name = invoice_data.vendor_name.strip()
        if invoice_data.customer_name:
            invoice_data.customer_name = invoice_data.customer_name.strip()
        if invoice_data.invoice_number:
            invoice_data.invoice_number = invoice_data.invoice_number.strip()
        
        # Validate amounts
        if invoice_data.subtotal and invoice_data.tax_amount and not invoice_data.total_amount:
            invoice_data.total_amount = invoice_data.subtotal + invoice_data.tax_amount
        
        # Detect currency if not found
        if not invoice_data.currency and invoice_data.raw_text:
            currency_symbols = {
                '$': 'USD',
                '€': 'EUR', 
                '£': 'GBP',
                '¥': 'JPY',
                '₹': 'INR'
            }
            
            for symbol, currency in currency_symbols.items():
                if symbol in invoice_data.raw_text:
                    invoice_data.currency = currency
                    break

# Global invoice parser instance
invoice_parser = InvoiceParser()
