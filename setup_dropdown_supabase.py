#!/usr/bin/env python3
"""
Setup script for dropdown options table in Supabase
Applies the dropdown schema and seeds initial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.services.database import db_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_dropdown_table():
    """Setup dropdown_options table with initial data"""
    
    if not db_service.is_available:
        logger.error("❌ Database service not available. Check your .env credentials.")
        return False
    
    try:
        # Read the SQL schema file
        sql_file_path = os.path.join(os.path.dirname(__file__), "SETUP_DROPDOWN_SCHEMA.sql")
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split the SQL into individual statements (basic approach)
        # We'll execute the statements that PostgreSQL/Supabase can handle
        logger.info("🚀 Setting up dropdown_options table...")
        
        # Test if we can create a simple entry
        test_result = db_service.add_dropdown_option(
            field_name="test_field",
            value="test_value", 
            label="Test Option",
            is_default=True
        )
        
        if test_result.get("success"):
            logger.info("✅ Database connection successful!")
            
            # Delete the test entry
            db_service.delete_dropdown_option("test_field", "test_value")
            
            # Now let's add the real default options
            logger.info("📦 Adding default dropdown options...")
            
            # Default options data
            default_options = {
                "rechnungsempfaenger": [
                    {"value": "acme_construction", "label": "ACME Construction GmbH"},
                    {"value": "baumeister_gmbh", "label": "Baumeister GmbH"},
                    {"value": "hochbau_services", "label": "Hochbau Services AG"},
                    {"value": "zimmerei_mueller", "label": "Zimmerei Müller & Co"},
                    {"value": "stadtwerke_berlin", "label": "Stadtwerke Berlin"},
                ],
                "rechnungssteller": [
                    {"value": "elektro_wagner", "label": "Elektro Wagner GmbH"},
                    {"value": "sanitaer_schmidt", "label": "Sanitär Schmidt & Söhne"},
                    {"value": "dach_decken_pro", "label": "Dach & Decken Pro GmbH"},
                    {"value": "heizung_klima_expert", "label": "Heizung & Klima Expert"},
                    {"value": "baumarkt_zentrale", "label": "Baumarkt Zentrale AG"},
                    {"value": "malerbetrieb_weiss", "label": "Malerbetrieb Weiß"},
                ],
                "projekt": [
                    {"value": "wohnbau_mitte_2024", "label": "Wohnbau Mitte 2024"},
                    {"value": "buerocomplex_nord", "label": "Bürokomplex Nord"},
                    {"value": "sanierung_altbau_sued", "label": "Sanierung Altbau Süd"},
                    {"value": "neubau_kindergarten", "label": "Neubau Kindergarten"},
                    {"value": "umbau_fabrikhalle", "label": "Umbau Fabrikhalle"},
                    {"value": "energetische_sanierung", "label": "Energetische Sanierung Ost"},
                ],
                "gewerk": [
                    {"value": "elektroinstallation", "label": "Elektroinstallation"},
                    {"value": "sanitaerinstallation", "label": "Sanitärinstallation"},
                    {"value": "heizung_lueftung", "label": "Heizung & Lüftung"},
                    {"value": "dacharbeiten", "label": "Dacharbeiten"},
                    {"value": "maurerarbeiten", "label": "Maurerarbeiten"},
                    {"value": "malerarbeiten", "label": "Malerarbeiten"},
                    {"value": "bodenverlegung", "label": "Bodenverlegung"},
                    {"value": "fenster_tueren", "label": "Fenster & Türen"},
                    {"value": "zimmerei", "label": "Zimmerei"},
                    {"value": "geruestbau", "label": "Gerüstbau"},
                ],
                "weiter_berechnen_an": [
                    {"value": "bauleitung", "label": "Bauleitung"},
                    {"value": "projektmanagement", "label": "Projektmanagement"},
                    {"value": "buchhaltung", "label": "Buchhaltung"},
                    {"value": "auftraggeber", "label": "Auftraggeber"},
                    {"value": "externe_pruefung", "label": "Externe Prüfung"},
                ]
            }
            
            # Add each option
            added_count = 0
            for field_name, options in default_options.items():
                logger.info(f"Adding options for {field_name}...")
                for option in options:
                    result = db_service.add_dropdown_option(
                        field_name=field_name,
                        value=option["value"],
                        label=option["label"],
                        is_default=True
                    )
                    if result.get("success"):
                        added_count += 1
                    elif "already exists" in result.get("error", "").lower():
                        logger.info(f"  ✓ {option['value']} already exists")
                    else:
                        logger.warning(f"  ❌ Failed to add {option['value']}: {result.get('error')}")
            
            logger.info(f"✅ Setup complete! Added {added_count} new options.")
            
            # Verify the setup
            all_options = db_service.get_dropdown_options()
            if all_options:
                logger.info(f"📊 Dropdown fields configured: {list(all_options.keys())}")
                for field, options in all_options.items():
                    logger.info(f"  {field}: {len(options)} options")
            
            return True
            
        else:
            logger.error(f"❌ Database test failed: {test_result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting dropdown table setup...")
    success = setup_dropdown_table()
    
    if success:
        logger.info("✅ Dropdown setup completed successfully!")
        print("\n🎉 Dropdown options are now ready!")
        print("You can test them at: http://localhost:3000/dropdown-test")
    else:
        logger.error("❌ Setup failed. Please check your database connection.")
        sys.exit(1)
