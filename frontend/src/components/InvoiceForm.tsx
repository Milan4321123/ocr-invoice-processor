'use client';

import React, { useState, useEffect } from 'react';
import { Save, X, AlertCircle, CheckCircle, Clock } from 'lucide-react';

// German Invoice Fields Interface
export interface GermanInvoiceFields {
  rechnungsempfaenger?: string;
  rechnungsempfaenger_id?: string;
  rechnungssteller?: string;
  rechnungssteller_id?: string;
  projekt?: string;
  projekt_id?: string;
  gewerk?: string;
  gewerk_id?: string;
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

export interface ConfidenceScores {
  [key: string]: number;
}

interface InvoiceFormProps {
  fields: GermanInvoiceFields;
  confidenceScores: ConfidenceScores;
  onFieldChange: (field: keyof GermanInvoiceFields, value: any) => void;
  onSave: (fields: GermanInvoiceFields) => Promise<boolean>;
  onCancel: () => void;
  isLoading?: boolean;
  hasUnsavedChanges?: boolean;
  className?: string;
}

// Confidence indicator component
const ConfidenceIndicator = ({ score }: { score?: number }) => {
  if (score === undefined) return null;
  
  const getColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle size={14} />;
    if (score >= 0.6) return <Clock size={14} />;
    return <AlertCircle size={14} />;
  };

