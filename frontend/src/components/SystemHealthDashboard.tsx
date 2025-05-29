'use client';

import React, { useState, useEffect } from 'react';

interface HealthComponent {
  status: 'healthy' | 'degraded' | 'error' | 'mock';
  response_time_ms?: number;
  error?: string;
  total_invoices?: number;
  connection?: string;
  config?: Record<string, string>;
  available_endpoints?: string[];
  write_access?: boolean;
  bucket?: string;
  // OCR-specific properties
  service?: string;
  timestamp?: number;
  checks?: Record<string, {
    status: string;
    details: string;
  }>;
}

interface SystemHealth {
  timestamp: string;
  overall_status: 'healthy' | 'degraded' | 'error';
  components: {
    database?: HealthComponent;
    storage?: HealthComponent;
    environment?: HealthComponent;
    api_endpoints?: HealthComponent;
    filesystem?: HealthComponent;
    ocr?: HealthComponent;
  };
}

const statusColors = {
  healthy: 'bg-green-100 text-green-800 border-green-200',
  degraded: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  error: 'bg-red-100 text-red-800 border-red-200',
  mock: 'bg-blue-100 text-blue-800 border-blue-200'
};

const statusIcons = {
  healthy: '✅',
  degraded: '⚠️',
  error: '❌',
  mock: '🔧'
};

export default function SystemHealthDashboard() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/system-health`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setHealth(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch system health');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const renderComponent = (name: string, component: HealthComponent) => {
    const isOcrComponent = name === 'ocr';
    const borderColor = isOcrComponent ? 'border-l-4 border-blue-400' : 'border-l-4 border-gray-200';
    
    return (
      <div key={name} className={`bg-white rounded-lg shadow-md p-6 ${borderColor}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 capitalize flex items-center gap-2">
            {isOcrComponent && <span className="text-xl">🔍</span>}
            {name.replace('_', ' ')}
            {isOcrComponent && <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">OCR</span>}
          </h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${statusColors[component.status]}`}>
            {statusIcons[component.status]} {component.status.toUpperCase()}
          </span>
        </div>
      
      <div className="space-y-2">
        {component.response_time_ms !== undefined && (
          <div className="flex justify-between">
            <span className="text-gray-600">Response Time:</span>
            <span className={`font-mono ${component.response_time_ms > 1000 ? 'text-red-600' : 'text-green-600'}`}>
              {component.response_time_ms}ms
            </span>
          </div>
        )}
        
        {component.total_invoices !== undefined && (
          <div className="flex justify-between">
            <span className="text-gray-600">Total Invoices:</span>
            <span className="font-mono">{component.total_invoices}</span>
          </div>
        )}
        
        {component.connection && (
          <div className="flex justify-between">
            <span className="text-gray-600">Connection:</span>
            <span className="font-mono">{component.connection}</span>
          </div>
        )}
        
        {component.bucket && (
          <div className="flex justify-between">
            <span className="text-gray-600">Bucket:</span>
            <span className="font-mono">{component.bucket}</span>
          </div>
        )}
        
        {component.write_access !== undefined && (
          <div className="flex justify-between">
            <span className="text-gray-600">Write Access:</span>
            <span className={`font-mono ${component.write_access ? 'text-green-600' : 'text-red-600'}`}>
              {component.write_access ? 'Yes' : 'No'}
            </span>
          </div>
        )}
        
        {component.config && (
          <div className="mt-3">
            <span className="text-gray-600 text-sm">Configuration:</span>
            <div className="mt-1 space-y-1">
              {Object.entries(component.config).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <span className="text-gray-500">{key}:</span>
                  <span className={`font-mono ${value === 'configured' ? 'text-green-600' : 'text-red-600'}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {component.available_endpoints && (
          <div className="mt-3">
            <span className="text-gray-600 text-sm">Available Endpoints:</span>
            <div className="mt-1 flex flex-wrap gap-1">
              {component.available_endpoints.map((endpoint) => (
                <span key={endpoint} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-mono">
                  {endpoint}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {component.service && (
          <div className="flex justify-between">
            <span className="text-gray-600">Service:</span>
            <span className="font-mono text-blue-600">{component.service}</span>
          </div>
        )}
        
        {component.checks && (
          <div className="mt-3">
            <span className="text-gray-600 text-sm">Health Checks:</span>
            <div className="mt-2 space-y-2">
              {Object.entries(component.checks).map(([checkName, checkData]) => (
                <div key={checkName} className="bg-gray-50 rounded p-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {checkName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded ${
                      checkData.status === 'healthy' ? 'bg-green-100 text-green-800' :
                      checkData.status === 'unhealthy' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {checkData.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">{checkData.details}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {component.error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
            <span className="text-red-600 text-sm font-medium">Error:</span>
            <p className="text-red-700 text-sm mt-1 font-mono">{component.error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

  if (loading && !health) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading system health...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">System Health Dashboard</h1>
              <p className="text-gray-600 mt-2">Monitor the health and status of all system components</p>
            </div>
            <button
              onClick={fetchHealth}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md flex items-center gap-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                '🔄'
              )}
              Refresh
            </button>
          </div>
          
          {lastUpdated && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {lastUpdated.toLocaleString()}
            </p>
          )}
        </div>

        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-400">❌</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Unable to fetch system health</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                  <p className="mt-2">This usually means the backend is not running or not accessible.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {health && (
          <>
            <div className="mb-8 bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Overall System Status</h2>
                <span className={`px-4 py-2 rounded-full text-lg font-medium border ${statusColors[health.overall_status]}`}>
                  {statusIcons[health.overall_status]} {health.overall_status.toUpperCase()}
                </span>
              </div>
              <p className="text-gray-600 text-sm mt-2">
                Checked at: {new Date(health.timestamp).toLocaleString()}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(health.components).map(([name, component]) =>
                renderComponent(name, component)
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
