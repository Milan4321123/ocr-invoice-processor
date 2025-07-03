'use client';

import React, { useState, useEffect } from 'react';
import PDFViewer from './PDFViewer';
import CleanInvoiceForm, { GermanInvoiceFields } from './CleanInvoiceForm';
import { FileText, Eye, Edit3, AlertTriangle, CheckCircle, Monitor, FileInput } from 'lucide-react';

interface InvoiceEditorDashboardProps {
  invoiceId: string;
  initialData?: {
    pdfUrl: string;
    fields: GermanInvoiceFields;
    filename?: string;
  };
}

export default function InvoiceEditorDashboard({ 
  invoiceId, 
  initialData 
}: InvoiceEditorDashboardProps) {
  const [pdfUrl, setPdfUrl] = useState<string>(initialData?.pdfUrl || '');
  const [fields, setFields] = useState<GermanInvoiceFields>(initialData?.fields || {});
  const [filename, setFilename] = useState<string>(initialData?.filename || '');
  const [isLoading, setIsLoading] = useState<boolean>(!initialData);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isCompleting, setIsCompleting] = useState<boolean>(false);
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

      // API call to load invoice data
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/invoices/${invoiceId}/editor`);
      if (!response.ok) {
        throw new Error(`Rechnung konnte nicht geladen werden: ${response.statusText}`);
      }

      const data = await response.json();
      setPdfUrl(data.pdfUrl);
      setFields(data.fields || {});
      setFilename(data.filename || `Rechnung ${invoiceId}`);
    } catch (err) {
      console.error('Error loading invoice data:', err);
      setError(err instanceof Error ? err.message : 'Rechnungsdaten konnten nicht geladen werden');
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
      setIsSaving(true);
      
      // API call to save invoice data with editor information for email notification
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Prepare editor information for email notification
      const editorInfo = {
        editor_email: updatedFields.rechnungspruefung_email || "editor@company.de",
        editor_name: "Rechnung Bearbeiter",
        changes_summary: [
          {
            field: "last_edited",
            old_value: new Date().toISOString(),
            new_value: "Rechnung wurde bearbeitet und gespeichert"
          }
        ]
      };

      const response = await fetch(`${apiUrl}/api/invoices/${invoiceId}/editor`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          fields: updatedFields,
          editor_info: editorInfo
        }),
      });

      if (!response.ok) {
        throw new Error(`Speichern fehlgeschlagen: ${response.statusText}`);
      }

      const result = await response.json();
      setFields(updatedFields);
      setHasUnsavedChanges(false);
      
      // Show success message including email confirmation
      if (result.email_sent) {
        alert(`✅ Rechnung erfolgreich gespeichert! Bestätigungs-E-Mail wurde an ${editorInfo.editor_email} gesendet.`);
      } else {
        alert('✅ Rechnung erfolgreich gespeichert!');
      }
      
      return true;
    } catch (err) {
      console.error('Error saving invoice:', err);
      alert(`❌ Fehler beim Speichern: ${err instanceof Error ? err.message : 'Unbekannter Fehler'}`);
      throw err;
    } finally {
      setIsSaving(false);
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
    setError('PDF-Dokument konnte nicht geladen werden');
  };

  const handleComplete = async () => {
    try {
      setIsCompleting(true);
      
      // First save the current changes
      await handleSave(fields);
      
      // Mark as completed - no automatic email sending
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Prepare completion data with editor info for completion email
      const completionData = {
        completion_info: {
          completed_by: fields.rechnungspruefung_email || "editor@company.de",
          completed_at: new Date().toISOString(),
          completion_notes: "Rechnung wurde vollständig bearbeitet - bereit für Bauleiter-Genehmigung über Dashboard"
        },
        editor_info: {
          editor_email: fields.rechnungspruefung_email || "editor@company.de",
          editor_name: fields.rechnungspruefung_email?.split('@')[0] || "Editor",
          changes_summary: [
            {
              field: "Status",
              old_value: "Bearbeitung",
              new_value: "Bearbeitung abgeschlossen - bereit für Bauleiter",
              timestamp: new Date().toLocaleString('de-DE')
            }
          ]
        }
      };

      const response = await fetch(`${apiUrl}/api/invoices/${invoiceId}/complete`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(completionData),
      });

      if (!response.ok) {
        throw new Error(`Abschluss fehlgeschlagen: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Show success message based on whether completion email was sent
      const emailMessage = result.completion_email_sent 
        ? "\n📧 Abschluss-E-Mail wurde gesendet"
        : "\n⚠️ Keine E-Mail-Benachrichtigung gesendet";
      
      alert(`✅ Rechnung erfolgreich abgeschlossen!${emailMessage}\n\n📋 Status: "Bearbeitung abgeschlossen - bereit für Bauleiter"\n\n💡 Nächster Schritt: Verwenden Sie die "An Bauleiter senden" Schaltfläche im Dashboard, um die Genehmigung zu beantragen.`);
      
      // Redirect to dashboard after completion
      window.location.href = '/dashboard';
      
      return true;
    } catch (err) {
      console.error('Error completing invoice:', err);
      alert(`❌ Fehler beim Abschließen: ${err instanceof Error ? err.message : 'Unbekannter Fehler'}`);
      throw err;
    } finally {
      setIsCompleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Rechnungseditor wird geladen</h2>
          <p className="text-gray-500">Dokument wird vorbereitet...</p>
        </div>
      </div>
    );
  }

  if (error && !pdfUrl) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Fehler beim Laden der Rechnung</h2>
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={loadInvoiceData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Modern Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 truncate max-w-md">
                {filename}
              </h1>
              <p className="text-sm text-gray-500">Rechnungs-ID: {invoiceId}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Mobile View Toggle */}
            <div className="lg:hidden flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setMobileView('pdf')}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
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
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  mobileView === 'form' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileInput className="h-4 w-4" />
                <span>Formular</span>
              </button>
            </div>

            {/* PDF Info */}
            {pdfNumPages > 0 && (
              <div className="hidden sm:flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-lg">
                <Eye className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">{pdfNumPages} Seite{pdfNumPages !== 1 ? 'n' : ''}</span>
              </div>
            )}

            {/* Unsaved Changes Indicator */}
            {hasUnsavedChanges && (
              <div className="flex items-center space-x-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
                <Edit3 className="h-4 w-4 text-amber-600" />
                <span className="text-sm text-amber-700 font-medium">Ungespeicherte Änderungen</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - Modern Split Screen */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-gray-100">
        {/* Left Side - Enhanced PDF Viewer */}
        <div className={`w-full lg:w-1/2 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 h-1/2 lg:h-full ${
          mobileView === 'pdf' ? 'block' : 'hidden lg:block'
        }`}>
          {pdfUrl ? (
            <div className="h-full flex flex-col">
              <div className="bg-gray-50 border-b border-gray-200 px-4 py-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">PDF-Dokument</span>
                  {pdfNumPages > 0 && (
                    <span className="text-xs text-gray-500">{pdfNumPages} Seite{pdfNumPages !== 1 ? 'n' : ''}</span>
                  )}
                </div>
              </div>
              <div className="flex-1">
                <PDFViewer
                  pdfUrl={pdfUrl}
                  onLoadSuccess={handlePdfLoadSuccess}
                  onLoadError={handlePdfLoadError}
                  className="h-full"
                />
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full bg-gray-50">
              <div className="text-center text-gray-500">
                <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-lg flex items-center justify-center">
                  <FileText className="h-8 w-8 text-gray-400" />
                </div>
                <p className="text-sm">Kein PDF-Dokument verfügbar</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Side - Enhanced Invoice Form */}
        <div className={`w-full lg:w-1/2 bg-gray-50 h-1/2 lg:h-full ${
          mobileView === 'form' ? 'block' : 'hidden lg:block'
        }`}>
          <CleanInvoiceForm
            fields={fields}
            onFieldChange={(fieldName: string, value: any) => handleFieldChange(fieldName as keyof GermanInvoiceFields, value)}
            onSave={() => handleSave(fields)}
            onComplete={handleComplete}
            isSaving={isSaving}
            isCompleting={isCompleting}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}
