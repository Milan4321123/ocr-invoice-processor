# 🚀 Folder Watcher & Manual OCR Implementation Plan

## 🎉 **PHASE 1 STATUS: COMPLETE ✅** 
**Completed:** June 22, 2025  
**See:** `PHASE_1_COMPLETION_SUMMARY.md` for detailed results

## 📋 **OVERVIEW**
Transform the current system from automatic OCR during upload to:
1. **File Upload Only** (drag & drop + folder watcher)
2. **Manual OCR Processing** (dashboard button click)
3. **Shared Upload Logic** (common service for both methods)

---

## 🎯 **TARGET ARCHITECTURE**

### Current Flow:
```
[Drag & Drop] → Upload → AUTO OCR → Database → Dashboard
```

### Target Flow:
```
[Drag & Drop] → Upload → Database (OCR: pending) → Dashboard → [Extract OCR Button] → OCR Processing
[Folder Watcher] → Upload → Database (OCR: pending) → Dashboard → [Extract OCR Button] → OCR Processing
```

---

## 📝 **PHASE-BY-PHASE EXECUTION PLAN**

### 🟢 **PHASE 1: Common Upload Service** 
**Goal**: Create shared upload logic without OCR processing
**Duration**: ~30 minutes

#### Files to Create/Modify:
- ✅ `/backend/services/file_upload_service.py` (NEW)
- ✅ `/backend/api/routes/upload.py` (MODIFY - add service integration)

#### Tasks:
1. **Create FileUploadService class**
   - File sanitization & validation
   - Storage operations (Supabase + mock)
   - Database record creation WITHOUT OCR
   - Configurable filename pattern enforcement

2. **Modify upload route**
   - Add feature flag: `USE_COMMON_UPLOAD_SERVICE`
   - Maintain backward compatibility
   - Use new service when enabled

3. **Test Phase 1**
   - Verify file uploads work
   - Confirm OCR status = "pending"
   - No breaking changes

---

### 🟡 **PHASE 2: Manual OCR Processing**
**Goal**: Add manual OCR extraction via dashboard button
**Duration**: ~45 minutes

#### Files to Create/Modify:
- ✅ `/backend/api/routes/invoices.py` (ADD new endpoint)
- ✅ `/frontend/src/components/InvoiceEditorDashboard.tsx` (ADD OCR button)

#### Tasks:
1. **Create manual OCR endpoint**
   - `POST /invoices/{id}/process-ocr`
   - Extract OCR for specific invoice
   - Update database with results

2. **Add dashboard OCR button**
   - Show "Extract OCR" for pending invoices
   - Show "Re-process OCR" for failed invoices
   - Loading state during processing

3. **Test Phase 2**
   - Upload file (OCR: pending)
   - Click "Extract OCR" button
   - Verify OCR data appears

---

### 🔵 **PHASE 3: Folder Watcher Service**
**Goal**: Implement automatic folder monitoring
**Duration**: ~60 minutes

#### Files to Create/Modify:
- ✅ `/backend/services/folder_watcher.py` (NEW)
- ✅ `/backend/api/routes/folder_watcher.py` (NEW)
- ✅ `/backend/main.py` (ADD folder watcher integration)

#### Tasks:
1. **Create FolderWatcher class**
   - Monitor specified directories
   - Process new PDF files
   - Use common upload service
   - Configurable patterns & rules

2. **Create management API**
   - Start/stop watcher
   - Add/remove watched folders
   - Get watcher status
   - Configuration management

3. **Test Phase 3**
   - Configure folder to watch
   - Drop PDF file in folder
   - Verify auto-upload (OCR: pending)
   - Manual OCR from dashboard

---

### 🟣 **PHASE 4: Frontend Integration**
**Goal**: Complete dashboard with folder watcher controls
**Duration**: ~30 minutes

#### Files to Create/Modify:
- ✅ `/frontend/src/app/folder-watcher/page.tsx` (NEW)
- ✅ `/frontend/src/components/FolderWatcherDashboard.tsx` (NEW)

#### Tasks:
1. **Folder Watcher Dashboard**
   - Start/stop watcher controls
   - Add/remove folders
   - View watcher status
   - Configuration interface

2. **Enhanced Invoice Dashboard**
   - OCR processing buttons
   - Status indicators
   - Bulk OCR processing

3. **Test Phase 4**
   - Complete end-to-end workflow
   - User interface validation

---

## 🔧 **TECHNICAL SPECIFICATIONS**

### Environment Variables:
```bash
# Upload behavior control
USE_COMMON_UPLOAD_SERVICE=true
ENABLE_FOLDER_WATCHER=true
AUTO_START_FOLDER_WATCHER=false

# Folder watcher settings
FOLDER_WATCHER_INTERVAL=5
FOLDER_WATCHER_MAX_FILES_PER_SCAN=10
```

### Database Schema Changes:
```sql
-- Add folder watcher configuration table
CREATE TABLE folder_watch_configs (
    id UUID PRIMARY KEY,
    folder_path TEXT NOT NULL,
    pattern TEXT DEFAULT '*.pdf',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Modify invoices table (if needed)
ALTER TABLE invoices ADD COLUMN source TEXT DEFAULT 'drag_drop'; -- 'drag_drop' | 'folder_watcher'
```

### API Endpoints:
```
# Manual OCR
POST /invoices/{id}/process-ocr

# Folder Watcher Management
GET /api/folder-watcher/status
POST /api/folder-watcher/start
POST /api/folder-watcher/stop
GET /api/folder-watcher/folders
POST /api/folder-watcher/folders
DELETE /api/folder-watcher/folders/{id}
```

---

## ✅ **SUCCESS CRITERIA**

### Phase 1:
- [ ] File uploads work with common service
- [ ] OCR status = "pending" in database
- [ ] No breaking changes to existing functionality

### Phase 2:
- [ ] Manual OCR button appears in dashboard
- [ ] OCR processing works on button click
- [ ] OCR data updates in real-time

### Phase 3:
- [ ] Folder watcher monitors directories
- [ ] New files auto-upload (OCR: pending)
- [ ] Watcher can be started/stopped via API

### Phase 4:
- [ ] Complete UI for folder watcher management
- [ ] End-to-end workflow functional
- [ ] User-friendly interface

---

## 🚦 **IMPLEMENTATION STRATEGY**

### Development Approach:
1. **Incremental Implementation** - Each phase builds on the previous
2. **Backward Compatibility** - Existing functionality remains intact
3. **Feature Flags** - Enable/disable new features independently
4. **Thorough Testing** - Validate each phase before proceeding

### Risk Mitigation:
- Keep original upload logic as fallback
- Use environment variables for easy rollback
- Test each phase independently
- Maintain database compatibility

---

## 🎯 **READY TO START?**

**Recommended Starting Point**: Phase 1 (Common Upload Service)

This creates the foundation for both folder watcher and manual OCR while ensuring no disruption to current functionality.

Would you like me to proceed with Phase 1 implementation?
