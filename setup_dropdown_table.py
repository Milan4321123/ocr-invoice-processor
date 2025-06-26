#!/usr/bin/env python3
"""
Setup script to create dropdown_options table in Supabase
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import after path setup
from dotenv import load_dotenv
from supabase import create_client, Client

def setup_dropdown_table():
    """Create dropdown_options table and seed with initial data"""
    
    # Load environment variables from backend/.env
    load_dotenv('backend/.env')
    
    supabase_url = os.getenv('SUPA_URL')
    supabase_key = os.getenv('SUPA_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Supabase credentials not found in backend/.env")
        print(f"SUPA_URL: {supabase_url}")
        print(f"SUPA_KEY: {'***' if supabase_key else 'None'}")
        return False
    
    print(f"🔌 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("📋 Creating dropdown_options table...")
        
        # Create table SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS dropdown_options (
            id BIGSERIAL PRIMARY KEY,
            field_name TEXT NOT NULL,
            value TEXT NOT NULL,
            label TEXT NOT NULL,
            is_default BOOLEAN DEFAULT FALSE,
            sort_order INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Execute table creation
        response = supabase.table('dropdown_options').select('*').limit(1).execute()
        print("✅ Table exists or was created successfully!")
        
        # Create unique constraint
        constraint_sql = """
        CREATE UNIQUE INDEX IF NOT EXISTS dropdown_options_field_value_unique 
        ON dropdown_options (field_name, value) 
        WHERE is_active = TRUE;
        """
        
        # Create indexes
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS dropdown_options_field_name_idx ON dropdown_options (field_name);
        CREATE INDEX IF NOT EXISTS dropdown_options_is_active_idx ON dropdown_options (is_active);
        CREATE INDEX IF NOT EXISTS dropdown_options_sort_order_idx ON dropdown_options (field_name, sort_order);
        """
        
        print("📊 Seeding initial data...")
        
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
        
        # Insert data using upsert to avoid duplicates
        try:
            response = supabase.table('dropdown_options').upsert(
                initial_data,
                on_conflict='field_name,value'
            ).execute()
            
            print(f"✅ Successfully inserted/updated {len(initial_data)} dropdown options!")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not insert data via upsert: {e}")
            print("🔄 Trying individual inserts...")
            
            # Try individual inserts
            inserted_count = 0
            for item in initial_data:
                try:
                    # Check if exists first
                    existing = supabase.table('dropdown_options').select('*').eq('field_name', item['field_name']).eq('value', item['value']).execute()
                    
                    if not existing.data:
                        response = supabase.table('dropdown_options').insert(item).execute()
                        inserted_count += 1
                        
                except Exception as insert_error:
                    print(f"❌ Error inserting {item['field_name']}.{item['value']}: {insert_error}")
            
            print(f"✅ Successfully inserted {inserted_count} new dropdown options!")
        
        # Verify the setup
        print("\n📊 Verifying setup...")
        for field_name in ['rechnungsempfaenger', 'rechnungssteller', 'projekt', 'gewerk', 'weiter_berechnen_an']:
            try:
                response = supabase.table('dropdown_options').select('*').eq('field_name', field_name).eq('is_active', True).execute()
                count = len(response.data)
                print(f"  {field_name}: {count} options")
            except Exception as e:
                print(f"  {field_name}: ❌ Error - {e}")
        
        print("\n🎉 Dropdown table setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up dropdown table: {e}")
        return False

if __name__ == "__main__":
    success = setup_dropdown_table()
    sys.exit(0 if success else 1)
