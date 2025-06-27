'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast, Toaster } from 'react-hot-toast'
import { 
  FileText, 
  Edit3, 
  Trash2, 
  Calendar, 
  DollarSign, 
  Building, 
  User,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw
} from 'lucide-react'
import FolderWatcherWidget from './FolderWatcherWidget'
import DeleteConfirmationDialog from './DeleteConfirmationDialog'

interface CleanInvoice {
  id: string
  file_name: string
  url: string
  file_path?: string
  status: 'pending' | 'uploaded' | 'edited' | 'pending_email' | 'edit_completed' | 'in_review_by_bauleiter' | 'approved_by_bauleiter' | 'rejected_by_bauleiter' | 'completed' | 'error'
  file_size: number
  created_at: string
  
  // Manual Review Status
  review_status?: 'pending' | 'under_review' | 'completed_review' | 'needs_attention'
  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string
  
  // German Business Fields
  rechnungsempfaenger?: string
  rechnungssteller?: string
  projekt?: string
  gewerk?: string
  rechnungsbetrag?: number
  rechnungseingang?: string
  faelligkeit?: string
  skonto_datum?: string
  skonto_prozent?: number
  rechnungsart?: string
  kfw_anrechenbare_kosten?: boolean
  rechnungspruefung?: string
  weiter_berechnen_an?: string
}

