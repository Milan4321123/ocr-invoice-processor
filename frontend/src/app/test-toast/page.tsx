'use client'

import React from 'react'
import { toast, Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'

export default function ToastTestPage() {
  const showSuccessToast = () => {
    toast.success('This is a success notification!')
  }

  const showErrorToast = () => {
    toast.error('This is an error notification!')
  }

  const showLoadingToast = () => {
    toast.loading('This is a loading notification...')
  }

  const showInfoToast = () => {
    toast('This is a regular notification!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
      <Toaster {...toastConfig} />
      
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
          Toast Notification Test
        </h1>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-8">
          <p className="text-gray-600 mb-6 text-center">
            Click the buttons below to test toast notifications. 
            They should appear at the bottom-right corner with enhanced styling.
          </p>
          
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={showSuccessToast}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Success Toast
            </button>
            
            <button
              onClick={showErrorToast}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Error Toast
            </button>
            
            <button
              onClick={showLoadingToast}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Loading Toast
            </button>
            
            <button
              onClick={showInfoToast}
              className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Info Toast
            </button>
          </div>
          
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">Expected Behavior:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Notifications appear at bottom-right corner</li>
              <li>• Enhanced styling with gradients and improved shadows</li>
              <li>• Appropriate colors for each notification type</li>
              <li>• Smooth animations and proper spacing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
