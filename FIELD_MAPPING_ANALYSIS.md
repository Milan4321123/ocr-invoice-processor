# 🔍 **FIELD MAPPING ANALYSIS - COMPLETE SYSTEM OVERVIEW**

## **PROBLEM STATEMENT**
We have inconsistent field naming conventions across different layers of the application, causing silent failures and data mapping issues. The goal is to standardize field names throughout the entire system.

---

## **📊 ACTUAL DATABASE SCHEMA**

Based on the live Supabase database, here are all the invoice table columns:

### **Business Fields (German Names)**
```sql
rechnungsempfaenger      VARCHAR  -- Customer/recipient name
rechnungssteller         VARCHAR  -- Vendor/issuer name  
rechnungsnummer          VARCHAR  -- Invoice number
rechnungsdatum           DATE     -- Invoice date
projekt                  VARCHAR  -- Project name
gewerk                   VARCHAR  -- Trade/work category
brutto_betrag            NUMERIC  -- Gross amount (with tax)
netto_betrag             NUMERIC  -- Net amount (without tax)
due_date                 DATE     -- Due date (English name!)
skonto_datum             DATE     -- Discount date
skonto_prozent           NUMERIC  -- Discount percentage
rechnungsart             VARCHAR  -- Invoice type
kfw_anrechenbar          BOOLEAN  -- KfW eligible
rechnungspruefung_email  VARCHAR  -- Review email
weiter_berechnen_an      VARCHAR  -- Forward billing to
```

### **Technical Fields (English Names)**
```sql
id, file_name, file_path, file_size, mime_type, currency,
customer_address, customer_name, vendor_address, vendor_name,
invoice_number, invoice_date, subtotal, tax_amount, total_amount,
payment_terms, po_number, entities, form_fields, tables, line_items,
filename, url, ocr_*, status, created_at, updated_at, etc.
```

---

## **🎯 CURRENT ENDPOINTS & FIELD MAPPINGS**

### **1. GET /invoices** 
**File:** `backend/api/routes/invoices.py`
**Used by:** Dashboard
**Data Flow:** Database → Database Service → API Response
**Field Mapping:** Uses `database.py` field transformations

```python
# database.py _map_db_to_app() transforms:
'rechnungsempfaenger' → 'customer_name'
'rechnungssteller' → 'vendor_name' 
'rechnungsnummer' → 'invoice_number'
'rechnungsdatum' → 'invoice_date'
'netto_betrag' → 'subtotal'
'brutto_betrag' → 'total_amount'
'projekt' → 'project'  # ⚠️ INCONSISTENCY!
'gewerk' → 'trade'
```

**Result:** Dashboard receives English field names like `project`, `total_amount`, etc.

---

### **2. GET /invoices/{id}/editor**
**File:** `backend/api/routes/invoices.py`
**Used by:** Invoice Editor
**Data Flow:** Database → Direct Query → German Field Names
**Field Mapping:** Manual German mapping in endpoint

```python
# Manual field mapping in endpoint:
"rechnungsempfaenger": invoice_data.get("rechnungsempfaenger"),
"rechnungssteller": invoice_data.get("rechnungssteller"),
"projekt": invoice_data.get("projekt"),  # ✅ Direct mapping
"gewerk": invoice_data.get("gewerk"),
"rechnungsbetrag": invoice_data.get("brutto_betrag"),  # ⚠️ MAPPING!
"rechnungseingang": invoice_data.get("rechnungsdatum"), # ⚠️ MAPPING!
"faelligkeit": invoice_data.get("due_date"),           # ⚠️ MAPPING!
```

**Result:** Editor receives German field names like `projekt`, `faelligkeit`, etc.

---

### **3. PUT /invoices/{id}/editor**
**File:** `backend/api/routes/invoices.py`
**Used by:** Invoice Editor Save
**Data Flow:** German Fields → Field Mapping → Database Update
**Field Mapping:** Custom mapping in endpoint

```python
# Field mapping in PUT endpoint:
field_mapping = {
    "faelligkeit": "due_date",             # ✅ German → English
    "rechnungseingang": "rechnungsdatum",   # ✅ German → German  
    "rechnungsbetrag": "brutto_betrag",     # ✅ German → German
    "rechnungsempfaenger": "rechnungsempfaenger", # ✅ Direct
    "rechnungssteller": "rechnungssteller",       # ✅ Direct
    "projekt": "projekt",                         # ✅ Direct
    "gewerk": "gewerk",                          # ✅ Direct
    "skonto_datum": "skonto_datum",              # ✅ Direct
    "skonto_prozent": "skonto_prozent",          # ✅ Direct
    "rechnungsart": "rechnungsart",              # ✅ Direct
    "kfw_anrechenbar": "kfw_anrechenbar",        # ✅ Direct
    "rechnungspruefung_email": "rechnungspruefung_email", # ✅ Direct
    "weiter_berechnen_an": "weiter_berechnen_an"         # ✅ Direct
}
```

**Result:** Updates work correctly with proper German → Database mapping

---

### **4. GET /api/reports/invoice-summary**
**File:** `backend/api/routes/reports.py`
**Used by:** Dashboard, Prüfbericht
**Data Flow:** Database → Database Service → English Field Names

