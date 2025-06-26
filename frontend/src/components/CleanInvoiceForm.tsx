'use client';

import React, { useState, useEffect } from 'react';
import { SearchableDropdown } from './SearchableDropdown';
import { dropdownService, DropdownOption } from '@/services/dropdown';

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

// Change tracking interfaces
interface PendingChange {
  type: 'add' | 'delete';
  fieldName: string;
  optionValue: string;
  optionLabel: string;
  timestamp: string;
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
  const [dropdownOptions, setDropdownOptions] = useState<Record<string, DropdownOption[]>>({
    rechnungsempfaenger: [],
    rechnungssteller: [],
    projekt: [],
    gewerk: [],
    weiter_berechnen_an: []
  });
  const [pendingChanges, setPendingChanges] = useState<PendingChange[]>([]);
  const [isCommittingChanges, setIsCommittingChanges] = useState(false);

  // Load dropdown options from API
  const loadDropdownOptions = async () => {
    try {
      const response = await dropdownService.getAllDropdownOptions();
      setDropdownOptions(response.dropdowns);
    } catch (error) {
      console.error('Failed to load dropdown options:', error);
    }
  };

  useEffect(() => {
    loadDropdownOptions();
  }, []);

  // Check if user has provided email before allowing changes
  const requireEmailForChanges = (): boolean => {
    const userEmail = fields.rechnungspruefung_email?.trim();
    if (!userEmail) {
      alert('Bitte geben Sie zuerst Ihre E-Mail-Adresse im Feld "Rechnungsprüfung Email" ein, bevor Sie Dropdown-Optionen bearbeiten können.');
      return false;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(userEmail)) {
      alert('Bitte geben Sie eine gültige E-Mail-Adresse ein.');
      return false;
    }
    
    return true;
  };

  // Add change to pending list
  const addPendingChange = (change: Omit<PendingChange, 'timestamp'>) => {
    const newChange: PendingChange = {
      ...change,
      timestamp: new Date().toISOString()
    };
    
    setPendingChanges(prev => [...prev, newChange]);
  };

  // Handle adding new dropdown option (staged)
  const handleAddNewOption = async (fieldName: string, newValue: string) => {
    if (!requireEmailForChanges()) {
      return;
    }

    // Add to local state immediately for UI feedback
    const newOption = {
      value: newValue.toLowerCase().replace(/\s+/g, '_'),
      label: newValue,
      is_default: false
    };

    setDropdownOptions(prev => ({
      ...prev,
      [fieldName]: [...prev[fieldName], newOption]
    }));

    // Track the change for later commit
    addPendingChange({
      type: 'add',
      fieldName,
      optionValue: newOption.value,
      optionLabel: newValue
    });

    // Set the new value in the form
    onFieldChange(fieldName, newOption.value);
  };

  // Handle deleting dropdown option (staged)
  const handleDeleteOption = async (fieldName: string, optionValue: string) => {
    const option = dropdownOptions[fieldName]?.find(opt => opt.value === optionValue);
    if (!option) return;

    if (!requireEmailForChanges()) {
      return;
    }

    // Remove from local state immediately for UI feedback
    setDropdownOptions(prev => ({
      ...prev,
      [fieldName]: prev[fieldName].filter(option => option.value !== optionValue)
    }));

    // Track the change for later commit
    addPendingChange({
      type: 'delete',
      fieldName,
      optionValue: option.value,
      optionLabel: option.label
    });

    // Clear field value if it was the deleted option
    if (fields[fieldName as keyof GermanInvoiceFields] === optionValue) {
      onFieldChange(fieldName, '');
    }
  };

