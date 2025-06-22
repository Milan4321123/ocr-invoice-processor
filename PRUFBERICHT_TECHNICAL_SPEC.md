# 🔧 Basic Prüfbericht - Technical Implementation Specification

## 📊 **Backend API Design**

### **New Route File: `/api/routes/reports.py`**

```python
# reports.py - New API endpoints for Prüfbericht data

@router.get("/reports/invoice-summary")
async def get_invoice_summary():
    """
    Get comprehensive invoice summary for Prüfbericht dashboard
    Returns: List of all invoices with key fields for Bau-Leiter review
    """

@router.get("/reports/data-quality")  
async def get_data_quality():
    """
    Get data quality metrics (OCR accuracy, missing fields, etc.)
    Returns: Quality statistics and missing data summary
    """

@router.get("/reports/critical-dates")
async def get_critical_dates():
    """
    Get payment deadline overview
    Returns: Invoices grouped by due date urgency
    """

@router.get("/reports/project-analysis")
async def get_project_analysis():
    """
    Get invoice distribution by project and vendor
    Returns: Project/vendor breakdown with totals
    """

@router.get("/reports/processing-status")
async def get_processing_status():
    """
    Get workflow status overview
    Returns: Count of invoices by processing status
    """

@router.get("/reports/export/{format}")
async def export_report(format: str):
    """
    Export Prüfbericht in various formats (pdf, excel, csv)
    Returns: File download or generation status
    """
```

### **Database Service Extensions**

```python
# database.py - New methods for report generation

def get_invoice_summary_data(self, filters: Dict = None):
    """Get all invoice data for summary table"""
    
def get_data_quality_metrics(self):
    """Calculate OCR accuracy and missing field statistics"""
    
def get_critical_dates_analysis(self):
    """Analyze payment deadlines and due dates"""
    
def get_project_vendor_breakdown(self):
    """Get invoice distribution by project and vendor"""
    
def get_processing_status_counts(self):
    """Count invoices by workflow status"""
```

---

## 🎨 **Frontend Component Architecture**

### **New Page: `/src/app/prufbericht/page.tsx`**

```typescript
// Prüfbericht main dashboard page
interface PrufberichtData {
  invoiceSummary: InvoiceSummaryItem[]
  dataQuality: DataQualityMetrics
  criticalDates: CriticalDatesInfo
  projectAnalysis: ProjectBreakdown[]
  processingStatus: StatusCounts
}

export default function PrufberichtPage() {
  // Main dashboard layout with all widgets
}
```

### **Widget Components**

```typescript
// InvoiceSummaryTable.tsx
interface InvoiceSummaryItem {
  id: string
  filename: string
  vendor_name: string
  total_amount: number
  invoice_date: string
  due_date: string
  ocr_status: string
  status: string
  ocr_confidence: number
  projekt: string
  source_type: string
}

// DataQualityWidget.tsx  
interface DataQualityMetrics {
  total_invoices: number
  ocr_completed: number
  ocr_pending: number
  missing_due_dates: number
  missing_amounts: number
  avg_confidence: number
  quality_score: number
}

// CriticalDatesWidget.tsx
interface CriticalDatesInfo {
  overdue: InvoiceSummaryItem[]
  due_this_week: InvoiceSummaryItem[]
  due_next_week: InvoiceSummaryItem[]
  future: InvoiceSummaryItem[]
}

// ProjectAnalysisChart.tsx
interface ProjectBreakdown {
  projekt: string
  invoice_count: number
  total_amount: number
  avg_confidence: number
  vendor_distribution: VendorStats[]
}

// ProcessingStatusWidget.tsx
interface StatusCounts {
  uploaded: number
  ocr_pending: number
  awaiting_review: number
  approved: number
  payment_ready: number
  paid: number
}
```

---

## 📋 **Database Query Specifications**

### **1. Invoice Summary Query**
```sql
-- Get all invoice data for main table
SELECT 
    i.id,
    COALESCE(i.filename, i.file_name) as filename,
    COALESCE(i.vendor_name, i.rechnungssteller) as vendor_name,
    COALESCE(i.total_amount, i.brutto_betrag) as total_amount,
    COALESCE(i.invoice_date, i.rechnungsdatum) as invoice_date,
    i.due_date,
    i.ocr_status,
    i.status,
    i.ocr_confidence,
    i.projekt,
    i.source_type,
    i.created_at,
    i.updated_at,
    i.url
FROM invoices i
ORDER BY i.created_at DESC;
```

