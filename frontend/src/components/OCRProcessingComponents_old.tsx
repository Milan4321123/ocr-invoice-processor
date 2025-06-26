/**
 * Enhanced OCR Processing Components for Phase 2
 * Provides better user experience for manual OCR processing
 */
import React, { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'

interface OCRProgress {
  invoiceId: string
  status: 'idle' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
}

interface OCRProcessingButtonProps {
  invoiceId: string
  invoiceFilename: string
  currentStatus: string | null | undefined
  onStatusChange: () => void
  disabled?: boolean
}

export function OCRProcessingButton({ 
  invoiceId, 
  invoiceFilename, 
  currentStatus, 
  onStatusChange,
  disabled = false 
}: OCRProcessingButtonProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)

  const processOCR = async () => {
    if (isProcessing) return
    
    setIsProcessing(true)
    setProgress(10)
    
    try {
      // Start progress animation
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 90))
      }, 300)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/ocr/process/${invoiceId}`, {
        method: 'POST'
      })

      clearInterval(progressInterval)
      setProgress(100)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to process invoice')
      }

      const result = await response.json()
      
      // Success feedback
      if (result.status === 'success') {
        toast.success(`✅ OCR processing completed for ${invoiceFilename}`, {
          duration: 4000,
          position: 'top-right'
        })
      } else if (result.status === 'already_processed') {
        toast.success(`ℹ️ OCR already processed for ${invoiceFilename}`, {
          duration: 3000
        })
      }
      
      // Trigger refresh
      setTimeout(() => {
        onStatusChange()
        setIsProcessing(false)
        setProgress(0)
      }, 1000)

    } catch (err) {
      setProgress(0)
      setIsProcessing(false)
      const errorMessage = err instanceof Error ? err.message : 'Failed to process invoice'
      toast.error(`❌ OCR failed: ${errorMessage}`, {
        duration: 5000,
        position: 'top-right'
      })
    }
  }

  const getButtonContent = () => {
    if (isProcessing) {
      return (
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Processing... {progress}%</span>
        </div>
      )
    }

    if (currentStatus === 'completed') {
      return (
        <div className="flex items-center space-x-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Re-process</span>
        </div>
      )
    }

    if (currentStatus === 'failed') {
      return (
        <div className="flex items-center space-x-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Retry OCR</span>
        </div>
      )
    }

    return (
      <div className="flex items-center space-x-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <span>Extract OCR</span>
      </div>
    )
  }

  const getButtonStyle = () => {
    if (disabled) {
      return "bg-gray-300 text-gray-500 cursor-not-allowed"
    }
    
    if (isProcessing) {
      return "bg-blue-500 text-white cursor-wait"
    }

    if (currentStatus === 'completed') {
      return "bg-green-600 hover:bg-green-700 text-white"
    }

    if (currentStatus === 'failed') {
      return "bg-orange-600 hover:bg-orange-700 text-white"
    }

    return "bg-purple-600 hover:bg-purple-700 text-white"
  }

  return (
    <button
      onClick={processOCR}
      disabled={disabled || isProcessing}
      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${getButtonStyle()}`}
      title={isProcessing ? `Processing OCR: ${progress}%` : undefined}
    >
      {getButtonContent()}
    </button>
  )
}

interface BatchOCRProps {
  invoices: Array<{
    id: string
    filename: string
    ocr_status?: string | null
  }>
  onRefresh: () => void
}

export function BatchOCRProcessor({ invoices, onRefresh }: BatchOCRProps) {
  const [isBatchProcessing, setBatchProcessing] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [results, setResults] = useState<{success: number, failed: number}>({success: 0, failed: 0})

  const pendingInvoices = invoices.filter(inv => 
    !inv.ocr_status || inv.ocr_status === 'failed' || inv.ocr_status === 'pending'
  )

  const processBatch = async () => {
    if (pendingInvoices.length === 0) {
      toast.error('No invoices pending OCR processing')
      return
    }

    setBatchProcessing(true)
    setCurrentIndex(0)
    setResults({success: 0, failed: 0})

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

    for (let i = 0; i < pendingInvoices.length; i++) {
      const invoice = pendingInvoices[i]
      setCurrentIndex(i + 1)

      try {
        const response = await fetch(`${apiUrl}/ocr/process/${invoice.id}`, {
          method: 'POST'
        })

        if (response.ok) {
          setResults(prev => ({...prev, success: prev.success + 1}))
          toast.success(`✅ ${invoice.filename} processed`, {duration: 2000})
        } else {
          setResults(prev => ({...prev, failed: prev.failed + 1}))
          toast.error(`❌ ${invoice.filename} failed`, {duration: 2000})
        }
      } catch (error) {
        setResults(prev => ({...prev, failed: prev.failed + 1}))
        toast.error(`❌ ${invoice.filename} error`, {duration: 2000})
      }

      // Small delay between processing
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    setBatchProcessing(false)
    toast.success(`🎉 Batch processing complete! ${results.success} succeeded, ${results.failed} failed`, {
      duration: 6000
    })
    
    // Refresh the invoice list
    setTimeout(onRefresh, 1000)
  }

  if (pendingInvoices.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-green-700 font-medium">All invoices have been processed</span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Batch OCR Processing</h3>
          <p className="text-sm text-gray-500">
            {pendingInvoices.length} invoice{pendingInvoices.length !== 1 ? 's' : ''} pending OCR processing
          </p>
        </div>
        
        <button
          onClick={processBatch}
          disabled={isBatchProcessing}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isBatchProcessing 
              ? 'bg-gray-300 text-gray-500 cursor-wait' 
              : 'bg-purple-600 hover:bg-purple-700 text-white'
          }`}
        >
          {isBatchProcessing ? (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing {currentIndex}/{pendingInvoices.length}</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Process All ({pendingInvoices.length})</span>
            </div>
          )}
        </button>
      </div>

      {isBatchProcessing && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress: {currentIndex}/{pendingInvoices.length}</span>
            <span>Success: {results.success} | Failed: {results.failed}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentIndex / pendingInvoices.length) * 100}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  )
}
