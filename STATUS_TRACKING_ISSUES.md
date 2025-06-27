# Current Status Tracking Issues

## Problem Summary
The 3-stage invoice workflow status transitions are not working correctly. Invoices are not properly transitioning between the three workflow stages when edited or completed.

## Identified Issues

### 1. **Status Not Updating on Edit** ⚠️ CRITICAL
**Problem**: When editing an invoice via `PUT /invoices/{id}/editor`, the status remains at its current value instead of changing to `"edited"`.

**Expected Behavior**:
- Status should change from `"uploaded"/"pending"/"completed"` → `"edited"`
- Review_status should change to `"under_review"`

**Current Behavior**:
- Status remains unchanged (e.g., stays `"completed"`)
- Review_status remains `null` or unchanged

**Evidence**:
```bash
# Test shows:
# Before edit: {"status": "completed", "review_status": null}
# After edit:  {"status": "completed", "review_status": null}
# Expected:    {"status": "edited", "review_status": "under_review"}
```

### 2. **Inconsistent Database Update Methods** ⚠️ HIGH
**Problem**: Different routes use different methods to update the database:
- `invoices.py` uses Supabase client: `db_service.client.table("invoices_clean").update()`
- `email_workflow.py` uses raw SQL: `db_service.execute_query()`

**Potential Issues**:
- Different error handling
- Different transaction handling
- Inconsistent field validation

### 3. **Missing Error Handling** ⚠️ MEDIUM
**Problem**: Status updates may fail silently without proper error reporting.

**Current Code Issues**:
- Supabase response validation insufficient
- No rollback mechanism if partial updates fail
- Debug logging not showing in production

### 4. **Frontend-Backend Status Mapping** ⚠️ MEDIUM
**Problem**: Frontend dashboard logic may not correctly interpret all status combinations.

**Potential Issues**:
- Edge cases with `null` review_status
- Status combinations not covered in UI logic
- Stats calculation inconsistencies

### 5. **Database Constraint Violations** ⚠️ LOW
**Problem**: Hardcoded status values in code may not match database constraints.

**Risk Factors**:
- Typos in status strings
- Case sensitivity issues
- Missing validation before database insert

## Root Cause Analysis

### Issue #1 Deep Dive: Status Not Updating

**Code Location**: `backend/api/routes/invoices.py:326-327`
```python
# Set status to "edited" when changes are made (2nd stage: in Bearbeitung)
"status": "edited",
"review_status": "under_review",
```

**Possible Causes**:

1. **Supabase Update Filtering**:
   ```python
   # This line might be removing status fields incorrectly:
   update_data = {k: v for k, v in update_data.items() if v is not None}
   ```
   - Status values are strings, not None, so should be included

2. **Supabase Response Handling**:
   ```python
   if not response.data:
       raise HTTPException(status_code=404, detail="Invoice not found or update failed")
   ```
   - May not properly validate if update actually occurred

3. **Database Permissions**:
   - RLS (Row Level Security) policies might prevent status updates
   - User permissions might not allow status field modifications

4. **Transaction Issues**:
   - Update might be rolled back due to other field validation errors
   - Concurrent updates might override status changes

## Debug Evidence

### Test Results
```bash
# From test_3_stage_workflow_corrected.py output:
=== Testing Status Transition Workflow ===

Before editing:
- ID: f1e5339a-c67c-4a5b-996f-47d2797e0dc9
- Status: completed
- Review Status: None

After editing:
- Status: completed  # ❌ Should be "edited"
- Review Status: None  # ❌ Should be "under_review"
```

### Missing Debug Output
- No debug logs appear in server output
- Suggests either:
  - Logging not configured properly
  - Server not running updated code
  - Update path not being executed

## Impact Assessment

### Business Impact
- **High**: 3-stage workflow completely non-functional
- Users cannot track invoice progress correctly
- Dashboard statistics are incorrect
- Email notifications may trigger incorrectly

### Technical Impact
- **Medium**: System continues to function for basic operations
- Data integrity maintained (no corruption)
- Performance not affected

### User Experience Impact
- **High**: Confusing workflow status display
- Inability to distinguish between processing stages
- Incorrect progress indicators

## Dependencies Affected

### Frontend Components
- `CleanInvoiceDashboard.tsx` - Status display incorrect
- Dashboard statistics - Wrong counts per stage
- Progress indicators - Not updating

### Backend Services
- Email workflow - May trigger at wrong times
- Audit logging - Status history incomplete
- Reporting - Workflow metrics incorrect

### Database State
- Status fields not reflecting actual workflow state
- Audit trail incomplete for status changes
- Query performance unaffected (indexes still work)

## Testing Gaps

### Current Test Coverage
- ✅ Status transition test exists (`test_3_stage_workflow_corrected.py`)
- ✅ API endpoint tests functional
- ❌ Missing unit tests for status update functions
- ❌ Missing integration tests for workflow combinations
- ❌ Missing frontend UI status display tests

### Required Test Scenarios
1. Status transitions for each workflow stage
2. Concurrent status updates
3. Database constraint validation
4. Error handling and rollback
5. Frontend status display accuracy
6. Email notification triggers