  return (
    <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getColor(score)}`}>
      {getIcon(score)}
      <span>{Math.round(score * 100)}%</span>
    </div>
  );
};

// Form field component with confidence indicator
const FormField = ({ 
  label, 
  value, 
  onChange, 
  confidence, 
  type = 'text', 
  required = false,
  placeholder = '',
  options = [] 
}: {
  label: string;
  value: any;
  onChange: (value: any) => void;
  confidence?: number;
  type?: 'text' | 'email' | 'number' | 'date' | 'select' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
}) => {
  const inputClasses = `
    w-full px-3 py-2 border border-gray-300 rounded-md 
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
    ${confidence && confidence < 0.6 ? 'border-yellow-300 bg-yellow-50' : ''}
  `;

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <ConfidenceIndicator score={confidence} />
      </div>
      
      {type === 'select' ? (
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className={inputClasses}
        >
          <option value="">{placeholder || `Select ${label}`}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === 'checkbox' ? (
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={value || false}
            onChange={(e) => onChange(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-600">{placeholder}</span>
        </div>
      ) : (
        <input
          type={type}
          value={value || ''}
          onChange={(e) => onChange(type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)}
          placeholder={placeholder}
          className={inputClasses}
          step={type === 'number' ? '0.01' : undefined}
        />
      )}
    </div>
  );
};

export default function InvoiceForm({ 
  fields,
  confidenceScores,
  onFieldChange,
  onSave, 
  onCancel, 
  isLoading = false,
  hasUnsavedChanges = false,
  className = "" 
}: InvoiceFormProps) {
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const success = await onSave(fields);
      if (!success) {
        throw new Error('Save failed');
      }
    } catch (error) {
      console.error('Save failed:', error);
      // TODO: Show error toast/notification
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (hasUnsavedChanges) {
      if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
        onCancel();
      }
    } else {
      onCancel();
    }
  };

  // Mock options for dropdowns (in real app, these would come from SharePoint)
  const rechnungsartOptions = [
    { value: 'rechnung', label: 'Rechnung' },
    { value: 'abschlagsrechnung', label: 'Abschlagsrechnung' },
    { value: 'schlussrechnung', label: 'Schlussrechnung' },
    { value: 'gutschrift', label: 'Gutschrift' }
  ];

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Invoice Editor
          </h2>
          <p className="text-sm text-gray-600">
            Edit extracted invoice fields
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors flex items-center space-x-1"
          >
            <X size={16} />
            <span>Cancel</span>
          </button>
          
          <button
            onClick={handleSave}
            disabled={!hasUnsavedChanges || isSaving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1"
          >
            <Save size={16} />
            <span>{isSaving ? 'Saving...' : 'Save'}</span>
          </button>
        </div>
      </div>

      {/* Form Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        
        {/* Basic Information */}
        <div className="space-y-4">
          <h3 className="text-md font-medium text-gray-900 border-b pb-2">
            Basic Information
          </h3>
          
          <div className="grid grid-cols-1 gap-4">
            <FormField
              label="Rechnungsempfänger (Invoice Recipient)"
              value={fields.rechnungsempfaenger}
              onChange={(value) => onFieldChange('rechnungsempfaenger', value)}
              confidence={confidenceScores.rechnungsempfaenger}
              placeholder="Enter recipient name"
              required
            />
            
            <FormField
              label="Rechnungssteller (Invoice Issuer)"
              value={fields.rechnungssteller}
              onChange={(value) => onFieldChange('rechnungssteller', value)}
              confidence={confidenceScores.rechnungssteller}
              placeholder="Enter issuer name"
              required
            />
            
            <FormField
              label="Rechnungsart (Invoice Type)"
              value={fields.rechnungsart}
              onChange={(value) => onFieldChange('rechnungsart', value)}
              confidence={confidenceScores.rechnungsart}
              type="select"
              options={rechnungsartOptions}
            />
          </div>
        </div>

        {/* Project Information */}
        <div className="space-y-4">
          <h3 className="text-md font-medium text-gray-900 border-b pb-2">
            Project Information
          </h3>
          
          <div className="grid grid-cols-1 gap-4">
            <FormField
              label="Projekt (Project)"
              value={fields.projekt}
              onChange={(value) => onFieldChange('projekt', value)}
              confidence={confidenceScores.projekt}
              placeholder="Enter project name"
            />
            
            <FormField
              label="Gewerk (Trade/Work Type)"
              value={fields.gewerk}
              onChange={(value) => onFieldChange('gewerk', value)}
              confidence={confidenceScores.gewerk}
              placeholder="Enter trade/work type"
            />
          </div>
        </div>

        {/* Financial Information */}
        <div className="space-y-4">
          <h3 className="text-md font-medium text-gray-900 border-b pb-2">
            Financial Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              label="Rechnungsbetrag (Invoice Amount)"
              value={fields.rechnungsbetrag}
              onChange={(value) => onFieldChange('rechnungsbetrag', value)}
              confidence={confidenceScores.rechnungsbetrag}
              type="number"
              placeholder="0.00"
              required
            />
            
            <FormField
              label="Skonto Prozent (Early Payment Discount %)"
              value={fields.skonto_prozent}
              onChange={(value) => onFieldChange('skonto_prozent', value)}
              confidence={confidenceScores.skonto_prozent}
              type="number"
              placeholder="0.00"
            />
          </div>
        </div>

        {/* Dates */}
        <div className="space-y-4">
          <h3 className="text-md font-medium text-gray-900 border-b pb-2">
            Important Dates
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormField
              label="Rechnungseingang (Receipt Date)"
              value={fields.rechnungseingang}
              onChange={(value) => onFieldChange('rechnungseingang', value)}
              confidence={confidenceScores.rechnungseingang}
              type="date"
            />
            
            <FormField
              label="Fälligkeit (Due Date)"
              value={fields.faelligkeit}
              onChange={(value) => onFieldChange('faelligkeit', value)}
              confidence={confidenceScores.faelligkeit}
              type="date"
            />
            
            <FormField
              label="Skonto Datum (Early Payment Date)"
              value={fields.skonto_datum}
              onChange={(value) => onFieldChange('skonto_datum', value)}
              confidence={confidenceScores.skonto_datum}
              type="date"
            />
          </div>
        </div>

        {/* Additional Information */}
        <div className="space-y-4">
          <h3 className="text-md font-medium text-gray-900 border-b pb-2">
            Additional Information
          </h3>
          
          <div className="space-y-4">
            <FormField
              label="KfW Anrechenbar (KfW Eligible)"
              value={fields.kfw_anrechenbar}
              onChange={(value) => onFieldChange('kfw_anrechenbar', value)}
              type="checkbox"
              placeholder="This invoice contains KfW eligible costs"
            />
            
            <FormField
              label="Rechnungsprüfung E-Mail (Review Email)"
              value={fields.rechnungspruefung_email}
              onChange={(value) => onFieldChange('rechnungspruefung_email', value)}
              type="email"
              placeholder="review@company.com"
            />
            
            <FormField
              label="Weiter berechnen an (Forward billing to)"
              value={fields.weiter_berechnen_an}
              onChange={(value) => onFieldChange('weiter_berechnen_an', value)}
              placeholder="Enter billing forward recipient"
            />
          </div>
        </div>
      </div>

      {/* Footer with change indicator */}
      {hasUnsavedChanges && (
        <div className="px-4 py-2 bg-yellow-50 border-t border-yellow-200">
          <p className="text-sm text-yellow-800">
            You have unsaved changes. Don't forget to save your work!
          </p>
        </div>
      )}
    </div>
  );
}
