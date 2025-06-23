import React from 'react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-5xl font-bold mb-6 text-gray-900">
          Invoice OCR Processing System
        </h1>
        <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
          Upload, process, and manage your PDF invoices with automated OCR technology. 
          Transform paper invoices into structured data effortlessly.
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center gap-6 mb-16">
          <Link 
            href="/upload" 
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 rounded-lg font-medium text-lg transition-colors flex items-center justify-center gap-3 shadow-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload Invoice
          </Link>
          <Link 
            href="/folder-watcher" 
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-6 rounded-lg font-medium text-lg transition-colors flex items-center justify-center gap-3 shadow-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0a2 2 0 002-2h6l2 2h6a2 2 0 012 2z" />
            </svg>
            Folder Watcher
          </Link>
        </div>

        <div className="flex justify-center mb-16">
          <Link 
            href="/dashboard" 
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            View Dashboard →
          </Link>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Manual Upload</h3>
            <p className="text-gray-600">Drag and drop PDF invoices for instant processing and review</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0a2 2 0 002-2h6l2 2h6a2 2 0 012 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Folder Watcher</h3>
            <p className="text-gray-600">Automatic monitoring and processing of invoices from network folders</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Approval Workflow</h3>
            <p className="text-gray-600">Review, edit, and approve invoices with skonto tracking in Prüfbericht</p>
          </div>
        </div>
      </div>
    </div>
  )
}
