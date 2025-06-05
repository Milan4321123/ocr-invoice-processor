/**
 * SearchableDropdown Component
 * A reusable dropdown component with search functionality and "Add New" capability
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Plus, X } from 'lucide-react';
import { DropdownOption } from '@/services/dropdown';

interface SearchableDropdownProps {
  label: string;
  value: string;
  options: DropdownOption[];
  onChange: (value: string) => void;
  onAddNew?: (newValue: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  showAddNew?: boolean;
}

export const SearchableDropdown: React.FC<SearchableDropdownProps> = ({
  label,
  value,
  options,
  onChange,
  onAddNew,
  placeholder = "Select an option...",
  disabled = false,
  className = "",
  showAddNew = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newOptionValue, setNewOptionValue] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter options based on search term
  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    option.value.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get display value for selected option
  const selectedOption = options.find(opt => opt.value === value);
  const displayValue = selectedOption ? selectedOption.label : value;

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleAddNew = () => {
    if (newOptionValue.trim() && onAddNew) {
      const trimmedValue = newOptionValue.trim();
      
      // Check for exact duplicates first
      const exactDuplicate = options.find(option => 
        option.value.toLowerCase() === trimmedValue.toLowerCase() ||
        option.label.toLowerCase() === trimmedValue.toLowerCase()
      );
      
      if (exactDuplicate) {
        alert(`This option already exists: "${exactDuplicate.label}"`);
        return;
      }
      
      // Check for similar options (case-insensitive)
      const similarOptions = options.filter(option => 
        option.label.toLowerCase().includes(trimmedValue.toLowerCase()) ||
        trimmedValue.toLowerCase().includes(option.label.toLowerCase())
      );
      
      if (similarOptions.length > 0) {
        const similarLabels = similarOptions.map(opt => opt.label).join(', ');
        const confirmed = confirm(
          `Similar options already exist: ${similarLabels}\n\nDo you still want to add "${trimmedValue}"?`
        );
        if (!confirmed) {
          return;
        }
      }
      
      onAddNew(trimmedValue);
      setNewOptionValue('');
      setShowAddDialog(false);
      setIsOpen(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && filteredOptions.length === 1) {
      handleSelect(filteredOptions[0].value);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setSearchTerm('');
    }
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      
      {/* Main dropdown trigger */}
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={`
            w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-left
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'hover:border-gray-400 cursor-pointer'}
            ${isOpen ? 'border-blue-500 ring-1 ring-blue-500' : ''}
            focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500
          `}
        >
          <span className={`block truncate ${!displayValue ? 'text-gray-500' : ''}`}>
            {displayValue || placeholder}
          </span>
          <ChevronDown
            className={`absolute right-2 top-2.5 h-4 w-4 text-gray-400 transition-transform
              ${isOpen ? 'rotate-180' : ''}
            `}
          />
        </button>

        {/* Dropdown menu */}
        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
            {/* Search input */}
            <div className="p-2 border-b border-gray-200">
              <input
                ref={inputRef}
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search options..."
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Options list */}
            <div className="max-h-60 overflow-y-auto">
              {filteredOptions.length > 0 ? (
                filteredOptions.map((option, index) => (
                  <button
                    key={`${option.value}_${index}_${option.is_default ? 'default' : 'custom'}`}
                    type="button"
                    onClick={() => handleSelect(option.value)}
                    className={`
                      w-full px-3 py-2 text-left hover:bg-blue-50 flex items-center justify-between
                      ${value === option.value ? 'bg-blue-100 text-blue-900' : 'text-gray-900'}
                    `}
                  >
                    <span>{option.label}</span>
                    {option.is_default && (
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        Standard
                      </span>
                    )}
                  </button>
                ))
              ) : (
                <div className="px-3 py-2 text-gray-500 text-sm">
                  No options found
                </div>
              )}
            </div>

            {/* Add new option button */}
            {showAddNew && onAddNew && (
              <div className="border-t border-gray-200 p-2">
                <button
                  type="button"
                  onClick={() => setShowAddDialog(true)}
                  className="w-full px-3 py-2 text-left text-blue-600 hover:bg-blue-50 flex items-center gap-2 text-sm"
                >
                  <Plus className="h-4 w-4" />
                  Add new option
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add new option dialog */}
      {showAddDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Add New {label}
              </h3>
              <button
                onClick={() => {
                  setShowAddDialog(false);
                  setNewOptionValue('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Option Name
              </label>
              <input
                type="text"
                value={newOptionValue}
                onChange={(e) => setNewOptionValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddNew()}
                placeholder={`Enter new ${label.toLowerCase()}`}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                autoFocus
              />
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowAddDialog(false);
                  setNewOptionValue('');
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleAddNew}
                disabled={!newOptionValue.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Add Option
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
