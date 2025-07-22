/**
 * Centralized API Configuration
 * Handles all backend connection logic for different environments
 */

/**
 * Determines the appropriate API URL based on environment
 * Priority:
 * 1. Server-side: INTERNAL_API_URL (Docker internal network)
 * 2. Client-side: NEXT_PUBLIC_API_URL (public-facing URL)
 * 3. Fallback: localhost for development
 */
export function getApiUrl(): string {
  // Server-side (Next.js API routes, SSR)
  if (typeof window === 'undefined') {
    // In Docker containers, use internal service name
    if (process.env.INTERNAL_API_URL) {
      return process.env.INTERNAL_API_URL;
    }
    // Fallback for server-side
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  // Client-side (browser)
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

/**
 * Get API URL for specific environments
 */
export const API_CONFIG = {
  // Main API base URL
  BASE_URL: getApiUrl(),
  
  // Environment detection
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development',
  isServer: typeof window === 'undefined',
  isClient: typeof window !== 'undefined',
  
  // Timeout configurations
  TIMEOUT: {
    DEFAULT: 30000, // 30 seconds
    UPLOAD: 300000, // 5 minutes for file uploads
    HEALTH: 10000,  // 10 seconds for health checks
  },
  
  // API endpoints
  ENDPOINTS: {
    // Health & System
    HEALTH: '/api/health',
    SYSTEM_HEALTH: '/api/system-health',
    
    // Authentication
    AUTH: {
      LOGIN: '/api/auth/login',
      LOGOUT: '/api/auth/logout',
      VERIFY: '/api/auth/verify',
    },
    
    // Invoices
    INVOICES: {
      BASE: '/api/invoices',
      BY_ID: (id: string) => `/api/invoices/${id}`,
      EDITOR: (id: string) => `/api/invoices/${id}/editor`,
      COMPLETE: (id: string) => `/api/invoices/${id}/complete`,
      DELETE: (id: string) => `/api/invoices/${id}`,
    },
    
    // Upload
    UPLOAD: '/api/upload',
    
    // Dropdowns
    DROPDOWNS: {
      BASE: '/api/dropdowns',
      ALL: '/api/dropdowns/all',
      BY_FIELD: (fieldName: string) => `/api/dropdowns/${fieldName}`,
      ADD_OPTION: '/api/dropdowns/add-option',
      DELETE_OPTION: (fieldName: string, optionValue: string) => 
        `/api/dropdowns/${fieldName}/${optionValue}`,
    },
    
    // Folder Watcher
    FOLDER_WATCHER: {
      STATUS: '/api/folder-watcher/status',
      START: '/api/folder-watcher/start',
      STOP: '/api/folder-watcher/stop',
      HEALTH: '/api/folder-watcher/health',
    },
    
    // Skonto Dashboard
    SKONTO: {
      SUMMARY: '/api/skonto/dashboard/summary',
      OPPORTUNITIES: '/api/skonto/dashboard/opportunities',
    },
    
    // Approval
    APPROVAL: {
      STATUS: (id: string) => `/api/approval/status/${id}`,
      ACTION: (token: string) => `/api/approval/${token}`,
    },
    
    // Reports
    REPORTS: {
      BASE: '/api/reports',
    },
  },
} as const;

/**
 * Build full URL for an endpoint
 */
export function buildApiUrl(endpoint: string): string {
  const baseUrl = API_CONFIG.BASE_URL;
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${cleanEndpoint}`;
}

/**
 * Common fetch options with timeout
 */
export function getRequestConfig(options: RequestInit = {}, timeout?: number): RequestInit {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout || API_CONFIG.TIMEOUT.DEFAULT);
  
  return {
    ...options,
    signal: controller.signal,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };
}

/**
 * Environment-specific configurations
 */
export const ENV_CONFIG = {
  // Docker environment detection
  isDocker: process.env.INTERNAL_API_URL?.includes('backend:'),
  
  // Development helpers
  dev: {
    logRequests: process.env.NODE_ENV === 'development',
    mockData: process.env.USE_MOCK_DATA === 'true',
  },
  
  // Production settings
  prod: {
    enableErrorReporting: process.env.NODE_ENV === 'production',
    enableAnalytics: process.env.NODE_ENV === 'production',
  },
} as const;

/**
 * Export singleton for direct use
 */
export default API_CONFIG;

/**
 * Legacy exports for backward compatibility
 */
export const getServerApiUrl = getApiUrl;
export const API_ENDPOINTS = API_CONFIG.ENDPOINTS;
