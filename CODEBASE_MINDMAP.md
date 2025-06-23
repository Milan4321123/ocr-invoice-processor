# OCR Invoice Processor - Codebase Mindmap

```mermaid
mindmap
  root((OCR Invoice Processor))
    Backend
      FastAPI Main
        main.py
          CORS Setup
          Route Imports
          Port 8001
      API Routes
        Health
          GET /health
        Upload
          POST /upload
          File handling
        Invoices
          GET /invoices
          GET /invoices/{id}/editor
          PUT /invoices/{id}/editor
          DELETE /invoices/{id}
        OCR
          POST /ocr/process
          OCR workflow
        Dropdowns
          GET /api/dropdowns
          POST /api/dropdowns/add-option
          Field management
        Reports
          GET /api/reports/invoice-summary
          GET /api/reports/data-quality
          GET /api/reports/critical-dates
          GET /api/reports/project-analysis
          GET /api/reports/processing-status
        Folder Watcher
          GET /api/folder-watcher/status
          POST /api/folder-watcher/start
      Services
        Database Service
          Supabase client
          Field mapping
          CRUD operations
        Upload Service
          File processing
          Storage handling
        Folder Watcher
          Background monitoring
          Auto-processing
      OCR Engine
        Document AI Service
          Google Cloud integration
        Invoice Parser
          Data extraction
        Mock Service
          Development testing
        Workflow
          Processing pipeline
      Config
        OCR Config
          Service settings
          API keys
    Frontend
      Next.js App
        Port 3000
        TypeScript
      Pages
        Home
          Upload buttons
          Navigation
        Dashboard
          Invoice overview
          Review status
          Business metrics
        Invoice Editor
          Manual review
          Field editing
          Dropdown integration
        Prüfbericht
          Audit reports
          Approval workflow
          Business analysis
      Components
        InvoiceForm
          Field mapping
          Dropdown handling
          Save functionality
        Dropzone
          File upload
        PDFViewer
          Document display
        SearchableDropdown
          Dynamic options
        FolderWatcher
          Status monitoring
      Services
        API Client
          Backend communication
        Dropdown Service
          Option management
    Database
      Supabase
        Tables
          invoices
            Core fields
            German business fields
            OCR data
            Timestamps
          dropdown_options
            Field definitions
            Values and labels
            Metadata
        Storage
          invoices bucket
          File URLs
        Policies
          Access control
    Data Flow
      Upload
        File → Backend → Storage
        OCR → Database
      Manual Review
        Dashboard → Editor
        Field updates → Database
      Business Workflow
        Editor → Supabase → Prüfbericht
        Dropdown integration
        Approval process
```

## API Endpoints Overview

### 🔥 **CRITICAL ENDPOINTS (Your Core Workflow)**
```mermaid
graph TD
    A[Dashboard] -->|GET| B[/api/reports/invoice-summary]
    B --> C[Invoice List with Business Data]
    C -->|Click Edit| D[/invoices/{id}/editor GET]
    D --> E[Invoice Editor Form]
    E -->|Save Changes| F[/invoices/{id}/editor PUT]
    F -->|❌ ISSUE HERE| G[Supabase Update]
    G --> H[/api/reports/prufbericht]
    
    E -->|Load Options| I[/api/dropdowns GET]
    E -->|Add New Option| J[/api/dropdowns/add-option POST]
```

### 🚨 **IDENTIFIED ISSUES**

1. **PUT /invoices/{id}/editor** - Updates not reaching database
2. **GET /invoices/{id}/editor** - Skonto fields returning null
3. **Field Mapping** - Inconsistencies in German ↔ English mapping

### 📁 **File Structure**
```
backend/
├── main.py                 # FastAPI app entry point
├── api/routes/            # Route handlers
│   ├── invoices.py        # 🔥 ISSUE: Editor endpoints
│   ├── reports.py         # ✅ Working: Dashboard data
│   ├── dropdowns.py       # ✅ Working: Options
│   └── ...
├── services/              # Business logic
│   ├── database.py        # 🔥 ISSUE: Field mapping
│   └── ...
└── ocr/                   # OCR processing

frontend/
├── src/app/               # Next.js pages
│   ├── dashboard/         # ✅ Working
│   ├── invoice-editor/    # 🔥 Connected to broken API
│   └── prufbericht/       # ✅ Working
├── src/components/        # UI components
│   ├── InvoiceForm.tsx    # 🔥 Calls broken API
│   └── ...
└── src/services/          # API clients
```
