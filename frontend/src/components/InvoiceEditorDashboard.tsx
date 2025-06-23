'use client';

import React, { useState, useEffect } from 'react';
import PDFViewer from './PDFViewer';
import InvoiceForm, { GermanInvoiceFields, ConfidenceScores } from './InvoiceForm';
import { FileText, Eye, Edit3, AlertTriangle, CheckCircle, Monitor, FileInput } from 'lucide-react';

interface InvoiceEditorDashboardProps {
  invoiceId: string;
  initialData?: {
    pdfUrl: string;
    fields: GermanInvoiceFields;
    confidenceScores: ConfidenceScores;
    filename?: string;
  };
}

export default function InvoiceEditorDashboard({ 
  invoiceId, 
  initialData 
}: InvoiceEditorDashboardProps) {
  const [pdfUrl, setPdfUrl] = useState<string>(initialData?.pdfUrl || '');
  const [fields, setFields] = useState<GermanInvoiceFields>(initialData?.fields || {});
  const [confidenceScores, setConfidenceScores] = useState<ConfidenceScores>(initialData?.confidenceScores || {});
  const [filename, setFilename] = useState<string>(initialData?.filename || '');
  const [isLoading, setIsLoading] = useState<boolean>(!initialData);
  const [error, setError] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false);
  const [pdfNumPages, setPdfNumPages] = useState<number>(0);
  const [mobileView, setMobileView] = useState<'pdf' | 'form'>('pdf'); // For mobile toggle

  // Load invoice data if not provided initially
  useEffect(() => {
    if (!initialData && invoiceId) {
      loadInvoiceData();
    }
  }, [invoiceId, initialData]);

  const loadInvoiceData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/invoices/${invoiceId}/editor`);
      if (!response.ok) {
        throw new Error(`Failed to load invoice: ${response.statusText}`);
      }

      const data = await response.json();
      setPdfUrl(data.pdfUrl);
      setFields(data.fields || {});
      setConfidenceScores(data.confidenceScores || {});
      setFilename(data.filename || `Invoice ${invoiceId}`);
    } catch (err) {
      console.error('Error loading invoice data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load invoice data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFieldChange = (field: keyof GermanInvoiceFields, value: any) => {
    setFields(prev => ({
      ...prev,
      [field]: value
    }));
    setHasUnsavedChanges(true);
  };

  const handleSave = async (updatedFields: GermanInvoiceFields) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/invoices/${invoiceId}/editor`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedFields),
      });

      if (!response.ok) {
        // Try to get detailed error message from backend
        let errorMessage = `Failed to save: ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = `Failed to save: ${errorData.detail.message || errorData.detail}`;
          }
        } catch (parseError) {
          // If we can't parse the error response, use the status text
          console.warn('Could not parse error response:', parseError);
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Save successful:', result);
      
      setFields(updatedFields);
      setHasUnsavedChanges(false);
      return true;
    } catch (err) {
      console.error('Error saving invoice:', err);
      console.error('Fields being saved:', updatedFields);
      throw err;
    }
  };

  const handleCancel = () => {
    // Reset to original data
    if (initialData) {
      setFields(initialData.fields);
    }
    setHasUnsavedChanges(false);
  };

  const handlePdfLoadSuccess = (numPages: number) => {
    setPdfNumPages(numPages);
  };

  const handlePdfLoadError = (error: any) => {
    console.error('PDF load error:', error);
    setError('Failed to load PDF document');
  };

  // Calculate overall confidence score
  const overallConfidence = Object.values(confidenceScores).length > 0 
    ? Math.round(Object.values(confidenceScores).reduce((a, b) => a + b, 0) / Object.values(confidenceScores).length)
    : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Loading Invoice Editor</h2>
          <p className="text-gray-500">Preparing your document...</p>
        </div>
      </div>
    );
  }

  if (error && !pdfUrl) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Error Loading Invoice</h2>
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={loadInvoiceData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <FileText className="h-6 w-6 text-blue-600" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900 truncate max-w-md">
                {filename}
              </h1>
              <p className="text-sm text-gray-500">Invoice ID: {invoiceId}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Mobile View Toggle */}
            <div className="lg:hidden flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setMobileView('pdf')}
                className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  mobileView === 'pdf' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Monitor className="h-4 w-4" />
                <span>PDF</span>
              </button>
              <button
                onClick={() => setMobileView('form')}
                className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  mobileView === 'form' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileInput className="h-4 w-4" />
                <span>Form</span>
              </button>
            </div>

            {/* PDF Info */}
            {pdfNumPages > 0 && (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Eye className="h-4 w-4" />
                <span>{pdfNumPages} page{pdfNumPages !== 1 ? 's' : ''}</span>
              </div>
            )}
            
            {/* Confidence Score */}
            {overallConfidence > 0 && (
              <div className="flex items-center space-x-2">
                {overallConfidence >= 80 ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                )}
                <span className="text-sm font-medium text-gray-700">
                  {overallConfidence}% confidence
                </span>
              </div>
            )}

            {/* Unsaved Changes Indicator */}
            {hasUnsavedChanges && (
              <div className="flex items-center space-x-2 text-sm text-amber-600">
                <Edit3 className="h-4 w-4" />
                <span>Unsaved changes</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - Split Screen */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Side - PDF Viewer (50% on desktop, conditional on mobile) */}
        <div className={`w-full lg:w-1/2 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 h-1/2 lg:h-full ${
          mobileView === 'pdf' ? 'block' : 'hidden lg:block'
        }`}>
          {pdfUrl ? (
            <PDFViewer
              pdfUrl={pdfUrl}
              onLoadSuccess={handlePdfLoadSuccess}
              onLoadError={handlePdfLoadError}
              className="h-full"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500">
                <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p>No PDF document available</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Side - Invoice Form (50% on desktop, conditional on mobile) */}
        <div className={`w-full lg:w-1/2 bg-gray-50 h-1/2 lg:h-full ${
          mobileView === 'form' ? 'block' : 'hidden lg:block'
        }`}>
          <InvoiceForm
            fields={fields}
            confidenceScores={confidenceScores}
            onFieldChange={handleFieldChange}
            onSave={handleSave}
            onCancel={handleCancel}
            isLoading={isLoading}
            hasUnsavedChanges={hasUnsavedChanges}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}
