# Prüfbericht (Audit Report) Functionality

## Overview

The Prüfbericht system provides comprehensive audit and analysis capabilities for the OCR Invoice Processor. It offers multiple report types designed for Bau-Leiter (construction managers) to monitor invoice processing, data quality, payment deadlines, and project costs.

## Available Reports

### 1. Data Quality Report (`/api/reports/data-quality`)

**Purpose**: Assess OCR accuracy and data completeness across all invoices.

**Key Metrics**:
- **Total Invoices**: Total number of invoices in the system
- **OCR Statistics**: 
  - Completed, pending, and failed OCR processes
  - OCR completion rate percentage
- **Missing Data Analysis**:
  - Count of invoices missing due dates (`faelligkeit`)
  - Count of invoices missing amounts (`rechnungsbetrag`)
  - Count of invoices missing vendor information (`rechnungssteller`)
- **Confidence Metrics**:
  - Average OCR confidence scores
  - Distribution of high/medium/low confidence invoices
- **Quality Score**:
  - Overall quality score (0-100)
  - OCR processing score
  - Data completeness score
  - OCR confidence score

**Example Usage**:
```bash
curl "http://localhost:8000/api/reports/data-quality"
```

### 2. Critical Dates Report (`/api/reports/critical-dates`)

**Purpose**: Monitor payment deadlines and identify urgent invoices.

**Key Features**:
- **Overdue**: Invoices past their due date (`faelligkeit`)
- **Due This Week**: Invoices due within 7 days
- **Due Next Week**: Invoices due within 8-14 days
- **Future**: Invoices due more than 14 days from now
- **No Due Date**: Invoices missing due date information

**Each Category Includes**:
- Invoice count
- Total amount (€)
- Full invoice details

**Example Usage**:
```bash
curl "http://localhost:8000/api/reports/critical-dates"
```

### 3. Project Analysis Report (`/api/reports/project-analysis`)

**Purpose**: Analyze invoice distribution by project and vendor.

**Key Features**:
- **Project Breakdown**:
  - Invoice count per project (`projekt`)
  - Total amount per project
  - Vendor count per project
  - Average OCR confidence per project
- **Vendor Breakdown**:
  - Invoice count per vendor (`rechnungssteller`)
  - Total amount per vendor
  - Project count per vendor
  - Average OCR confidence per vendor
- **Summary Statistics**:
  - Total projects, vendors, invoices
  - Grand total amount

**Example Usage**:
```bash
curl "http://localhost:8000/api/reports/project-analysis"
```

### 4. Processing Status Report (`/api/reports/processing-status`)

**Purpose**: Monitor workflow status and processing stages.

**Key Features**:
- **Processing Status Groups**:
  - `pending`: Invoices awaiting approval
  - `approved`: Invoices approved for payment
  - `completed`: Invoices fully processed
  - Custom status values
- **OCR Status Groups**:
  - `completed`: OCR processing finished
  - `pending`: OCR processing queued
  - `failed`: OCR processing failed
- **Statistics per Group**:
  - Invoice count
  - Total amount (€)
  - Full invoice details

**Example Usage**:
```bash
curl "http://localhost:8000/api/reports/processing-status"
```

### 5. Invoice Summary Report (`/api/reports/invoice-summary`)

**Purpose**: Comprehensive invoice listing with enhanced metadata for dashboard view.

**Key Features**:
- **Enhanced Fields** (automatically calculated):
  - `urgency`: Payment urgency level
  - `days_until_due`: Days until payment due
  - `has_missing_data`: Data completeness indicator
  - `ocr_quality`: OCR processing quality level
- **Filtering Support**:
  - `status_filter`: Filter by processing status
  - `project_filter`: Filter by project name (`projekt`)
- **Pagination Support**:
  - `limit`: Number of invoices to return (default: 50)
  - `offset`: Starting offset for pagination (default: 0)

**Example Usage**:
```bash
# Basic summary
curl "http://localhost:8000/api/reports/invoice-summary"

# Filtered by project
curl "http://localhost:8000/api/reports/invoice-summary?project_filter=Neubau Bürogebäude München"

# Filtered by status with pagination
curl "http://localhost:8000/api/reports/invoice-summary?status_filter=pending&limit=20&offset=0"
```

## Database Schema Mapping

The Prüfbericht system correctly maps to the German business field names in the `invoices_clean` table:

| Report Field | Database Field | Description |
|--------------|----------------|-------------|
| Due Date | `faelligkeit` | Payment due date |
| Amount | `rechnungsbetrag` | Invoice amount |
| Vendor | `rechnungssteller` | Invoice issuer/vendor |
| Customer | `rechnungsempfaenger` | Invoice recipient |
| Project | `projekt` | Project name |
| Trade | `gewerk` | Trade/work category |
| Invoice Type | `rechnungsart` | Type of invoice |
| KfW Eligible | `kfw_anrechenbare_kosten` | KfW eligible costs |
| Invoice Date | `rechnungseingang` | Invoice receipt date |

## Data Quality Indicators

### OCR Quality Levels
- **High**: Confidence ≥ 0.8 (80%)
- **Medium**: Confidence 0.6-0.79 (60-79%)
- **Low**: Confidence < 0.6 (<60%)

### Urgency Levels
- **Overdue**: Past due date
- **Due This Week**: Due within 7 days
- **Due Next Week**: Due within 8-14 days
- **Future**: Due > 14 days
- **No Due Date**: Missing due date

### Quality Score Calculation
- **Overall Quality**: Average of OCR processing + Data completeness + OCR confidence
- **OCR Processing**: Percentage of invoices with completed OCR
- **Data Completeness**: Percentage of invoices with complete core fields
- **OCR Confidence**: Average confidence score across all invoices

## API Response Format

All reports follow a consistent response format:

```json
{
  "success": true,
  "data": { /* report-specific data */ },
  "summary": { /* optional summary statistics */ },
  "pagination": { /* optional pagination info */ }
}
```

Error responses:
```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

## Integration with Frontend

The Prüfbericht endpoints are designed to integrate seamlessly with dashboard components:

1. **KPI Cards**: Use data quality and processing status summaries
2. **Charts**: Use project analysis and critical dates data
3. **Tables**: Use invoice summary with filtering and pagination
4. **Alerts**: Use overdue and urgent invoice counts

## Performance Considerations

- All reports cache data appropriately for dashboard performance
- Large datasets use pagination to prevent timeout issues
- Database queries are optimized for the `invoices_clean` schema
- Reports automatically handle missing or malformed data gracefully

## Testing

The comprehensive test suite (`test_prufbericht_comprehensive.py`) validates:
- All endpoint functionality
- Data quality calculations
- Filtering and pagination
- Error handling
- Real-world data scenarios

## Future Enhancements

Potential improvements for the Prüfbericht system:
1. **Export Functionality**: PDF/Excel export of reports
2. **Scheduled Reports**: Automated report generation
3. **Custom Alerts**: Configurable thresholds and notifications
4. **Historical Trending**: Time-based analysis and trends
5. **Advanced Filtering**: Multi-field filtering and search
6. **Dashboard Widgets**: Pre-configured dashboard components
