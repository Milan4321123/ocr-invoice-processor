'use client';

import { useState, useEffect } from 'react';
import { FolderIcon, ClockIcon, DocumentCheckIcon, PlayIcon, StopIcon } from '@heroicons/react/24/outline';

interface WatcherStatus {
  status: 'stopped' | 'running' | 'error' | 'starting' | 'stopping';
  folders_watched: number;
  statistics: {
    total_files_processed: number;
    successful_uploads: number;
    failed_uploads: number;
    last_activity: string | null;
  };
  uptime_seconds: number;
}

export default function FolderWatcherWidget() {
  const [status, setStatus] = useState<WatcherStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
    // Poll status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/folder-watcher/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Error fetching folder watcher status:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatUptime = (seconds: number): string => {
    if (seconds === 0) return '0s';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'starting': case 'stopping': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return 'Running';
      case 'stopped': return 'Stopped';
      case 'error': return 'Error';
      case 'starting': return 'Starting...';
      case 'stopping': return 'Stopping...';
      default: return 'Unknown';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <FolderIcon className="w-5 h-5 text-blue-600" />
          Folder Watcher
        </h3>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(status?.status || 'stopped')}`}>
          <div className="flex items-center gap-1">
            {status?.status === 'running' && (
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            )}
            {getStatusText(status?.status || 'stopped')}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {status?.folders_watched || 0}
          </div>
          <div className="text-xs text-blue-700 font-medium">Active Folders</div>
        </div>
        
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {status?.statistics.successful_uploads || 0}
          </div>
          <div className="text-xs text-green-700 font-medium">Successful Uploads</div>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">Last Activity:</span>
          <span className="font-medium text-gray-900">
            {status?.statistics.last_activity ? 
              new Date(status.statistics.last_activity).toLocaleTimeString('de-DE', {
                hour: '2-digit',
                minute: '2-digit'
              }) : 
              'No activity'
            }
          </span>
        </div>
        
        {status?.status === 'running' && (
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Uptime:</span>
            <span className="font-medium text-gray-900">
              {formatUptime(status.uptime_seconds)}
            </span>
          </div>
        )}
        
        {(status?.statistics.failed_uploads || 0) > 0 && (
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Failed Uploads:</span>
            <span className="font-medium text-red-600">
              {status?.statistics.failed_uploads || 0}
            </span>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <button 
          onClick={() => window.location.href = '/folder-watcher'}
          className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-2 rounded-lg transition-colors text-sm font-medium flex items-center justify-center gap-2"
        >
          <FolderIcon className="w-4 h-4" />
          Configure
        </button>
        
        {status?.status === 'running' ? (
          <button 
            className="px-3 py-2 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg transition-colors"
            title="Stop Watcher"
          >
            <StopIcon className="w-4 h-4" />
          </button>
        ) : (
          <button 
            className="px-3 py-2 bg-green-50 hover:bg-green-100 text-green-700 rounded-lg transition-colors"
            title="Start Watcher"
          >
            <PlayIcon className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
