'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast, Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'

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
  project?: string
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
  summary: {
    total_invoices: number
    overdue_count: number
    urgent_count: number
    upcoming_count: number
    missing_due_dates: number
  }
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
        throw new Error('Failed to fetch some report data')
      }

      // Parse all responses
      const [
        invoiceSummaryData,
        dataQualityData,
        criticalDatesData,
        projectAnalysisData,
        processingStatusData
      ] = await Promise.all([
        invoiceSummaryResponse.json(),
        dataQualityResponse.json(),
        criticalDatesResponse.json(),
        projectAnalysisResponse.json(),
        processingStatusResponse.json()
      ])

      // Set all data
      if (invoiceSummaryData.success) {
        setInvoices(invoiceSummaryData.data || [])
      }
      if (dataQualityData.success) {
        setDataQuality(dataQualityData.metrics || null)
      }
      if (criticalDatesData.success) {
        setCriticalDates(criticalDatesData.data || null)
      }
      if (projectAnalysisData.success) {
        setProjects(projectAnalysisData.data?.projects || [])
      }
      if (processingStatusData.success) {
        setProcessingStatus(processingStatusData.data || null)
      }

      toast.success('Prüfbericht data loaded successfully')
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
      <Toaster {...toastConfig} />
      
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
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center mr-4">
              <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{invoices.length}</div>
              <div className="text-sm text-gray-500">Total Invoices</div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-yellow-50 rounded-full flex items-center justify-center mr-4">
              <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {invoices.filter(inv => inv.has_missing_data).length}
              </div>
              <div className="text-sm text-gray-500">Need Review</div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center mr-4">
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {criticalDates?.overdue?.count || 0}
              </div>
              <div className="text-sm text-gray-500">Overdue</div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center mr-4">
              <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {dataQuality?.quality_score?.overall?.toFixed(1) || '0.0'}%
              </div>
              <div className="text-sm text-gray-500">Quality Score</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        
        {/* Data Quality Widget */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Data Quality</h2>
          {dataQuality ? (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm">
                  <span>OCR Completion</span>
                  <span>{dataQuality.ocr_statistics.completion_rate.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${dataQuality.ocr_statistics.completion_rate}%` }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm">
                  <span>Data Completeness</span>
                  <span>{dataQuality.quality_score.data_completeness.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${Math.max(0, dataQuality.quality_score.data_completeness)}%` }}
                  ></div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="text-center p-3 bg-green-50 rounded">
                  <div className="text-lg font-semibold text-green-600">{dataQuality.confidence_metrics.high_confidence}</div>
                  <div className="text-xs text-green-600">High Confidence</div>
                </div>
                <div className="text-center p-3 bg-red-50 rounded">
                  <div className="text-lg font-semibold text-red-600">{dataQuality.missing_data.total_missing}</div>
                  <div className="text-xs text-red-600">Missing Data</div>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No data quality metrics available</p>
          )}
        </div>

        {/* Critical Dates Widget */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">⏰ Critical Dates</h2>
          {criticalDates ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-red-50 rounded">
                <span className="text-sm font-medium text-red-800">Overdue</span>
                <div className="text-right">
                  <div className="text-lg font-semibold text-red-600">{criticalDates.overdue.count}</div>
                  <div className="text-xs text-red-600">{formatCurrency(criticalDates.overdue.total_amount)}</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-orange-50 rounded">
                <span className="text-sm font-medium text-orange-800">Due This Week</span>
                <div className="text-right">
                  <div className="text-lg font-semibold text-orange-600">{criticalDates.due_this_week.count}</div>
                  <div className="text-xs text-orange-600">{formatCurrency(criticalDates.due_this_week.total_amount)}</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-yellow-50 rounded">
                <span className="text-sm font-medium text-yellow-800">Due Next Week</span>
                <div className="text-right">
                  <div className="text-lg font-semibold text-yellow-600">{criticalDates.due_next_week.count}</div>
                  <div className="text-xs text-yellow-600">{formatCurrency(criticalDates.due_next_week.total_amount)}</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium text-gray-800">No Due Date</span>
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-600">{criticalDates.no_due_date.count}</div>
                  <div className="text-xs text-gray-600">{formatCurrency(criticalDates.no_due_date.total_amount)}</div>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No critical dates data available</p>
          )}
        </div>

        {/* Processing Status Widget */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">⚙️ Processing Status</h2>
          {processingStatus ? (
            <div className="space-y-3">
              {Object.entries(processingStatus.processing_status).map(([status, data]) => (
                <div key={status} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm font-medium text-gray-800 capitalize">{status}</span>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-gray-600">{data.count}</div>
                    <div className="text-xs text-gray-600">{formatCurrency(data.total_amount)}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No processing status data available</p>
          )}
        </div>
      </div>

      {/* Invoice Summary Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">📋 Invoice Summary</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Urgency
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quality
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">{invoice.filename}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{invoice.vendor_name || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatCurrency(invoice.total_amount)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatDate(invoice.due_date)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(invoice.status)}`}>
                      {invoice.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getUrgencyColor(invoice.urgency)}`}>
                      {invoice.urgency.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getOcrQualityColor(invoice.ocr_quality)}`}>
                      {invoice.ocr_quality}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link
                      href={`/dashboard/${invoice.id}`}
                      className="text-blue-600 hover:text-blue-900"
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

      {/* Project Analysis Section */}
      {projects.length > 0 && (
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🏗️ Project Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((project, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-2">{project.name}</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Invoices:</span>
                    <span className="font-medium">{project.invoice_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Total:</span>
                    <span className="font-medium">{formatCurrency(project.total_amount)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Vendors:</span>
                    <span className="font-medium">{project.vendor_count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Confidence:</span>
                    <span className="font-medium">{(project.avg_confidence * 100).toFixed(1)}%</span>
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