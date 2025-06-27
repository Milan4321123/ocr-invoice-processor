# Invoice Status Tracking Architecture

## Overview
The OCR Invoice Processor implements a 3-stage workflow system for invoice processing with status tracking across frontend (Next.js/React) and backend (FastAPI) with Supabase as the database.

## System Components

### 1. Database Layer (Supabase)
**Table**: `invoices_clean`

**Key Status Fields**:
- `status` (varchar): Main workflow status
- `review_status` (text): Review-specific status
- `approval_status` (varchar): Approval workflow status

**Status Constraints**:
```sql
-- status field allowed values
CHECK (status::text = ANY(ARRAY[
  'pending'::text,
  'uploaded'::text, 
  'edited'::text,
  'pending_email'::text,
  'edit_completed'::text,
  'in_review_by_bauleiter'::text,
  'approved_by_bauleiter'::text,
  'rejected_by_bauleiter'::text,
  'completed'::text,
  'error'::text
]))

-- review_status field allowed values  
CHECK (review_status = ANY(ARRAY[
  'pending'::text,
  'under_review'::text,
  'completed_review'::text,
  'needs_attention'::text
]))

-- approval_status field allowed values
CHECK (approval_status::text = ANY(ARRAY[
  'pending'::text,
  'approved'::text,
  'rejected'::text
]))
```

### 2. Backend Layer (FastAPI)

**Main Route Files**:
- `backend/api/routes/invoices.py` - Core invoice CRUD operations
- `backend/api/routes/email_workflow.py` - Email notifications and workflow

**Key Endpoints**:
- `PUT /invoices/{id}/editor` - Update invoice data (triggers status change)
- `PUT /invoices/{id}/complete` - Mark invoice as completed
- `POST /email/editor-notification` - Send editor notification

**Status Update Functions**:
- `_update_invoice_status()` - Updates main status field
- `_update_invoice_review_status()` - Updates review_status field

### 3. Frontend Layer (Next.js/React)

**Main Components**:
- `CleanInvoiceDashboard.tsx` - Main dashboard with status display
- Status calculation functions for UI display

**Status Display Logic**:
- `getWorkflowStatusLabel()` - Converts status to German labels
- `getWorkflowStatusColor()` - Color coding for status
- Dashboard stats counting by workflow stage

## 3-Stage Workflow Design

### Stage 1: "nicht begonnen" (Not Started)
**Criteria**: 
- `status = 'pending'` OR `status = 'uploaded'`
- `review_status = 'pending'` OR `review_status = null`

**User Actions**: Upload invoice, initial OCR processing

### Stage 2: "in Bearbeitung" (In Progress) 
**Criteria**:
- `status = 'edited'`
- `review_status = 'under_review'`

**User Actions**: Edit invoice fields, validate data

### Stage 3: "abgeschlossen" (Completed)
**Criteria**:
- `status = 'completed'`
- `review_status = 'completed_review'`

**User Actions**: Final approval, mark as done

## Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Supabase      │
│   Dashboard     │    │   FastAPI       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ GET /invoices         │                       │
         │──────────────────────►│ SELECT * FROM         │
         │                       │ invoices_clean        │
         │                       │──────────────────────►│
         │                       │                       │
         │                       │ ◄──────────────────────│
         │ ◄──────────────────────│ Return invoice data   │
         │                       │                       │
         │ PUT /invoices/{id}/    │                       │
         │ editor                │                       │
         │──────────────────────►│ UPDATE invoices_clean │
         │                       │ SET status='edited',  │
         │                       │ review_status=        │
         │                       │ 'under_review'        │
         │                       │──────────────────────►│
         │                       │                       │
         │ ◄──────────────────────│ ◄──────────────────────│
         │ Success response      │ Update confirmation   │
```

## Status Transition Flow

```
Initial Upload
     │
     ▼
┌─────────────┐
│   pending   │ ──► Stage 1: "nicht begonnen"
│ (uploaded)  │
└─────────────┘
     │ Edit Action
     ▼
┌─────────────┐
│   edited    │ ──► Stage 2: "in Bearbeitung"  
│under_review │
└─────────────┘
     │ Complete Action
     ▼
┌─────────────┐
│ completed   │ ──► Stage 3: "abgeschlossen"
│completed_   │
│  review     │
└─────────────┘
```

## Integration Points

### 1. Supabase Client (Frontend ↔ Database)
- Direct queries for dashboard data
- Real-time updates via Supabase subscriptions

### 2. FastAPI Routes (Frontend ↔ Backend)
- REST API endpoints for invoice operations
- Status updates via HTTP requests

### 3. Database Service (Backend ↔ Database) 
- Both Supabase client and raw SQL queries
- Abstraction layer for database operations

## Configuration Dependencies

### Environment Variables
- `SUPABASE_URL` - Database connection
- `SUPABASE_ANON_KEY` - API access key
- Email service configuration for notifications

### Database Schema Dependencies
- Status field constraints must match application logic
- Foreign key relationships for audit trails
- Indexes for performance on status queries

## Security Considerations

### Access Control
- Row-level security (RLS) policies in Supabase
- API authentication for backend routes
- Editor permissions for status changes

### Audit Trail
- `updated_at` timestamps for all changes
- `reviewed_by` tracking for accountability
- Email logs for notification history
