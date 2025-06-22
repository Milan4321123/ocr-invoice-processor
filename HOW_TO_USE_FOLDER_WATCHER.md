# 🚀 **HOW TO USE THE FOLDER WATCHER - COMPLETE GUIDE**

## **🎯 Quick Start**

### **1. Start the Backend Server**
```bash
cd /Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend
python main.py
```

### **2. Configure a Folder to Watch**
```bash
# Add a folder to monitor
curl -X POST http://localhost:8001/api/folder-watcher/folders \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/Users/yourusername/Documents/invoices-inbox",
    "pattern": "*.pdf",
    "recursive": false,
    "enabled": true
  }'
```

### **3. Start Monitoring**
```bash
# Start the folder watcher service
curl -X POST http://localhost:8001/api/folder-watcher/start
```

### **4. Drop Files and Watch Magic Happen!**
```bash
# Copy any PDF file to the watched folder
cp /path/to/your/invoice.pdf /Users/yourusername/Documents/invoices-inbox/

# The file will be automatically:
# ✅ Detected within 1-2 seconds
# ✅ Uploaded to the system  
# ✅ Added to the invoice database
# ✅ Available for OCR processing
```

## **📊 Monitor Progress**

### **Check Status**
```bash
curl -s http://localhost:8001/api/folder-watcher/status | jq .
```

### **View Statistics**
```bash
curl -s http://localhost:8001/api/folder-watcher/statistics | jq .
```

### **See Your Invoices**
```bash
curl -s http://localhost:8001/invoices | jq '.invoices[0:3]'
```

## **🎮 Frontend Dashboard**

### **Access the UI**
1. Start frontend: `cd frontend && npm run dev`
2. Open: `http://localhost:3000/folder-watcher`
3. **Manage folders visually with the beautiful UI!**

### **Dashboard Features**
- ✅ **Start/Stop** monitoring with one click
- ✅ **Add/Remove** folders with a simple form
- ✅ **Real-time statistics** and progress monitoring
- ✅ **Enable/Disable** individual folders
- ✅ **Live status** indicators and health checks

## **🏭 Production Use Cases**

### **Email Integration**
```bash
# Set up email to auto-save attachments
mkdir -p /company/invoices/email-inbox
# Configure folder watcher to monitor this directory
# Email system saves PDF attachments here
# Invoices automatically processed!
```

### **Scanner Integration**
```bash
# Configure scanner software to save to:
mkdir -p /company/invoices/scanner-inbox
# Scanned documents automatically uploaded!
```

### **Network Drive Monitoring**
```bash
# Monitor shared network folders
/shared/accounting/invoices-to-process/
# Team members drop files, automatically processed!
```

### **Dropbox/Google Drive Integration**
```bash
# Monitor cloud sync folders
/Users/username/Dropbox/Company/Invoices/
# Files synced from cloud automatically processed!
```

## **⚙️ Advanced Configuration**

### **Multiple Folders**
```bash
# Monitor multiple directories
curl -X POST .../folders -d '{"folder_path": "/invoices/urgent", "pattern": "*.pdf"}'
curl -X POST .../folders -d '{"folder_path": "/invoices/regular", "pattern": "*.pdf"}'
curl -X POST .../folders -d '{"folder_path": "/receipts", "pattern": "receipt_*.pdf"}'
```

### **Custom File Patterns**
```bash
# Only process files matching specific patterns
{"pattern": "invoice_*.pdf"}     # Only files starting with "invoice_"
{"pattern": "*_2025.pdf"}        # Only 2025 files
{"pattern": "*.PDF"}             # Uppercase extension
```

### **Recursive Monitoring**
```bash
# Monitor subdirectories too
{"recursive": true}
# Watches: /invoices/, /invoices/2025/, /invoices/clients/, etc.
```

## **🔧 API Reference**

### **Service Management**
- `GET /api/folder-watcher/status` - Service status
- `POST /api/folder-watcher/start` - Start monitoring
- `POST /api/folder-watcher/stop` - Stop monitoring
- `GET /api/folder-watcher/health` - Health check

### **Folder Management**  
- `GET /api/folder-watcher/folders` - List folders
- `POST /api/folder-watcher/folders` - Add folder
- `DELETE /api/folder-watcher/folders/{id}` - Remove folder
- `POST /api/folder-watcher/folders/{id}/enable` - Enable folder
- `POST /api/folder-watcher/folders/{id}/disable` - Disable folder

### **Monitoring**
- `GET /api/folder-watcher/statistics` - Detailed stats
- `POST /api/folder-watcher/process-pending` - Process queued files

## **🎉 SUCCESS! Your Folder Watcher is Ready!**

The folder watcher system is **fully functional** and ready for production use:

- ✅ **Real-time monitoring** of any directory
- ✅ **Automatic file processing** within seconds
- ✅ **Beautiful web interface** for management
- ✅ **Comprehensive API** for automation
- ✅ **Production-ready** with error handling
- ✅ **Scalable** to multiple folders and patterns

**Just drop PDF files into watched folders and they'll be automatically processed!** 🚀
