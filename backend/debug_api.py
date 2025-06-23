#!/usr/bin/env python3
"""
Enhanced Debug script to test API endpoint issues with comprehensive error handling
"""
import sys
import os
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.append('/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend')

from services.database import db_service

class DebugHelper:
    """Helper class for enhanced debugging with better error handling"""
    
    @staticmethod
    def safe_print(message: str, level: str = "INFO"):
        """Safe print with timestamp and level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    @staticmethod
    def validate_invoice_exists(invoice_id: str) -> bool:
        """Validate that an invoice exists before attempting operations"""
        try:
            DebugHelper.safe_print(f"Validating invoice exists: {invoice_id}")
            result = db_service.client.table("invoices").select("id,rechnungsnummer,rechnungssteller").eq("id", invoice_id).execute()
            
            if not result.data:
                DebugHelper.safe_print(f"❌ Invoice {invoice_id} does not exist", "ERROR")
                return False
            
            invoice_info = result.data[0]
            DebugHelper.safe_print(f"✅ Invoice exists: {invoice_info.get('rechnungsnummer')} from {invoice_info.get('rechnungssteller')}")
            return True
            
        except Exception as e:
            DebugHelper.safe_print(f"❌ Error validating invoice: {str(e)}", "ERROR")
            DebugHelper.safe_print(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
    
    @staticmethod
    def get_table_columns(table_name: str) -> Optional[list]:
        """Get table columns to validate field mapping"""
        try:
            # Query with a limit of 1 to get column structure
            result = db_service.client.table(table_name).select("*").limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                DebugHelper.safe_print(f"Table '{table_name}' columns: {columns}")
                return columns
            return None
        except Exception as e:
            DebugHelper.safe_print(f"❌ Error getting table columns: {str(e)}", "ERROR")
            return None
    
    @staticmethod
    def analyze_supabase_response(result) -> Dict[str, Any]:
        """Analyze Supabase response for comprehensive debugging"""
        analysis = {
            "success": False,
            "has_data": False,
            "has_error": False,
            "data_count": 0,
            "error_details": None,
            "raw_result": str(result)
        }
        
        try:
            # Check if result has data
            if hasattr(result, 'data') and result.data:
                analysis["has_data"] = True
                analysis["data_count"] = len(result.data) if isinstance(result.data, list) else 1
                analysis["success"] = True
            
            # Check for errors
            if hasattr(result, 'error') and result.error:
                analysis["has_error"] = True
                analysis["error_details"] = str(result.error)
                analysis["success"] = False
            
            # Additional Supabase-specific checks
            if hasattr(result, 'status_code'):
                analysis["status_code"] = result.status_code
                if result.status_code >= 400:
                    analysis["success"] = False
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis

def test_enhanced_manual_update():
    """Enhanced test with comprehensive error handling"""
    DebugHelper.safe_print("=== Enhanced Manual Database Update Test ===")
    
    invoice_id = "12760fc2-1d87-4344-9d49-045c864c0de5"
    
    # First, validate the invoice exists
    if not DebugHelper.validate_invoice_exists(invoice_id):
        DebugHelper.safe_print("❌ Cannot proceed - invoice does not exist", "ERROR")
        return False
    
    # Get table structure
    DebugHelper.get_table_columns("invoices")
    
    # Test data with problematic field mapping
    test_data = {
        "skonto_prozent": 15.5,
        "rechnungsart": "Enhanced Debug Test Update",
        "faelligkeit": "2025-04-01"  # ❌ PROBLEM: This should map to due_date
    }
    
    DebugHelper.safe_print(f"❌ PROBLEMATIC: Updating with unmapped field 'faelligkeit': {test_data}")
    
    try:
        # This was the PROBLEM - using German field name directly
        result = db_service.client.table("invoices").update(test_data).eq("id", invoice_id).execute()
        
        # Enhanced analysis
        analysis = DebugHelper.analyze_supabase_response(result)
        DebugHelper.safe_print(f"Update analysis: {json.dumps(analysis, indent=2)}")
        
        if not analysis["success"]:
            DebugHelper.safe_print("❌ Update failed - likely due to field mapping issue", "ERROR")
            return False
            
        # Verify the update
        verify = db_service.client.table("invoices").select("skonto_prozent,rechnungsart,due_date").eq("id", invoice_id).execute()
        verify_analysis = DebugHelper.analyze_supabase_response(verify)
        DebugHelper.safe_print(f"Verification: {json.dumps(verify_analysis, indent=2)}")
        
        if verify.data:
            DebugHelper.safe_print(f"✅ Verification data: {verify.data[0]}")
        
        return True
        
    except Exception as e:
        DebugHelper.safe_print(f"❌ Exception in manual update: {str(e)}", "ERROR")
        DebugHelper.safe_print(f"Exception type: {type(e)}", "ERROR")
        DebugHelper.safe_print(f"Traceback: {traceback.format_exc()}", "ERROR")
        return False

def test_corrected_api_logic():
    """Test the CORRECTED API endpoint logic with proper field mapping"""
    DebugHelper.safe_print("\n=== Testing CORRECTED API Endpoint Logic ===")
    
    invoice_id = "12760fc2-1d87-4344-9d49-045c864c0de5"
    
    # Validate invoice exists first
    if not DebugHelper.validate_invoice_exists(invoice_id):
        DebugHelper.safe_print("❌ Cannot proceed - invoice does not exist", "ERROR")
        return False
    
    # Simulate the request body (what comes from frontend)
    frontend_fields = {
        "skonto_prozent": 25.5,
        "faelligkeit": "2025-05-01",  # German field name from frontend
        "rechnungsart": "Corrected API Logic Test"
    }
    
    DebugHelper.safe_print(f"🔄 Frontend fields: {frontend_fields}")
    
    # ✅ CORRECTED: Proper field mapping (this is what the API should do)
    update_data = {}
    
    # Map frontend German fields to database English fields
    field_mapping = {
        "faelligkeit": "due_date",  # ✅ CRITICAL: Map German to English
        "rechnungseingang": "rechnungsdatum",
        "rechnungsbetrag": "brutto_betrag",
        # Direct mappings (same in both)
        "skonto_prozent": "skonto_prozent",
        "rechnungsart": "rechnungsart",
        "rechnungsempfaenger": "rechnungsempfaenger",
        "rechnungssteller": "rechnungssteller",
        "projekt": "projekt",
        "gewerk": "gewerk"
    }
    
    for frontend_field, value in frontend_fields.items():
        if frontend_field in field_mapping:
            db_field = field_mapping[frontend_field]
            update_data[db_field] = value
            DebugHelper.safe_print(f"✅ Mapped '{frontend_field}' -> '{db_field}': {value}")
        else:
            # If not in mapping, use as-is (for backward compatibility)
            update_data[frontend_field] = value
            DebugHelper.safe_print(f"⚠️ Direct field '{frontend_field}': {value}")
    
    DebugHelper.safe_print(f"✅ Final update_data: {update_data}")
    
    try:
        result = db_service.client.table("invoices").update(update_data).eq("id", invoice_id).execute()
        
        # Enhanced analysis
        analysis = DebugHelper.analyze_supabase_response(result)
        DebugHelper.safe_print(f"API logic analysis: {json.dumps(analysis, indent=2)}")
        
        if analysis["success"]:
            DebugHelper.safe_print("✅ Corrected API logic successful!")
        else:
            DebugHelper.safe_print("❌ Corrected API logic failed", "ERROR")
            return False
        
        # Verify the update with explicit field selection
        verify = db_service.client.table("invoices").select("skonto_prozent,rechnungsart,due_date,updated_at").eq("id", invoice_id).execute()
        verify_analysis = DebugHelper.analyze_supabase_response(verify)
        
        if verify.data:
            DebugHelper.safe_print(f"✅ Verification successful: {verify.data[0]}")
        else:
            DebugHelper.safe_print("❌ Verification failed", "ERROR")
        
        return True
        
    except Exception as e:
        DebugHelper.safe_print(f"❌ Exception in corrected API logic: {str(e)}", "ERROR")
        DebugHelper.safe_print(f"Traceback: {traceback.format_exc()}", "ERROR")
        return False

def test_database_connection():
    """Test database connection and basic functionality"""
    DebugHelper.safe_print("\n=== Testing Database Connection ===")
    
    try:
        # Test basic connection
        if not db_service.is_available:
            DebugHelper.safe_print("❌ Database service not available", "ERROR")
            return False
        
        DebugHelper.safe_print("✅ Database service available")
        
        # Test basic query
        result = db_service.client.table("invoices").select("count").execute()
        analysis = DebugHelper.analyze_supabase_response(result)
        
        if analysis["success"]:
            DebugHelper.safe_print("✅ Database connection test successful")
            return True
        else:
            DebugHelper.safe_print(f"❌ Database connection test failed: {analysis}", "ERROR")
            return False
            
    except Exception as e:
        DebugHelper.safe_print(f"❌ Database connection error: {str(e)}", "ERROR")
        return False

def test_field_mapping_validation():
    """Test field mapping validation"""
    DebugHelper.safe_print("\n=== Testing Field Mapping Validation ===")
    
    # Get actual table structure
    columns = DebugHelper.get_table_columns("invoices")
    if not columns:
        DebugHelper.safe_print("❌ Could not get table structure", "ERROR")
        return False
    
    # Check critical field mappings
    critical_mappings = {
        "faelligkeit": "due_date",  # Most critical mapping
        "rechnungsdatum": "rechnungsdatum",  # Should exist
        "brutto_betrag": "brutto_betrag",   # Should exist
        "skonto_prozent": "skonto_prozent", # Should exist after migration
    }
    
    DebugHelper.safe_print("🔍 Validating critical field mappings:")
    
    for frontend_field, db_field in critical_mappings.items():
        if db_field in columns:
            DebugHelper.safe_print(f"✅ '{frontend_field}' -> '{db_field}' (exists in DB)")
        else:
            DebugHelper.safe_print(f"❌ '{frontend_field}' -> '{db_field}' (MISSING from DB)", "ERROR")
    
    return True

if __name__ == "__main__":
    DebugHelper.safe_print("OCR Invoice Processor - Enhanced API Endpoint Debug")
    DebugHelper.safe_print("=" * 60)
    
    # Test database connection first
    if not test_database_connection():
        DebugHelper.safe_print("❌ Database connection failed - cannot proceed", "ERROR")
        sys.exit(1)
    
    # Test field mapping validation
    test_field_mapping_validation()
    
    # Test the problematic case (what was causing issues)
    DebugHelper.safe_print("\n" + "=" * 60)
    DebugHelper.safe_print("🔴 TESTING PROBLEMATIC CASE (what was failing)")
    test_enhanced_manual_update()
    
    # Test the corrected logic
    DebugHelper.safe_print("\n" + "=" * 60)
    DebugHelper.safe_print("🟢 TESTING CORRECTED LOGIC (what should work)")
    test_corrected_api_logic()
    
    DebugHelper.safe_print("\n" + "=" * 60)
    DebugHelper.safe_print("🏁 Debug session completed")
