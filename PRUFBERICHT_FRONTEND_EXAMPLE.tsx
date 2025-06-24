/**
 * Prüfbericht (Audit Report) API Integration Example
 * 
 * This example shows how to integrate the Prüfbericht APIs into a React dashboard.
 * Replace with your actual frontend framework and styling preferences.
 */

import React, { useState, useEffect } from 'react';

// Types for the API responses
interface DataQualityMetrics {
  total_invoices: number;
  ocr_statistics: {
    completed: number;
    pending: number;
    failed: number;
    completion_rate: number;
  };
  missing_data: {
    due_dates: number;
    amounts: number;
    vendors: number;
    total_missing: number;
  };
  quality_score: {
    overall: number;
    ocr_processing: number;
    data_completeness: number;
    ocr_confidence: number;
  };
}

interface CriticalDatesData {
  overdue: { count: number; total_amount: number };
  due_this_week: { count: number; total_amount: number };
  due_next_week: { count: number; total_amount: number };
  no_due_date: { count: number; total_amount: number };
}

interface ProjectSummary {
  total_projects: number;
  total_vendors: number;
  total_invoices: number;
  total_amount: number;
}

// API service functions
const PrufberichtAPI = {
  async getDataQuality(): Promise<DataQualityMetrics> {
    const response = await fetch('/api/reports/data-quality');
    const data = await response.json();
    return data.metrics;
  },

  async getCriticalDates(): Promise<CriticalDatesData> {
    const response = await fetch('/api/reports/critical-dates');
    const data = await response.json();
    return data.data;
  },

  async getProjectAnalysis(): Promise<ProjectSummary> {
    const response = await fetch('/api/reports/project-analysis');
    const data = await response.json();
    return data.data.summary;
  },

  async getInvoiceSummary(filters?: { project?: string; status?: string; limit?: number }) {
    const params = new URLSearchParams();
    if (filters?.project) params.append('project_filter', filters.project);
    if (filters?.status) params.append('status_filter', filters.status);
    if (filters?.limit) params.append('limit', filters.limit.toString());
    
    const response = await fetch(`/api/reports/invoice-summary?${params}`);
    return response.json();
  }
};

