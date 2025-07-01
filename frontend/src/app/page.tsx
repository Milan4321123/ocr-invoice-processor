'use client'

import React from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  const navigateToUpload = () => {
    router.push('/upload')
  }

  const navigateToFolderWatcher = () => {
    router.push('/dashboard') // For now, linking to dashboard until you have a specific folder watcher page
  }

  return (
    <div className="container mx-auto px-4 py-8 pt-20">
      <div className="max-w-4xl mx-auto">
        {/* Welcome Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Willkommen
          </h1>
          <p className="text-xl text-gray-600">
            OCR Invoice Processor - Wählen Sie eine Option
          </p>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          {/* Upload Button */}
          <div 
            onClick={navigateToUpload}
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1 border-2 border-transparent hover:border-blue-200"
          >
            <div className="p-8 text-center">
              <div className="bg-blue-100 rounded-full p-4 w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Datei hochladen
              </h2>
              <p className="text-gray-600">
                PDF-Rechnungen einzeln hochladen und verarbeiten
              </p>
            </div>
          </div>

          {/* Folder Watcher Button */}
          <div 
            onClick={navigateToFolderWatcher}
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1 border-2 border-transparent hover:border-green-200"
          >
            <div className="p-8 text-center">
              <div className="bg-green-100 rounded-full p-4 w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0a2 2 0 002-2h6l2 2h6a2 2 0 012 2v1" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Ordner überwachen
              </h2>
              <p className="text-gray-600">
                Automatische Verarbeitung von Dateien aus überwachten Ordnern
              </p>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-12 bg-gray-50 rounded-lg p-6 max-w-2xl mx-auto">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              🔄 Automatisierte Rechnungsverarbeitung
            </h3>
            <p className="text-gray-600">
              Laden Sie PDF-Rechnungen hoch oder überwachen Sie Ordner für die automatische Verarbeitung. 
              Das System extrahiert Daten, ermöglicht manuelle Bearbeitung und versendet Benachrichtigungen.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
