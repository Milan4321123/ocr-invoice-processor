'use client'

import React from 'react'
import { Toaster } from 'react-hot-toast'
import { toastConfig } from '@/lib/toast-config'
import { FolderWatcherDashboard } from '@/components/FolderWatcherDashboard'

export default function FolderWatcherPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <FolderWatcherDashboard />
      <Toaster {...toastConfig} />
    </div>
  )
}
