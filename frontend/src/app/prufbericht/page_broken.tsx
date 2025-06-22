'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast } from 'react-hot-toast'

// Types for Prüfbericht data
interface InvoiceSummaryItem {
  id: string
  filename: string
  vendor_name?: string
  total_amount?: number
  invoice_date?: string
  due_date?: string
  ocr_status: string
  status: string
  ocr_confidence?: number
  projekt?: string
  source_type?: string
  urgency: string
  days_until_due?: number
  has_missing_data: boolean
  ocr_quality: string
  created_at: string
  url?: string
}

interface DataQualityMetrics {
  total_invoices: number
  ocr_statistics: {
    completed: number
    pending: number
    failed: number
    completion_rate: number
  }
  missing_data: {
    due_dates: number
    amounts: number
    vendors: number
    total_missing: number
  }
  confidence_metrics: {
    average: number
    average_percentage: number
    high_confidence: number
    medium_confidence: number
    low_confidence: number
  }
  quality_score: {
    overall: number
    ocr_processing: number
    data_completeness: number
    ocr_confidence: number
  }
}

interface CriticalDatesInfo {
  overdue: { count: number; total_amount: number; invoices: InvoiceSummaryItem[] }
  due_this_week: { count: number; total_amount: number; invoices: InvoiceSummaryItem[] }
  due_next_week: { count: number; total_amount: number; invoices: InvoiceSummaryItem[] }
  future: { count: number; total_amount: number; invoices: InvoiceSummaryItem[] }
  no_due_date: { count: number; total_amount: number; invoices: InvoiceSummaryItem[] }
}

interface ProjectBreakdown {
  name: string
  invoice_count: number
  total_amount: number
  vendor_count: number
  vendors: string[]
  avg_confidence: number
}

interface ProcessingStatusData {
  processing_status: Record<string, { count: number; total_amount: number }>
  ocr_status: Record<string, { count: number; total_amount: number }>
  summary: {
    total_invoices: number
    total_amount: number
    status_distribution: Record<string, number>
    ocr_distribution: Record<string, number>
  }
}

