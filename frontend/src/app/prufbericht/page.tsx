'use client';

import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, Clock, CheckCircle, XCircle, Filter, Download, RefreshCw, Mail, ThumbsUp, ThumbsDown } from 'lucide-react';

interface SkontoMetrics {
  totalInvoices: number;
  totalSkontoAmount: number;
  capturedSkonto: number;
  missedSkonto: number;
  pendingReview: number;
  averageProcessingTime: number;
}

interface SkontoInvoice {
  id: string;
  invoiceNumber: string;
  vendor: string;
  amount: number;
  skontoRate: number;
  skontoAmount: number;
  skontoDeadline: string;
  status: 'captured' | 'missed' | 'pending' | 'expired';
  processedDate?: string;
  daysRemaining?: number;
}

export default function PrufberichtPage() {
  const [metrics, setMetrics] = useState<SkontoMetrics | null>(null);
  const [invoices, setInvoices] = useState<SkontoInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Mock data for demonstration - replace with actual API calls
      const mockMetrics: SkontoMetrics = {
        totalInvoices: 847,
        totalSkontoAmount: 89750,
        capturedSkonto: 67320,
        missedSkonto: 12450,
        pendingReview: 23,
        averageProcessingTime: 2.3
      };

      const mockInvoices: SkontoInvoice[] = [
        {
          id: '1',
          invoiceNumber: 'INV-2024-001',
          vendor: 'Siemens AG',
          amount: 15420,
          skontoRate: 2.5,
          skontoAmount: 385.50,
          skontoDeadline: '2024-01-15',
          status: 'pending',
          daysRemaining: 5
        },
        {
          id: '2',
          invoiceNumber: 'INV-2024-002',
          vendor: 'BMW Group',
          amount: 28750,
          skontoRate: 3.0,
          skontoAmount: 862.50,
          skontoDeadline: '2024-01-12',
          status: 'captured',
          processedDate: '2024-01-10'
        },
        {
          id: '3',
          invoiceNumber: 'INV-2024-003',
          vendor: 'Mercedes-Benz',
          amount: 42100,
          skontoRate: 2.0,
          skontoAmount: 842.00,
          skontoDeadline: '2024-01-08',
          status: 'missed',
          daysRemaining: -2
        },
        {
          id: '4',
          invoiceNumber: 'INV-2024-004',
          vendor: 'Volkswagen AG',
          amount: 18900,
          skontoRate: 2.5,
          skontoAmount: 472.50,
          skontoDeadline: '2024-01-20',
          status: 'pending',
          daysRemaining: 10
        }
      ];

      setMetrics(mockMetrics);
      setInvoices(mockInvoices);
      setError(null);
      
    } catch (error) {
      console.error('Error fetching Skonto data:', error);
      setError('Failed to load Skonto data');
    } finally {
      setLoading(false);
    }
  };

  // Action handlers for Skonto management
  const handleSendReminder = async (invoiceId: string) => {
    try {
      setActionLoading(invoiceId);
      const response = await fetch(`/api/invoices/${invoiceId}/send-skonto-reminder`, {
        method: 'POST',
      });
      
      if (response.ok) {
        // Refresh data after action
        await fetchData();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send reminder');
      }
    } catch (error) {
      console.error('Error sending reminder:', error);
      alert('Failed to send reminder: ' + (error as Error).message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleMarkAsTaken = async (invoiceId: string) => {
    try {
      setActionLoading(invoiceId);
      const response = await fetch(`/api/invoices/${invoiceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skonto_decision: 'taken'
        }),
      });
      
      if (response.ok) {
        // Refresh data after action
        await fetchData();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to mark as taken');
      }
    } catch (error) {
      console.error('Error marking as taken:', error);
      alert('Failed to mark as taken: ' + (error as Error).message);
    } finally {
      setActionLoading(null);
    }
  };

  const handleMarkAsMissed = async (invoiceId: string) => {
    try {
      setActionLoading(invoiceId);
      const response = await fetch(`/api/invoices/${invoiceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skonto_decision: 'missed'
        }),
      });
      
      if (response.ok) {
        // Refresh data after action
        await fetchData();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to mark as missed');
      }
    } catch (error) {
      console.error('Error marking as missed:', error);
      alert('Failed to mark as missed: ' + (error as Error).message);
    } finally {
      setActionLoading(null);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredInvoices = invoices.filter(invoice => {
    const matchesStatus = filterStatus === 'all' || invoice.status === filterStatus;
    const matchesSearch = 
      invoice.invoiceNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.vendor.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      captured: { bgColor: 'glass-card border-green-200', textColor: 'text-green-700', icon: CheckCircle },
      missed: { bgColor: 'glass-card border-red-200', textColor: 'text-red-700', icon: XCircle },
      pending: { bgColor: 'glass-card border-yellow-200', textColor: 'text-yellow-700', icon: Clock },
      expired: { bgColor: 'glass-card border-gray-200', textColor: 'text-gray-700', icon: AlertCircle }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig];
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 rounded-xl px-2.5 py-0.5 text-xs font-semibold border shadow-sm ${config.bgColor} ${config.textColor}`}>
        <Icon className="h-3 w-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen gradient-bg-light relative overflow-hidden">
        {/* Floating Background Elements */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute top-40 right-20 w-40 h-40 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-20 left-1/3 w-36 h-36 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '4s' }}></div>
        
        <div className="flex items-center justify-center min-h-screen">
          <div className="glass-card p-8 text-center animate-pulse rounded-xl border shadow">
            <div className="flex items-center justify-center space-x-2">
              <RefreshCw className="h-6 w-6 animate-spin text-purple-600" />
              <span className="text-lg font-medium text-gray-700">Loading Skonto Report...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen gradient-bg-light relative overflow-hidden">
        {/* Floating Background Elements */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-red-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-orange-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
        
        <div className="flex items-center justify-center min-h-screen">
          <div className="glass-card p-8 text-center max-w-md rounded-xl border shadow">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading Report</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg-light relative overflow-hidden">
      {/* Floating Background Elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
      <div className="absolute top-40 right-20 w-40 h-40 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
      <div className="absolute bottom-20 left-1/3 w-36 h-36 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '4s' }}></div>
      <div className="absolute top-1/2 right-10 w-28 h-28 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '1s' }}></div>

      <div className="relative z-10 pt-20 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header Section */}
          <div className="mb-8">
            <div className="glass-card p-6 border-0 shadow-xl rounded-xl">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                    Skonto Prüfbericht
                  </h1>
                  <p className="text-gray-600">
                    Comprehensive analysis of discount opportunities and performance
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 mt-4 md:mt-0">
                  <span className="inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold bg-gradient-to-r from-green-100 to-green-200 text-green-700 border border-green-300">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    Real-time Analytics
                  </span>
                  <span className="inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold bg-gradient-to-r from-blue-100 to-blue-200 text-blue-700 border border-blue-300">
                    <Clock className="h-3 w-3 mr-1" />
                    Auto-updated
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Metrics Section */}
          {metrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
              <div className="glass-card border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 rounded-xl">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">Total Invoices</p>
                      <p className="text-2xl font-bold text-gray-900">{metrics.totalInvoices.toLocaleString()}</p>
                    </div>
                    <div className="h-12 w-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                      <AlertCircle className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 rounded-xl">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">Total Skonto</p>
                      <p className="text-2xl font-bold text-gray-900">€{metrics.totalSkontoAmount.toLocaleString()}</p>
                    </div>
                    <div className="h-12 w-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <TrendingUp className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 rounded-xl">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">Captured</p>
                      <p className="text-2xl font-bold text-green-600">€{metrics.capturedSkonto.toLocaleString()}</p>
                    </div>
                    <div className="h-12 w-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 rounded-xl">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">Missed</p>
                      <p className="text-2xl font-bold text-red-600">€{metrics.missedSkonto.toLocaleString()}</p>
                    </div>
                    <div className="h-12 w-12 bg-gradient-to-r from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                      <XCircle className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 rounded-xl">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">Pending</p>
                      <p className="text-2xl font-bold text-yellow-600">{metrics.pendingReview}</p>
                    </div>
                    <div className="h-12 w-12 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-lg flex items-center justify-center">
                      <Clock className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass-card border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 rounded-xl">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-1">Avg. Processing</p>
                      <p className="text-2xl font-bold text-gray-900">{metrics.averageProcessingTime.toFixed(1)}d</p>
                    </div>
                    <div className="h-12 w-12 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center">
                      <Clock className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Filters and Controls */}
          <div className="glass-card border-0 shadow-lg mb-6 rounded-xl">
            <div className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="flex flex-col md:flex-row gap-4 flex-1">
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">Filter by Status:</span>
                    <select 
                      value={filterStatus} 
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="w-40 bg-white/50 border border-white/20 rounded-md px-3 py-1 text-sm"
                    >
                      <option value="all">All Status</option>
                      <option value="captured">Captured</option>
                      <option value="missed">Missed</option>
                      <option value="pending">Pending</option>
                      <option value="expired">Expired</option>
                    </select>
                  </div>
                  
                  <input
                    placeholder="Search invoices or vendors..."
                    value={searchTerm}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                    className="max-w-xs bg-white/50 border border-white/20 rounded-md px-3 py-1 text-sm placeholder:text-gray-500"
                  />
                </div>
                
                <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg px-4 py-2 rounded-md text-sm font-medium transition-colors inline-flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Export Report
                </button>
              </div>
            </div>
          </div>

          {/* Invoices Table */}
          <div className="glass-card border-0 shadow-xl rounded-xl">
            <div className="border-b border-white/20 p-6">
              <h3 className="text-xl font-semibold text-gray-800">
                Skonto Invoice Details ({filteredInvoices.length} invoices)
              </h3>
            </div>
            <div className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skonto</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deadline</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredInvoices.map((invoice, index) => (
                      <tr 
                        key={invoice.id} 
                        className="hover:bg-white/50 transition-colors duration-200"
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{invoice.invoiceNumber}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{invoice.vendor}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">€{invoice.amount.toLocaleString()}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {invoice.skontoRate}% (€{invoice.skontoAmount.toLocaleString()})
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(invoice.skontoDeadline).toLocaleDateString()}
                            {invoice.daysRemaining !== undefined && (
                              <div className={`text-xs ${invoice.daysRemaining > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {invoice.daysRemaining > 0 ? `${invoice.daysRemaining} days left` : `${Math.abs(invoice.daysRemaining)} days overdue`}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(invoice.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            {/* Send Reminder Button */}
                            <button 
                              onClick={() => handleSendReminder(invoice.id)}
                              disabled={actionLoading === invoice.id || invoice.status === 'captured' || invoice.status === 'missed'}
                              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-blue-600 bg-blue-50 hover:bg-blue-100 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Send Skonto Reminder"
                            >
                              <Mail className="h-3 w-3 mr-1" />
                              Reminder
                            </button>
                            
                            {/* Mark as Taken Button */}
                            <button 
                              onClick={() => handleMarkAsTaken(invoice.id)}
                              disabled={actionLoading === invoice.id || invoice.status === 'captured' || invoice.status === 'missed'}
                              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-green-600 bg-green-50 hover:bg-green-100 hover:text-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Mark Skonto as Taken"
                            >
                              <ThumbsUp className="h-3 w-3 mr-1" />
                              Taken
                            </button>
                            
                            {/* Mark as Missed Button */}
                            <button 
                              onClick={() => handleMarkAsMissed(invoice.id)}
                              disabled={actionLoading === invoice.id || invoice.status === 'captured' || invoice.status === 'missed'}
                              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-md text-red-600 bg-red-50 hover:bg-red-100 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Mark Skonto as Missed"
                            >
                              <ThumbsDown className="h-3 w-3 mr-1" />
                              Missed
                            </button>
                            
                            {actionLoading === invoice.id && (
                              <div className="inline-flex items-center px-2 py-1">
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-purple-600"></div>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredInvoices.length === 0 && (
                <div className="text-center py-12">
                  <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
                  <p className="text-gray-500">Try adjusting your search criteria or filters.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