// Dashboard Component
const PrufberichtDashboard: React.FC = () => {
  const [dataQuality, setDataQuality] = useState<DataQualityMetrics | null>(null);
  const [criticalDates, setCriticalDates] = useState<CriticalDatesData | null>(null);
  const [projectSummary, setProjectSummary] = useState<ProjectSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const [quality, dates, projects] = await Promise.all([
          PrufberichtAPI.getDataQuality(),
          PrufberichtAPI.getCriticalDates(),
          PrufberichtAPI.getProjectAnalysis()
        ]);
        
        setDataQuality(quality);
        setCriticalDates(dates);
        setProjectSummary(projects);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return <div className="dashboard-loading">Loading Prüfbericht...</div>;
  }

  return (
    <div className="prufbericht-dashboard">
      <h1>Prüfbericht - Invoice Audit Dashboard</h1>
      
      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard
          title="Total Invoices"
          value={dataQuality?.total_invoices || 0}
          icon="📄"
        />
        <KPICard
          title="OCR Success Rate"
          value={`${dataQuality?.ocr_statistics.completion_rate.toFixed(1)}%`}
          icon="🤖"
          status={dataQuality?.ocr_statistics.completion_rate >= 90 ? 'good' : 
                  dataQuality?.ocr_statistics.completion_rate >= 75 ? 'warning' : 'danger'}
        />
        <KPICard
          title="Overall Quality"
          value={`${dataQuality?.quality_score.overall.toFixed(1)}%`}
          icon="⭐"
          status={dataQuality?.quality_score.overall >= 80 ? 'good' : 
                  dataQuality?.quality_score.overall >= 60 ? 'warning' : 'danger'}
        />
        <KPICard
          title="Total Value"
          value={`€${projectSummary?.total_amount.toLocaleString()}`}
          icon="💰"
        />
      </div>

      {/* Critical Alerts */}
      <div className="alerts-section">
        <h2>🚨 Critical Alerts</h2>
        <div className="alert-grid">
          {criticalDates?.overdue.count > 0 && (
            <AlertCard
              type="danger"
              title="Overdue Invoices"
              count={criticalDates.overdue.count}
              amount={criticalDates.overdue.total_amount}
            />
          )}
          {criticalDates?.due_this_week.count > 0 && (
            <AlertCard
              type="warning"
              title="Due This Week"
              count={criticalDates.due_this_week.count}
              amount={criticalDates.due_this_week.total_amount}
            />
          )}
          {criticalDates?.no_due_date.count > 0 && (
            <AlertCard
              type="info"
              title="Missing Due Dates"
              count={criticalDates.no_due_date.count}
              amount={criticalDates.no_due_date.total_amount}
            />
          )}
        </div>
      </div>

      {/* Data Quality Breakdown */}
      <div className="quality-section">
        <h2>📊 Data Quality Analysis</h2>
        <div className="quality-grid">
          <QualityMetric
            label="OCR Processing"
            value={dataQuality?.quality_score.ocr_processing}
            description={`${dataQuality?.ocr_statistics.completed}/${dataQuality?.total_invoices} invoices processed`}
          />
          <QualityMetric
            label="Data Completeness"
            value={dataQuality?.quality_score.data_completeness}
            description={`${dataQuality?.missing_data.total_missing} missing fields`}
          />
          <QualityMetric
            label="OCR Confidence"
            value={dataQuality?.quality_score.ocr_confidence}
            description="Average confidence score"
          />
        </div>
      </div>

      {/* Project Overview */}
      <div className="projects-section">
        <h2>🏗️ Project Overview</h2>
        <div className="project-stats">
          <div className="stat">
            <span className="stat-label">Active Projects</span>
            <span className="stat-value">{projectSummary?.total_projects}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Vendors</span>
            <span className="stat-value">{projectSummary?.total_vendors}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Avg. per Project</span>
            <span className="stat-value">
              €{((projectSummary?.total_amount || 0) / (projectSummary?.total_projects || 1)).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper Components
const KPICard: React.FC<{
  title: string;
  value: string | number;
  icon: string;
  status?: 'good' | 'warning' | 'danger';
}> = ({ title, value, icon, status }) => (
  <div className={`kpi-card ${status || ''}`}>
    <div className="kpi-icon">{icon}</div>
    <div className="kpi-content">
      <div className="kpi-title">{title}</div>
      <div className="kpi-value">{value}</div>
    </div>
  </div>
);

const AlertCard: React.FC<{
  type: 'danger' | 'warning' | 'info';
  title: string;
  count: number;
  amount: number;
}> = ({ type, title, count, amount }) => (
  <div className={`alert-card alert-${type}`}>
    <div className="alert-title">{title}</div>
    <div className="alert-count">{count} invoices</div>
    <div className="alert-amount">€{amount.toLocaleString()}</div>
  </div>
);

const QualityMetric: React.FC<{
  label: string;
  value?: number;
  description: string;
}> = ({ label, value, description }) => (
  <div className="quality-metric">
    <div className="metric-label">{label}</div>
    <div className="metric-value">{value?.toFixed(1)}%</div>
    <div className="metric-description">{description}</div>
    <div className="metric-bar">
      <div 
        className="metric-fill" 
        style={{ width: `${Math.min(value || 0, 100)}%` }}
      />
    </div>
  </div>
);

export default PrufberichtDashboard;

// CSS styles (add to your stylesheet)
const styles = `
.prufbericht-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.kpi-card.good { border-left: 4px solid #10b981; }
.kpi-card.warning { border-left: 4px solid #f59e0b; }
.kpi-card.danger { border-left: 4px solid #ef4444; }

.kpi-icon {
  font-size: 2em;
}

.kpi-value {
  font-size: 1.8em;
  font-weight: bold;
  color: #1f2937;
}

.alert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.alert-card {
  padding: 15px;
  border-radius: 6px;
  text-align: center;
}

.alert-danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert-warning {
  background: #fffbeb;
  border: 1px solid #fed7aa;
  color: #d97706;
}

.alert-info {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #2563eb;
}

.quality-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.quality-metric {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.metric-bar {
  background: #e5e7eb;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 10px;
}

.metric-fill {
  background: #3b82f6;
  height: 100%;
  transition: width 0.3s ease;
}
`;
