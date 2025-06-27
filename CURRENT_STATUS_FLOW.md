# Current Status Tracking Flow Analysis

## Actual System Behavior vs Expected Behavior

### Current Database State Analysis

Based on test results, here's what's actually happening in the system:

## 1. Invoice Upload Flow

### Expected Flow:
```
User uploads PDF → Status: "pending" → OCR Processing → Status: "uploaded"
```

### Actual Flow:
```
User uploads PDF → Status: "completed" → Review Status: null
```

**Analysis**: Invoices are being created with `status: "completed"` immediately, skipping the initial stages.

## 2. Invoice Edit Flow

### Expected Flow:
```
Status: "uploaded/pending" + Edit Action → Status: "edited" + Review Status: "under_review"
```

### Actual Flow:
```
Status: "completed" + Edit Action → Status: "completed" + Review Status: null
                                   (NO CHANGE)
```

**Analysis**: The edit endpoint is not updating status fields despite having the correct code.

## 3. Invoice Complete Flow

### Expected Flow:
```
Status: "edited" + Complete Action → Status: "completed" + Review Status: "completed_review"
```

### Actual Flow:
```
Status: ??? + Complete Action → Status: "completed" + Review Status: "completed_review"
```

**Analysis**: Complete flow may work, but input conditions are never met due to edit flow failure.

## Current Workflow Stages in Reality

### Stage Distribution (Based on Database Query):
```sql
-- What we expect to see:
-- nicht begonnen: status='pending'/'uploaded', review_status='pending'/null
-- in Bearbeitung: status='edited', review_status='under_review'  
-- abgeschlossen: status='completed', review_status='completed_review'

-- What we actually see:
-- Most invoices: status='completed', review_status=null
-- Few invoices: status='uploaded', review_status=null
```

## Detailed Code Path Analysis

### 1. Editor Update Endpoint Path

**File**: `backend/api/routes/invoices.py`
**Endpoint**: `PUT /invoices/{invoice_id}/editor`

**Code Execution Path**:
```python
1. Receive request with invoice fields
2. Build update_data dictionary:
   {
     "rechnungsempfaenger": "...",
     "status": "edited",           # ← This should be set
     "review_status": "under_review", # ← This should be set
     "updated_at": "now()"
   }
3. Filter out None values:
   update_data = {k: v for k, v in update_data.items() if v is not None}
4. Execute Supabase update:
   db_service.client.table("invoices_clean").update(update_data).eq("id", invoice_id)
5. Return success
```

**Problem Points**:
- ✅ Status values are hardcoded strings (not None) - should pass filter
- ❓ Supabase update execution - unclear if actually executing
- ❓ Database constraints - might be rejecting update
- ❓ Response validation - might be returning false positive

### 2. Database Update Mechanism

**Current Implementation**:
```python
# Using Supabase client
response = db_service.client.table("invoices_clean").update(update_data).eq("id", invoice_id).execute()

if not response.data:
    raise HTTPException(status_code=404, detail="Invoice not found or update failed")
```

**Potential Issues**:
- **Row Level Security (RLS)**: May block status field updates
- **Column Permissions**: Status columns might be protected
- **Response Interpretation**: `response.data` validation might be incorrect
- **Silent Failures**: Database errors not being caught

### 3. Alternative Update Path (Email Workflow)

**File**: `backend/api/routes/email_workflow.py`
**Functions**: `_update_invoice_status()`, `_update_invoice_review_status()`

**Code Path**:
```python
async def _update_invoice_status(invoice_id: str, status: str):
    query = """
    UPDATE invoices_clean 
    SET status = %s, updated_at = NOW()
    WHERE id = %s
    """
    await db_service.execute_query(query, (status, invoice_id))
```

**Differences**:
- Uses raw SQL instead of Supabase client
- Different error handling mechanism
- Separate functions for status vs review_status

## Database Schema vs Application Logic

### Schema Constraints:
```sql
-- Status field constraint
CHECK (status::text = ANY(ARRAY[
  'pending', 'uploaded', 'edited', 'pending_email', 
  'edit_completed', 'in_review_by_bauleiter', 
  'approved_by_bauleiter', 'rejected_by_bauleiter', 
  'completed', 'error'
]))

-- Review status constraint  
CHECK (review_status = ANY(ARRAY[
  'pending', 'under_review', 'completed_review', 'needs_attention'
]))
```

### Application Status Values:
```python
# In invoices.py
"status": "edited",
"review_status": "under_review",

# In email_workflow.py  
await _update_invoice_status(request.invoice_id, 'uploaded')
await _update_invoice_review_status(request.invoice_id, 'under_review')
```

**Analysis**: ✅ All values match schema constraints.

## Frontend Dashboard Logic

### Status Display Functions:

```typescript
const getWorkflowStatusLabel = (invoice: CleanInvoice): string => {
  // Stage 1: nicht begonnen
  if ((invoice.status === 'uploaded' || invoice.status === 'pending') && 
      (!invoice.review_status || invoice.review_status === 'pending')) {
    return 'nicht begonnen';
  }
  
  // Stage 2: in Bearbeitung  
  if (invoice.status === 'edited' && invoice.review_status === 'under_review') {
    return 'in Bearbeitung';
  }
  
  // Stage 3: abgeschlossen
  if (invoice.status === 'completed' && invoice.review_status === 'completed_review') {
    return 'abgeschlossen';
  }
  
  return `${invoice.status} (${invoice.review_status || 'no review'})`;
};
```

**Analysis**: 
- ✅ Logic correctly maps expected status combinations
- ❌ Most invoices fall through to default case: `"completed (no review)"`
- This confirms that invoices have `status: "completed"` but `review_status: null`

## Root Cause Hypotheses

### Hypothesis 1: Supabase Client Issue
**Theory**: The Supabase client update is not actually executing or failing silently.

**Evidence**:
- No debug logs appearing despite being added
- Status not changing despite correct code logic
- Similar pattern across multiple tests

**Test**: Switch to raw SQL queries like email_workflow.py uses.

### Hypothesis 2: Database Permissions Issue  
**Theory**: Row Level Security or column permissions prevent status updates.

**Evidence**:
- Other fields (invoice data) update successfully
- Only status/review_status fields not updating
- Different user/role permissions for different columns

**Test**: Check RLS policies and column permissions in Supabase dashboard.

### Hypothesis 3: Transaction/Concurrency Issue
**Theory**: Status updates are being overwritten by concurrent operations.

**Evidence**:
- System has multiple update paths
- File uploads might reset status
- Race conditions between different services

**Test**: Add explicit transaction handling and locking.

### Hypothesis 4: Server Code Not Updated
**Theory**: The running server doesn't have the latest code changes.

**Evidence**:
- Debug logs not appearing
- Status logic looks correct but not working
- Recent code changes may not be deployed

**Test**: Full server restart and verification of running code.

## Immediate Investigation Plan

### Step 1: Verify Server State
```bash
# Restart backend server completely
cd backend && python main.py

# Verify debug logs appear in output
```

### Step 2: Test Raw SQL Approach
```python
# Replace Supabase client update with raw SQL query
# Similar to email_workflow.py approach
```

### Step 3: Check Database Permissions
```sql
# In Supabase dashboard, verify:
# 1. RLS policies on invoices_clean table
# 2. Column-level permissions
# 3. Role assignments
```

### Step 4: Add Comprehensive Logging
```python
# Add logging at every step of update process
# Verify data reaches database layer
# Check response validation logic
```
