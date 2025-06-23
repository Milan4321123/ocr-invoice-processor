'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast, Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'
import { OCRProcessingButton, BatchOCRProcessor } from '@/components/OCRProcessingComponents'

interface Invoice {
  id: string
  filename: string
  url: string
  status: 'uploaded' | 'processing' | 'completed' | 'error'
  file_size: number
  created_at: string
  
  // OCR Data Fields
  ocr_status?: 'completed' | 'failed' | 'processing' | null
  ocr_text?: string
  ocr_confidence?: number
  ocr_pages?: number
  ocr_processing_time?: number
  ocr_error?: string
  ocr_processed_at?: string
  
  // Structured Invoice Data
  invoice_number?: string
  invoice_date?: string
  due_date?: string
  vendor_name?: string
  vendor_address?: string
  customer_name?: string
  customer_address?: string
  subtotal?: number
  tax_amount?: number
  total_amount?: number
  currency?: string
  payment_terms?: string
  po_number?: string
  
  // Complex OCR Data
  entities?: any[]
  form_fields?: any[]
  tables?: any[]
  line_items?: any[]
}

export default function DashboardPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(false)

  useEffect(() => {
    fetchInvoices()
  }, [])

  // Auto-refresh when OCR processing is happening
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (autoRefresh) {
      interval = setInterval(fetchInvoices, 3000) // Refresh every 3 seconds
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  // Check if any invoices are processing to enable auto-refresh
  useEffect(() => {
    const processingInvoices = invoices.some(inv => inv.ocr_status === 'processing')
    setAutoRefresh(processingInvoices)
  }, [invoices])

  const fetchInvoices = async () => {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/invoices`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch invoices')
      }
      
      const data = await response.json()
      setInvoices(data.invoices || []) // Fix: extract invoices array from response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load invoices'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'uploaded':
        return 'bg-blue-100 text-blue-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getOcrStatusColor = (status: string | null | undefined): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getOcrStatusDisplay = (status: string | null | undefined) => {
    switch (status) {
      case 'completed':
        return (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <span>Completed</span>
          </div>
        )
      case 'failed':
        return (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>Failed</span>
          </div>
        )
      case 'processing':
        return (
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Processing</span>
          </div>
        )
      case 'pending':
        return (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <span>Pending</span>
          </div>
        )
      default:
        return (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <span>Not processed</span>
          </div>
        )
    }
  }

  const formatCurrency = (amount: number | null | undefined, currency: string = 'USD'): string => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD'
    }).format(amount)
  }

  const deleteInvoice = async (id: string) => {
    if (!confirm('Are you sure you want to delete this invoice?')) {
      return
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/invoices/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to delete invoice')
      }

      setInvoices(invoices.filter(invoice => invoice.id !== id))
      toast.success('Invoice deleted successfully')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete invoice'
      toast.error(errorMessage)
    }
  }

  const processInvoice = async (id: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/ocr/process/${id}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to process invoice')
      }

      toast.success('Invoice OCR processing started')
      fetchInvoices() // Refresh the list
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process invoice'
      toast.error(errorMessage)
    }
  }

  const viewOcrData = async (invoice: Invoice) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/invoices/${invoice.id}/ocr`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch OCR data')
      }
      
      const data = await response.json()
      
      // Create a detailed OCR data display
      const ocrInfo = data.ocr_data
      let message = `📄 OCR Data for ${invoice.filename}\n\n`
      
      if (ocrInfo.ocr_status === 'completed') {
        message += `✅ Status: Completed\n`
        message += `🎯 Confidence: ${(ocrInfo.ocr_confidence * 100).toFixed(1)}%\n`
        message += `📝 Pages: ${ocrInfo.ocr_pages}\n`
        message += `⏱️ Processing Time: ${ocrInfo.ocr_processing_time?.toFixed(2)}s\n\n`
        
        if (ocrInfo.structured_data) {
          const structured = ocrInfo.structured_data
          message += `📋 EXTRACTED DATA:\n`
          if (structured.invoice_number) message += `Invoice #: ${structured.invoice_number}\n`
          if (structured.invoice_date) message += `Date: ${structured.invoice_date}\n`
          if (structured.vendor_name) message += `Vendor: ${structured.vendor_name}\n`
          if (structured.total_amount) message += `Total: ${formatCurrency(structured.total_amount, structured.currency)}\n`
          if (structured.payment_terms) message += `Terms: ${structured.payment_terms}\n`
        }
        
        if (ocrInfo.entities?.length > 0) {
          message += `\n🏷️ ENTITIES (${ocrInfo.entities.length}):\n`
          ocrInfo.entities.slice(0, 5).forEach((entity: any) => {
            message += `• ${entity.type}: ${entity.text} (${(entity.confidence * 100).toFixed(1)}%)\n`
          })
        }
      } else if (ocrInfo.ocr_status === 'failed') {
        message += `❌ Status: Failed\n`
        message += `Error: ${ocrInfo.ocr_error}\n`
      } else {
        message += `⏳ Status: ${ocrInfo.ocr_status || 'Not processed'}\n`
      }
      
      alert(message)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch OCR data'
      toast.error(errorMessage)
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

  return (
    <div className="container mx-auto px-4 py-8">
      <Toaster {...toastConfig} />
      
      <div className="mb-8">
        <Link 
          href="/" 
          className="text-blue-600 hover:text-blue-800 flex items-center gap-2 mb-4"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </Link>
        
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Invoice Dashboard</h1>
            <p className="text-gray-600">
              Manage and track your uploaded invoices and their processing status.
            </p>
          </div>
          <div className="flex space-x-3">
            <Link
              href="/prufbericht"
              className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              📋 Prüfbericht
            </Link>
            <Link
              href="/upload"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Upload New Invoice
            </Link>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {invoices.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-24 h-24 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-xl font-medium text-gray-900 mb-2">No invoices uploaded</h3>
          <p className="text-gray-600 mb-6">Get started by uploading your first invoice.</p>
          <Link
            href="/upload"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-block"
          >
            Upload Invoice
          </Link>
        </div>
      ) : (
        <div>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
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
                <div className="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center mr-4">
                  <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {invoices.filter(i => i.ocr_status === 'completed').length}
                  </div>
                  <div className="text-sm text-gray-500">OCR Processed</div>
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
                    {invoices.filter(i => i.ocr_status === 'failed').length}
                  </div>
                  <div className="text-sm text-gray-500">OCR Failed</div>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-purple-50 rounded-full flex items-center justify-center mr-4">
                  <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7c-2 0-3 1-3 3z" />
                  </svg>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatFileSize(invoices.reduce((acc, invoice) => acc + invoice.file_size, 0))}
                  </div>
                  <div className="text-sm text-gray-500">Total Size</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Batch OCR Processor */}
          <div className="mb-6">
            <BatchOCRProcessor 
              invoices={invoices} 
              onRefresh={fetchInvoices}
            />
          </div>
          
          {/* Table */}
          <div className="bg-white shadow-sm rounded-lg overflow-hidden border border-gray-100">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200" style={{ minWidth: '800px' }}>
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    OCR Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Extracted Data
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded At
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
                        <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                          {invoice.filename}
                          <div className="text-xs text-gray-500">{invoice.id.substring(0, 8)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(invoice.status)}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col space-y-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded border inline-flex items-center ${getOcrStatusColor(invoice.ocr_status)}`}>
                          {getOcrStatusDisplay(invoice.ocr_status)}
                        </span>
                        {invoice.ocr_confidence !== undefined && invoice.ocr_confidence > 0 && (
                          <span className="text-xs text-gray-500">
                            {(invoice.ocr_confidence * 100).toFixed(1)}% confidence
                          </span>
                        )}
                        {autoRefresh && invoice.ocr_status === 'processing' && (
                          <span className="text-xs text-blue-600 animate-pulse">
                            Auto-refreshing...
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs">
                        {invoice.ocr_status === 'completed' ? (
                          <div className="space-y-1">
                            {invoice.invoice_number && (
                              <div className="text-xs">
                                <span className="font-medium">Invoice:</span> {invoice.invoice_number}
                              </div>
                            )}
                            {invoice.vendor_name && (
                              <div className="text-xs">
                                <span className="font-medium">Vendor:</span> {invoice.vendor_name}
                              </div>
                            )}
                            {invoice.total_amount && (
                              <div className="text-xs">
                                <span className="font-medium">Total:</span> {formatCurrency(invoice.total_amount, invoice.currency)}
                              </div>
                            )}
                            {invoice.invoice_date && (
                              <div className="text-xs">
                                <span className="font-medium">Date:</span> {invoice.invoice_date}
                              </div>
                            )}
                            {(!invoice.invoice_number && !invoice.vendor_name && !invoice.total_amount) && (
                              <div className="text-xs text-gray-500">No key data extracted</div>
                            )}
                          </div>
                        ) : invoice.ocr_status === 'failed' ? (
                          <div className="text-xs text-red-600">
                            OCR processing failed
                          </div>
                        ) : (
                          <div className="text-xs text-gray-500">
                            OCR not processed
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatFileSize(invoice.file_size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(invoice.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end items-center space-x-2">
                        <a 
                          href={invoice.url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50"
                          title="View PDF"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </a>
                        
                        <Link 
                          href={`/invoice-editor/${invoice.id}`}
                          className="text-indigo-600 hover:text-indigo-800 px-2 py-1 rounded hover:bg-indigo-50"
                          title="Edit Invoice"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </Link>
                        
                        {invoice.ocr_status === 'completed' && (
                          <button 
                            onClick={() => viewOcrData(invoice)}
                            className="text-green-600 hover:text-green-800 px-2 py-1 rounded hover:bg-green-50"
                            title="View OCR Data"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </button>
                        )}
                        
                        <OCRProcessingButton
                          invoiceId={invoice.id}
                          invoiceFilename={invoice.filename}
                          currentStatus={invoice.ocr_status}
                          onStatusChange={fetchInvoices}
                          disabled={invoice.ocr_status === 'processing'}
                        />
                        
                        <button 
                          onClick={() => deleteInvoice(invoice.id)}
                          className="text-red-600 hover:text-red-800 px-2 py-1 rounded hover:bg-red-50"
                          title="Delete Invoice"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