export default function PrufberichtPage() {
  const [invoices, setInvoices] = useState<InvoiceSummaryItem[]>([])
  const [dataQuality, setDataQuality] = useState<DataQualityMetrics | null>(null)
  const [criticalDates, setCriticalDates] = useState<CriticalDatesInfo | null>(null)
  const [projects, setProjects] = useState<ProjectBreakdown[]>([])
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

  useEffect(() => {
    fetchPrufberichtData()
  }, [])

  const fetchPrufberichtData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all Prüfbericht data in parallel
      const [
        invoiceSummaryResponse,
        dataQualityResponse,
        criticalDatesResponse,
        projectAnalysisResponse,
        processingStatusResponse
      ] = await Promise.all([
        fetch(`${apiUrl}/api/reports/invoice-summary`),
        fetch(`${apiUrl}/api/reports/data-quality`),
        fetch(`${apiUrl}/api/reports/critical-dates`),
        fetch(`${apiUrl}/api/reports/project-analysis`),
        fetch(`${apiUrl}/api/reports/processing-status`)
      ])

      // Check if all requests were successful
      if (!invoiceSummaryResponse.ok || !dataQualityResponse.ok || !criticalDatesResponse.ok || 
          !projectAnalysisResponse.ok || !processingStatusResponse.ok) {
        throw new Error('Failed to fetch Prüfbericht data')
      }

      // Parse responses
      const [
        invoiceData,
        qualityData,
        datesData,
        projectData,
        statusData
      ] = await Promise.all([
        invoiceSummaryResponse.json(),
        dataQualityResponse.json(),
        criticalDatesResponse.json(),
        projectAnalysisResponse.json(),
        processingStatusResponse.json()
      ])

      // Update state
      setInvoices(invoiceData.data || [])
      setDataQuality(qualityData.metrics)
      setCriticalDates(datesData.data)
      setProjects(projectData.data?.projects || [])
      setProcessingStatus(statusData.data)

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
      case 'payment_ready': return 'bg-purple-100 text-purple-800'
      case 'paid': return 'bg-gray-100 text-gray-800'
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

  const getOcrQualityColor = (quality: string): string => {
    switch (quality) {
      case 'high': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
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
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">📋 Prüfbericht Dashboard</h1>
            <p className="text-gray-600 mt-2">Comprehensive invoice audit and control center for Bau-Leiter</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={fetchPrufberichtData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              🔄 Refresh Data
            </button>
            <Link
              href="/dashboard"
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-2xl">📊</div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Invoices</p>
              <p className="text-2xl font-bold text-gray-900">{dataQuality?.total_invoices || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-2xl">⚠️</div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Need Review</p>
              <p className="text-2xl font-bold text-orange-600">
                {invoices.filter(inv => inv.status === 'pending' || inv.has_missing_data).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-2xl">🔴</div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Overdue</p>
              <p className="text-2xl font-bold text-red-600">{criticalDates?.overdue.count || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="text-2xl">📈</div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Quality Score</p>
              <p className="text-2xl font-bold text-green-600">
                {dataQuality?.quality_score.overall || 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Data Quality Widget */}
      {dataQuality && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Data Quality Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">OCR Processing</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Completed:</span>
                  <span className="text-sm font-medium text-green-600">{dataQuality.ocr_statistics.completed}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Pending:</span>
                  <span className="text-sm font-medium text-yellow-600">{dataQuality.ocr_statistics.pending}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Failed:</span>
                  <span className="text-sm font-medium text-red-600">{dataQuality.ocr_statistics.failed}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Success Rate:</span>
                  <span className="text-sm font-medium">{dataQuality.ocr_statistics.completion_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Missing Data</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Due Dates:</span>
                  <span className="text-sm font-medium text-red-600">{dataQuality.missing_data.due_dates}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Amounts:</span>
                  <span className="text-sm font-medium text-red-600">{dataQuality.missing_data.amounts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Vendors:</span>
                  <span className="text-sm font-medium text-red-600">{dataQuality.missing_data.vendors}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Missing:</span>
                  <span className="text-sm font-medium text-red-600">{dataQuality.missing_data.total_missing}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">OCR Confidence</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Average:</span>
                  <span className="text-sm font-medium">{dataQuality.confidence_metrics.average_percentage.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">High (>80%):</span>
                  <span className="text-sm font-medium text-green-600">{dataQuality.confidence_metrics.high_confidence}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Medium (60-80%):</span>
                  <span className="text-sm font-medium text-yellow-600">{dataQuality.confidence_metrics.medium_confidence}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Low (<60%):</span>
                  <span className="text-sm font-medium text-red-600">{dataQuality.confidence_metrics.low_confidence}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Critical Dates Widget */}
      {criticalDates && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">⏰ Critical Payment Dates</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{criticalDates.overdue.count}</div>
              <div className="text-sm text-red-800">Overdue</div>
              <div className="text-xs text-red-600">{formatCurrency(criticalDates.overdue.total_amount)}</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{criticalDates.due_this_week.count}</div>
              <div className="text-sm text-orange-800">Due This Week</div>
              <div className="text-xs text-orange-600">{formatCurrency(criticalDates.due_this_week.total_amount)}</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{criticalDates.due_next_week.count}</div>
              <div className="text-sm text-yellow-800">Due Next Week</div>
              <div className="text-xs text-yellow-600">{formatCurrency(criticalDates.due_next_week.total_amount)}</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{criticalDates.future.count}</div>
              <div className="text-sm text-green-800">Future</div>
              <div className="text-xs text-green-600">{formatCurrency(criticalDates.future.total_amount)}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-600">{criticalDates.no_due_date.count}</div>
              <div className="text-sm text-gray-800">No Due Date</div>
              <div className="text-xs text-gray-600">{formatCurrency(criticalDates.no_due_date.total_amount)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Invoice Summary Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">📋 Invoice Summary Table</h2>
          <p className="text-sm text-gray-600 mt-1">Complete overview of all invoices for Bau-Leiter review</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dates</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OCR Quality</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.map((invoice) => (
                <tr key={invoice.id} className={invoice.has_missing_data ? 'bg-yellow-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{invoice.filename}</div>
                    <div className="text-xs text-gray-500">{invoice.projekt || 'No Project'}</div>
                    <div className="text-xs text-gray-500">
                      <span className={`px-2 py-1 rounded-full text-xs ${invoice.source_type === 'folder_watcher' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                        {invoice.source_type || 'manual'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{invoice.vendor_name || 'Unknown Vendor'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(invoice.total_amount)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <div>Invoice: {formatDate(invoice.invoice_date)}</div>
                      <div className="flex items-center">
                        <span>Due: {formatDate(invoice.due_date)}</span>
                        {invoice.days_until_due !== null && (
                          <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getUrgencyColor(invoice.urgency)}`}>
                            {invoice.days_until_due < 0 ? `${Math.abs(invoice.days_until_due)} days overdue` : 
                             invoice.days_until_due === 0 ? 'Due today' :
                             `${invoice.days_until_due} days left`}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(invoice.status)}`}>
                      {invoice.status}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">
                      OCR: {invoice.ocr_status}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getOcrQualityColor(invoice.ocr_quality)}`}>
                      {invoice.ocr_quality} ({((invoice.ocr_confidence || 0) * 100).toFixed(0)}%)
                    </span>
                    {invoice.has_missing_data && (
                      <div className="text-xs text-red-600 mt-1">Missing data</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex space-x-2">
                      <Link
                        href={`/dashboard/${invoice.id}`}
                        className="text-blue-600 hover:text-blue-800"
                        title="View Details"
                      >
                        👁️
                      </Link>
                      {invoice.url && (
                        <a
                          href={invoice.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-green-600 hover:text-green-800"
                          title="View PDF"
                        >
                          📄
                        </a>
                      )}
                      {invoice.has_missing_data && (
                        <button
                          className="text-orange-600 hover:text-orange-800"
                          title="Needs Review"
                        >
                          ⚠️
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Project Analysis */}
      {projects.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🏗️ Project Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.slice(0, 6).map((project) => (
              <div key={project.name} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-medium text-gray-900">{project.name}</h3>
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Invoices:</span>
                    <span className="font-medium">{project.invoice_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total:</span>
                    <span className="font-medium">{formatCurrency(project.total_amount)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Vendors:</span>
                    <span className="font-medium">{project.vendor_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Avg Quality:</span>
                    <span className="font-medium">{(project.avg_confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
