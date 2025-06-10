'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast, Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'

interface Invoice {
  id: string
  filename: string
  url: string
  status: string
  file_size: number
  created_at: string
}

interface OcrData {
  ocr_status: string
  ocr_text: string
  ocr_confidence: number
  ocr_pages: number
  ocr_processing_time: number
  ocr_error?: string
  ocr_processed_at: string
  entities: any[]
  form_fields: any[]
  tables: any[]
  structured_data: {
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
    line_items?: any[]
  }
}

export default function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [ocrData, setOcrData] = useState<OcrData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [invoiceId, setInvoiceId] = useState<string | null>(null)

  useEffect(() => {
    const loadParams = async () => {
      const resolvedParams = await params;
      setInvoiceId(resolvedParams.id);
    };
    loadParams();
  }, [params]);

  useEffect(() => {
    if (invoiceId) {
      fetchInvoiceData();
    }
  }, [invoiceId]);

  const fetchInvoiceData = async () => {
    if (!invoiceId) return;
    
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      
      // Fetch invoice details
      const invoiceResponse = await fetch(`${apiUrl}/invoices/${invoiceId}`)
      if (!invoiceResponse.ok) {
        throw new Error('Failed to fetch invoice')
      }
      const invoiceData = await invoiceResponse.json()
      setInvoice(invoiceData.invoice)
      
      // Fetch OCR data
      const ocrResponse = await fetch(`${apiUrl}/invoices/${invoiceId}/ocr`)
      if (ocrResponse.ok) {
        const ocrResult = await ocrResponse.json()
        setOcrData(ocrResult.ocr_data)
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load invoice data'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const processOcr = async () => {
    if (!invoiceId) return;
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/ocr/process/${invoiceId}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to process OCR')
      }

      toast.success('OCR processing started')
      setTimeout(fetchInvoiceData, 2000) // Refresh after 2 seconds
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process OCR'
      toast.error(errorMessage)
    }
  }

  const formatCurrency = (amount: number | null | undefined, currency: string = 'USD'): string => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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

  if (error || !invoice) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-800">{error || 'Invoice not found'}</p>
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
        <Link 
          href="/dashboard" 
          className="text-blue-600 hover:text-blue-800 flex items-center gap-2 mb-4"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </Link>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Invoice Details</h1>
            <p className="text-gray-600 mb-4">{invoice.filename}</p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Uploaded: {formatDate(invoice.created_at)}</span>
              <span>Size: {(invoice.file_size / 1024).toFixed(1)} KB</span>
            </div>
          </div>
          <div className="flex space-x-3">
            <a 
              href={invoice.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              View PDF
            </a>
            {(!ocrData || ocrData.ocr_status !== 'completed') && (
              <button
                onClick={processOcr}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Process OCR
              </button>
            )}
          </div>
        </div>
      </div>

      {/* OCR Data */}
      {ocrData ? (
        <div className="space-y-6">
          {/* OCR Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">OCR Processing Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Status</div>
                <div className={`text-lg font-semibold ${
                  ocrData.ocr_status === 'completed' ? 'text-green-600' :
                  ocrData.ocr_status === 'failed' ? 'text-red-600' : 'text-yellow-600'
                }`}>
                  {ocrData.ocr_status}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Confidence</div>
                <div className="text-lg font-semibold text-gray-900">
                  {(ocrData.ocr_confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Pages</div>
                <div className="text-lg font-semibold text-gray-900">{ocrData.ocr_pages}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-500">Processing Time</div>
                <div className="text-lg font-semibold text-gray-900">{ocrData.ocr_processing_time?.toFixed(2)}s</div>
              </div>
            </div>
            {ocrData.ocr_error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="text-sm font-medium text-red-800">Error Details:</div>
                <div className="text-sm text-red-700 mt-1">{ocrData.ocr_error}</div>
              </div>
            )}
          </div>

          {/* Structured Data */}
          {ocrData.structured_data && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Extracted Invoice Data</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
                  <div className="space-y-3">
                    {ocrData.structured_data.invoice_number && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Invoice Number:</span>
                        <div className="text-lg font-semibold text-gray-900">{ocrData.structured_data.invoice_number}</div>
                      </div>
                    )}
                    {ocrData.structured_data.invoice_date && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Invoice Date:</span>
                        <div className="text-lg text-gray-900">{ocrData.structured_data.invoice_date}</div>
                      </div>
                    )}
                    {ocrData.structured_data.due_date && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Due Date:</span>
                        <div className="text-lg text-gray-900">{ocrData.structured_data.due_date}</div>
                      </div>
                    )}
                    {ocrData.structured_data.po_number && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">PO Number:</span>
                        <div className="text-lg text-gray-900">{ocrData.structured_data.po_number}</div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Financial Information</h3>
                  <div className="space-y-3">
                    {ocrData.structured_data.subtotal && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Subtotal:</span>
                        <div className="text-lg text-gray-900">{formatCurrency(ocrData.structured_data.subtotal, ocrData.structured_data.currency)}</div>
                      </div>
                    )}
                    {ocrData.structured_data.tax_amount && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Tax Amount:</span>
                        <div className="text-lg text-gray-900">{formatCurrency(ocrData.structured_data.tax_amount, ocrData.structured_data.currency)}</div>
                      </div>
                    )}
                    {ocrData.structured_data.total_amount && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Total Amount:</span>
                        <div className="text-xl font-bold text-green-600">{formatCurrency(ocrData.structured_data.total_amount, ocrData.structured_data.currency)}</div>
                      </div>
                    )}
                    {ocrData.structured_data.payment_terms && (
                      <div>
                        <span className="text-sm font-medium text-gray-500">Payment Terms:</span>
                        <div className="text-lg text-gray-900">{ocrData.structured_data.payment_terms}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Vendor and Customer Info */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                {ocrData.structured_data.vendor_name && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Vendor Information</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-lg font-semibold text-gray-900">{ocrData.structured_data.vendor_name}</div>
                      {ocrData.structured_data.vendor_address && (
                        <div className="text-sm text-gray-600 mt-1">{ocrData.structured_data.vendor_address}</div>
                      )}
                    </div>
                  </div>
                )}
                
                {ocrData.structured_data.customer_name && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Customer Information</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-lg font-semibold text-gray-900">{ocrData.structured_data.customer_name}</div>
                      {ocrData.structured_data.customer_address && (
                        <div className="text-sm text-gray-600 mt-1">{ocrData.structured_data.customer_address}</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Entities */}
          {ocrData.entities && ocrData.entities.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Detected Entities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {ocrData.entities.map((entity, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm font-medium text-gray-500">{entity.type}</div>
                    <div className="text-lg text-gray-900">{entity.text}</div>
                    <div className="text-xs text-gray-400">Confidence: {(entity.confidence * 100).toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Form Fields */}
          {ocrData.form_fields && ocrData.form_fields.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Form Fields</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ocrData.form_fields.map((field, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm font-medium text-gray-500">{field.name}</div>
                    <div className="text-lg text-gray-900">{field.value}</div>
                    <div className="text-xs text-gray-400">Confidence: {(field.confidence * 100).toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw OCR Text */}
          {ocrData.ocr_text && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Raw OCR Text</h2>
              <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">{ocrData.ocr_text}</pre>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-8 text-center">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-xl font-medium text-gray-900 mb-2">No OCR Data Available</h3>
          <p className="text-gray-600 mb-6">This invoice hasn't been processed with OCR yet.</p>
          <button
            onClick={processOcr}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Process with OCR
          </button>
        </div>
      )}
    </div>
  )
}
