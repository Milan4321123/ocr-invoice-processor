# Code Audit Plan - Unused Code Cleanup

## Overview
This document outlines a systematic approach to identify and remove unused code from the OCR Invoice Processor codebase to ensure maintainability and eliminate confusion.

## Audit Strategy

### Phase 1: Backend API Endpoints Analysis
**Goal**: Identify unused or redundant API endpoints

#### 1.1 Route Files Audit
- [ ] `backend/api/routes/invoices.py` - Core invoice operations
- [ ] `backend/api/routes/upload.py` - File upload handling
- [ ] `backend/api/routes/email_workflow.py` - Email notifications
- [ ] `backend/api/routes/folder_watcher.py` - Folder monitoring
- [ ] `backend/api/routes/dropdowns.py` - Dropdown data
- [ ] `backend/api/routes/approval.py` - Approval workflow
- [ ] `backend/api/routes/approval_workflow.py` - Additional approval logic
- [ ] `backend/api/routes/reports.py` - Report generation
- [ ] `backend/api/routes/health.py` - System health checks

#### 1.2 Endpoint Usage Analysis
**Method**: Check frontend calls and cross-reference with backend endpoints
```bash
# Find all API calls in frontend
grep -r "fetch\|axios\|/api/" frontend/src/
grep -r "localhost:8000" frontend/src/
```

#### 1.3 Duplicate Endpoint Detection
**Look for**:
- Multiple endpoints doing the same thing
- Deprecated endpoint versions
- Test-only endpoints in production code

### Phase 2: Frontend Component Analysis
**Goal**: Identify unused React components and pages

#### 2.1 Component Files Audit
- [ ] `frontend/src/components/` - All React components
- [ ] `frontend/src/app/` - Next.js pages and layouts
- [ ] `frontend/src/services/` - Frontend service utilities

#### 2.2 Component Usage Detection
**Method**: Search for component imports and usage
```bash
# For each component, check if it's imported anywhere
find frontend/src -name "*.tsx" -o -name "*.ts" | xargs grep -l "ComponentName"
```

#### 2.3 Page Route Analysis
**Check**:
- Pages that are not linked from anywhere
- Test pages left in production
- Duplicate functionality across pages

### Phase 3: Service Layer Analysis
**Goal**: Clean up unused service methods and utilities

#### 3.1 Backend Services
- [ ] `backend/services/database.py` - Database operations
- [ ] `backend/services/email_service.py` - Email handling
- [ ] `backend/services/upload_service.py` - File upload logic
- [ ] `backend/services/folder_watcher.py` - File monitoring

#### 3.2 Frontend Services
- [ ] `frontend/src/services/dropdown.ts` - Dropdown utilities
- [ ] `frontend/src/services/sharepoint.ts` - SharePoint integration

#### 3.3 Method Usage Analysis
**For each service method**:
1. Search where it's called
2. Determine if it's still needed
3. Check for duplicate functionality

### Phase 4: Configuration and Utility Files
**Goal**: Remove unused configuration and helper files

#### 4.1 Configuration Files
- [ ] Environment files (.env, .env.example)
- [ ] Docker configurations
- [ ] Next.js and build configurations

#### 4.2 Utility Libraries
- [ ] `frontend/src/lib/` - Utility functions
- [ ] Type definitions in `frontend/src/types/`

### Phase 5: Dead Code Flow Analysis
**Goal**: Identify code paths that are never executed

#### 5.1 Workflow Analysis
**Core Flows to Validate**:
1. **Invoice Upload Flow**
   - Drag & drop upload
   - Folder watcher upload
   - Manual upload

2. **Invoice Processing Flow**
   - OCR processing
   - Data extraction
   - Validation

3. **Status Workflow**
   - 3-stage status transitions
   - Email notifications
   - Approval workflow

4. **Dashboard Flow**
   - Invoice listing
   - Status display
   - Actions (edit, delete, complete)

5. **Editor Flow**
   - PDF viewing
   - Field editing
   - Save/validation

#### 5.2 Integration Points
- [ ] Email service integrations
- [ ] Storage (Supabase) operations
- [ ] Authentication flows
- [ ] Error handling paths

## Audit Tools and Commands

### 1. Find Unused Imports
```bash
# Python unused imports (backend)
pip install unimport
unimport --check backend/

# TypeScript unused exports (frontend)
npx ts-unused-exports frontend/tsconfig.json
```

### 2. Find Unused Functions/Methods
```bash
# Search for function definitions vs usage
grep -r "def function_name" backend/
grep -r "function_name" backend/
```

### 3. Find Unreachable Code
```bash
# Look for code after return statements
grep -A 5 "return" backend/**/*.py | grep -B 5 -A 5 "^\s*[^#]"
```

### 4. Check Frontend Component Usage
```bash
# For each component, check if it's imported
for component in $(find frontend/src/components -name "*.tsx" | xargs basename -s .tsx); do
    echo "Checking $component:"
    grep -r "import.*$component" frontend/src/
done
```

## Cleanup Priorities

### High Priority (Remove Immediately)
1. **Duplicate endpoints** - Multiple ways to do same thing
2. **Test pages in production** - Development/test components
3. **Unused API routes** - Endpoints not called by frontend
4. **Dead service methods** - Methods never called

### Medium Priority (Review and Remove)
1. **Unused utility functions** - Helper methods not used
2. **Redundant components** - Similar functionality components
3. **Obsolete configuration** - Old config options

### Low Priority (Document and Keep)
1. **Future-use code** - Planned features
2. **Error handling** - Defensive code that might be needed
3. **Logging and debugging** - Development aids

## Cleanup Execution Plan

### Step 1: Automated Detection
Run all audit tools and generate reports

### Step 2: Manual Review
Review each identified unused code piece:
- Confirm it's truly unused
- Check if it's needed for future features
- Verify no hidden dependencies

### Step 3: Safe Removal
Remove code in stages:
1. Comment out first
2. Test the application
3. Permanently delete if no issues

### Step 4: Documentation Update
Update documentation to reflect removed features

### Step 5: Testing
Run comprehensive tests after cleanup:
- All workflow tests
- Frontend functionality tests
- API endpoint tests

## Expected Outcomes

### Code Quality Improvements
- ✅ Reduced codebase size
- ✅ Clearer code architecture
- ✅ Faster development and debugging
- ✅ Easier maintenance

### Performance Benefits
- ✅ Smaller bundle sizes
- ✅ Faster build times
- ✅ Reduced memory usage

### Developer Experience
- ✅ Less confusion about code paths
- ✅ Clearer component hierarchy
- ✅ Easier code navigation
- ✅ Better code reviews

## Risk Mitigation

### Before Cleanup
1. **Full backup** - Git commit current state
2. **Test suite run** - Ensure all tests pass
3. **Documentation** - Document current functionality

### During Cleanup
1. **Incremental changes** - Small, testable commits
2. **Feature testing** - Test each change immediately
3. **Rollback plan** - Ready to revert if issues

### After Cleanup
1. **Comprehensive testing** - Full system test
2. **Performance monitoring** - Check for any regressions
3. **Team review** - Code review of changes

## Timeline

- **Week 1**: Automated detection and analysis
- **Week 2**: Manual review and categorization
- **Week 3**: Safe removal and testing
- **Week 4**: Documentation and final validation

This systematic approach ensures we maintain code quality while safely removing unnecessary complexity.