```python
# Uses db_service.get_invoices() which applies transformations:
filters['projekt'] = project_filter  # ⚠️ Uses German name in filter
# But response has English names due to database service mapping
```

**Result:** Reports receive English field names but filter uses German names

---

### **5. Frontend Components**
**File:** `frontend/src/components/InvoiceForm.tsx`
**Interface:** `GermanInvoiceFields`

```typescript
export interface GermanInvoiceFields {
  rechnungsempfaenger?: string;
  rechnungssteller?: string;
  projekt?: string;           // ✅ German name
  gewerk?: string;
  rechnungsbetrag?: number;   // ✅ German name  
  rechnungseingang?: string;  // ✅ German name
  faelligkeit?: string;       // ✅ German name
  skonto_datum?: string;
  skonto_prozent?: number;
  rechnungsart?: string;
  kfw_anrechenbar?: boolean;
  rechnungspruefung_email?: string;
  weiter_berechnen_an?: string;
}
```

**Result:** Frontend consistently uses German field names

---

## **🚨 IDENTIFIED INCONSISTENCIES**

### **1. Database Service vs Direct Queries**
- **Database Service** (`database.py`): Transforms `projekt` → `project`
- **Invoice Editor**: Uses direct queries with `projekt` field name
- **Result**: Dashboard shows `project`, Editor uses `projekt`

### **2. Mixed Language Field Names in Database** 
- **German**: `projekt`, `gewerk`, `rechnungsempfaenger`, `skonto_datum`
- **English**: `due_date`, `customer_name`, `vendor_name`, `total_amount`
- **Result**: Confusion about which fields use which language

### **3. Field Name Mapping Inconsistencies**
- **GET Editor**: `brutto_betrag` → `rechnungsbetrag` (amount field)
- **PUT Editor**: `rechnungsbetrag` → `brutto_betrag` (reverse mapping)
- **Dashboard**: `brutto_betrag` → `total_amount` (English name)

### **4. Filter Field Names**
- **Reports**: Uses `filters['projekt']` (German) but returns English field names
- **Database Service**: Expects German field names for filters

---

## **📋 COMMUNICATION PATHWAYS**

```mermaid
graph TD
    A[Frontend German Fields] -->|PUT /invoices/{id}/editor| B[Invoice Editor API]
    B -->|Direct Supabase Query| C[Database German/English Mix]
    
    D[Dashboard] -->|GET /invoices| E[Invoice List API] 
    E -->|db_service.get_invoices| F[Database Service]
    F -->|Field Transformation| G[English Field Names]
    
    H[Reports] -->|GET /api/reports/*| I[Reports API]
    I -->|db_service + German filters| F
    
    C -->|GET /invoices/{id}/editor| J[Editor GET API]
    J -->|Manual German Mapping| A
```

---

## **🎯 PROPOSED SOLUTION**

### **Option 1: All German Names (Recommended)**
- Standardize ALL database columns to German names
- Remove English field transformations from `database.py`
- Update any remaining English field references
- Frontend already uses German names ✅
- Business users prefer German terms ✅

### **Option 2: All English Names**
- Convert all German database columns to English
- Update frontend to use English field names
- Remove German field mappings
- More developer-friendly but less business-friendly

### **Option 3: Consistent Dual Mapping**
- Keep database as-is (mixed languages)
- Ensure ALL endpoints use the same mapping logic
- Route all database access through `database.py` service
- Most complex but preserves existing data

---

## **🔧 REQUIRED CHANGES (Option 1 - All German)**

### **Database Changes**
```sql
-- Rename English columns to German
ALTER TABLE invoices RENAME COLUMN due_date TO faelligkeit;
ALTER TABLE invoices RENAME COLUMN customer_name TO rechnungsempfaenger_name;
ALTER TABLE invoices RENAME COLUMN vendor_name TO rechnungssteller_name;
ALTER TABLE invoices RENAME COLUMN total_amount TO brutto_betrag_backup;
-- etc.
```

### **Code Changes**
1. Remove field transformations from `database.py`
2. Update all API endpoints to use German field names consistently
3. Update any hardcoded English field references
4. Ensure all filters use German field names

---

## **📊 IMPACT ANALYSIS**

| Endpoint | Current State | Required Changes |
|----------|---------------|------------------|
| `GET /invoices` | Uses English names via db service | Remove transformations |
| `GET /invoices/{id}/editor` | Uses German names | ✅ No change needed |
| `PUT /invoices/{id}/editor` | Maps German→DB correctly | ✅ No change needed |
| `GET /api/reports/*` | Mixed German filters + English output | Use German consistently |
| Frontend | Uses German names | ✅ No change needed |
| Database | Mixed German/English columns | Rename English columns |

---

## **✅ NEXT STEPS**

1. **Decision**: Choose naming convention (German recommended)
2. **Database Migration**: Rename columns to chosen convention  
3. **Code Updates**: Remove/update field mappings
4. **Testing**: Verify all endpoints work with new convention
5. **Documentation**: Update API docs with new field names

**Recommendation:** Go with Option 1 (All German) since frontend and business users already expect German field names, and most database columns are already German.
