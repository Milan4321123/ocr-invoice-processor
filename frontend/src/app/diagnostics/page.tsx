'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

export default function DiagnosticsPage() {
  const [results, setResults] = useState<{
    envVars: any;
    supabaseTest: { status: string; message: string; data: any };
    backendTest: { status: string; message: string; data: any };
    corsTest: { status: string; message: string; data: any };
    invoiceTest: { status: string; message: string; data: any };
  }>({
    envVars: {},
    supabaseTest: { status: 'loading', message: '', data: null },
    backendTest: { status: 'loading', message: '', data: null },
    corsTest: { status: 'loading', message: '', data: null },
    invoiceTest: { status: 'loading', message: '', data: null }
  });

  useEffect(() => {
    // Check environment variables
    const envVars = {
      NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || 'NOT_SET',
      NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'SET (****)' : 'NOT_SET',
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'NOT_SET',
      NODE_ENV: process.env.NODE_ENV || 'NOT_SET',
      HOST: typeof window !== 'undefined' ? window.location.host : 'SERVER_SIDE',
      PROTOCOL: typeof window !== 'undefined' ? window.location.protocol : 'SERVER_SIDE'
    };
    
    setResults(prev => ({ ...prev, envVars }));

    // Test Supabase connection
    testSupabaseConnection();
    
    // Test backend connection
    testBackendConnection();
    
    // Test CORS
    testCorsConnection();
  }, []);

  const testSupabaseConnection = async () => {
    try {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
      
      if (!supabaseUrl || !supabaseKey) {
        setResults(prev => ({
          ...prev,
          supabaseTest: {
            status: 'error',
            message: 'Supabase environment variables not set',
            data: null
          }
        }));
        return;
      }

      const supabase = createClient(supabaseUrl, supabaseKey);
      
      // Test a simple query
      const { data, error } = await supabase
        .from('invoices_clean')
        .select('id, file_name')
        .limit(1);

      if (error) {
        setResults(prev => ({
          ...prev,
          supabaseTest: {
            status: 'error',
            message: `Supabase Error: ${error.message}`,
            data: error
          }
        }));
      } else {
        setResults(prev => ({
          ...prev,
          supabaseTest: {
            status: 'success',
            message: 'Supabase connection successful',
            data: data
          }
        }));
      }
    } catch (error) {        setResults(prev => ({
          ...prev,
          supabaseTest: {
            status: 'error',
            message: `Connection Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            data: error
          }
        }));
    }
  };

  const testBackendConnection = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      
      if (!apiUrl) {
        setResults(prev => ({
          ...prev,
          backendTest: {
            status: 'error',
            message: 'API URL not set',
            data: null
          }
        }));
        return;
      }

      const response = await fetch(`${apiUrl}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setResults(prev => ({
          ...prev,
          backendTest: {
            status: 'success',
            message: 'Backend connection successful',
            data: data
          }
        }));
      } else {
        setResults(prev => ({
          ...prev,
          backendTest: {
            status: 'error',
            message: `Backend Error: ${response.status} ${response.statusText}`,
            data: null
          }
        }));
      }
    } catch (error) {        setResults(prev => ({
          ...prev,
          backendTest: {
            status: 'error',
            message: `Connection Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            data: error
          }
        }));
    }
  };

  const testCorsConnection = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      
      const response = await fetch(`${apiUrl}/api/invoices`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Origin': window.location.origin
        }
      });

      if (response.ok) {
        const data = await response.json();
        setResults(prev => ({
          ...prev,
          corsTest: {
            status: 'success',
            message: 'CORS test successful',
            data: { invoiceCount: data.total || 0 }
          }
        }));
      } else {
        setResults(prev => ({
          ...prev,
          corsTest: {
            status: 'error',
            message: `CORS Error: ${response.status} ${response.statusText}`,
            data: null
          }
        }));
      }
    } catch (error) {        setResults(prev => ({
          ...prev,
          corsTest: {
            status: 'error',
            message: `CORS Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            data: error
          }
        }));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'loading': return '⏳';
      default: return '❓';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          🔍 Frontend Diagnostics
        </h1>

        {/* Environment Variables */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Environment Variables</h2>
          <div className="space-y-2">
            {Object.entries(results.envVars).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="font-mono text-sm text-gray-600">{key}:</span>
                <span className={`font-mono text-sm ${value === 'NOT_SET' ? 'text-red-600' : 'text-green-600'}`}>
                  {String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Connection Tests */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Supabase Test */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">
              {getStatusIcon(results.supabaseTest.status)} Supabase Connection
            </h3>
            <p className={`text-sm mb-2 ${
              results.supabaseTest.status === 'success' ? 'text-green-600' : 
              results.supabaseTest.status === 'error' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {results.supabaseTest.message}
            </p>
            {results.supabaseTest.data && (
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
                {JSON.stringify(results.supabaseTest.data, null, 2)}
              </pre>
            )}
          </div>

          {/* Backend Test */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">
              {getStatusIcon(results.backendTest.status)} Backend Connection
            </h3>
            <p className={`text-sm mb-2 ${
              results.backendTest.status === 'success' ? 'text-green-600' : 
              results.backendTest.status === 'error' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {results.backendTest.message}
            </p>
            {results.backendTest.data && (
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
                {JSON.stringify(results.backendTest.data, null, 2)}
              </pre>
            )}
          </div>

          {/* CORS Test */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">
              {getStatusIcon(results.corsTest.status)} CORS Test
            </h3>
            <p className={`text-sm mb-2 ${
              results.corsTest.status === 'success' ? 'text-green-600' : 
              results.corsTest.status === 'error' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {results.corsTest.message}
            </p>
            {results.corsTest.data && (
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
                {JSON.stringify(results.corsTest.data, null, 2)}
              </pre>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-lg font-semibold mb-4">Actions</h3>
          <div className="flex gap-4">
            <button
              onClick={() => {
                testSupabaseConnection();
                testBackendConnection();
                testCorsConnection();
              }}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            >
              🔄 Retry All Tests
            </button>
            <button
              onClick={() => window.location.reload()}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              🔄 Reload Page
            </button>
          </div>
        </div>

        {/* Debug Info */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-lg font-semibold mb-4">Debug Information</h3>
          <div className="text-sm space-y-2">
            <p><strong>Current URL:</strong> {window.location.href}</p>
            <p><strong>User Agent:</strong> {navigator.userAgent}</p>
            <p><strong>Timestamp:</strong> {new Date().toISOString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
