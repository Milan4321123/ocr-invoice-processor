'use client'

import React from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Navigation from './Navigation'

interface ClientWrapperProps {
  children: React.ReactNode
}

export default function ClientWrapper({ children }: ClientWrapperProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <>
      {isAuthenticated && <Navigation />}
      <main className={isAuthenticated ? 'pt-16' : ''}>
        {children}
      </main>
    </>
  )
}