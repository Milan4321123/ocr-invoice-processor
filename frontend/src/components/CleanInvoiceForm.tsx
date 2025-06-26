'use client';

import React from 'react';
import { SearchableDropdown } from './SearchableDropdown';

// German invoice field types
export interface GermanInvoiceFields {
  rechnungsempfaenger?: string;
  rechnungssteller?: string;
  projekt?: string;
  gewerk?: string;
  rechnungsbetrag?: number;
  rechnungseingang?: string;
  faelligkeit?: string;
  skonto_datum?: string;
  skonto_prozent?: number;
  rechnungsart?: string;
  kfw_anrechenbar?: boolean;
  rechnungspruefung_email?: string;
  weiter_berechnen_an?: string;
}

interface CleanInvoiceFormProps {
  fields: GermanInvoiceFields;
  onFieldChange: (fieldName: string, value: any) => void;
  onSave: () => void;
  isSaving?: boolean;
  className?: string;
}

const CleanInvoiceForm: React.FC<CleanInvoiceFormProps> = ({
  fields,
  onFieldChange,
  onSave,
  isSaving = false,
  className = ""
}) => {
  // Dummy dropdown options - in real app these would come from API
  const dropdownOptions = {
    rechnungsempfaenger: [
      { value: 'acme-construction', label: 'ACME Construction GmbH', is_default: true },
      { value: 'bauleiter-office', label: 'Bauleiter Office', is_default: true }
    ],
    rechnungssteller: [
      { value: 'elektro-wagner', label: 'Elektro Wagner GmbH', is_default: true },
      { value: 'sanitaer-mueller', label: 'Sanitär Müller', is_default: true }
    ],
    projekt: [
      { value: 'projekt-alpha', label: 'Projekt Alpha - Bürogebäude', is_default: true },
      { value: 'projekt-beta', label: 'Projekt Beta - Wohnkomplex', is_default: true }
    ],
    gewerk: [
      { value: 'elektroinstallation', label: 'Elektroinstallation', is_default: true },
      { value: 'sanitaer', label: 'Sanitär', is_default: true }
    ]
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Invoice Details</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Dropdown fields */}
          <SearchableDropdown
            label="Rechnungsempfänger"
            value={fields.rechnungsempfaenger || ''}
            options={dropdownOptions.rechnungsempfaenger}
            onChange={(value) => onFieldChange('rechnungsempfaenger', value)}
            placeholder="Select recipient..."
          />
          
          <SearchableDropdown
            label="Rechnungssteller"
            value={fields.rechnungssteller || ''}
            options={dropdownOptions.rechnungssteller}
            onChange={(value) => onFieldChange('rechnungssteller', value)}
            placeholder="Select vendor..."
          />
          
          <SearchableDropdown
            label="Projekt"
            value={fields.projekt || ''}
            options={dropdownOptions.projekt}
            onChange={(value) => onFieldChange('projekt', value)}
            placeholder="Select project..."
          />
          
          <SearchableDropdown
            label="Gewerk"
            value={fields.gewerk || ''}
            options={dropdownOptions.gewerk}
            onChange={(value) => onFieldChange('gewerk', value)}
            placeholder="Select trade..."
          />

          {/* Text/Number inputs */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rechnungsbetrag
            </label>
            <input
              type="number"
              step="0.01"
              value={fields.rechnungsbetrag || ''}
              onChange={(e) => onFieldChange('rechnungsbetrag', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="0.00"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rechnungseingang
            </label>
            <input
              type="date"
              value={fields.rechnungseingang || ''}
              onChange={(e) => onFieldChange('rechnungseingang', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fälligkeit
            </label>
            <input
              type="date"
              value={fields.faelligkeit || ''}
              onChange={(e) => onFieldChange('faelligkeit', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Skonto Datum
            </label>
            <input
              type="date"
              value={fields.skonto_datum || ''}
              onChange={(e) => onFieldChange('skonto_datum', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Skonto Prozent
            </label>
            <input
              type="number"
              step="0.1"
              value={fields.skonto_prozent || ''}
              onChange={(e) => onFieldChange('skonto_prozent', parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="0.0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rechnungsart
            </label>
            <select
              value={fields.rechnungsart || 'rechnung'}
              onChange={(e) => onFieldChange('rechnungsart', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="rechnung">Rechnung</option>
              <option value="gutschrift">Gutschrift</option>
              <option value="mahnung">Mahnung</option>
            </select>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              checked={fields.kfw_anrechenbar || false}
              onChange={(e) => onFieldChange('kfw_anrechenbar', e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              KfW anrechenbar
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rechnungsprüfung Email
            </label>
            <input
              type="email"
              value={fields.rechnungspruefung_email || ''}
              onChange={(e) => onFieldChange('rechnungspruefung_email', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="email@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Weiter berechnen an
            </label>
            <input
              type="text"
              value={fields.weiter_berechnen_an || ''}
              onChange={(e) => onFieldChange('weiter_berechnen_an', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="Department or contact"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onSave}
            disabled={isSaving}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium disabled:bg-gray-400"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CleanInvoiceForm;
