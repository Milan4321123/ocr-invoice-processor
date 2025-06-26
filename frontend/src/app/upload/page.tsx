'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Dropzone from '../../components/Dropzone'
import toast, { Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'

interface UploadedFile {
  id: string
  url: string
  status: string
  filename: string
  file_size: number
  message: string
}

export default function UploadPage() {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const router = useRouter()

  const handleUploadStart = () => {
    setIsUploading(true)
    toast.loading('Uploading file...', { id: 'upload' })
  }

  const handleUploadComplete = (data: UploadedFile) => {
    setUploadedFile(data)
    setIsUploading(false)
    toast.success('File uploaded successfully!', { id: 'upload' })
  }

  const handleUploadError = (error: string) => {
    setIsUploading(false)
    toast.error(error, { id: 'upload' })
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const navigateToDashboard = () => {
    router.push('/dashboard')
  }

  const uploadAnother = () => {
    setUploadedFile(null)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Toaster {...toastConfig} />
      
      <div className="max-w-2xl mx-auto">
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
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Invoice</h1>
          <p className="text-gray-600">
            Upload your PDF invoice for storage and manual editing with searchable dropdowns.
          </p>
        </div>

        {!uploadedFile ? (
          <div className="space-y-6">
            <Dropzone
              onUploadStart={handleUploadStart}
              onUploadComplete={handleUploadComplete}
              onUploadError={handleUploadError}
            />
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Filename Requirements:</h3>
              <p className="text-sm text-gray-600 mb-2">
                <code className="bg-gray-200 px-2 py-1 rounded">
                  YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf
                </code>
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• <strong>YYYYMMDD:</strong> Date in format (e.g., 20241201)</li>
                <li>• <strong>IDENTIFIER:</strong> Invoice or order number (e.g., INV001)</li>
                <li>• <strong>VENDOR:</strong> Company name (e.g., ACME)</li>
                <li>• <strong>TYPE:</strong> Document type (e.g., SUPPLY, SERVICE)</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <svg className="w-6 h-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h2 className="text-lg font-semibold text-green-800">Upload Successful!</h2>
            </div>
            
            <div className="space-y-2 mb-6">
              <p><strong>Filename:</strong> {uploadedFile.filename}</p>
              <p><strong>File Size:</strong> {formatFileSize(uploadedFile.file_size)}</p>
              <p><strong>Status:</strong> {uploadedFile.status}</p>
              <p><strong>File ID:</strong> {uploadedFile.id}</p>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={navigateToDashboard}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                View Dashboard
              </button>
              <button
                onClick={uploadAnother}
                className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Upload Another File
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