### **2. Data Quality Metrics Query**  
```sql
-- Calculate quality statistics
SELECT 
    COUNT(*) as total_invoices,
    COUNT(CASE WHEN ocr_status = 'completed' THEN 1 END) as ocr_completed,
    COUNT(CASE WHEN ocr_status = 'pending' THEN 1 END) as ocr_pending,
    COUNT(CASE WHEN ocr_status = 'failed' THEN 1 END) as ocr_failed,
    COUNT(CASE WHEN due_date IS NULL THEN 1 END) as missing_due_dates,
    COUNT(CASE WHEN COALESCE(total_amount, brutto_betrag) IS NULL THEN 1 END) as missing_amounts,
    COUNT(CASE WHEN COALESCE(vendor_name, rechnungssteller) IS NULL THEN 1 END) as missing_vendors,
    AVG(COALESCE(ocr_confidence, 0)) as avg_confidence,
    MIN(COALESCE(ocr_confidence, 0)) as min_confidence,
    MAX(COALESCE(ocr_confidence, 0)) as max_confidence
FROM invoices;
```

### **3. Critical Dates Analysis Query**
```sql
-- Analyze payment deadlines
SELECT 
    i.*,
    CASE 
        WHEN i.due_date < CURRENT_DATE THEN 'overdue'
        WHEN i.due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_this_week'
        WHEN i.due_date <= CURRENT_DATE + INTERVAL '14 days' THEN 'due_next_week'
        ELSE 'future'
    END as urgency_category,
    CURRENT_DATE - i.due_date as days_overdue,
    i.due_date - CURRENT_DATE as days_until_due
FROM invoices i
WHERE i.due_date IS NOT NULL
ORDER BY i.due_date ASC;
```

### **4. Project Analysis Query**
```sql
-- Project and vendor breakdown
SELECT 
    i.projekt,
    COUNT(*) as invoice_count,
    SUM(COALESCE(i.total_amount, i.brutto_betrag)) as total_amount,
    AVG(COALESCE(i.ocr_confidence, 0)) as avg_confidence,
    COUNT(DISTINCT COALESCE(i.vendor_name, i.rechnungssteller)) as vendor_count,
    MIN(i.created_at) as first_invoice,
    MAX(i.created_at) as latest_invoice
FROM invoices i
WHERE i.projekt IS NOT NULL
GROUP BY i.projekt
ORDER BY total_amount DESC;
```

### **5. Processing Status Query**
```sql
-- Workflow status counts
SELECT 
    i.status,
    COUNT(*) as count,
    SUM(COALESCE(i.total_amount, i.brutto_betrag)) as total_value,
    AVG(COALESCE(i.ocr_confidence, 0)) as avg_confidence
FROM invoices i
GROUP BY i.status
ORDER BY count DESC;
```

---

## 🎯 **UI/UX Design Specifications**

### **Layout Structure**
```
┌─────────────────────────────────────────────────────────────┐
│                    📋 Prüfbericht Dashboard                  │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Data Quality   │ Critical Dates  │   Processing Status     │
│     Widget      │     Widget      │       Widget            │
├─────────────────┴─────────────────┴─────────────────────────┤
│                  Project Analysis Chart                     │
├─────────────────────────────────────────────────────────────┤
│                 Invoice Summary Table                       │
│  [Filter] [Search] [Export]                    [Pagination] │
└─────────────────────────────────────────────────────────────┘
```

### **Color Coding System**
```
📊 Status Colors:
├── 🟢 Approved/Completed (Green)
├── 🟡 Pending/Review (Yellow)  
├── 🔴 Overdue/Failed (Red)
├── 🔵 In Progress (Blue)
└── ⚪ Unknown/Empty (Gray)

📈 Quality Indicators:
├── 🟢 High Confidence (>80%)
├── 🟡 Medium Confidence (60-80%)
└── 🔴 Low Confidence (<60%)
```

### **Interactive Features**
```
🖱️ User Interactions:
├── Click row → View invoice details
├── Sort columns → Reorder table data
├── Filter options → Show/hide invoices
├── Export buttons → Download reports
└── Refresh button → Update data
```

---

## 📱 **Responsive Design**

### **Desktop View (>1024px)**
- Full dashboard with all widgets visible
- Large invoice summary table
- Side-by-side widget layout

### **Tablet View (768-1024px)**  
- Stacked widget layout
- Condensed table with scroll
- Essential columns only

### **Mobile View (<768px)**
- Card-based invoice list
- Collapsible widget sections
- Touch-friendly buttons

---

## 🔒 **Security Considerations**

### **Access Control**
- Bau-Leiter role verification
- Project-based data filtering
- Audit log for report access

### **Data Privacy**
- Sensitive data masking options
- Export permission controls
- Session-based access

---

## 📈 **Performance Optimization**

### **Backend**
- Database query optimization
- Response caching for reports
- Pagination for large datasets

### **Frontend**  
- Component memoization
- Virtual scrolling for tables
- Lazy loading for charts

---

## 🧪 **Testing Strategy**

### **Unit Tests**
- Database query validation
- Component rendering tests
- Data calculation accuracy

### **Integration Tests**
- API endpoint responses
- Full dashboard loading
- Export functionality

### **User Acceptance Tests**
- Bau-Leiter workflow testing
- Report accuracy validation
- Performance benchmarks

This specification provides a complete roadmap for implementing the Basic Prüfbericht, giving the Bau-Leiter full visibility and control over invoice data in the system.
