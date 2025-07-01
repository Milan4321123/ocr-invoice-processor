'use client';

import { useState } from 'react';
import { toast } from 'react-hot-toast';

interface EmailTestResult {
  success: boolean;
  message: string;
  email_result?: any;
  test_parameters?: any;
  workflow_results?: any;
  summary?: any;
  email_configuration?: {
    sendgrid_configured: boolean;
    smtp_configured: boolean;
    from_email: string;
    base_url: string;
  };
}

export default function EmailTestPage() {
  const [bauleiterEmail, setBauleiterEmail] = useState('adhikarimilan4321@gmail.com');
  const [editorEmail, setEditorEmail] = useState('milan.test@company.com');
  const [editorName, setEditorName] = useState('Milan Adhikari');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<EmailTestResult | null>(null);

  const testBauleiterEmail = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/email-test/bauleiter-approval', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bauleiter_email: bauleiterEmail,
          editor_name: editorName,
          editor_email: editorEmail,
          use_sample_data: true
        })
      });

      const result = await response.json();
      setResults(result);
      
      if (result.success) {
        toast.success('Bauleiter Approval E-Mail erfolgreich gesendet!');
      } else {
        toast.error('Fehler beim Senden der E-Mail');
      }
    } catch (error) {
      toast.error('Netzwerkfehler');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const testEditorEmail = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/email-test/editor-notification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          editor_email: editorEmail,
          editor_name: editorName,
          use_sample_data: true
        })
      });

      const result = await response.json();
      setResults(result);
      
      if (result.success) {
        toast.success('Editor Notification E-Mail erfolgreich gesendet!');
      } else {
        toast.error('Fehler beim Senden der E-Mail');
      }
    } catch (error) {
      toast.error('Netzwerkfehler');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const testCompleteWorkflow = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/email-test/send-sample-invoice-workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          editor_email: editorEmail,
          bauleiter_email: bauleiterEmail,
          editor_name: editorName
        })
      });

      const result = await response.json();
      setResults(result);
      
      if (result.success) {
        toast.success(`Workflow-Test abgeschlossen! ${result.summary?.emails_sent || 0} E-Mails gesendet.`);
      } else {
        toast.error('Fehler beim Workflow-Test');
      }
    } catch (error) {
      toast.error('Netzwerkfehler');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkEmailConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/email-test/email-config');
      const result = await response.json();
      setResults(result);
      
      if (result.success) {
        toast.success('E-Mail Konfiguration erfolgreich abgerufen');
      } else {
        toast.error('Fehler beim Abrufen der Konfiguration');
      }
    } catch (error) {
      toast.error('Netzwerkfehler');
      console.error('Error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
            📧 E-Mail System Test
          </h1>

          {/* Configuration Section */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-blue-800 mb-4">Konfiguration</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bauleiter E-Mail
                </label>
                <input
                  type="email"
                  value={bauleiterEmail}
                  onChange={(e) => setBauleiterEmail(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="bauleiter@company.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Editor E-Mail
                </label>
                <input
                  type="email"
                  value={editorEmail}
                  onChange={(e) => setEditorEmail(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="editor@company.com"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Editor Name
                </label>
                <input
                  type="text"
                  value={editorName}
                  onChange={(e) => setEditorName(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Max Mustermann"
                />
              </div>
            </div>
          </div>

          {/* Test Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <button
              onClick={checkEmailConfig}
              className="p-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
            >
              📋 Konfiguration prüfen
            </button>
            
            <button
              onClick={testEditorEmail}
              disabled={loading}
              className="p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50"
            >
              {loading ? '⏳' : '📝'} Editor Notification
            </button>
            
            <button
              onClick={testBauleiterEmail}
              disabled={loading}
              className="p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
            >
              {loading ? '⏳' : '👨‍💼'} Bauleiter Approval
            </button>
            
            <button
              onClick={testCompleteWorkflow}
              disabled={loading}
              className="p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium disabled:opacity-50"
            >
              {loading ? '⏳' : '🔄'} Complete Workflow
            </button>
          </div>

          {/* Results Section */}
          {results && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Test Ergebnisse
              </h3>
              
              <div className={`p-4 rounded-lg mb-4 ${
                results.success ? 'bg-green-100 border border-green-300' : 'bg-red-100 border border-red-300'
              }`}>
                <div className="flex items-center">
                  <span className={`text-lg mr-2 ${results.success ? 'text-green-600' : 'text-red-600'}`}>
                    {results.success ? '✅' : '❌'}
                  </span>
                  <span className={`font-medium ${results.success ? 'text-green-800' : 'text-red-800'}`}>
                    {results.message}
                  </span>
                </div>
              </div>

              {/* Email Configuration Results */}
              {results.email_configuration && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">E-Mail Konfiguration:</h4>
                  <div className="bg-white p-4 rounded border text-sm">
                    <div className="grid grid-cols-2 gap-2">
                      <div>SendGrid: {results.email_configuration.sendgrid_configured ? '✅' : '❌'}</div>
                      <div>SMTP: {results.email_configuration.smtp_configured ? '✅' : '❌'}</div>
                      <div>From: {results.email_configuration.from_email}</div>
                      <div>Base URL: {results.email_configuration.base_url}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Workflow Results */}
              {results.workflow_results && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">Workflow Ergebnisse:</h4>
                  <div className="space-y-2">
                    {Object.entries(results.workflow_results).map(([key, result]: [string, any]) => (
                      <div key={key} className="bg-white p-3 rounded border text-sm">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{key.replace('_', ' ')}</span>
                          <span className={result.success ? 'text-green-600' : 'text-red-600'}>
                            {result.success ? '✅' : '❌'}
                          </span>
                        </div>
                        {result.message_id && (
                          <div className="text-gray-600 text-xs mt-1">
                            Message ID: {result.message_id}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Summary */}
              {results.summary && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-700 mb-2">Zusammenfassung:</h4>
                  <div className="bg-white p-4 rounded border text-sm">
                    <div>E-Mails gesendet: {results.summary.emails_sent} / {results.summary.total_emails}</div>
                    <div>Alle erfolgreich: {results.summary.all_successful ? '✅' : '❌'}</div>
                  </div>
                </div>
              )}

              {/* Raw Results */}
              <details className="mt-4">
                <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                  Rohe Daten anzeigen
                </summary>
                <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto max-h-96">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </details>
            </div>
          )}

          {/* Information Section */}
          <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="font-semibold text-yellow-800 mb-2">ℹ️ Information</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Die E-Mails werden mit Beispieldaten einer Test-Rechnung gesendet</li>
              <li>• Genehmigungslinks in der Bauleiter-E-Mail sind funktionsfähig</li>
              <li>• Für Produktionsumgebung sollten echte Firmendaten verwendet werden</li>
              <li>• Die E-Mail-Konfiguration erfolgt über Umgebungsvariablen</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
