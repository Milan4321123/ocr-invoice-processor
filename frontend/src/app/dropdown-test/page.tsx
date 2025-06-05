/**
 * Simple test page to demonstrate dropdown functionality
 */
'use client';

import React, { useState, useEffect } from 'react';
import { SearchableDropdown } from '../../components/SearchableDropdown';
import { dropdownService, DropdownOption } from '../../services/dropdown';

export default function DropdownTestPage() {
  const [dropdownOptions, setDropdownOptions] = useState<Record<string, DropdownOption[]>>({});
  const [selectedValues, setSelectedValues] = useState({
    rechnungsempfaenger: '',
    rechnungssteller: '',
    projekt: '',
    gewerk: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDropdowns = async () => {
      try {
        setLoading(true);
        const response = await dropdownService.getAllDropdownOptions();
        setDropdownOptions(response.dropdowns);
      } catch (error) {
        console.error('Failed to load dropdowns:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDropdowns();
  }, []);

  const handleValueChange = (field: string, value: string) => {
    setSelectedValues(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddNew = async (field: string, newValue: string) => {
    try {
      const response = await dropdownService.addDropdownOption({
        field_name: field,
        value: newValue,
        label: newValue
      });

      if (response.success) {
        if (response.duplicate_detected) {
          // Option already exists, but backend returned it anyway
          console.log(`Option "${newValue}" already exists in ${field}`);
          alert(`Option "${newValue}" already exists in ${field}`);
          return;
        }

        // Update local options - check if it already exists to prevent duplicates
        if (response.option) {
          setDropdownOptions(prev => {
            const currentOptions = prev[field] || [];
            const exists = currentOptions.some(opt => 
              opt.value === response.option!.value || 
              opt.label === response.option!.label
            );
            
            if (exists) {
              return prev; // Don't add duplicate
            }
            
            return {
              ...prev,
              [field]: [...currentOptions, response.option!]
            };
          });

          // Set the new value as selected
          setSelectedValues(prev => ({
            ...prev,
            [field]: response.option!.value
          }));

          alert(`Successfully added "${newValue}" to ${field}!`);
        }
      } else {
        // Handle potential duplicates from backend
        if (response.duplicate_detected && response.potential_duplicates) {
          const duplicateList = response.potential_duplicates
            .map((dup: any) => `"${dup.existing_option.label}" (${Math.round(dup.similarity * 100)}% similar)`)
            .join('\n');
          
          const confirmed = confirm(
            `Potential duplicates found:\n${duplicateList}\n\nDo you still want to add "${newValue}"?`
          );
          
          if (confirmed && response.suggested_option) {
            // Force add the option locally
            setDropdownOptions(prev => ({
              ...prev,
              [field]: [...(prev[field] || []), response.suggested_option!]
            }));
            
            setSelectedValues(prev => ({
              ...prev,
              [field]: response.suggested_option!.value
            }));
            
            alert(`Added "${newValue}" locally (bypassed duplicate detection)`);
          }
        } else {
          alert(`Failed to add option: ${response.message || 'Unknown error'}`);
        }
      }
    } catch (error) {
      console.error(`Failed to add option to ${field}:`, error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      // Still set locally as fallback, but check for duplicates first
      setDropdownOptions(prev => {
        const currentOptions = prev[field] || [];
        const exists = currentOptions.some(opt => 
          opt.value.toLowerCase() === newValue.toLowerCase() || 
          opt.label.toLowerCase() === newValue.toLowerCase()
        );
        
        if (exists) {
          alert(`Option "${newValue}" already exists locally`);
          return prev;
        }
        
        return {
          ...prev,
          [field]: [...currentOptions, {
            value: newValue.toLowerCase().replace(/\s+/g, '_'),
            label: newValue,
            is_default: false
          }]
        };
      });
      
      setSelectedValues(prev => ({
        ...prev,
        [field]: newValue.toLowerCase().replace(/\s+/g, '_')
      }));
      
      alert(`Added "${newValue}" locally (API error: ${errorMessage})`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dropdown options...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            German Invoice Dropdown Test
          </h1>
          <p className="text-gray-600 mb-8">
            Test the searchable dropdown functionality with hardcoded German invoice options.
            You can search existing options or add new ones.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SearchableDropdown
              label="Rechnungsempfänger (Invoice Recipient)"
              value={selectedValues.rechnungsempfaenger}
              options={dropdownOptions.rechnungsempfaenger || []}
              onChange={(value) => handleValueChange('rechnungsempfaenger', value)}
              onAddNew={(newValue) => handleAddNew('rechnungsempfaenger', newValue)}
              placeholder="Select or add recipient..."
            />

            <SearchableDropdown
              label="Rechnungssteller (Invoice Issuer)"
              value={selectedValues.rechnungssteller}
              options={dropdownOptions.rechnungssteller || []}
              onChange={(value) => handleValueChange('rechnungssteller', value)}
              onAddNew={(newValue) => handleAddNew('rechnungssteller', newValue)}
              placeholder="Select or add issuer..."
            />

            <SearchableDropdown
              label="Projekt (Project)"
              value={selectedValues.projekt}
              options={dropdownOptions.projekt || []}
              onChange={(value) => handleValueChange('projekt', value)}
              onAddNew={(newValue) => handleAddNew('projekt', newValue)}
              placeholder="Select or add project..."
            />

            <SearchableDropdown
              label="Gewerk (Trade/Work Type)"
              value={selectedValues.gewerk}
              options={dropdownOptions.gewerk || []}
              onChange={(value) => handleValueChange('gewerk', value)}
              onAddNew={(newValue) => handleAddNew('gewerk', newValue)}
              placeholder="Select or add trade type..."
            />
          </div>

          {/* Display current selections */}
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Current Selections:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Rechnungsempfänger:</span>{' '}
                <span className="text-blue-600">{selectedValues.rechnungsempfaenger || 'None'}</span>
              </div>
              <div>
                <span className="font-medium">Rechnungssteller:</span>{' '}
                <span className="text-blue-600">{selectedValues.rechnungssteller || 'None'}</span>
              </div>
              <div>
                <span className="font-medium">Projekt:</span>{' '}
                <span className="text-blue-600">{selectedValues.projekt || 'None'}</span>
              </div>
              <div>
                <span className="font-medium">Gewerk:</span>{' '}
                <span className="text-blue-600">{selectedValues.gewerk || 'None'}</span>
              </div>
            </div>
          </div>

          {/* Statistics */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Dropdown Statistics:</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {dropdownOptions.rechnungsempfaenger?.length || 0}
                </div>
                <div className="text-gray-600">Recipients</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {dropdownOptions.rechnungssteller?.length || 0}
                </div>
                <div className="text-gray-600">Issuers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {dropdownOptions.projekt?.length || 0}
                </div>
                <div className="text-gray-600">Projects</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {dropdownOptions.gewerk?.length || 0}
                </div>
                <div className="text-gray-600">Trades</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
