'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface ApprovalResponse {
  success: boolean;
  message: string;
  action: 'approve' | 'reject';
  invoice_id: string;
  invoice_details?: {
    rechnungsnummer: string;
    lieferant: string;
    rechnungsbetrag: string;
    projekt: string;
  };
  error?: string;
}

export default function ApprovalPage() {
  const params = useParams();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<ApprovalResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const token = params?.token as string;

  useEffect(() => {
    if (token) {
      handleApproval();
    }
  }, [token]);

  const handleApproval = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`http://localhost:8000/api/approval/${token}`, {
        method: 'GET',
        headers: {
          'Accept': 'text/html,application/json',
        },
      });

      if (response.headers.get('content-type')?.includes('application/json')) {
        const data = await response.json();
        setResult(data);
        
        if (data.success) {
          toast.success(`Rechnung ${data.action === 'approve' ? 'genehmigt' : 'abgelehnt'}!`);
        } else {
          toast.error(data.error || 'Fehler bei der Bearbeitung');
          setError(data.error || 'Unbekannter Fehler');
        }
      } else {
        // Handle HTML response (error pages)
        const htmlText = await response.text();
        if (htmlText.includes('Token Expired')) {
          setError('Token abgelaufen');
          toast.error('Der Genehmigungslink ist abgelaufen');
        } else if (htmlText.includes('Invalid Token')) {
          setError('Ungültiger Token');
          toast.error('Der Genehmigungslink ist ungültig');
        } else {
          setError('Fehler bei der Verarbeitung');
          toast.error('Fehler bei der Verarbeitung der Anfrage');
        }
      }
    } catch (err) {
      console.error('Approval error:', err);
      setError('Netzwerkfehler');
      toast.error('Netzwerkfehler - Bitte versuchen Sie es später erneut');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Genehmigung wird verarbeitet...
          </h2>
          <p className="text-gray-600">
            Bitte warten Sie, während Ihre Entscheidung verarbeitet wird.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-2xl w-full">
        {result && result.success ? (
          // Success state
          <div className="text-center">
            <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-6 ${
              result.action === 'approve' 
                ? 'bg-green-100 text-green-600' 
                : 'bg-red-100 text-red-600'
            }`}>
              {result.action === 'approve' ? (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </div>
            
            <h1 className={`text-2xl font-bold mb-4 ${
              result.action === 'approve' ? 'text-green-800' : 'text-red-800'
            }`}>
              {result.action === 'approve' ? '✅ Rechnung genehmigt' : '❌ Rechnung abgelehnt'}
            </h1>
            
            <p className="text-gray-600 mb-6">
              {result.message}
            </p>

            {result.invoice_details && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
                <h3 className="font-semibold text-gray-800 mb-3">Rechnung Details:</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rechnungsnummer:</span>
                    <span className="font-medium">{result.invoice_details.rechnungsnummer}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Lieferant:</span>
                    <span className="font-medium">{result.invoice_details.lieferant}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Betrag:</span>
                    <span className="font-medium">{result.invoice_details.rechnungsbetrag}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Projekt:</span>
                    <span className="font-medium">{result.invoice_details.projekt}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-blue-800 text-sm">
                <strong>Nächste Schritte:</strong> {' '}
                {result.action === 'approve' 
                  ? 'Die Rechnung wird automatisch zur finalen Bearbeitung weitergeleitet.' 
                  : 'Die Rechnung wird zur Überarbeitung an den Editor zurückgesendet.'}
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Zum Dashboard
              </button>
              <button
                onClick={() => window.close()}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Fenster schließen
              </button>
            </div>
          </div>
        ) : (
          // Error state
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mb-6">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            
            <h1 className="text-2xl font-bold text-red-800 mb-4">
              Fehler bei der Genehmigung
            </h1>
            
            <p className="text-gray-600 mb-6">
              {error || 'Ein unbekannter Fehler ist aufgetreten.'}
            </p>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-yellow-800 mb-2">Mögliche Ursachen:</h3>
              <ul className="text-sm text-yellow-700 text-left space-y-1">
                <li>• Der Genehmigungslink ist abgelaufen (gültig für 7 Tage)</li>
                <li>• Der Link wurde bereits verwendet</li>
                <li>• Der Link ist beschädigt oder ungültig</li>
                <li>• Technischer Fehler im System</li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Zum Dashboard
              </button>
              <button
                onClick={() => router.push('/contact')}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Support kontaktieren
              </button>
            </div>
          </div>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-500">
            Invoice Management System - Automatische Genehmigung
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Zeitstempel: {new Date().toLocaleString('de-DE')}
          </p>
        </div>
      </div>
    </div>
  );
}
