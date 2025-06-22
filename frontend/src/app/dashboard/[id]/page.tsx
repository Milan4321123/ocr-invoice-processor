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
  const [processing, setProcessing] = useState(false)
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
      setError(null)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      
      // Add timeout for API requests
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 second timeout
      
      // Fetch invoice details
      const invoiceResponse = await fetch(`${apiUrl}/invoices/${invoiceId}`, {
        signal: controller.signal
      })
      
      if (!invoiceResponse.ok) {
        throw new Error(`Failed to fetch invoice: ${invoiceResponse.status} ${invoiceResponse.statusText}`)
      }
      
      const invoiceData = await invoiceResponse.json()
      setInvoice(invoiceData.invoice)
      
      // Fetch OCR data (optional, may not exist)
      try {
        const ocrResponse = await fetch(`${apiUrl}/invoices/${invoiceId}/ocr`, {
          signal: controller.signal
        })
        
        if (ocrResponse.ok) {
          const ocrResult = await ocrResponse.json()
          setOcrData(ocrResult.ocr_data)
        } else if (ocrResponse.status !== 404) {
          // Only log non-404 errors (404 means no OCR data exists yet)
          console.warn('Failed to fetch OCR data:', ocrResponse.status)
        }
      } catch (ocrError) {
        console.warn('OCR data fetch error:', ocrError)
        // Don't throw here - OCR data is optional
      }
      
      clearTimeout(timeoutId)
      
    } catch (err) {
      let errorMessage = 'Failed to load invoice data'
      
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          errorMessage = 'Request timed out. Please check your connection and try again.'
        } else {
          errorMessage = err.message
        }
      }
      
      console.error('Fetch error:', err)
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const processOcr = async () => {
    if (!invoiceId || processing) return;
    
    setProcessing(true)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      
      // Add timeout and better error handling
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout
      
      const response = await fetch(`${apiUrl}/ocr/process/${invoiceId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      toast.success('OCR processing started successfully')
      
      // Refresh the data after a short delay
      setTimeout(() => {
        fetchInvoiceData()
      }, 2000)
      
    } catch (err) {
      let errorMessage = 'Failed to process OCR'
      
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          errorMessage = 'OCR processing timed out. Please try again.'
        } else {
          errorMessage = err.message
        }
      }
      
      console.error('OCR processing error:', err)
      toast.error(errorMessage)
    } finally {
      setProcessing(false)
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
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
              onClick={(e) => {
                // Check if URL is valid before opening
                if (!invoice.url || invoice.url.trim() === '') {
                  e.preventDefault()
                  toast.error('PDF file is not available')
                }
              }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              <span>View PDF</span>
            </a>
            {(!ocrData || ocrData.ocr_status !== 'completed') && (
              <button
                onClick={processOcr}
                disabled={processing}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
                  processing 
                    ? 'bg-gray-400 cursor-not-allowed text-white' 
                    : 'bg-purple-600 hover:bg-purple-700 text-white'
                }`}
              >
                {processing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span>Process OCR</span>
                  </>
                )}
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
            disabled={processing}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
              processing 
                ? 'bg-gray-400 cursor-not-allowed text-white' 
                : 'bg-purple-600 hover:bg-purple-700 text-white'
            }`}
          >
            {processing ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing OCR...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span>Process with OCR</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