export default function CleanInvoiceDashboard() {
  const [invoices, setInvoices] = useState<CleanInvoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteDialog, setDeleteDialog] = useState<{
    isOpen: boolean
    invoiceId: string
    fileName: string
    uploadSource: 'drag-drop' | 'folder-watcher' | 'manual' | 'unknown'
  }>({
    isOpen: false,
    invoiceId: '',
    fileName: '',
    uploadSource: 'unknown'
  })

  useEffect(() => {
    fetchInvoices()
  }, [])

  const fetchInvoices = async () => {
    try {
      setLoading(true)
      setError(null)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/invoices`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch invoices: ${response.statusText}`)
      }
      
      const data = await response.json()
      setInvoices(data.invoices || [])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load invoices'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const deleteInvoice = async (id: string, filename: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/invoices/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Rechnung konnte nicht gelöscht werden')
      }

      toast.success(`Rechnung "${filename}" erfolgreich gelöscht`)
      await fetchInvoices() // Refresh the list
      
      // Close delete dialog
      setDeleteDialog({
        isOpen: false,
        invoiceId: '',
        fileName: '',
        uploadSource: 'unknown'
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Rechnung konnte nicht gelöscht werden'
      toast.error(errorMessage)
    }
  }

  const openDeleteDialog = (invoice: CleanInvoice) => {
    // Detect upload source from file_path or other indicators
    let uploadSource: 'drag-drop' | 'folder-watcher' | 'manual' | 'unknown' = 'unknown'
    
    if (invoice.file_path) {
      if (invoice.file_path.startsWith('folder_watcher/')) {
        uploadSource = 'folder-watcher'
      } else if (invoice.file_path.startsWith('manual/')) {
        uploadSource = 'manual'
      } else {
        uploadSource = 'drag-drop'
      }
    }
    
    setDeleteDialog({
      isOpen: true,
      invoiceId: invoice.id,
      fileName: invoice.file_name,
      uploadSource
    })
  }

  const closeDeleteDialog = () => {
    setDeleteDialog({
      isOpen: false,
      invoiceId: '',
      fileName: '',
      uploadSource: 'unknown'
    })
  }

  const handleDeleteConfirm = async () => {
    await deleteInvoice(deleteDialog.invoiceId, deleteDialog.fileName)
  }

  const getStatusColor = (status: string | undefined): string => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50'
      case 'processing': return 'text-blue-600 bg-blue-50'
      case 'error': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getReviewStatusColor = (reviewStatus: string | undefined): string => {
    switch (reviewStatus) {
      case 'completed_review': return 'text-green-600 bg-green-50'
      case 'under_review': return 'text-blue-600 bg-blue-50'
      case 'needs_attention': return 'text-yellow-600 bg-yellow-50'
      case null:
      case undefined:
      case 'pending': return 'text-orange-600 bg-orange-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getReviewStatusLabel = (reviewStatus: string | undefined): string => {
    switch (reviewStatus) {
      case 'completed_review': return 'Abgeschlossen'
      case 'under_review': return 'In Bearbeitung'
      case 'needs_attention': return 'Aufmerksamkeit erforderlich'
      case null:
      case undefined:
      case 'pending': return 'Erfassung/Prüfung'
      default: return reviewStatus || 'Unbekannt'
    }
  }

  const getWorkflowStatusColor = (status: string | undefined, reviewStatus: string | undefined): string => {
    // 3-stage workflow: nicht begonnen -> in Bearbeitung -> abgeschlossen
    if (status === 'completed' && reviewStatus === 'completed_review') {
      return 'text-green-600 bg-green-50'  // abgeschlossen
    } else if (status === 'edited' && reviewStatus === 'under_review') {
      return 'text-blue-600 bg-blue-50'    // in Bearbeitung  
    } else {
      return 'text-orange-600 bg-orange-50' // nicht begonnen (uploaded/pending)
    }
  }

  const getWorkflowStatusLabel = (status: string | undefined, reviewStatus: string | undefined): string => {
    // 3-stage workflow: nicht begonnen -> in Bearbeitung -> abgeschlossen
    if (status === 'completed' && reviewStatus === 'completed_review') {
      return 'abgeschlossen'
    } else if (status === 'edited' && reviewStatus === 'under_review') {
      return 'in Bearbeitung'
    } else {
      return 'nicht begonnen'
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string): string => {
    try {
      // Handle different date formats
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        // Try parsing as DD.MM.YYYY or DD-MM-YYYY
        const parts = dateString.split(/[.-]/)
        if (parts.length === 3) {
          const day = parseInt(parts[0])
          const month = parseInt(parts[1]) - 1 // Month is 0-indexed
          const year = parseInt(parts[2])
          if (year > 1900 && month >= 0 && month < 12 && day >= 1 && day <= 31) {
            return new Date(year, month, day).toLocaleDateString('de-DE', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit'
            })
          }
        }
        return dateString // Return as-is if can't parse
      }
      return date.toLocaleDateString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  const formatCurrency = (amount: number | undefined): string => {
    if (!amount) return '---'
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Rechnungen werden geladen</h2>
          <p className="text-gray-500">Bitte warten...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Rechnungsverwaltung</h1>
                <p className="text-gray-500">Verwalten und bearbeiten Sie Ihre Rechnungen</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={fetchInvoices}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Aktualisieren</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="text-red-700 font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Rechnungen gesamt</p>
                <p className="text-2xl font-bold text-gray-900">{invoices.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Abgeschlossen</p>
                <p className="text-2xl font-bold text-gray-900">
                  {invoices.filter(inv => inv.status === 'completed' && inv.review_status === 'completed_review').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">In Bearbeitung</p>
                <p className="text-2xl font-bold text-gray-900">
                  {invoices.filter(inv => inv.status === 'edited' && inv.review_status === 'under_review').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Nicht begonnen</p>
                <p className="text-2xl font-bold text-gray-900">
                  {invoices.filter(inv => 
                    !(inv.status === 'completed' && inv.review_status === 'completed_review') &&
                    !(inv.status === 'edited' && inv.review_status === 'under_review')
                  ).length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <DollarSign className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Gesamtbetrag</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(
                    invoices.reduce((sum, inv) => sum + (inv.rechnungsbetrag || 0), 0)
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Folder Watcher Widget */}
        <div className="mb-8">
          <FolderWatcherWidget />
        </div>

        {/* Invoice List */}
        <div className="bg-white shadow-sm border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Rechnungen</h2>
              <div className="text-sm text-gray-500 bg-blue-50 px-3 py-1 rounded-full">
                ← → Horizontal scrollen für alle Felder
              </div>
            </div>
          </div>

          {invoices.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Rechnungen gefunden</h3>
              <p className="text-gray-500">Laden Sie Rechnungen hoch, um zu beginnen.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200" style={{ minWidth: '1800px' }}>
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10 min-w-[200px]">
                      Rechnungsdetails
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                      Rechnungsempfänger
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                      Rechnungssteller
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Projekt
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                      Gewerk
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Rechnungsbetrag
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Rechnungseingang
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Fälligkeit
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Skonto Datum
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                      Skonto %
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[120px]">
                      Rechnungsart
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[100px]">
                      KfW Kosten
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                      Rechnungsprüfung
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]">
                      Weiter berechnen an
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 bg-gray-50 z-10 min-w-[160px]">
                      Aktionen
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap sticky left-0 bg-white z-10 min-w-[200px]">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-gray-400" />
                          <div>
                            <div className="text-sm font-medium text-gray-900 truncate max-w-[140px]">
                              {invoice.file_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {formatFileSize(invoice.file_size)}
                            </div>
                            <div className="text-xs text-gray-400">
                              {new Date(invoice.created_at).toLocaleDateString('de-DE', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit'
                              })}
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[120px]">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getWorkflowStatusColor(invoice.status, invoice.review_status)}`}>
                          {getWorkflowStatusLabel(invoice.status, invoice.review_status)}
                        </span>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[150px]">
                        <div className="text-sm text-gray-900 truncate max-w-[130px]" title={invoice.rechnungsempfaenger || ''}>
                          {invoice.rechnungsempfaenger || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[150px]">
                        <div className="text-sm text-gray-900 truncate max-w-[130px]" title={invoice.rechnungssteller || ''}>
                          {invoice.rechnungssteller || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[120px]">
                        <div className="text-sm text-gray-900 truncate max-w-[100px]" title={invoice.projekt || ''}>
                          {invoice.projekt || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[100px]">
                        <div className="text-sm text-gray-900 truncate max-w-[80px]" title={invoice.gewerk || ''}>
                          {invoice.gewerk || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap text-right min-w-[120px]">
                        <div className="text-sm font-medium text-gray-900">
                          {formatCurrency(invoice.rechnungsbetrag)}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[120px]">
                        <div className="text-sm text-gray-900">
                          {invoice.rechnungseingang ? formatDate(invoice.rechnungseingang) : '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[120px]">
                        <div className="text-sm text-gray-900">
                          {invoice.faelligkeit ? formatDate(invoice.faelligkeit) : '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[120px]">
                        <div className="text-sm text-gray-900">
                          {invoice.skonto_datum ? formatDate(invoice.skonto_datum) : '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap text-right min-w-[100px]">
                        <div className="text-sm text-gray-900">
                          {invoice.skonto_prozent ? `${invoice.skonto_prozent}%` : '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[120px]">
                        <div className="text-sm text-gray-900 truncate max-w-[100px]" title={invoice.rechnungsart || ''}>
                          {invoice.rechnungsart || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap text-center min-w-[100px]">
                        <div className="text-sm text-gray-900">
                          {invoice.kfw_anrechenbare_kosten ? (
                            <CheckCircle className="h-5 w-5 text-green-600 mx-auto" />
                          ) : (
                            <span className="text-gray-400">---</span>
                          )}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[150px]">
                        <div className="text-sm text-gray-900 truncate max-w-[130px]" title={invoice.rechnungspruefung || ''}>
                          {invoice.rechnungspruefung || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap min-w-[150px]">
                        <div className="text-sm text-gray-900 truncate max-w-[130px]" title={invoice.weiter_berechnen_an || ''}>
                          {invoice.weiter_berechnen_an || '---'}
                        </div>
                      </td>
                      
                      <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium sticky right-0 bg-white z-10 min-w-[160px]">
                        <div className="flex items-center justify-end space-x-2">
                          <Link
                            href={`/invoice-editor/${invoice.id}`}
                            className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                          >
                            <Edit3 className="h-4 w-4" />
                            <span>Bearbeiten</span>
                          </Link>
                          
                          <button
                            onClick={() => openDeleteDialog(invoice)}
                            className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                            <span>Löschen</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Delete Confirmation Dialog */}
        <DeleteConfirmationDialog
          isOpen={deleteDialog.isOpen}
          fileName={deleteDialog.fileName}
          uploadSource={deleteDialog.uploadSource}
          onConfirm={handleDeleteConfirm}
          onCancel={closeDeleteDialog}
        />
      </main>
    </div>
  )
}
