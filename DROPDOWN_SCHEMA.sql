-- Required database tables for dropdown system

-- 1. Dropdown options table
CREATE TABLE public.dropdown_options (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  field_name character varying(100) NOT NULL,
  value character varying(255) NOT NULL,
  label character varying(255) NOT NULL,
  is_default boolean NOT NULL DEFAULT false,
  is_active boolean NOT NULL DEFAULT true,
  sort_order integer DEFAULT 0,
  metadata jsonb NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  
  CONSTRAINT dropdown_options_pkey PRIMARY KEY (id),
  CONSTRAINT dropdown_options_unique_field_value UNIQUE (field_name, value),
  CONSTRAINT dropdown_options_valid_fields CHECK (
    field_name = ANY (
      ARRAY[
        'rechnungsempfaenger'::text,
        'rechnungssteller'::text,
        'projekt'::text,
        'gewerk'::text,
        'rechnungsart'::text,
        'rechnungspruefung'::text
      ]
    )
  )
) TABLESPACE pg_default;

-- 2. Indexes for performance
CREATE INDEX idx_dropdown_options_field_name ON public.dropdown_options (field_name);
CREATE INDEX idx_dropdown_options_active ON public.dropdown_options (is_active);
CREATE INDEX idx_dropdown_options_field_active ON public.dropdown_options (field_name, is_active);

-- 3. Insert default options
INSERT INTO public.dropdown_options (field_name, value, label, is_default, sort_order) VALUES
-- rechnungsempfaenger (Invoice Recipients)
('rechnungsempfaenger', 'acme_construction', 'ACME Construction GmbH', true, 1),
('rechnungsempfaenger', 'baumeister_gmbh', 'Baumeister GmbH', true, 2),
('rechnungsempfaenger', 'hochbau_services', 'Hochbau Services AG', true, 3),
('rechnungsempfaenger', 'zimmerei_mueller', 'Zimmerei Müller & Co', true, 4),
('rechnungsempfaenger', 'stadtwerke_berlin', 'Stadtwerke Berlin', true, 5),

-- rechnungssteller (Invoice Senders/Vendors)
('rechnungssteller', 'elektro_wagner', 'Elektro Wagner GmbH', true, 1),
('rechnungssteller', 'sanitaer_schmidt', 'Sanitär Schmidt & Söhne', true, 2),
('rechnungssteller', 'dach_decken_pro', 'Dach & Decken Pro GmbH', true, 3),
('rechnungssteller', 'heizung_klima_expert', 'Heizung & Klima Expert', true, 4),
('rechnungssteller', 'baumarkt_zentrale', 'Baumarkt Zentrale AG', true, 5),
('rechnungssteller', 'malerbetrieb_weiss', 'Malerbetrieb Weiß', true, 6),

-- projekt (Projects)
('projekt', 'wohnbau_mitte_2024', 'Wohnbau Mitte 2024', true, 1),
('projekt', 'buerocomplex_nord', 'Bürokomplex Nord', true, 2),
('projekt', 'sanierung_altbau_sued', 'Sanierung Altbau Süd', true, 3),
('projekt', 'neubau_kindergarten', 'Neubau Kindergarten', true, 4),
('projekt', 'umbau_fabrikhalle', 'Umbau Fabrikhalle', true, 5),
('projekt', 'energetische_sanierung', 'Energetische Sanierung Ost', true, 6),

-- gewerk (Trades/Work Types)
('gewerk', 'elektroinstallation', 'Elektroinstallation', true, 1),
('gewerk', 'sanitaerinstallation', 'Sanitärinstallation', true, 2),
('gewerk', 'heizung_lueftung', 'Heizung & Lüftung', true, 3),
('gewerk', 'dacharbeiten', 'Dacharbeiten', true, 4),
('gewerk', 'maurerarbeiten', 'Maurerarbeiten', true, 5),
('gewerk', 'malerarbeiten', 'Malerarbeiten', true, 6),
('gewerk', 'bodenverlegung', 'Bodenverlegung', true, 7),
('gewerk', 'fenster_tueren', 'Fenster & Türen', true, 8),
('gewerk', 'zimmerei', 'Zimmerei', true, 9),
('gewerk', 'geruestbau', 'Gerüstbau', true, 10),

-- rechnungsart (Invoice Types)
('rechnungsart', 'abschlagsrechnung', 'Abschlagsrechnung', true, 1),
('rechnungsart', 'schlussrechnung', 'Schlussrechnung', true, 2),
('rechnungsart', 'teilrechnung', 'Teilrechnung', true, 3),
('rechnungsart', 'anzahlungsrechnung', 'Anzahlungsrechnung', true, 4),
('rechnungsart', 'stornorechnung', 'Stornorechnung', true, 5),

-- rechnungspruefung (Invoice Review Status)
('rechnungspruefung', 'nicht_geprueft', 'Nicht geprüft', true, 1),
('rechnungspruefung', 'in_pruefung', 'In Prüfung', true, 2),
('rechnungspruefung', 'geprueft_ok', 'Geprüft - OK', true, 3),
('rechnungspruefung', 'geprueft_korrektur', 'Geprüft - Korrektur erforderlich', true, 4),
('rechnungspruefung', 'freigegeben', 'Freigegeben', true, 5),
('rechnungspruefung', 'abgelehnt', 'Abgelehnt', true, 6);
