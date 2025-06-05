-- Migration: Create dropdown_options table for persistent dropdown data
-- Date: 2025-06-05
-- Description: Move from hardcoded dropdown options to database-stored options

-- Create dropdown_options table
CREATE TABLE IF NOT EXISTS dropdown_options (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    field_name VARCHAR(100) NOT NULL,
    value VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dropdown_options_field_name ON dropdown_options(field_name);
CREATE INDEX IF NOT EXISTS idx_dropdown_options_active ON dropdown_options(field_name, is_active);

-- Create unique constraint to prevent duplicate options
CREATE UNIQUE INDEX IF NOT EXISTS idx_dropdown_options_unique 
ON dropdown_options(field_name, value) WHERE is_active = true;

-- Enable RLS (Row Level Security)
ALTER TABLE dropdown_options ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your auth requirements)
CREATE POLICY "Allow all operations on dropdown_options" ON dropdown_options
    FOR ALL USING (true) WITH CHECK (true);

-- Add trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dropdown_options_updated_at BEFORE UPDATE
    ON dropdown_options FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default hardcoded options as database records
-- Rechnungsempfänger (Invoice Recipients)
INSERT INTO dropdown_options (field_name, value, label, is_default, metadata) VALUES
('rechnungsempfaenger', 'acme_construction', 'ACME Construction GmbH', true, '{"contact": "info@acme-construction.de"}'),
('rechnungsempfaenger', 'baumeister_gmbh', 'Baumeister GmbH', true, '{"contact": "info@baumeister.de"}'),
('rechnungsempfaenger', 'hochbau_services', 'Hochbau Services AG', true, '{"contact": "office@hochbau-services.de"}'),
('rechnungsempfaenger', 'zimmerei_mueller', 'Zimmerei Müller & Co', true, '{"contact": "info@zimmerei-mueller.de"}'),
('rechnungsempfaenger', 'stadtwerke_berlin', 'Stadtwerke Berlin', true, '{"contact": "service@stadtwerke-berlin.de"}'),

-- Rechnungssteller (Invoice Issuers/Vendors)
('rechnungssteller', 'elektro_wagner', 'Elektro Wagner GmbH', true, '{"contact": "info@elektro-wagner.de", "phone": "+49 30 444555"}'),
('rechnungssteller', 'sanitaer_schmidt', 'Sanitär Schmidt & Söhne', true, '{"contact": "service@sanitaer-schmidt.de", "phone": "+49 421 999000"}'),
('rechnungssteller', 'dach_decken_pro', 'Dach & Decken Pro GmbH', true, '{"contact": "info@dach-decken-pro.de", "phone": "+49 89 123456"}'),
('rechnungssteller', 'heizung_klima_expert', 'Heizung & Klima Expert', true, '{"contact": "service@hk-expert.de", "phone": "+49 40 777888"}'),
('rechnungssteller', 'baumarkt_zentrale', 'Baumarkt Zentrale AG', true, '{"contact": "orders@baumarkt-zentrale.de", "phone": "+49 69 555666"}'),
('rechnungssteller', 'malerbetrieb_weiss', 'Malerbetrieb Weiß', true, '{"contact": "info@malerbetrieb-weiss.de", "phone": "+49 621 333444"}'),

-- Projekt (Projects)
('projekt', 'wohnbau_mitte_2024', 'Wohnbau Mitte 2024', true, '{"code": "WBM-2024-001", "location": "Berlin Mitte", "status": "active"}'),
('projekt', 'buerocomplex_nord', 'Bürokomplex Nord', true, '{"code": "BCN-2024-002", "location": "Hamburg Nord", "status": "active"}'),
('projekt', 'sanierung_altbau_sued', 'Sanierung Altbau Süd', true, '{"code": "SAS-2024-003", "location": "München Süd", "status": "active"}'),
('projekt', 'neubau_kindergarten', 'Neubau Kindergarten', true, '{"code": "NKG-2024-004", "location": "Köln", "status": "active"}'),
('projekt', 'umbau_fabrikhalle', 'Umbau Fabrikhalle', true, '{"code": "UFH-2024-005", "location": "Dresden", "status": "active"}'),
('projekt', 'energetische_sanierung', 'Energetische Sanierung Ost', true, '{"code": "ESO-2024-006", "location": "Leipzig", "status": "active"}'),

-- Gewerk (Trades/Crafts)
('gewerk', 'elektroinstallation', 'Elektroinstallation', true, '{"category": "technical", "code": "ELK"}'),
('gewerk', 'sanitaerinstallation', 'Sanitärinstallation', true, '{"category": "technical", "code": "SAN"}'),
('gewerk', 'heizung_lueftung', 'Heizung & Lüftung', true, '{"category": "technical", "code": "HLK"}'),
('gewerk', 'dacharbeiten', 'Dacharbeiten', true, '{"category": "construction", "code": "DAC"}'),
('gewerk', 'maurerarbeiten', 'Maurerarbeiten', true, '{"category": "construction", "code": "MAU"}'),
('gewerk', 'malerarbeiten', 'Malerarbeiten', true, '{"category": "finishing", "code": "MAL"}'),
('gewerk', 'bodenverlegung', 'Bodenverlegung', true, '{"category": "finishing", "code": "BOD"}'),
('gewerk', 'fenster_tueren', 'Fenster & Türen', true, '{"category": "construction", "code": "FEN"}'),
('gewerk', 'zimmerei', 'Zimmerei', true, '{"category": "construction", "code": "ZIM"}'),
('gewerk', 'geruestbau', 'Gerüstbau', true, '{"category": "construction", "code": "GER"}');

-- Verify the migration
SELECT 
    field_name,
    COUNT(*) as option_count,
    COUNT(*) FILTER (WHERE is_default = true) as default_count,
    COUNT(*) FILTER (WHERE is_default = false) as custom_count
FROM dropdown_options 
WHERE is_active = true
GROUP BY field_name
ORDER BY field_name;
