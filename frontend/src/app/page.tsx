'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  FileText, 
  BarChart3, 
  Activity,
  Upload,
  FolderOpen,
  ArrowRight,
  Sparkles
} from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Check if user has auth data in localStorage immediately
  useEffect(() => {
    // Quick check for auth data
    const hasAuthToken = typeof window !== 'undefined' && localStorage.getItem('authToken');
    
    if (!hasAuthToken) {
      console.log('🔒 No auth token found, redirecting to login immediately');
      router.replace('/login');
      return;
    }

    // Secondary check after auth context loads
    if (!isLoading && !isAuthenticated) {
      console.log('🔒 Not authenticated after loading, redirecting to login');
      router.replace('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading only briefly while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen gradient-bg-light flex items-center justify-center">
        <div className="text-center glass-card rounded-2xl p-8 animate-fade-in">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <h2 className="text-lg font-semibold gradient-text mb-2">Checking authentication...</h2>
        </div>
      </div>
    );
  }

  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  const navigationCards = [
    {
      title: 'Dashboard',
      description: 'Manage and process your invoices',
      icon: LayoutDashboard,
      href: '/dashboard',
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100'
    },
    {
      title: 'Upload',
      description: 'Upload invoices with drag & drop',
      icon: Upload,
      href: '/upload',
      gradient: 'from-emerald-500 to-emerald-600',
      bgGradient: 'from-emerald-50 to-emerald-100'
    },
    {
      title: 'Folder Watcher',
      description: 'Configure automatic file monitoring',
      icon: FolderOpen,
      href: '/dashboard/folder-watcher',
      gradient: 'from-orange-500 to-orange-600',
      bgGradient: 'from-orange-50 to-orange-100'
    },
    {
      title: 'Prüfbericht',
      description: 'View Skonto reports and analytics',
      icon: BarChart3,
      href: '/prufbericht',
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100'
    },
    {
      title: 'Health',
      description: 'Monitor system health and status',
      icon: Activity,
      href: '/health',
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-50 to-green-100'
    },
    {
      title: 'Invoices',
      description: 'Quick access to invoice management',
      icon: FileText,
      href: '/dashboard',
      gradient: 'from-indigo-500 to-indigo-600',
      bgGradient: 'from-indigo-50 to-indigo-100'
    }
  ];

  return (
    <div className="min-h-screen gradient-bg-light relative overflow-hidden">
      {/* Floating Background Elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
      <div className="absolute top-40 right-20 w-40 h-40 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
      <div className="absolute bottom-20 left-1/3 w-36 h-36 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '4s' }}></div>
      
      <div className="relative z-10 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header Section */}
          <div className="text-center mb-16">
            <div className="glass-card rounded-2xl p-8 mb-8 border-0 shadow-xl animate-fade-in">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center shadow-lg animate-glow">
                  <FileText className="h-8 w-8 text-white" />
                </div>
              </div>
              <h1 className="text-4xl font-bold mb-4">
                <span className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Welcome to OCR Invoice Processor
                </span>
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Streamline your invoice processing with AI-powered OCR technology and automated workflows
              </p>
              <div className="flex items-center justify-center mt-4">
                <span className="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium glass-card text-purple-700 border border-purple-200">
                  <Sparkles className="h-4 w-4 mr-1" />
                  Modern Glass UI Design
                </span>
              </div>
            </div>
          </div>

          {/* Navigation Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {navigationCards.map((card, index) => (
              <Link
                key={card.title}
                href={card.href}
                className="group glass-card rounded-2xl p-6 border-0 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="text-center">
                  <div className={`w-16 h-16 bg-gradient-to-r ${card.gradient} rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                    <card.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold gradient-text mb-2 group-hover:scale-105 transition-transform duration-300">
                    {card.title}
                  </h3>
                  <p className="text-gray-600 mb-4 text-sm">
                    {card.description}
                  </p>
                  <div className="flex items-center justify-center text-purple-600 group-hover:text-purple-700 transition-colors">
                    <span className="text-sm font-medium">Get Started</span>
                    <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform duration-300" />
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Quick Stats Section */}
          <div className="mt-16">
            <div className="glass-card rounded-2xl p-8 border-0 shadow-xl animate-fade-in">
              <h2 className="text-2xl font-bold gradient-text text-center mb-8">
                System Overview
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold gradient-text mb-2">AI-Powered</div>
                  <div className="text-gray-600">OCR Technology</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold gradient-text mb-2">Automated</div>
                  <div className="text-gray-600">Workflow Processing</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold gradient-text mb-2">Real-time</div>
                  <div className="text-gray-600">Status Tracking</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
