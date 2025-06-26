"""Database-backed dropdown options management with fallback to hardcoded options"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel
import difflib

# Import centralized database service
from services.database import db_service

router = APIRouter()
logger = logging.getLogger(__name__)

class DropdownOption(BaseModel):
    """Model for dropdown option"""
    value: str
    label: str
    is_default: bool = False

class AddOptionRequest(BaseModel):
    """Model for adding new option to dropdown"""
    field_name: str
    value: str
    label: Optional[str] = None

class SuggestionRequest(BaseModel):
    """Model for OCR suggestion request"""
    extracted_values: Dict[str, str]

# Fallback hardcoded options (used when database is unavailable)
# These serve as both fallback data and initial migration data
FALLBACK_DROPDOWN_OPTIONS = {
    "rechnungsempfaenger": [
        {"value": "acme_construction", "label": "ACME Construction GmbH", "is_default": True},
        {"value": "baumeister_gmbh", "label": "Baumeister GmbH", "is_default": True},
        {"value": "hochbau_services", "label": "Hochbau Services AG", "is_default": True},
        {"value": "zimmerei_mueller", "label": "Zimmerei Müller & Co", "is_default": True},
        {"value": "stadtwerke_berlin", "label": "Stadtwerke Berlin", "is_default": True},
    ],
    "rechnungssteller": [
        {"value": "elektro_wagner", "label": "Elektro Wagner GmbH", "is_default": True},
        {"value": "sanitaer_schmidt", "label": "Sanitär Schmidt & Söhne", "is_default": True},
        {"value": "dach_decken_pro", "label": "Dach & Decken Pro GmbH", "is_default": True},
        {"value": "heizung_klima_expert", "label": "Heizung & Klima Expert", "is_default": True},
        {"value": "baumarkt_zentrale", "label": "Baumarkt Zentrale AG", "is_default": True},
        {"value": "malerbetrieb_weiss", "label": "Malerbetrieb Weiß", "is_default": True},
    ],
    "projekt": [
        {"value": "wohnbau_mitte_2024", "label": "Wohnbau Mitte 2024", "is_default": True},
        {"value": "buerocomplex_nord", "label": "Bürokomplex Nord", "is_default": True},
        {"value": "sanierung_altbau_sued", "label": "Sanierung Altbau Süd", "is_default": True},
        {"value": "neubau_kindergarten", "label": "Neubau Kindergarten", "is_default": True},
        {"value": "umbau_fabrikhalle", "label": "Umbau Fabrikhalle", "is_default": True},
        {"value": "energetische_sanierung", "label": "Energetische Sanierung Ost", "is_default": True},
    ],
    "gewerk": [
        {"value": "elektroinstallation", "label": "Elektroinstallation", "is_default": True},
        {"value": "sanitaerinstallation", "label": "Sanitärinstallation", "is_default": True},
        {"value": "heizung_lueftung", "label": "Heizung & Lüftung", "is_default": True},
        {"value": "dacharbeiten", "label": "Dacharbeiten", "is_default": True},
        {"value": "maurerarbeiten", "label": "Maurerarbeiten", "is_default": True},
        {"value": "malerarbeiten", "label": "Malerarbeiten", "is_default": True},
        {"value": "bodenverlegung", "label": "Bodenverlegung", "is_default": True},
        {"value": "fenster_tueren", "label": "Fenster & Türen", "is_default": True},
        {"value": "zimmerei", "label": "Zimmerei", "is_default": True},
        {"value": "geruestbau", "label": "Gerüstbau", "is_default": True},
    ]
}

# In-memory storage for custom options (simple approach for 100+ invoices/month)
# This gets reset on server restart, but works well for current needs
CUSTOM_OPTIONS: Dict[str, List[Dict[str, Any]]] = {
    "rechnungsempfaenger": [],
    "rechnungssteller": [],
    "projekt": [],
    "gewerk": []
}

# Database helper functions
def _get_dropdown_options_from_db(field_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Get dropdown options from database"""
    db_options = db_service.get_dropdown_options(field_name)
    
    if not db_options:
        logger.warning("Database unavailable, using fallback options")
        if field_name:
            return {field_name: FALLBACK_DROPDOWN_OPTIONS.get(field_name, [])}
        return FALLBACK_DROPDOWN_OPTIONS
    
    return db_options

