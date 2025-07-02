'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { 
  FolderIcon, 
  ClockIcon, 
  DocumentCheckIcon, 
  PlayIcon, 
  StopIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

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

interface FileNotification {
  id: string;
  type: 'file_detected' | 'processing_started' | 'upload_success' | 'upload_failed' | 'validation_failed';
  filename: string;
  file_path: string;
  timestamp: string;
  message: string;
  error?: string;
  invoice_id?: string;
  file_size?: number;
  watch_config_id?: string;
}

export default function FolderWatcherWidget() {
  const [status, setStatus] = useState<WatcherStatus | null>(null);
  const [notifications, setNotifications] = useState<FileNotification[]>([]);
  const [showNotifications, setShowNotifications] = useState(true); // Changed from false to true
  const [loading, setLoading] = useState(true);
  const [lastNotificationCount, setLastNotificationCount] = useState(0);

  useEffect(() => {
    fetchStatus();
    fetchNotifications();
    // Poll status and notifications every 5 seconds for faster updates
    const interval = setInterval(() => {
      fetchStatus();
      fetchNotifications();
    }, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Show toast notifications for new events
  useEffect(() => {
    console.log('🔔 Notification effect triggered:', {
      notificationsLength: notifications.length,
      lastNotificationCount,
      hasNewNotifications: notifications.length > lastNotificationCount && lastNotificationCount > 0
    });
    
    if (notifications.length > lastNotificationCount && lastNotificationCount > 0) {
      const newNotifications = notifications.slice(0, notifications.length - lastNotificationCount);
      console.log('🆕 New notifications detected:', newNotifications);
      
      newNotifications.forEach(notification => {
        console.log('🔔 Showing toast for:', notification.type, notification.filename);
        switch (notification.type) {
          case 'upload_success':
            toast.success(`Datei erfolgreich hochgeladen: ${notification.filename}`);
            break;
          case 'validation_failed':
            toast.error(`Validierungsfehler: ${notification.error || 'Dateiname oder Format ungültig'}`);
            break;
          case 'upload_failed':
            toast.error(`Upload fehlgeschlagen: ${notification.error || 'Unbekannter Fehler'}`);
            break;
        }
      });
    }
    setLastNotificationCount(notifications.length);
  }, [notifications, lastNotificationCount]);

  const fetchStatus = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/folder-watcher/status`);
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

  const fetchNotifications = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      console.log('🔍 Fetching notifications from:', `${apiUrl}/api/folder-watcher/notifications?limit=5`);
      const response = await fetch(`${apiUrl}/api/folder-watcher/notifications?limit=5`);
      if (response.ok) {
        const data = await response.json();
        console.log('📨 Received notifications:', data);
        setNotifications(data.notifications || []);
      } else {
        console.error('❌ Failed to fetch notifications:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('❌ Error fetching notifications:', error);
    }
  };

  const clearNotifications = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/folder-watcher/notifications`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setNotifications([]);
      }
    } catch (error) {
      console.error('Error clearing notifications:', error);
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

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('de-DE', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        day: '2-digit',
        month: '2-digit'
      });
    } catch {
      return timestamp;
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'upload_success':
        return <CheckCircleIcon className="w-4 h-4 text-green-600" />;
      case 'upload_failed':
        return <XCircleIcon className="w-4 h-4 text-red-600" />;
      case 'validation_failed':
        return <ExclamationTriangleIcon className="w-4 h-4 text-orange-600" />;
      case 'processing_started':
        return <ClockIcon className="w-4 h-4 text-blue-600" />;
      case 'file_detected':
        return <DocumentCheckIcon className="w-4 h-4 text-yellow-600" />;
      default:
        return <ExclamationTriangleIcon className="w-4 h-4 text-gray-600" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'upload_success':
        return 'glass-card border-green-200';
      case 'upload_failed':
        return 'glass-card border-red-200';
      case 'validation_failed':
        return 'glass-card border-orange-200';
      case 'processing_started':
        return 'glass-card border-blue-200';
      case 'file_detected':
        return 'glass-card border-yellow-200';
      default:
        return 'glass-card border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="glass-card rounded-xl border-0 shadow-lg p-6 animate-fade-in">
        <div className="animate-pulse">
          <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-1/3 mb-4"></div>
          <div className="h-8 bg-gradient-to-r from-gray-200 to-gray-300 rounded mb-2"></div>
          <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-700 glass-card border-green-200';
      case 'error': return 'text-red-700 glass-card border-red-200';
      case 'starting': case 'stopping': return 'text-yellow-700 glass-card border-yellow-200';
      default: return 'text-gray-700 glass-card border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return 'Läuft';
      case 'stopped': return 'Gestoppt';
      case 'error': return 'Fehler';
      case 'starting': return 'Startet...';
      case 'stopping': return 'Stoppt...';
      default: return 'Unbekannt';
    }
  };

  return (
    <div className="glass-card rounded-xl border-0 shadow-xl p-6 hover:shadow-2xl transition-all transform hover:scale-[1.02] animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold gradient-text flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
            <FolderIcon className="w-5 h-5 text-white" />
          </div>
          Ordnerüberwachung
        </h3>
        <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(status?.status || 'stopped')}`}>
          <div className="flex items-center gap-1">
            {status?.status === 'running' && (
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            )}
            {getStatusText(status?.status || 'stopped')}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 glass-card rounded-xl border-0 shadow-lg">
          <div className="text-2xl font-bold gradient-text">
            {status?.folders_watched || 0}
          </div>
          <div className="text-xs text-gray-700 font-medium">Aktive Ordner</div>
        </div>
        
        <div className="text-center p-3 glass-card rounded-xl border-0 shadow-lg">
          <div className="text-2xl font-bold gradient-text">
            {status?.statistics.successful_uploads || 0}
          </div>
          <div className="text-xs text-gray-700 font-medium">Erfolgreiche Uploads</div>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-700">Letzte Aktivität:</span>
          <span className="font-medium gradient-text">
            {status?.statistics.last_activity ? 
              new Date(status.statistics.last_activity).toLocaleTimeString('de-DE', {
                hour: '2-digit',
                minute: '2-digit'
              }) : 
              'Keine Aktivität'
            }
          </span>
        </div>
        
        {status?.status === 'running' && (
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-700">Laufzeit:</span>
            <span className="font-medium gradient-text">
              {formatUptime(status.uptime_seconds)}
            </span>
          </div>
        )}
        
        {(status?.statistics.failed_uploads || 0) > 0 && (
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-700">Fehlgeschlagene Uploads:</span>
            <span className="font-medium text-red-600">
              {status?.statistics.failed_uploads || 0}
            </span>
          </div>
        )}
      </div>

      {/* Simple notification for latest activity */}
      {status?.statistics.last_activity && (
        <div className="mb-4 p-3 glass-card rounded-xl border border-white/20 shadow-lg">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-gray-700">Letzte Datei verarbeitet um</span>
            <span className="font-medium gradient-text">
              {new Date(status.statistics.last_activity).toLocaleTimeString('de-DE')}
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-1">
            💡 Für detaillierte Benachrichtigungen und Konfiguration{' '}
            <a 
              href="/dashboard/folder-watcher" 
              className="text-blue-600 hover:text-purple-600 underline font-medium"
            >
              hier klicken
            </a>
          </p>
        </div>
      )}

      {/* Notifications Section */}
      {notifications.length > 0 && (
        <div className="mb-4 border-t border-white/20 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium gradient-text flex items-center gap-2">
              📋 Letzte Aktivitäten
              <span className="glass-card text-blue-800 text-xs px-2 py-1 rounded-full border border-blue-200">
                {notifications.length}
              </span>
            </h4>
            <div className="flex gap-1">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-1 glass-card hover:bg-white/20 rounded text-gray-600 hover:text-gray-800 transition-all"
                title={showNotifications ? 'Verstecken' : 'Anzeigen'}
              >
                <EyeIcon className="w-4 h-4" />
              </button>
              <button
                onClick={clearNotifications}
                className="p-1 glass-card hover:bg-white/20 rounded text-gray-600 hover:text-red-600 transition-all"
                title="Benachrichtigungen löschen"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {showNotifications && (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-2 rounded-xl border text-sm shadow-lg ${getNotificationColor(notification.type)}`}
                >
                  <div className="flex items-start gap-2">
                    {getNotificationIcon(notification.type)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-gray-900 truncate text-xs">
                          {notification.filename}
                        </p>
                        <span className="text-xs text-gray-600 ml-2">
                          {formatTimestamp(notification.timestamp)}
                        </span>
                      </div>
                      <p className="text-gray-700 mt-1 text-xs">{notification.message}</p>
                      {notification.error && (
                        <div className={`text-xs mt-1 p-1 rounded ${
                          notification.type === 'validation_failed' 
                            ? 'text-orange-700 glass-card border border-orange-200' 
                            : 'text-red-600 glass-card border border-red-200'
                        }`}>
                          {notification.type === 'validation_failed' ? '⚠️' : '❌'} {notification.error}
                          {notification.type === 'validation_failed' && (
                            <div className="mt-1 text-xs text-orange-600">
                              💡 Dateiname muss dem Muster folgen: JJJJMMTT_KENNUNG_LIEFERANT_TYP.pdf
                            </div>
                          )}
                        </div>
                      )}
                      <div className="flex items-center gap-2 mt-1 text-xs text-gray-600">
                        {notification.file_size && (
                          <span>{formatFileSize(notification.file_size)}</span>
                        )}
                        {notification.invoice_id && (
                          <span className="font-mono text-green-600">
                            ID: {notification.invoice_id.slice(0, 8)}...
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2">
        <button 
          onClick={() => window.location.href = '/dashboard/folder-watcher'}
          className="flex-1 glass-card hover:bg-white/20 text-blue-700 px-4 py-2 rounded-xl transition-all transform hover:scale-105 text-sm font-medium flex items-center justify-center gap-2 border border-blue-200 shadow-lg"
        >
          <FolderIcon className="w-4 h-4" />
          Konfigurieren
        </button>
        
        {status?.status === 'running' ? (
          <button 
            className="px-3 py-2 glass-card hover:bg-white/20 text-red-700 rounded-xl transition-all transform hover:scale-105 border border-red-200 shadow-lg"
            title="Überwachung stoppen"
          >
            <StopIcon className="w-4 h-4" />
          </button>
        ) : (
          <button 
            className="px-3 py-2 glass-card hover:bg-white/20 text-green-700 rounded-xl transition-all transform hover:scale-105 border border-green-200 shadow-lg"
            title="Überwachung starten"
          >
            <PlayIcon className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
