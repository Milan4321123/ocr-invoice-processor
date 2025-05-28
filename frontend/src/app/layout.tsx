import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Invoice OCR System',
  description: 'Process and manage invoices with OCR technology',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="bg-white shadow-sm border-b">
          <nav className="container mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center">
              <Link href="/" className="font-bold text-xl text-blue-600 hover:text-blue-700">
                Invoice OCR
              </Link>
            </div>
            <div className="space-x-4">
              <Link 
                href="/dashboard" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md font-medium"
              >
                Dashboard
              </Link>
              <Link 
                href="/upload" 
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md font-medium"
              >
                Upload
              </Link>
            </div>
          </nav>
        </header>
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </body>
    </html>
  )
}
