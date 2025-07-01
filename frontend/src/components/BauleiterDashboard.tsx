/**
 * Bauleiter Dashboard Component
 * 
 * Shows pending approvals and completed decisions for Bauleiter workflow.
 * Reuses existing database service patterns and UI components.
 */
import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface PendingApproval {
  id: string;
  file_name: string;
  rechnungsnummer?: string;
  lieferant?: string;
  rechnungsbetrag?: number;
  projekt?: string;
  sent_to_bauleiter_at?: string;
  bauleiter_email?: string;
  editor_name?: string;
  url?: string;
}

interface BauleiterDashboardProps {
  bauleiterEmail?: string;
}

const BauleiterDashboard: React.FC<BauleiterDashboardProps> = ({ bauleiterEmail }) => {
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPendingApprovals = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Use the new API endpoint for pending approvals
      let url = `${apiUrl}/api/invoices/pending-approval`;
      if (bauleiterEmail) {
        url += `?bauleiter_email=${encodeURIComponent(bauleiterEmail)}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch pending approvals: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setPendingApprovals(result.pending_approvals || []);
        setError(null);
      } else {
        throw new Error(result.error || 'Failed to fetch pending approvals');
      }
      
    } catch (err) {
      console.error('Error fetching pending approvals:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      toast.error('Fehler beim Laden der ausstehenden Genehmigungen');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingApprovals();
  }, [bauleiterEmail]);

  const formatCurrency = (amount: number | undefined): string => {
    if (!amount) return '-';
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return '-';
    try {
      return new Date(dateString).toLocaleString('de-DE');
    } catch {
      return dateString;
    }
  };

  const openInvoiceForApproval = (invoice: PendingApproval) => {
    if (invoice.url) {
      window.open(invoice.url, '_blank');
    } else {
      toast.error('PDF nicht verfügbar');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-center mt-2 text-gray-600">Lade ausstehende Genehmigungen...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Fehler beim Laden</h3>
          <p className="text-red-600 text-sm mt-1">{error}</p>
          <button 
            onClick={fetchPendingApprovals}
            className="mt-3 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
          >
            Erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Bauleiter Dashboard
        </h2>
        <p className="text-gray-600 mt-1">
          {bauleiterEmail ? `Genehmigungen für: ${bauleiterEmail}` : 'Alle ausstehenden Genehmigungen'}
        </p>
      </div>

      {/* Summary Card */}
      <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Ausstehende Genehmigungen
            </h3>
            <p className="text-sm text-gray-600">
              {pendingApprovals.length} Rechnung{pendingApprovals.length !== 1 ? 'en' : ''} zur Prüfung
            </p>
          </div>
          <div className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full font-medium">
            {pendingApprovals.length}
          </div>
        </div>
      </div>

      {/* Pending Approvals List */}
      {pendingApprovals.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="text-gray-400 text-6xl mb-4">✅</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Keine ausstehenden Genehmigungen
          </h3>
          <p className="text-gray-600">
            Alle Rechnungen wurden bereits bearbeitet.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingApprovals.map((invoice) => (
            <div key={invoice.id} className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">
                        {invoice.file_name || `Rechnung ${invoice.id.slice(0, 8)}`}
                      </h4>
                      <div className="text-sm text-gray-600 mt-1 space-y-1">
                        {invoice.rechnungsnummer && (
                          <div>Rechnungsnummer: {invoice.rechnungsnummer}</div>
                        )}
                        {invoice.lieferant && (
                          <div>Lieferant: {invoice.lieferant}</div>
                        )}
                        {invoice.projekt && (
                          <div>Projekt: {invoice.projekt}</div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-lg font-semibold text-gray-900">
                        {formatCurrency(invoice.rechnungsbetrag)}
                      </div>
                      <div className="text-sm text-gray-500">
                        Gesendet: {formatDate(invoice.sent_to_bauleiter_at)}
                      </div>
                      {invoice.editor_name && (
                        <div className="text-sm text-gray-500">
                          von: {invoice.editor_name}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="ml-4">
                  <button
                    onClick={() => openInvoiceForApproval(invoice)}
                    className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors flex items-center space-x-2"
                  >
                    <span>📄</span>
                    <span>PDF öffnen</span>
                  </button>
                  <p className="text-xs text-gray-500 mt-1 text-center">
                    E-Mail für Genehmigung prüfen
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Refresh Button */}
      <div className="mt-6 text-center">
        <button 
          onClick={fetchPendingApprovals}
          className="bg-gray-600 text-white px-6 py-2 rounded hover:bg-gray-700 transition-colors"
        >
          🔄 Aktualisieren
        </button>
      </div>
    </div>
  );
};

export default BauleiterDashboard;
