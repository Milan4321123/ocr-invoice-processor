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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 pt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Welcome Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-600 rounded-full mb-6">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Willkommen
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Intelligente OCR-Rechnungsverarbeitung für Ihr Unternehmen. 
              Wählen Sie eine Option, um zu beginnen.
            </p>
          </div>

          {/* Action Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto mb-16">
            {/* Upload Card */}
            <div 
              onClick={navigateToUpload}
              className="group relative bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden border border-gray-100"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 opacity-0 group-hover:opacity-5 transition-opacity duration-300"></div>
              <div className="relative p-8">
                <div className="flex items-center mb-6">
                  <div className="bg-blue-100 group-hover:bg-blue-200 rounded-xl p-4 transition-colors duration-300">
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h2 className="text-2xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
                      Datei hochladen
                    </h2>
                    <p className="text-blue-600 font-medium">Einzelne Verarbeitung</p>
                  </div>
                </div>
                <p className="text-gray-600 leading-relaxed mb-4">
                  PDF-Rechnungen einzeln hochladen und sofort verarbeiten lassen. 
                  Ideal für gelegentliche Uploads und direkte Bearbeitung.
                </p>
                <div className="flex items-center text-blue-600 font-medium group-hover:text-blue-700">
                  <span>Jetzt hochladen</span>
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Folder Watcher Card */}
            <div 
              onClick={navigateToFolderWatcher}
              className="group relative bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden border border-gray-100"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-green-600 opacity-0 group-hover:opacity-5 transition-opacity duration-300"></div>
              <div className="relative p-8">
                <div className="flex items-center mb-6">
                  <div className="bg-green-100 group-hover:bg-green-200 rounded-xl p-4 transition-colors duration-300">
                    <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0a2 2 0 002-2h6l2 2h6a2 2 0 012 2v1" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <h2 className="text-2xl font-bold text-gray-900 group-hover:text-green-600 transition-colors duration-300">
                      Ordner überwachen
                    </h2>
                    <p className="text-green-600 font-medium">Automatisierte Verarbeitung</p>
                  </div>
                </div>
                <p className="text-gray-600 leading-relaxed mb-4">
                  Automatische Überwachung und Verarbeitung von Dateien aus 
                  überwachten Ordnern. Ideal für kontinuierliche Workflows.
                </p>
                <div className="flex items-center text-green-600 font-medium group-hover:text-green-700">
                  <span>Dashboard öffnen</span>
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Features Overview */}
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                � Leistungsstarke Funktionen
              </h3>
              <p className="text-gray-600">
                Automatisierte Rechnungsverarbeitung mit intelligenter OCR-Technologie
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4">
                <div className="bg-purple-100 rounded-lg p-3 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">OCR-Extraktion</h4>
                <p className="text-sm text-gray-600">Automatische Datenextraktion aus PDF-Rechnungen</p>
              </div>
              
              <div className="text-center p-4">
                <div className="bg-yellow-100 rounded-lg p-3 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Bearbeitung</h4>
                <p className="text-sm text-gray-600">Manuelle Überprüfung und Korrektur der Daten</p>
              </div>
              
              <div className="text-center p-4">
                <div className="bg-red-100 rounded-lg p-3 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Benachrichtigung</h4>
                <p className="text-sm text-gray-600">Automatische E-Mail-Updates über den Status</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
