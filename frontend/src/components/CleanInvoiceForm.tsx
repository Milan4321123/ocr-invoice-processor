'use client';

import React, { useState } from 'react';
import { Save, X, AlertCircle, CheckCircle } from 'lucide-react';

// German Invoice Fields Interface - Clean Version
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
  onFieldChange: (field: keyof GermanInvoiceFields, value: any) => void;
  onSave: (fields: GermanInvoiceFields, submitForReview?: boolean) => Promise<boolean>;
  onCancel: () => void;
  isLoading?: boolean;
  hasUnsavedChanges?: boolean;
  className?: string;
}

export default function CleanInvoiceForm({
  fields,
  onFieldChange,
  onSave,
  onCancel,
  isLoading = false,
  hasUnsavedChanges = false,
  className = ''
}: CleanInvoiceFormProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');

  const handleSave = async (submitForReview = false) => {
    setIsSaving(true);
    setSaveStatus('saving');
    
    try {
      const success = await onSave(fields, submitForReview);
      if (success) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus('idle'), 2000);
      } else {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Invoice Editor</h2>
        <div className="flex items-center space-x-2">
          {saveStatus === 'success' && (
            <div className="flex items-center text-green-600">
              <CheckCircle className="h-4 w-4 mr-1" />
              <span className="text-sm">Saved</span>
            </div>
          )}
          {saveStatus === 'error' && (
            <div className="flex items-center text-red-600">
              <AlertCircle className="h-4 w-4 mr-1" />
              <span className="text-sm">Save failed</span>
            </div>
          )}
          {hasUnsavedChanges && (
            <span className="text-sm text-orange-600">Unsaved changes</span>
          )}
        </div>
      </div>

      {/* Form Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Rechnungsempfänger */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rechnungsempfänger
          </label>
          <input
            type="text"
            value={fields.rechnungsempfaenger || ''}
            onChange={(e) => onFieldChange('rechnungsempfaenger', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter customer name"
          />
        </div>

        {/* Rechnungssteller */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rechnungssteller
          </label>
          <input
            type="text"
            value={fields.rechnungssteller || ''}
            onChange={(e) => onFieldChange('rechnungssteller', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter vendor name"
          />
        </div>

        {/* Projekt */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Projekt
          </label>
          <input
            type="text"
            value={fields.projekt || ''}
            onChange={(e) => onFieldChange('projekt', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter project name"
          />
        </div>

        {/* Gewerk */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Gewerk
          </label>
          <input
            type="text"
            value={fields.gewerk || ''}
            onChange={(e) => onFieldChange('gewerk', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter trade/craft"
          />
        </div>

        {/* Rechnungsbetrag */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rechnungsbetrag (€)
          </label>
          <input
            type="number"
            step="0.01"
            value={fields.rechnungsbetrag || ''}
            onChange={(e) => onFieldChange('rechnungsbetrag', parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="0.00"
          />
        </div>

        {/* Rechnungseingang */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rechnungseingang
          </label>
          <input
            type="date"
            value={fields.rechnungseingang || ''}
            onChange={(e) => onFieldChange('rechnungseingang', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Fälligkeit */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fälligkeit
          </label>
          <input
            type="date"
            value={fields.faelligkeit || ''}
            onChange={(e) => onFieldChange('faelligkeit', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Skonto Datum */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Skonto Datum
          </label>
          <input
            type="date"
            value={fields.skonto_datum || ''}
            onChange={(e) => onFieldChange('skonto_datum', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Skonto Prozent */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Skonto Prozent (%)
          </label>
          <input
            type="number"
            step="0.1"
            value={fields.skonto_prozent || ''}
            onChange={(e) => onFieldChange('skonto_prozent', parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="0.0"
          />
        </div>

        {/* Rechnungsart */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rechnungsart
          </label>
          <select
            value={fields.rechnungsart || 'rechnung'}
            onChange={(e) => onFieldChange('rechnungsart', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="rechnung">Rechnung</option>
            <option value="gutschrift">Gutschrift</option>
            <option value="mahnung">Mahnung</option>
            <option value="angebot">Angebot</option>
          </select>
        </div>

        {/* Rechnungsprüfung Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rechnungsprüfung Email
          </label>
          <input
            type="email"
            value={fields.rechnungspruefung_email || ''}
            onChange={(e) => onFieldChange('rechnungspruefung_email', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="email@example.com"
          />
        </div>

        {/* Weiter berechnen an */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Weiter berechnen an
          </label>
          <input
            type="text"
            value={fields.weiter_berechnen_an || ''}
            onChange={(e) => onFieldChange('weiter_berechnen_an', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter billing forwarding info"
          />
        </div>

        {/* KfW Anrechenbar */}
        <div className="md:col-span-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={fields.kfw_anrechenbar || false}
              onChange={(e) => onFieldChange('kfw_anrechenbar', e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">KfW Anrechenbar</span>
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-6 mt-6 border-t border-gray-200">
        <button
          onClick={onCancel}
          disabled={isSaving}
          className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 flex items-center"
        >
          <X className="h-4 w-4 mr-2" />
          Cancel
        </button>
        
        <div className="flex space-x-3">
          <button
            onClick={() => handleSave(false)}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 flex items-center"
          >
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          
          <button
            onClick={() => handleSave(true)}
            disabled={isSaving}
            className="px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 flex items-center"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            {isSaving ? 'Submitting...' : 'Submit for Review'}
          </button>
        </div>
      </div>
    </div>
  );
}
