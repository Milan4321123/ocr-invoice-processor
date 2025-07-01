import React from 'react'
import './globals.css'
import { Inter } from 'next/font/google'
import ClientWrapper from './ClientWrapper'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Invoice Management System',
  description: 'Upload and manage PDF invoices with searchable dropdowns and workflow automation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientWrapper>
          {children}
        </ClientWrapper>
      </body>
    </html>
  )
}
