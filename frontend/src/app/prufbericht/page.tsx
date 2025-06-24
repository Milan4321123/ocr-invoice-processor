'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast, Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'

// Simplified types for business-focused Prüfbericht
interface InvoiceItem {
  id: string
  filename: string
  vendor_name?: string
  total_amount?: number
  invoice_date?: string
  due_date?: string
  skonto_date?: string
  skonto_percentage?: number
  status: string
  approval_status: 'pending' | 'approved' | 'rejected'
  urgency: string
  days_until_due?: number
  days_until_skonto?: number
  created_at: string
  url?: string
  notes?: string
  approved_by?: string
  approved_at?: string
}

interface CriticalDatesInfo {
  overdue: { count: number; total_amount: number; invoices: InvoiceItem[] }
  due_this_week: { count: number; total_amount: number; invoices: InvoiceItem[] }
  due_next_week: { count: number; total_amount: number; invoices: InvoiceItem[] }
  skonto_expiring: { count: number; total_amount: number; potential_savings: number; invoices: InvoiceItem[] }
  future: { count: number; total_amount: number; invoices: InvoiceItem[] }
}

export default function PrufberichtPage() {
  const [invoices, setInvoices] = useState<InvoiceItem[]>([])
  const [criticalDates, setCriticalDates] = useState<CriticalDatesInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchPrufberichtData()
  }, [])

  const fetchPrufberichtData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch data from our new Prüfbericht API endpoints
      const [
        invoiceSummaryResponse,
        criticalDatesResponse
      ] = await Promise.all([
        fetch(`${apiUrl}/api/reports/invoice-summary`),
        fetch(`${apiUrl}/api/reports/critical-dates`)
      ])

      // Check if requests were successful
      if (!invoiceSummaryResponse.ok || !criticalDatesResponse.ok) {
        throw new Error('Failed to fetch Prüfbericht data')
      }

      // Parse responses
      const [
        invoiceSummaryData,
        criticalDatesData
      ] = await Promise.all([
        invoiceSummaryResponse.json(),
        criticalDatesResponse.json()
      ])

      // Set data
      if (invoiceSummaryData.success) {
        setInvoices(invoiceSummaryData.data || [])
      }
      if (criticalDatesData.success) {
        setCriticalDates(criticalDatesData.data || null)
      }

      toast.success('Prüfbericht loaded successfully')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load Prüfbericht data'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number | undefined): string => {
    if (!amount) return '€0.00'
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount)
  }

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('de-DE')
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'uploaded': return 'bg-blue-100 text-blue-800'
      case 'processing': return 'bg-blue-100 text-blue-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getUrgencyColor = (urgency: string): string => {
    switch (urgency) {
      case 'overdue': return 'bg-red-100 text-red-800'
      case 'due_this_week': return 'bg-orange-100 text-orange-800'
      case 'due_next_week': return 'bg-yellow-100 text-yellow-800'
      case 'future': return 'bg-green-100 text-green-800'
      case 'no_due_date': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getApprovalStatusColor = (status: string): string => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleApproval = async (invoiceId: string, action: 'approve' | 'reject') => {
    try {
      const response = await fetch(`${apiUrl}/api/invoices/${invoiceId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        toast.success(`Invoice ${action}ed successfully`)
        fetchPrufberichtData() // Refresh data
      } else {
        throw new Error(`Failed to ${action} invoice`)
      }
    } catch (error) {
      toast.error(`Failed to ${action} invoice`)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error Loading Prüfbericht</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={fetchPrufberichtData}
                  className="bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded-md text-sm font-medium"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Toaster {...toastConfig} />
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📋 Prüfbericht - Invoice Approval Dashboard</h1>
        <p className="text-gray-600">Review and approve invoices, manage critical dates and skonto opportunities</p>
      </div>

      {/* Critical Dates Overview */}
      {criticalDates && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          
          {/* Overdue */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-red-700">{criticalDates.overdue.count}</div>
                <div className="text-sm text-red-600">Overdue Invoices</div>
                <div className="text-xs text-red-500 mt-1">{formatCurrency(criticalDates.overdue.total_amount)}</div>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Due This Week */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-orange-700">{criticalDates.due_this_week.count}</div>
                <div className="text-sm text-orange-600">Due This Week</div>
                <div className="text-xs text-orange-500 mt-1">{formatCurrency(criticalDates.due_this_week.total_amount)}</div>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Skonto Expiring */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-yellow-700">{criticalDates.skonto_expiring?.count || 0}</div>
                <div className="text-sm text-yellow-600">Skonto Expiring</div>
                <div className="text-xs text-yellow-500 mt-1">
                  Save: {formatCurrency(criticalDates.skonto_expiring?.potential_savings || 0)}
                </div>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
          </div>

          {/* Future */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-700">{criticalDates.future.count}</div>
                <div className="text-sm text-green-600">Future Invoices</div>
                <div className="text-xs text-green-500 mt-1">{formatCurrency(criticalDates.future.total_amount)}</div>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* Invoice Approval Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Invoice Approval Queue</h2>
            <div className="text-sm text-gray-500">
              {invoices.filter(inv => inv.approval_status === 'pending').length} pending approval
            </div>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skonto</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{invoice.filename}</div>
                    <div className="text-sm text-gray-500">
                      {formatDate(invoice.created_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{invoice.vendor_name || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(invoice.total_amount)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatDate(invoice.due_date)}</div>
                    <div className="text-xs text-gray-500">
                      {invoice.days_until_due !== undefined && (
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getUrgencyColor(invoice.urgency)}`}>
                          {invoice.days_until_due > 0 ? `${invoice.days_until_due} days` : 'Overdue'}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {invoice.skonto_date && invoice.skonto_percentage ? (
                      <div>
                        <div className="text-sm text-gray-900">{invoice.skonto_percentage}%</div>
                        <div className="text-xs text-gray-500">{formatDate(invoice.skonto_date)}</div>
                        {invoice.days_until_skonto !== undefined && invoice.days_until_skonto >= 0 && (
                          <div className="text-xs text-yellow-600">{invoice.days_until_skonto} days left</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">No skonto</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getApprovalStatusColor(invoice.approval_status)}`}>
                      {invoice.approval_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    {invoice.approval_status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleApproval(invoice.id, 'approve')}
                          className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleApproval(invoice.id, 'reject')}
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    <Link
                      href={`/dashboard/${invoice.id}`}
                      className="text-blue-600 hover:text-blue-900 text-xs"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
