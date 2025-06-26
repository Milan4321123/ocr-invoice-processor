-- SUPABASE SETUP: Execute this in SQL Editor
-- Creates dropdown_options table and seeds with default data

-- 1. Create the table
CREATE TABLE dropdown_options (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
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

-- 2. Create constraints and indexes
CREATE UNIQUE INDEX dropdown_options_field_value_unique 
ON dropdown_options (field_name, value) 
WHERE is_active = TRUE;

CREATE INDEX dropdown_options_field_name_idx ON dropdown_options (field_name);
CREATE INDEX dropdown_options_is_active_idx ON dropdown_options (is_active);

-- 3. Insert default data
INSERT INTO dropdown_options (field_name, value, label, is_default, sort_order) VALUES
-- Recipients
('rechnungsempfaenger', 'acme_construction', 'ACME Construction GmbH', TRUE, 1),
('rechnungsempfaenger', 'baumeister_gmbh', 'Baumeister GmbH', TRUE, 2),
('rechnungsempfaenger', 'hochbau_services', 'Hochbau Services AG', TRUE, 3),
('rechnungsempfaenger', 'zimmerei_mueller', 'Zimmerei Müller & Co', TRUE, 4),
('rechnungsempfaenger', 'stadtwerke_berlin', 'Stadtwerke Berlin', TRUE, 5),

-- Vendors
('rechnungssteller', 'elektro_wagner', 'Elektro Wagner GmbH', TRUE, 1),
('rechnungssteller', 'sanitaer_schmidt', 'Sanitär Schmidt & Söhne', TRUE, 2),
('rechnungssteller', 'dach_decken_pro', 'Dach & Decken Pro GmbH', TRUE, 3),
('rechnungssteller', 'heizung_klima_expert', 'Heizung & Klima Expert', TRUE, 4),
('rechnungssteller', 'baumarkt_zentrale', 'Baumarkt Zentrale AG', TRUE, 5),
('rechnungssteller', 'malerbetrieb_weiss', 'Malerbetrieb Weiß', TRUE, 6),

-- Projects
('projekt', 'wohnbau_mitte_2024', 'Wohnbau Mitte 2024', TRUE, 1),
('projekt', 'buerocomplex_nord', 'Bürokomplex Nord', TRUE, 2),
('projekt', 'sanierung_altbau_sued', 'Sanierung Altbau Süd', TRUE, 3),
('projekt', 'neubau_kindergarten', 'Neubau Kindergarten', TRUE, 4),
('projekt', 'umbau_fabrikhalle', 'Umbau Fabrikhalle', TRUE, 5),
('projekt', 'energetische_sanierung', 'Energetische Sanierung Ost', TRUE, 6),

-- Trades
('gewerk', 'elektroinstallation', 'Elektroinstallation', TRUE, 1),
('gewerk', 'sanitaerinstallation', 'Sanitärinstallation', TRUE, 2),
('gewerk', 'heizung_lueftung', 'Heizung & Lüftung', TRUE, 3),
('gewerk', 'dacharbeiten', 'Dacharbeiten', TRUE, 4),
('gewerk', 'maurerarbeiten', 'Maurerarbeiten', TRUE, 5),
('gewerk', 'malerarbeiten', 'Malerarbeiten', TRUE, 6),
('gewerk', 'bodenverlegung', 'Bodenverlegung', TRUE, 7),
('gewerk', 'fenster_tueren', 'Fenster & Türen', TRUE, 8),
('gewerk', 'zimmerei', 'Zimmerei', TRUE, 9),
('gewerk', 'geruestbau', 'Gerüstbau', TRUE, 10),

-- Forward billing
('weiter_berechnen_an', 'bauleitung', 'Bauleitung', TRUE, 1),
('weiter_berechnen_an', 'projektmanagement', 'Projektmanagement', TRUE, 2),
('weiter_berechnen_an', 'buchhaltung', 'Buchhaltung', TRUE, 3),
('weiter_berechnen_an', 'auftraggeber', 'Auftraggeber', TRUE, 4),
('weiter_berechnen_an', 'externe_pruefung', 'Externe Prüfung', TRUE, 5);

-- 4. Verify setup
SELECT 
    field_name,
    COUNT(*) as total_options,
    COUNT(*) FILTER (WHERE is_default = TRUE) as default_options
FROM dropdown_options 
WHERE is_active = TRUE
GROUP BY field_name
ORDER BY field_name;