def _add_dropdown_option_to_db(field_name: str, value: str, label: str, is_default: bool = False, metadata: Dict = None) -> Dict[str, Any]:
    """Add a new dropdown option to database"""
    return db_service.add_dropdown_option(field_name, value, label, is_default, metadata)

def _delete_dropdown_option_from_db(field_name: str, value: str) -> Dict[str, Any]:
    """Delete a dropdown option from database (soft delete - set is_active=false)"""
    return db_service.delete_dropdown_option(field_name, value)

def _get_valid_field_names() -> List[str]:
    """Get list of valid field names (from fallback or database)"""
    return list(FALLBACK_DROPDOWN_OPTIONS.keys())

def _calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity for OCR suggestions and duplicate detection"""
    if not text1 or not text2:
        return 0.0
    
    # Use difflib for similarity calculation
    similarity = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    return similarity

def _normalize_text(text: str) -> str:
    """Normalize text for better duplicate detection"""
    if not text:
        return ""
    
    # Convert to lowercase and remove common company suffixes/prefixes
    normalized = text.lower().strip()
    
    # Remove common German company suffixes
    company_suffixes = ['gmbh', 'ag', 'kg', 'ohg', 'gbr', 'eg', 'ev', 'ug', 'co', '&', 'und', 'plus']
    for suffix in company_suffixes:
        # Remove suffix at the end (with optional punctuation)
        patterns = [f' {suffix}', f'.{suffix}', f'&{suffix}', f'+{suffix}']
        for pattern in patterns:
            if normalized.endswith(pattern):
                normalized = normalized[:-len(pattern)].strip()
    
    # Remove common punctuation and extra spaces
    normalized = normalized.replace('.', '').replace(',', '').replace('-', ' ')
    normalized = ' '.join(normalized.split())  # Remove extra whitespace
    
    return normalized

def _find_potential_duplicates(new_label: str, existing_options: List[Dict[str, Any]], similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
    """Find potential duplicates using fuzzy matching"""
    potential_duplicates = []
    new_normalized = _normalize_text(new_label)
    
    for option in existing_options:
        existing_normalized = _normalize_text(option["label"])
        
        # Calculate similarity between normalized texts
        similarity = _calculate_similarity(new_normalized, existing_normalized)
        
        if similarity >= similarity_threshold:
            potential_duplicates.append({
                "option": option,
                "similarity": similarity,
                "normalized_new": new_normalized,
                "normalized_existing": existing_normalized
            })
    
    # Sort by similarity (highest first)
    potential_duplicates.sort(key=lambda x: x["similarity"], reverse=True)
    
    return potential_duplicates

def _get_all_options_for_field(field_name: str) -> List[Dict[str, Any]]:
    """Get all options (database/fallback + custom) for a field"""
    if field_name not in _get_valid_field_names():
        return []
    
    # Start with database/fallback options
    db_options = _get_dropdown_options_from_db(field_name)
    all_options = db_options.get(field_name, []).copy()
    
    # Add custom in-memory options (these are temporary until next server restart)
    if field_name in CUSTOM_OPTIONS:
        all_options.extend(CUSTOM_OPTIONS[field_name])
    
    return all_options

@router.get("/dropdowns/stats")
async def get_dropdown_stats():
    """Get statistics about dropdown options"""
    stats = {}
    total_options = 0
    valid_field_names = _get_valid_field_names()
    
    for field_name in valid_field_names:
        # Get options from database/fallback
        db_options = _get_dropdown_options_from_db(field_name)
        default_count = len(db_options.get(field_name, []))
        custom_count = len(CUSTOM_OPTIONS.get(field_name, []))
        field_total = default_count + custom_count
        
        stats[field_name] = {
            "default_options": default_count,
            "custom_options": custom_count,
            "total_options": field_total
        }
        total_options += field_total
    
    return {
        "field_stats": stats,
        "total_options": total_options,
        "total_fields": len(valid_field_names)
    }

@router.get("/dropdowns/{field_name}")
async def get_dropdown_options(field_name: str):
    """Get all dropdown options for a specific field"""
    if field_name not in _get_valid_field_names():
        raise HTTPException(status_code=400, detail=f"Invalid field name: {field_name}")
    
    all_options = _get_all_options_for_field(field_name)
    
    return {
        "field_name": field_name,
        "options": all_options,
        "total": len(all_options)
    }

@router.get("/dropdowns")
async def get_all_dropdown_options():
    """Get all dropdown options for all fields"""
    all_dropdowns = {}
    valid_field_names = _get_valid_field_names()
    
    for field_name in valid_field_names:
        all_dropdowns[field_name] = _get_all_options_for_field(field_name)
    
    return {
        "dropdowns": all_dropdowns,
        "field_names": valid_field_names
    }

@router.post("/dropdowns/add-option")
async def add_dropdown_option(request: AddOptionRequest):
    """Add a new option to a dropdown field with enhanced duplicate detection"""
    if request.field_name not in _get_valid_field_names():
        raise HTTPException(status_code=400, detail=f"Invalid field name: {request.field_name}")
    
    if not request.value or not request.value.strip():
        raise HTTPException(status_code=400, detail="Option value cannot be empty")
    
    # Use label or default to value
    label = request.label if request.label and request.label.strip() else request.value
    
    # Generate a safe value from the label if not provided
    safe_value = request.value.lower().replace(" ", "_").replace("&", "and").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    
    # Get existing options for duplicate detection
    existing_options = _get_all_options_for_field(request.field_name)
    existing_values = [opt["value"] for opt in existing_options]
    
    # Check for exact value duplicate
    if safe_value in existing_values:
        existing_option = next(opt for opt in existing_options if opt["value"] == safe_value)
        return {
            "success": True,
            "message": f"Option already exists in {request.field_name}",
            "duplicate_detected": True,
            "existing_option": existing_option,
            "option": {
                "value": safe_value,
                "label": label,
                "is_default": False
            }
        }
    
    # Check for potential duplicates using fuzzy matching
    potential_duplicates = _find_potential_duplicates(label, existing_options, similarity_threshold=0.8)
    
    if potential_duplicates:
        # Return the potential duplicates for user confirmation
        return {
            "success": False,
            "message": "Potential duplicates found",
            "duplicate_detected": True,
            "potential_duplicates": [
                {
                    "existing_option": dup["option"],
                    "similarity": dup["similarity"],
                    "normalized_new": dup["normalized_new"],
                    "normalized_existing": dup["normalized_existing"]
                }
                for dup in potential_duplicates[:3]  # Return top 3 matches
            ],
            "suggested_option": {
                "value": safe_value,
                "label": label,
                "is_default": False
            }
        }
    
    # No duplicates found, add the new option
    new_option = {
        "value": safe_value,
        "label": label,
        "is_default": False
    }
    
    # Try to persist to database first
    db_result = _add_dropdown_option_to_db(request.field_name, safe_value, label, is_default=False)
    
    if not db_result.get("success"):
        # Database failed, add to in-memory storage as fallback
        CUSTOM_OPTIONS[request.field_name].append(new_option)
        logger.warning(f"Database persist failed, added to memory: {request.field_name} - {label}")
    else:
        logger.info(f"Successfully added option to database: {request.field_name} - {label}")
    
    return {
        "success": True,
        "message": f"Option added to {request.field_name}",
        "duplicate_detected": False,
        "option": new_option,
        "persisted_to_db": db_result.get("success", False)
    }

@router.delete("/dropdowns/{field_name}/{option_value}")
async def delete_dropdown_option(field_name: str, option_value: str):
    """Delete a custom dropdown option (cannot delete default options)"""
    if field_name not in _get_valid_field_names():
        raise HTTPException(status_code=400, detail=f"Invalid field name: {field_name}")
    
    # Check if it's a default option from database/fallback
    db_options = _get_dropdown_options_from_db(field_name)
    default_values = [opt["value"] for opt in db_options.get(field_name, [])]
    if option_value in default_values:
        raise HTTPException(status_code=400, detail="Cannot delete default options")
    
    # Remove from custom options
    if field_name in CUSTOM_OPTIONS:
        CUSTOM_OPTIONS[field_name] = [
            opt for opt in CUSTOM_OPTIONS[field_name] 
            if opt["value"] != option_value
        ]
    
    # Try to delete from database as well (soft delete)
    db_result = _delete_dropdown_option_from_db(field_name, option_value)
    
    logger.info(f"Deleted custom option from {field_name}: {option_value}")
    
    return {
        "success": True,
        "message": f"Option '{option_value}' deleted from {field_name}",
        "deleted_option": option_value,
        "deleted_from_db": db_result.get("success", False)
    }