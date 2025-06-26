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

interface CleanInvoice {
  id: string
  file_name: string
  url: string
  status: 'uploaded' | 'processing' | 'completed' | 'error'
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
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/invoices/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete invoice')
      }

      toast.success(`Invoice "${filename}" deleted successfully`)
      await fetchInvoices() // Refresh the list
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete invoice'
      toast.error(errorMessage)
    }
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
      default: return 'text-gray-600 bg-gray-50'
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
      return new Date(dateString).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
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
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Loading Invoices</h2>
          <p className="text-gray-500">Please wait...</p>
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
                <h1 className="text-2xl font-bold text-gray-900">Invoice Management</h1>
                <p className="text-gray-500">Manage and edit your invoices</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={fetchInvoices}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
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
                <p className="text-sm font-medium text-gray-600">Total Invoices</p>
                <p className="text-2xl font-bold text-gray-900">{invoices.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Reviewed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {invoices.filter(inv => inv.review_status === 'completed_review').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Review</p>
                <p className="text-2xl font-bold text-gray-900">
                  {invoices.filter(inv => !inv.review_status || inv.review_status === 'pending').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3">
              <DollarSign className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Amount</p>
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
            <h2 className="text-lg font-semibold text-gray-900">Invoices</h2>
          </div>

          {invoices.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
              <p className="text-gray-500">Upload some invoices to get started.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Invoice Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Business Info
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount & Dates
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-gray-400" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {invoice.file_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {formatFileSize(invoice.file_size)} • {formatDate(invoice.created_at)}
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="space-y-1">
                          {invoice.rechnungssteller && (
                            <div className="flex items-center space-x-2 text-sm">
                              <Building className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-900">{invoice.rechnungssteller}</span>
                            </div>
                          )}
                          {invoice.rechnungsempfaenger && (
                            <div className="flex items-center space-x-2 text-sm">
                              <User className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-500">{invoice.rechnungsempfaenger}</span>
                            </div>
                          )}
                          {invoice.projekt && (
                            <div className="text-sm text-gray-500">
                              Project: {invoice.projekt}
                            </div>
                          )}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2 text-sm">
                            <DollarSign className="h-4 w-4 text-gray-400" />
                            <span className="font-medium text-gray-900">
                              {formatCurrency(invoice.rechnungsbetrag)}
                            </span>
                          </div>
                          {invoice.rechnungseingang && (
                            <div className="flex items-center space-x-2 text-sm">
                              <Calendar className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-500">
                                {new Date(invoice.rechnungseingang).toLocaleDateString('de-DE')}
                              </span>
                            </div>
                          )}
                          {invoice.faelligkeit && (
                            <div className="text-sm text-gray-500">
                              Due: {new Date(invoice.faelligkeit).toLocaleDateString('de-DE')}
                            </div>
                          )}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="space-y-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(invoice.status)}`}>
                            {invoice.status || 'uploaded'}
                          </span>
                          {invoice.review_status && (
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getReviewStatusColor(invoice.review_status)}`}>
                              {invoice.review_status.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <Link
                            href={`/invoice-editor/${invoice.id}`}
                            className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                          >
                            <Edit3 className="h-4 w-4" />
                            <span>Edit</span>
                          </Link>
                          
                          <button
                            onClick={() => deleteInvoice(invoice.id, invoice.file_name)}
                            className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                            <span>Delete</span>
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
      </main>
    </div>
  )
}
