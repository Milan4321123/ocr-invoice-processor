"""
Single Source of Truth for Field Mappings
==========================================

This module defines all field mappings for the invoice system based on the 
invoices_clean table schema. This eliminates scattered mappings across the codebase.

Database Schema (invoices_clean):
- German business field names (rechnungsempfaenger, rechnungssteller, etc.)
- Direct mapping to business requirements
- No legacy field support needed
"""

from typing import Dict, Set, Any

# ========================================
# CORE FIELD DEFINITIONS
# ========================================

# Fields that exist in the invoices_clean table
DATABASE_FIELDS: Set[str] = {
    # Core file fields
    'id', 'file_name', 'file_path', 'file_size', 'mime_type',
    
    # German business fields (primary)
    'rechnungsempfaenger',      # Customer/recipient
    'rechnungssteller',         # Vendor/supplier  
    'projekt',                  # Project
    'gewerk',                   # Trade category
    'weiter_berechnen_an',      # Bill to
    'rechnungsbetrag',          # Invoice amount
    'kfw_anrechenbare_kosten',  # KfW eligible costs
    'rechnungseingang',         # Invoice receipt date
    'faelligkeit',              # Due date
    'skonto_datum',             # Early payment date
    'skonto_prozent',           # Early payment discount
    'rechnungsart',             # Invoice type
    'rechnungspruefung',        # Invoice verification
    
    # System fields
    'status', 'ocr_status', 'ocr_text', 'raw_ocr_data',
    'created_at', 'updated_at',
    
    # Review workflow fields
    'review_status', 'reviewed_by', 'reviewed_at', 'review_notes'
}

# ========================================
# INPUT SOURCE MAPPINGS
# ========================================

# Map OCR/API input field names to database field names
OCR_TO_DATABASE: Dict[str, str] = {
    # OCR commonly returns these English field names
    'customer_name': 'rechnungsempfaenger',
    'vendor_name': 'rechnungssteller',
    'supplier_name': 'rechnungssteller',
    'receiver_name': 'rechnungsempfaenger',
    'total_amount': 'rechnungsbetrag',
    'gross_amount': 'rechnungsbetrag',
    'invoice_date': 'rechnungseingang',
    'due_date': 'faelligkeit',
    'po_number': 'projekt',
    'purchase_order': 'projekt',
    'invoice_number': 'rechnungsnummer',
    'invoice_id': 'rechnungsnummer',
    
    # Legacy field support (temporary)
    'brutto_betrag': 'rechnungsbetrag',
    'rechnungsdatum': 'rechnungseingang',
}

# Map frontend form field names to database field names
FORM_TO_DATABASE: Dict[str, str] = {
    # Frontend might send these
    'customerName': 'rechnungsempfaenger',
    'vendorName': 'rechnungssteller',
    'project': 'projekt',
    'amount': 'rechnungsbetrag',
    'invoiceDate': 'rechnungseingang',
    'dueDate': 'faelligkeit',
}

# ========================================
# OUTPUT MAPPINGS
# ========================================

# Map database fields to frontend display names (English for dashboard)
DATABASE_TO_DISPLAY: Dict[str, str] = {
    'rechnungsempfaenger': 'Customer',
    'rechnungssteller': 'Vendor',
    'projekt': 'Project',
    'gewerk': 'Trade Category',
    'weiter_berechnen_an': 'Bill To',
    'rechnungsbetrag': 'Amount',
    'kfw_anrechenbare_kosten': 'KfW Eligible',
    'rechnungseingang': 'Invoice Date',
    'faelligkeit': 'Due Date',
    'skonto_datum': 'Early Payment Date',
    'skonto_prozent': 'Early Payment %',
    'rechnungsart': 'Invoice Type',
    'rechnungspruefung': 'Verification',
    'review_status': 'Review Status',
    'reviewed_by': 'Reviewed By',
    'reviewed_at': 'Reviewed At',
    'review_notes': 'Review Notes'
}

