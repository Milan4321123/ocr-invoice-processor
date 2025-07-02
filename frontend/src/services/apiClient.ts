/**
 * API Client with Authentication Support
 * Handles all API requests with automatic token management
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T = any> {
  success?: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export class ApiClient {
  private static instance: ApiClient;
  
  private constructor() {}

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('authToken');
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
      // Token expired or invalid - redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        window.location.href = '/login';
      }
      throw new Error('Authentication required');
    }

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.error || `HTTP ${response.status}`);
    }

    return data;
  }

  public async request<T = any>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getAuthToken();
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    };

    const response = await fetch(`${API_BASE}${endpoint}`, config);
    return this.handleResponse<T>(response);
  }

  public async get<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  public async post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  public async put<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  public async delete<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // Form data upload (e.g., file uploads)
  public async postFormData<T = any>(endpoint: string, formData: FormData): Promise<T> {
    const token = this.getAuthToken();
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
        // Don't set Content-Type for FormData - browser will set it with boundary
      },
      body: formData,
    });

    return this.handleResponse<T>(response);
  }

  // Special method for login (no auth required)
  public async login(username: string, password: string): Promise<any> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse(response);
  }

  // Health check (no auth required)
  public async healthCheck(): Promise<any> {
    const response = await fetch(`${API_BASE}/api/health`, {
      method: 'GET',
    });
    return this.handleResponse(response);
  }
}

// Export singleton instance
export const apiClient = ApiClient.getInstance();

// Convenience exports for common operations
export const api = {
  // Authentication
  login: (username: string, password: string) => apiClient.login(username, password),
  
  // Health
  health: () => apiClient.healthCheck(),
  
  // Invoices
  getInvoices: () => apiClient.get('/api/invoices'),
  getInvoice: (id: string) => apiClient.get(`/api/invoices/${id}`),
  updateInvoice: (id: string, data: any) => apiClient.put(`/api/invoices/${id}`, data),
  completeInvoice: (id: string) => apiClient.post(`/api/invoices/${id}/complete`),
  
  // Upload
  uploadFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.postFormData('/api/upload', formData);
  },
  
  // Dropdowns
  getDropdowns: () => apiClient.get('/api/dropdowns/all'),
  addDropdownOption: (data: any) => apiClient.post('/api/dropdowns/add', data),
  
  // Email testing
  sendTestEmail: (data: any) => apiClient.post('/api/email-test/bauleiter-approval', data),
  
  // Folder watcher
  getFolderWatcherStatus: () => apiClient.get('/api/folder-watcher/status'),
};
