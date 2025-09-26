"use client";

import React, { useState, useEffect } from 'react';
import { getApiUrl } from '@/config/api';
import { testSupabaseConnection } from '@/lib/supabase';

// Force dynamic rendering to prevent static generation errors
export const dynamic = 'force-dynamic';

export default function ConnectivityTestPage() {
  const [backendStatus, setBackendStatus] = useState<string>('Testing...');
  const [supabaseStatus, setSupabaseStatus] = useState<string>('Testing...');
  const [loginTest, setLoginTest] = useState<string>('');

  useEffect(() => {
    testConnections();
  }, []);

  const testConnections = async () => {
    // Test backend health
    try {
      const backendUrl = getApiUrl();
      const response = await fetch(`${backendUrl}/api/health`);
      const data = await response.json();
      
      if (response.ok) {
        setBackendStatus(`✅ Backend Connected: ${JSON.stringify(data)}`);
      } else {
        setBackendStatus(`❌ Backend Error: ${response.status} - ${JSON.stringify(data)}`);
      }
    } catch (error) {
      setBackendStatus(`❌ Backend Connection Failed: ${error}`);
    }

    // Test Supabase connection
    try {
      const result = await testSupabaseConnection();
      if (result.success) {
        setSupabaseStatus(`✅ Supabase Connected: ${JSON.stringify(result.data)}`);
      } else {
        setSupabaseStatus(`❌ Supabase Error: ${result.error}`);
      }
    } catch (error) {
      setSupabaseStatus(`❌ Supabase Connection Failed: ${error}`);
    }
  };

  const testLogin = async () => {
    setLoginTest('Testing login...');
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: 'admin',
          password: 'admin123'
        })
      });

      const data = await response.text(); // Get raw text first
      setLoginTest(`Login Test Result (${response.status}): ${data}`);

      // Try to parse as JSON if possible
      try {
        const jsonData = JSON.parse(data);
        setLoginTest(`Login Test Result (${response.status}): ${JSON.stringify(jsonData, null, 2)}`);
      } catch (e) {
        // If not JSON, keep the raw text
        setLoginTest(`Login Test Result (${response.status}) - NOT JSON: ${data.substring(0, 500)}...`);
      }
    } catch (error) {
      setLoginTest(`❌ Login Test Failed: ${error}`);
    }
  };

  const testDirectBackend = async () => {
    setLoginTest('Testing direct backend login...');
    try {
      const backendUrl = getApiUrl();
      const formData = new FormData();
      formData.append('username', 'admin');
      formData.append('password', 'admin123');

      const response = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.text(); // Get raw text first
      setLoginTest(`Direct Backend Login Test (${response.status}): ${data}`);

      // Try to parse as JSON if possible
      try {
        const jsonData = JSON.parse(data);
        setLoginTest(`Direct Backend Login Test (${response.status}): ${JSON.stringify(jsonData, null, 2)}`);
      } catch (e) {
        // If not JSON, keep the raw text
        setLoginTest(`Direct Backend Login Test (${response.status}) - NOT JSON: ${data.substring(0, 500)}...`);
      }
    } catch (error) {
      setLoginTest(`❌ Direct Backend Login Test Failed: ${error}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Connectivity Test</h1>
        
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Backend Health Test</h2>
            <p className="text-sm text-gray-600 mb-2">Testing: {process.env.NEXT_PUBLIC_API_URL}/api/health</p>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">{backendStatus}</pre>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Supabase Connection Test</h2>
            <p className="text-sm text-gray-600 mb-2">Testing: {process.env.NEXT_PUBLIC_SUPABASE_URL}</p>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">{supabaseStatus}</pre>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Login Tests</h2>
            <div className="space-x-4 mb-4">
              <button 
                onClick={testLogin}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Test Frontend Login Proxy
              </button>
              <button 
                onClick={testDirectBackend}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              >
                Test Direct Backend Login
              </button>
            </div>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto whitespace-pre-wrap">{loginTest}</pre>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Environment Variables</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
{`NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL}
NEXT_PUBLIC_SUPABASE_URL: ${process.env.NEXT_PUBLIC_SUPABASE_URL}
NEXT_PUBLIC_SUPABASE_ANON_KEY: ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'Set' : 'Not Set'}`}
            </pre>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <button 
              onClick={testConnections}
              className="bg-purple-500 text-white px-6 py-2 rounded hover:bg-purple-600"
            >
              Refresh All Tests
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
