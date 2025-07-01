'use client'

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

const Navigation: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Don't show navigation on login page or if not authenticated
  if (!isAuthenticated || pathname === '/login') {
    return null;
  }

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="text-xl font-bold text-blue-600">
              📄 Invoice Manager
            </Link>
            
            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-6">
              <Link 
                href="/" 
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  pathname === '/' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                🏠 Home
              </Link>
              
              <Link 
                href="/dashboard" 
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  pathname === '/dashboard' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                � Dashboard
              </Link>
              
              <Link 
                href="/prufbericht" 
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  pathname === '/prufbericht' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                }`}
              >
                � Prüfbericht
              </Link>
              
              <Link 
                href="/health" 
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  pathname === '/health' 
                    ? 'bg-green-100 text-green-700' 
                    : 'text-gray-700 hover:text-green-600 hover:bg-gray-100'
                }`}
              >
                � Health
              </Link>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-700">
                Hallo, {user?.full_name || user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white text-sm px-4 py-2 rounded-md transition-colors"
              >
                🚪 Abmelden
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
