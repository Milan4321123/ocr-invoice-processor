-- Create dropdown_options table for dynamic dropdown management
-- This table stores all dropdown options for invoice fields

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

-- Create unique constraint to prevent duplicate field_name + value combinations
CREATE UNIQUE INDEX IF NOT EXISTS dropdown_options_field_value_unique 
ON dropdown_options (field_name, value) 
WHERE is_active = TRUE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS dropdown_options_field_name_idx ON dropdown_options (field_name);
CREATE INDEX IF NOT EXISTS dropdown_options_is_active_idx ON dropdown_options (is_active);
CREATE INDEX IF NOT EXISTS dropdown_options_sort_order_idx ON dropdown_options (field_name, sort_order);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_dropdown_options_updated_at ON dropdown_options;
CREATE TRIGGER update_dropdown_options_updated_at
    BEFORE UPDATE ON dropdown_options
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default dropdown options
-- These will serve as the base options for the system

-- Rechnungsempfänger (Invoice Recipients)
INSERT INTO dropdown_options (field_name, value, label, is_default, sort_order) VALUES
('rechnungsempfaenger', 'acme_construction', 'ACME Construction GmbH', TRUE, 1),
('rechnungsempfaenger', 'baumeister_gmbh', 'Baumeister GmbH', TRUE, 2),
('rechnungsempfaenger', 'hochbau_services', 'Hochbau Services AG', TRUE, 3),
('rechnungsempfaenger', 'zimmerei_mueller', 'Zimmerei Müller & Co', TRUE, 4),
('rechnungsempfaenger', 'stadtwerke_berlin', 'Stadtwerke Berlin', TRUE, 5)
ON CONFLICT (field_name, value) DO NOTHING;

-- Rechnungssteller (Invoice Vendors)
INSERT INTO dropdown_options (field_name, value, label, is_default, sort_order) VALUES
('rechnungssteller', 'elektro_wagner', 'Elektro Wagner GmbH', TRUE, 1),
('rechnungssteller', 'sanitaer_schmidt', 'Sanitär Schmidt & Söhne', TRUE, 2),
('rechnungssteller', 'dach_decken_pro', 'Dach & Decken Pro GmbH', TRUE, 3),
('rechnungssteller', 'heizung_klima_expert', 'Heizung & Klima Expert', TRUE, 4),
('rechnungssteller', 'baumarkt_zentrale', 'Baumarkt Zentrale AG', TRUE, 5),
('rechnungssteller', 'malerbetrieb_weiss', 'Malerbetrieb Weiß', TRUE, 6)
ON CONFLICT (field_name, value) DO NOTHING;

-- Projekt (Projects)
INSERT INTO dropdown_options (field_name, value, label, is_default, sort_order) VALUES
('projekt', 'wohnbau_mitte_2024', 'Wohnbau Mitte 2024', TRUE, 1),
('projekt', 'buerocomplex_nord', 'Bürokomplex Nord', TRUE, 2),
('projekt', 'sanierung_altbau_sued', 'Sanierung Altbau Süd', TRUE, 3),
('projekt', 'neubau_kindergarten', 'Neubau Kindergarten', TRUE, 4),
('projekt', 'umbau_fabrikhalle', 'Umbau Fabrikhalle', TRUE, 5),
('projekt', 'energetische_sanierung', 'Energetische Sanierung Ost', TRUE, 6)
ON CONFLICT (field_name, value) DO NOTHING;

-- Gewerk (Trades/Crafts)
INSERT INTO dropdown_options (field_name, value, label, is_default, sort_order) VALUES
('gewerk', 'elektroinstallation', 'Elektroinstallation', TRUE, 1),
('gewerk', 'sanitaerinstallation', 'Sanitärinstallation', TRUE, 2),
('gewerk', 'heizung_lueftung', 'Heizung & Lüftung', TRUE, 3),
('gewerk', 'dacharbeiten', 'Dacharbeiten', TRUE, 4),
('gewerk', 'maurerarbeiten', 'Maurerarbeiten', TRUE, 5),
('gewerk', 'malerarbeiten', 'Malerarbeiten', TRUE, 6),
('gewerk', 'bodenverlegung', 'Bodenverlegung', TRUE, 7),
('gewerk', 'fenster_tueren', 'Fenster & Türen', TRUE, 8),
('gewerk', 'zimmerei', 'Zimmerei', TRUE, 9),
('gewerk', 'geruestbau', 'Gerüstbau', TRUE, 10)
ON CONFLICT (field_name, value) DO NOTHING;

-- Weiter berechnen an (Forward billing to)
INSERT INTO dropdown_options (field_name, value, label, is_default, sort_order) VALUES
('weiter_berechnen_an', 'bauleitung', 'Bauleitung', TRUE, 1),
('weiter_berechnen_an', 'projektmanagement', 'Projektmanagement', TRUE, 2),
('weiter_berechnen_an', 'buchhaltung', 'Buchhaltung', TRUE, 3),
('weiter_berechnen_an', 'auftraggeber', 'Auftraggeber', TRUE, 4),
('weiter_berechnen_an', 'externe_pruefung', 'Externe Prüfung', TRUE, 5)
ON CONFLICT (field_name, value) DO NOTHING;

-- Verify the setup
SELECT 
    field_name,
    COUNT(*) as total_options,
    COUNT(*) FILTER (WHERE is_default = TRUE) as default_options,
    COUNT(*) FILTER (WHERE is_default = FALSE) as custom_options
FROM dropdown_options 
WHERE is_active = TRUE
GROUP BY field_name
ORDER BY field_name;
