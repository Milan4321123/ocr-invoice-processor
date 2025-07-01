'use client'

import React from 'react'
import { AuthProvider } from '../contexts/AuthContext'
import Navigation from '../components/Navigation'

interface ClientWrapperProps {
  children: React.ReactNode
}

export default function ClientWrapper({ children }: ClientWrapperProps) {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main>
          {children}
        </main>
      </div>
    </AuthProvider>
  )
}
