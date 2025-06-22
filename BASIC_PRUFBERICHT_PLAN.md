# 📋 Basic Prüfbericht (Audit Report) - Implementation Plan

## 🎯 **Purpose**
Create a **Basic Prüfbericht Dashboard** that gives the **Bau-Leiter** complete visibility into all invoice data stored in Supabase, enabling proper control and verification before payment processing.

---

## 📊 **Current Supabase Data Structure**

### **Available Data Fields**
After database migration, we have access to:

#### **🗂️ Basic Invoice Info**
- `id`, `filename`, `file_size`, `created_at`
- `source_type` (drag_drop, folder_watcher, manual)
- `source_metadata` (upload details)
- `url` (public file link)

#### **💰 Financial Data**  
- `netto_betrag` (Net Amount)
- `brutto_betrag` (Gross Amount) 
- `subtotal`, `tax_amount`, `total_amount`
- `currency` (EUR)

#### **📅 Date Information**
- `rechnungsdatum` (Invoice Date)
- `invoice_date` (English equivalent)
- `due_date` (Payment Due Date)
- `created_at`, `updated_at`, `processed_at`

#### **👥 Business Entities**
- `rechnungssteller` (Invoice Issuer/Vendor)
- `rechnungsempfaenger` (Invoice Recipient/Customer)
- `vendor_name`, `customer_name`
- `projekt` (Project), `gewerk` (Trade/Craft)

#### **🔍 OCR & Processing Status**
- `ocr_status` (pending, completed, failed)
- `ocr_confidence` (0.0-1.0)
- `ocr_text`, `ocr_pages`, `ocr_processing_time`
- `status` (pending, approved, paid, etc.)

#### **📋 Structured Data**
- `invoice_number`, `po_number`
- `payment_terms`
- `line_items` (JSON), `entities` (JSON)

---

## 🏗️ **Basic Prüfbericht Dashboard Design**

### **Section 1: Invoice Overview Table**
**Purpose**: Show all invoices with key data for Bau-Leiter review

```
| Status | Filename | Vendor | Amount | Invoice Date | Due Date | OCR Status | Actions |
|--------|----------|---------|---------|-------------|----------|------------|---------|
| 🟡 Pending | INV001.pdf | Elektro Wagner | €1,428.00 | 22.06.2025 | 22.07.2025 | ✅ Completed | Review |
| 🟢 Approved | INV002.pdf | Sanitär Schmidt | €850.00 | 20.06.2025 | 20.07.2025 | ⏳ Pending | Process |
```

### **Section 2: Data Quality Overview**
**Purpose**: Show OCR accuracy and missing information

```
📊 Data Quality Summary:
├── Total Invoices: 15
├── OCR Processed: 12 (80%)
├── Manual Review Needed: 3
├── Missing Due Dates: 2
├── Missing Amounts: 1
└── Average OCR Confidence: 87%
```

### **Section 3: Critical Dates Dashboard**
**Purpose**: Highlight payment deadlines (for future Skonto implementation)

```
⏰ Payment Deadlines:
├── 🔴 Overdue (0)
├── 🟡 Due This Week (3)
├── 🟢 Due Next Week (5)
└── 📅 Future (7)
```

### **Section 4: Project & Vendor Analysis**
**Purpose**: Show invoice distribution by project and vendor

```
📈 Invoice Distribution:
├── By Project:
│   ├── Wohnbau Mitte 2024: 8 invoices, €12,450
│   └── Bürokomplex Nord: 7 invoices, €9,890
├── By Vendor:
│   ├── Elektro Wagner: 4 invoices, €5,670
│   └── Sanitär Schmidt: 3 invoices, €3,980
```

### **Section 5: Processing Status Overview**
**Purpose**: Track workflow progress

```
🔄 Processing Status:
├── 📤 Uploaded: 2
├── ⏳ OCR Pending: 3  
├── 👁️ Awaiting Review: 5
├── ✅ Approved: 4
└── 💳 Payment Ready: 1
```

---

## 🛠️ **Implementation Approach**

### **Phase 1: Data Aggregation API**
Create new backend endpoints to gather Prüfbericht data:

```python
# New API endpoints needed:
GET /api/reports/invoice-summary     # Overview table data
GET /api/reports/data-quality        # OCR accuracy, missing fields
GET /api/reports/critical-dates      # Payment deadlines
GET /api/reports/project-analysis    # Project/vendor breakdown
GET /api/reports/processing-status   # Workflow status counts
```

### **Phase 2: Dashboard Components**
Create React components for each section:

```typescript
// New components needed:
- InvoiceSummaryTable.tsx
- DataQualityWidget.tsx  
- CriticalDatesWidget.tsx
- ProjectAnalysisChart.tsx
- ProcessingStatusWidget.tsx
- PrufberichtLayout.tsx
```

### **Phase 3: Export Functionality**
Add report export capabilities:

```
📄 Export Options:
├── PDF Report (for compliance)
├── Excel Export (for analysis)
├── CSV Data (for external tools)
└── Print-friendly View
```

---

## 🎯 **Strategic Benefits**

### **For Bau-Leiter:**
- ✅ **Complete Visibility**: See all invoice data in one place
- ✅ **Data Validation**: Identify missing/incorrect information
- ✅ **Workflow Control**: Track approval status of all invoices
- ✅ **Compliance Ready**: Generate audit reports for accountants

### **For Company:**
- ✅ **Process Transparency**: Clear audit trail of all invoices
- ✅ **Quality Control**: Monitor OCR accuracy and manual corrections
- ✅ **Financial Oversight**: Project-based cost tracking
- ✅ **Efficiency Metrics**: Processing time and bottleneck identification

---

## 📋 **Required Database Queries**

### **Main Data Query**
```sql
SELECT 
    id, filename, vendor_name, total_amount, 
    invoice_date, due_date, ocr_status, status,
    projekt, source_type, ocr_confidence,
    created_at, updated_at
FROM invoices 
ORDER BY created_at DESC;
```

### **Data Quality Query**
```sql
SELECT 
    COUNT(*) as total_invoices,
    COUNT(CASE WHEN ocr_status = 'completed' THEN 1 END) as ocr_completed,
    COUNT(CASE WHEN due_date IS NULL THEN 1 END) as missing_due_dates,
    COUNT(CASE WHEN total_amount IS NULL THEN 1 END) as missing_amounts,
    AVG(ocr_confidence) as avg_confidence
FROM invoices;
```

### **Project Analysis Query**
```sql
SELECT 
    projekt,
    COUNT(*) as invoice_count,
    SUM(total_amount) as total_amount,
    AVG(ocr_confidence) as avg_confidence
FROM invoices 
WHERE projekt IS NOT NULL
GROUP BY projekt
ORDER BY total_amount DESC;
```

---

## 🔄 **Next Steps**

1. **Backend API Development**: Create report endpoints
2. **Frontend Components**: Build dashboard widgets  
3. **Data Visualization**: Add charts and metrics
4. **Export Functionality**: PDF/Excel generation
5. **User Testing**: Get Bau-Leiter feedback

---

## 💡 **Future Enhancements**

Once basic Prüfbericht is working:

1. **Interactive Filters**: Filter by date range, project, vendor
2. **Drill-down Details**: Click invoice to see full OCR data
3. **Approval Workflow**: Mark invoices as approved/rejected
4. **Notification System**: Alert for missing data or deadlines
5. **Comparison Reports**: Month-over-month analysis

This basic Prüfbericht will give the Bau-Leiter complete control and visibility over the invoice processing system, establishing the foundation for more advanced features like Skonto management and automated reminders.
