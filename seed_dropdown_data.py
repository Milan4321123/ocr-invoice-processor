#!/usr/bin/env python3
"""
Seed the existing dropdown_options table with initial data
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
from supabase import create_client, Client

def seed_dropdown_data():
    """Seed the dropdown_options table with initial data"""
    
    # Load environment variables from backend/.env
    load_dotenv('backend/.env')
    
    supabase_url = os.getenv('SUPA_URL')
    supabase_key = os.getenv('SUPA_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Supabase credentials not found")
        return False
    
    print(f"🔌 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("📊 Checking existing data...")
        
        # Check if table has data
        response = supabase.table('dropdown_options').select('field_name').execute()
        existing_count = len(response.data)
        print(f"Found {existing_count} existing options")
        
        # Define initial data
        initial_data = [
            # Rechnungsempfänger
            {'field_name': 'rechnungsempfaenger', 'value': 'acme_construction', 'label': 'ACME Construction GmbH', 'is_default': True, 'sort_order': 1},
            {'field_name': 'rechnungsempfaenger', 'value': 'baumeister_gmbh', 'label': 'Baumeister GmbH', 'is_default': True, 'sort_order': 2},
            {'field_name': 'rechnungsempfaenger', 'value': 'hochbau_services', 'label': 'Hochbau Services AG', 'is_default': True, 'sort_order': 3},
            {'field_name': 'rechnungsempfaenger', 'value': 'zimmerei_mueller', 'label': 'Zimmerei Müller & Co', 'is_default': True, 'sort_order': 4},
            {'field_name': 'rechnungsempfaenger', 'value': 'stadtwerke_berlin', 'label': 'Stadtwerke Berlin', 'is_default': True, 'sort_order': 5},
            
            # Rechnungssteller
            {'field_name': 'rechnungssteller', 'value': 'elektro_wagner', 'label': 'Elektro Wagner GmbH', 'is_default': True, 'sort_order': 1},
            {'field_name': 'rechnungssteller', 'value': 'sanitaer_schmidt', 'label': 'Sanitär Schmidt & Söhne', 'is_default': True, 'sort_order': 2},
            {'field_name': 'rechnungssteller', 'value': 'dach_decken_pro', 'label': 'Dach & Decken Pro GmbH', 'is_default': True, 'sort_order': 3},
            {'field_name': 'rechnungssteller', 'value': 'heizung_klima_expert', 'label': 'Heizung & Klima Expert', 'is_default': True, 'sort_order': 4},
            {'field_name': 'rechnungssteller', 'value': 'baumarkt_zentrale', 'label': 'Baumarkt Zentrale AG', 'is_default': True, 'sort_order': 5},
            {'field_name': 'rechnungssteller', 'value': 'malerbetrieb_weiss', 'label': 'Malerbetrieb Weiß', 'is_default': True, 'sort_order': 6},
            
            # Projekt
            {'field_name': 'projekt', 'value': 'wohnbau_mitte_2024', 'label': 'Wohnbau Mitte 2024', 'is_default': True, 'sort_order': 1},
            {'field_name': 'projekt', 'value': 'buerocomplex_nord', 'label': 'Bürokomplex Nord', 'is_default': True, 'sort_order': 2},
            {'field_name': 'projekt', 'value': 'sanierung_altbau_sued', 'label': 'Sanierung Altbau Süd', 'is_default': True, 'sort_order': 3},
            {'field_name': 'projekt', 'value': 'neubau_kindergarten', 'label': 'Neubau Kindergarten', 'is_default': True, 'sort_order': 4},
            {'field_name': 'projekt', 'value': 'umbau_fabrikhalle', 'label': 'Umbau Fabrikhalle', 'is_default': True, 'sort_order': 5},
            {'field_name': 'projekt', 'value': 'energetische_sanierung', 'label': 'Energetische Sanierung Ost', 'is_default': True, 'sort_order': 6},
            
            # Gewerk
            {'field_name': 'gewerk', 'value': 'elektroinstallation', 'label': 'Elektroinstallation', 'is_default': True, 'sort_order': 1},
            {'field_name': 'gewerk', 'value': 'sanitaerinstallation', 'label': 'Sanitärinstallation', 'is_default': True, 'sort_order': 2},
            {'field_name': 'gewerk', 'value': 'heizung_lueftung', 'label': 'Heizung & Lüftung', 'is_default': True, 'sort_order': 3},
            {'field_name': 'gewerk', 'value': 'dacharbeiten', 'label': 'Dacharbeiten', 'is_default': True, 'sort_order': 4},
            {'field_name': 'gewerk', 'value': 'maurerarbeiten', 'label': 'Maurerarbeiten', 'is_default': True, 'sort_order': 5},
            {'field_name': 'gewerk', 'value': 'malerarbeiten', 'label': 'Malerarbeiten', 'is_default': True, 'sort_order': 6},
            {'field_name': 'gewerk', 'value': 'bodenverlegung', 'label': 'Bodenverlegung', 'is_default': True, 'sort_order': 7},
            {'field_name': 'gewerk', 'value': 'fenster_tueren', 'label': 'Fenster & Türen', 'is_default': True, 'sort_order': 8},
            {'field_name': 'gewerk', 'value': 'zimmerei', 'label': 'Zimmerei', 'is_default': True, 'sort_order': 9},
            {'field_name': 'gewerk', 'value': 'geruestbau', 'label': 'Gerüstbau', 'is_default': True, 'sort_order': 10},
            
            # Weiter berechnen an
            {'field_name': 'weiter_berechnen_an', 'value': 'bauleitung', 'label': 'Bauleitung', 'is_default': True, 'sort_order': 1},
            {'field_name': 'weiter_berechnen_an', 'value': 'projektmanagement', 'label': 'Projektmanagement', 'is_default': True, 'sort_order': 2},
            {'field_name': 'weiter_berechnen_an', 'value': 'buchhaltung', 'label': 'Buchhaltung', 'is_default': True, 'sort_order': 3},
            {'field_name': 'weiter_berechnen_an', 'value': 'auftraggeber', 'label': 'Auftraggeber', 'is_default': True, 'sort_order': 4},
            {'field_name': 'weiter_berechnen_an', 'value': 'externe_pruefung', 'label': 'Externe Prüfung', 'is_default': True, 'sort_order': 5},
        ]
        
        print(f"📥 Inserting {len(initial_data)} dropdown options...")
        
        # Insert data one by one to handle conflicts gracefully
        inserted_count = 0
        skipped_count = 0
        
        for item in initial_data:
            try:
                # Check if exists first
                existing = supabase.table('dropdown_options').select('*').eq('field_name', item['field_name']).eq('value', item['value']).execute()
                
                if not existing.data:
                    response = supabase.table('dropdown_options').insert(item).execute()
                    inserted_count += 1
                    print(f"  ✅ Added: {item['field_name']}.{item['value']}")
                else:
                    skipped_count += 1
                    print(f"  ⏭️  Skipped (exists): {item['field_name']}.{item['value']}")
                    
            except Exception as insert_error:
                print(f"  ❌ Error inserting {item['field_name']}.{item['value']}: {insert_error}")
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Inserted: {inserted_count} new options")
        print(f"  ⏭️  Skipped: {skipped_count} existing options")
        
        # Verify the setup
        print("\n🔍 Verifying setup...")
        for field_name in ['rechnungsempfaenger', 'rechnungssteller', 'projekt', 'gewerk', 'weiter_berechnen_an']:
            try:
                response = supabase.table('dropdown_options').select('*').eq('field_name', field_name).eq('is_active', True).execute()
                count = len(response.data)
                print(f"  📋 {field_name}: {count} options")
            except Exception as e:
                print(f"  ❌ {field_name}: Error - {e}")
        
        print("\n🎉 Dropdown data seeding completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding dropdown data: {e}")
        return False

if __name__ == "__main__":
    success = seed_dropdown_data()
    sys.exit(0 if success else 1)
