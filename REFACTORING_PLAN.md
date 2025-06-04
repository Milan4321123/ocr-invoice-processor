# Main.py Refactoring Plan

## Current Issue
- `main.py` has 1902 lines of code
- Too large for optimal LLM-friendliness
- Single file contains all API logic, models, utilities, and business logic

## Proposed File Structure

### 1. Keep `main.py` as Application Entry Point (~50-100 lines)
```python
# main.py - FastAPI app initialization and route registration only
from fastapi import FastAPI
from api.routes import health, upload, invoices, debug
from core.config import settings
from core.middleware import setup_middleware

app = FastAPI(title="Invoice OCR API", version="0.1.0")
setup_middleware(app)

# Register route modules
app.include_router(health.router, tags=["health"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
app.include_router(debug.router, prefix="/debug", tags=["debug"])
```

### 2. Core Application Structure (~300-400 lines total)
```
backend/
├── main.py                    # App entry point (50-100 lines)
├── core/
│   ├── __init__.py
│   ├── config.py             # Configuration and settings (100-150 lines)
│   ├── middleware.py         # Request middleware and logging (50-100 lines)
│   └── dependencies.py       # Shared dependencies (50-100 lines)
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── health.py         # Health check endpoints (50-100 lines)
│       ├── upload.py         # File upload logic (300-400 lines)
│       ├── invoices.py       # Invoice CRUD operations (200-300 lines)
│       └── debug.py          # Debug endpoints (100-150 lines)
├── models/
│   ├── __init__.py
│   ├── database.py           # Database models and schemas (200-300 lines)
│   └── requests.py           # API request/response models (100-150 lines)
├── services/
│   ├── __init__.py
│   ├── file_service.py       # File upload/storage logic (150-200 lines)
│   ├── database_service.py   # Database operations (150-200 lines)
│   └── ocr_service.py        # OCR integration wrapper (100-150 lines)
└── utils/
    ├── __init__.py
    ├── validation.py         # File and data validation (100-150 lines)
    └── helpers.py            # Utility functions (100-150 lines)
```

### 3. Benefits of This Structure

#### LLM-Friendliness (5/5 stars)
- **Small, focused files**: Each file 50-400 lines max
- **Clear separation**: Easy to understand what each file does
- **Context-friendly**: Each file fits comfortably in LLM context window
- **Focused edits**: Can work on specific functionality without loading entire codebase

#### Maintainability
- **Single responsibility**: Each file has one clear purpose
- **Easy navigation**: Developers can quickly find relevant code
- **Reduced conflicts**: Multiple developers can work on different features simultaneously
- **Better testing**: Each module can be unit tested independently

#### Simplicity Preserved
- **No dependency injection**: Keep direct imports and function calls
- **Minimal abstraction**: Each service is a simple module with functions
- **Flat hierarchy**: Only 2-3 levels deep, easy to understand
- **Direct dependencies**: Clear, explicit imports between modules

### 4. Migration Strategy

#### Phase 1: Extract Route Handlers (Day 1)
1. Create `api/routes/` directory
2. Move route functions to appropriate route files
3. Keep all business logic in route handlers (no service layer yet)
4. Update imports in `main.py`

#### Phase 2: Extract Models and Schemas (Day 2)
1. Create `models/` directory
2. Move Pydantic models and database schemas
3. Update imports in route files

#### Phase 3: Extract Core Utilities (Day 3)
1. Create `core/`, `utils/` directories
2. Move configuration, middleware, validation logic
3. Update imports across all files

#### Phase 4: Optional Service Layer (Day 4)
1. Create `services/` directory for complex business logic
2. Move only the most complex operations to services
3. Keep simple operations directly in route handlers

### 5. File Size Guidelines

- **Route files**: 200-400 lines max
- **Service files**: 150-300 lines max  
- **Utility files**: 100-200 lines max
- **Model files**: 100-300 lines max
- **Core files**: 50-150 lines max

### 6. Example Route File Structure

```python
# api/routes/upload.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from services.file_service import process_file_upload
from utils.validation import validate_pdf_file
from models.requests import UploadResponse

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF invoice file"""
    # Validation
    validation_error = validate_pdf_file(file)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)
    
    # Process upload
    try:
        result = await process_file_upload(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
```

## Next Steps

1. **Start with Phase 1**: Extract route handlers to separate files
2. **Test thoroughly**: Ensure each phase works before moving to next
3. **Keep it simple**: Don't over-engineer the new structure
4. **Maintain current patterns**: Keep the same direct, simple approach

This refactoring will transform the codebase from:
- **LLM-friendliness**: 3/5 → 5/5 stars
- **Maintainability**: 3/5 → 5/5 stars
- **While preserving**: Simple architecture and minimal over-engineering