# Map database fields to API response fields (for frontend compatibility)
DATABASE_TO_API: Dict[str, str] = {
    # Keep German names for editor (direct mapping)
    'rechnungsempfaenger': 'rechnungsempfaenger',
    'rechnungssteller': 'rechnungssteller',
    'projekt': 'projekt',
    'gewerk': 'gewerk',
    'weiter_berechnen_an': 'weiter_berechnen_an',
    'rechnungsbetrag': 'rechnungsbetrag',
    'kfw_anrechenbare_kosten': 'kfw_anrechenbare_kosten',
    'rechnungseingang': 'rechnungseingang',
    'faelligkeit': 'faelligkeit',
    'skonto_datum': 'skonto_datum',
    'skonto_prozent': 'skonto_prozent',
    'rechnungsart': 'rechnungsart',
    'rechnungspruefung': 'rechnungspruefung',
    'review_status': 'review_status',
    'reviewed_by': 'reviewed_by',
    'reviewed_at': 'reviewed_at',
    'review_notes': 'review_notes',
    
    # Also provide English aliases for dashboard compatibility
    'customer_name': 'rechnungsempfaenger',
    'vendor_name': 'rechnungssteller',
    'total_amount': 'rechnungsbetrag',
    'invoice_date': 'rechnungseingang',
    'due_date': 'faelligkeit',
    'po_number': 'projekt',
}

# ========================================
# UTILITY FUNCTIONS
# ========================================

def map_input_to_database(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert input data (OCR, form, API) to database field names.
    
    Args:
        input_data: Dictionary with various field name formats
        
    Returns:
        Dictionary with database field names only
    """
    mapped_data = {}
    
    for input_field, value in input_data.items():
        # Skip None/empty values
        if value is None or value == "":
            continue
            
        # Direct database field (no mapping needed)
        if input_field in DATABASE_FIELDS:
            mapped_data[input_field] = value
        # OCR/API field mapping
        elif input_field in OCR_TO_DATABASE:
            db_field = OCR_TO_DATABASE[input_field]
            mapped_data[db_field] = value
        # Form field mapping
        elif input_field in FORM_TO_DATABASE:
            db_field = FORM_TO_DATABASE[input_field]
            mapped_data[db_field] = value
        # Unknown field - log warning but don't fail
        else:
            print(f"Warning: Unknown field '{input_field}' ignored")
    
    return mapped_data

def map_database_to_api(db_data: Dict[str, Any], include_english_aliases: bool = True) -> Dict[str, Any]:
    """
    Convert database data to API response format.
    
    Args:
        db_data: Data from database with German field names
        include_english_aliases: Whether to include English field aliases for dashboard
        
    Returns:
        Dictionary formatted for API response
    """
    api_data = {}
    
    # Direct mapping (German field names)
    for db_field, value in db_data.items():
        if db_field in DATABASE_FIELDS:
            api_data[db_field] = value
    
    # Add English aliases for dashboard compatibility
    if include_english_aliases:
        api_data.update({
            'customer_name': db_data.get('rechnungsempfaenger'),
            'vendor_name': db_data.get('rechnungssteller'),
            'total_amount': db_data.get('rechnungsbetrag'),
            'invoice_date': db_data.get('rechnungseingang'),
            'due_date': db_data.get('faelligkeit'),
            'po_number': db_data.get('projekt'),
        })
    
    return api_data

def get_display_name(db_field: str) -> str:
    """Get human-readable display name for a database field."""
    return DATABASE_TO_DISPLAY.get(db_field, db_field.replace('_', ' ').title())

def validate_database_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that all fields exist in the database schema.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        Dictionary with only valid database fields
    """
    return {
        field: value for field, value in data.items() 
        if field in DATABASE_FIELDS
    }

# ========================================
# FIELD VALIDATION
# ========================================

def get_required_fields() -> Set[str]:
    """Get list of required fields for invoice creation."""
    return {'file_name'}

def get_business_fields() -> Set[str]:
    """Get list of business-relevant fields (German names)."""
    return {
        'rechnungsempfaenger', 'rechnungssteller', 'projekt', 'gewerk',
        'weiter_berechnen_an', 'rechnungsbetrag', 'kfw_anrechenbare_kosten',
        'rechnungseingang', 'faelligkeit', 'skonto_datum', 'skonto_prozent',
        'rechnungsart', 'rechnungspruefung'
    }

def get_review_fields() -> Set[str]:
    """Get list of review workflow fields."""
    return {'review_status', 'reviewed_by', 'reviewed_at', 'review_notes'}

def get_system_fields() -> Set[str]:
    """Get list of system-managed fields."""
    return {
        'id', 'file_name', 'file_path', 'file_size', 'mime_type',
        'status', 'ocr_status', 'ocr_text', 'raw_ocr_data',
        'created_at', 'updated_at'
    }