  // Send email notification
  const sendChangeNotificationEmail = async (email: string, changes: any[]) => {
    console.log('🚀 sendChangeNotificationEmail called with:', { email, changes });
    
    try {
      console.log('📧 Making email request to /api/email/dropdown-change-notification');
      
      const response = await fetch('/api/email/dropdown-change-notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_email: email,
          changes
        })
      });
      
      console.log('📨 Email response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ Email response error:', errorData);
        throw new Error(errorData.detail || 'Failed to send email notification');
      }
      
      const result = await response.json();
      console.log('✅ Email notification sent successfully:', result.message_id);
      
    } catch (error) {
      console.error('❌ Email notification failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`❌ Email failed: ${errorMessage}`);
    }
  };

  // Commit all pending changes to database and send email notification
  const commitPendingChanges = async () => {
    const userEmail = fields.rechnungspruefung_email?.trim();
    if (!userEmail) {
      alert('Bitte geben Sie zuerst Ihre E-Mail-Adresse im Feld "Rechnungsprüfung Email" ein.');
      return;
    }

    if (pendingChanges.length === 0) {
      return; // No changes to commit
    }

    setIsCommittingChanges(true);
    
    try {
      const results = [];
      
      for (const change of pendingChanges) {
        if (change.type === 'add') {
          const response = await dropdownService.addDropdownOption({
            field_name: change.fieldName,
            value: change.optionValue,
            label: change.optionLabel
          });
          results.push({...change, success: response.success});
        } else if (change.type === 'delete') {
          try {
            await dropdownService.deleteDropdownOption(change.fieldName, change.optionValue);
            results.push({...change, success: true});
          } catch (error) {
            results.push({...change, success: false, error: error});
          }
        }
      }

      // Send email notification
      await sendChangeNotificationEmail(userEmail, results);
      
      // Clear pending changes
      setPendingChanges([]);

      alert(`Änderungen erfolgreich gespeichert! Bestätigungs-E-Mail wurde an ${userEmail} gesendet.`);
      
    } catch (error) {
      console.error('Failed to commit changes:', error);
      alert('Fehler beim Speichern der Änderungen. Bitte versuchen Sie es erneut.');
    } finally {
      setIsCommittingChanges(false);
    }
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header with Save Buttons */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Rechnungsdetails</h3>
            <p className="text-sm text-gray-500 mt-1">Füllen Sie die Rechnungsinformationen unten aus</p>
          </div>
          
          {/* Top-right Action Buttons */}
          <div className="flex items-center gap-3">
            {/* Pending Changes Indicator */}
            {pendingChanges.length > 0 && (
              <div className="flex items-center gap-2 px-3 py-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-yellow-700">
                  {pendingChanges.length} ausstehende Änderung{pendingChanges.length !== 1 ? 'en' : ''}
                </span>
              </div>
            )}
            
            {/* Dropdown Changes Save Button */}
            <button
              onClick={async () => {
                if (pendingChanges.length > 0) {
                  await commitPendingChanges();
                }
              }}
              disabled={isCommittingChanges || pendingChanges.length === 0}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                pendingChanges.length > 0 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg' 
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              {isCommittingChanges ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Wird gespeichert...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  <span>Dropdown-Änderungen speichern</span>
                </>
              )}
            </button>

            {/* Main Invoice Save Button */}
            <button
              onClick={onSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200 disabled:bg-gray-400"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Rechnung wird gespeichert...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Rechnung speichern</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Form Content - Scrollable */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="p-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Dropdown Fields */}
          <div className="space-y-6">
            <SearchableDropdown
              label="Rechnungsempfänger"
              value={fields.rechnungsempfaenger || ''}
              options={dropdownOptions.rechnungsempfaenger}
              onChange={(value) => onFieldChange('rechnungsempfaenger', value)}
              onAddNew={(newValue) => handleAddNewOption('rechnungsempfaenger', newValue)}
              onDelete={(optionValue) => handleDeleteOption('rechnungsempfaenger', optionValue)}
              placeholder="Empfänger auswählen..."
            />

            <SearchableDropdown
              label="Rechnungssteller"
              value={fields.rechnungssteller || ''}
              options={dropdownOptions.rechnungssteller}
              onChange={(value) => onFieldChange('rechnungssteller', value)}
              onAddNew={(newValue) => handleAddNewOption('rechnungssteller', newValue)}
              onDelete={(optionValue) => handleDeleteOption('rechnungssteller', optionValue)}
              placeholder="Aussteller auswählen..."
            />

            <SearchableDropdown
              label="Projekt"
              value={fields.projekt || ''}
              options={dropdownOptions.projekt}
              onChange={(value) => onFieldChange('projekt', value)}
              onAddNew={(newValue) => handleAddNewOption('projekt', newValue)}
              onDelete={(optionValue) => handleDeleteOption('projekt', optionValue)}
              placeholder="Projekt auswählen..."
            />

            <SearchableDropdown
              label="Gewerk"
              value={fields.gewerk || ''}
              options={dropdownOptions.gewerk}
              onChange={(value) => onFieldChange('gewerk', value)}
              onAddNew={(newValue) => handleAddNewOption('gewerk', newValue)}
              onDelete={(optionValue) => handleDeleteOption('gewerk', optionValue)}
              placeholder="Gewerk auswählen..."
            />

            <SearchableDropdown
              label="Weiter berechnen an"
              value={fields.weiter_berechnen_an || ''}
              options={dropdownOptions.weiter_berechnen_an}
              onChange={(value) => onFieldChange('weiter_berechnen_an', value)}
              onAddNew={(newValue) => handleAddNewOption('weiter_berechnen_an', newValue)}
              onDelete={(optionValue) => handleDeleteOption('weiter_berechnen_an', optionValue)}
              placeholder="Abteilung oder Kontakt auswählen..."
            />
          </div>

          {/* Input Fields */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rechnungsbetrag
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">€</span>
                <input
                  type="number"
                  step="0.01"
                  value={fields.rechnungsbetrag || ''}
                  onChange={(e) => onFieldChange('rechnungsbetrag', parseFloat(e.target.value) || 0)}
                  className="w-full pl-8 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rechnungseingang
              </label>
              <input
                type="date"
                value={fields.rechnungseingang || ''}
                onChange={(e) => onFieldChange('rechnungseingang', e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fälligkeit
              </label>
              <input
                type="date"
                value={fields.faelligkeit || ''}
                onChange={(e) => onFieldChange('faelligkeit', e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skonto Datum
                </label>
                <input
                  type="date"
                  value={fields.skonto_datum || ''}
                  onChange={(e) => onFieldChange('skonto_datum', e.target.value)}
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skonto Prozent
                </label>
                <div className="relative">
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={fields.skonto_prozent || ''}
                    onChange={(e) => onFieldChange('skonto_prozent', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="0.00"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">%</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rechnungsart
              </label>
              <select
                value={fields.rechnungsart || ''}
                onChange={(e) => onFieldChange('rechnungsart', e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Typ auswählen...</option>
                <option value="rechnung">Rechnung</option>
                <option value="gutschrift">Gutschrift</option>
                <option value="mahnung">Mahnung</option>
              </select>
            </div>

            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <input
                type="checkbox"
                checked={fields.kfw_anrechenbar || false}
                onChange={(e) => onFieldChange('kfw_anrechenbar', e.target.checked)}
                className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label className="ml-3 block text-sm font-medium text-gray-700">
                KfW anrechenbar
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rechnungsprüfung Email *
              </label>
              <input
                type="email"
                value={fields.rechnungspruefung_email || ''}
                onChange={(e) => onFieldChange('rechnungspruefung_email', e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="email@beispiel.de"
                required
              />
              <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Erforderlich für Dropdown-Änderungen und E-Mail-Benachrichtigungen
              </p>
            </div>
          </div>
        </div>

        {/* Discard Changes Option */}
        {pendingChanges.length > 0 && (
          <div className="mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={() => {
                setPendingChanges([]);
                loadDropdownOptions(); // Reload to reset UI
              }}
              className="flex items-center gap-2 text-red-600 hover:text-red-700 font-medium transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>Alle Änderungen verwerfen</span>
            </button>
          </div>
        )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CleanInvoiceForm;
