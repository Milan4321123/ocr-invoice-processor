'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { toast } from 'react-hot-toast'

// Minimal working version for testing
export default function PrufberichtPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setLoading(false), 1000)
  }, [])

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
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">📋 Prüfbericht Dashboard</h1>
            <p className="text-gray-600 mt-2">Comprehensive invoice audit and control center for Bau-Leiter</p>
          </div>
          <div className="flex space-x-3">
            <Link
              href="/dashboard"
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Prüfbericht System</h2>
        <p className="text-gray-600 mb-6">Implementation in progress. Basic navigation is working.</p>
        <div className="flex justify-center space-x-4">
          <Link
            href="/dashboard"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
