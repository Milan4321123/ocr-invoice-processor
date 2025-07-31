# 🏢 OCR Invoice Processor - Company Edition

> **Complete invoice processing solution with OCR technology, workflow management, and automated notifications.**

## 🚀 Quick Start for Company Deployment

### For IT Administrators

**1. One-Command Setup:**
```bash
git clone https://github.com/YOUR-COMPANY/ocr-invoice-processor.git
cd ocr-invoice-processor
./company-setup.sh
```

**2. Start Application:**
```bash
# Quick Start Options
./quick-start.sh        # Simple start
./docker-start.sh       # Full setup with health checks

# Advanced Docker Management
./docker-manager.sh start    # Start with full management
./docker-manager.sh status   # Check health status
./docker-manager.sh logs     # View real-time logs
```

**3. Access Application:**
- **Main App**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

### For End Users

**Windows:**
1. Double-click `quick-start.bat`
2. Wait for startup message
3. Open browser to http://localhost:3000

**Mac/Linux:**
1. Run `./quick-start.sh` in terminal
2. Wait for startup message  
3. Open browser to http://localhost:3000

---

## 📋 What This System Does

### Core Features
- **📄 PDF Invoice Upload** - Drag & drop or browse upload
- **🔍 OCR Processing** - Automatic text extraction from invoices
- **✏️ Invoice Editor** - Review and edit extracted data
- **📊 Dashboard** - View all invoices with filtering and search
- **📧 Email Notifications** - Automated workflow emails
- **💰 Skonto Management** - Early payment discount tracking
- **👥 Multi-user Support** - Role-based access control

### Workflow
1. **Upload** invoice PDF
2. **OCR Processing** extracts data automatically
3. **Review & Edit** extracted information
4. **Complete** invoice processing
5. **Send to Bauleiter** for approval
6. **Track** Skonto opportunities
7. **Automated Reminders** for deadlines

---

## 🛠️ Technical Architecture

```
Frontend (React/Next.js) ←→ Backend (Python/FastAPI) ←→ Database (Supabase)
                              ↕
                         Email Service (SendGrid)
                              ↕
                         OCR Service (Google Cloud)
```

### Technologies Used
- **Frontend**: React, Next.js, Tailwind CSS
- **Backend**: Python, FastAPI, Pydantic
- **Database**: Supabase (PostgreSQL)
- **Email**: SendGrid
- **OCR**: Google Cloud Document AI
- **Deployment**: Docker, Docker Compose

---

## 📁 File Structure

```
ocr-invoice-processor/
├── 🚀 Quick Start Scripts
│   ├── quick-start.sh/.bat    # Simple start
│   ├── quick-stop.sh/.bat     # Simple stop
│   ├── docker-start.sh        # Full setup
│   └── company-setup.sh       # Initial setup
│
├── 🐳 Docker Configuration
│   ├── docker-compose.yml     # Production
│   ├── docker-compose.dev.yml # Development
│   └── Dockerfiles            # Container builds
│
├── ⚙️ Configuration
│   ├── .env                   # Your settings (create from template)
│   └── environment.template   # Unified configuration template
│
├── 📖 Documentation
│   ├── README.md              # This file
│   ├── DOCKER_DEPLOYMENT_GUIDE.md
│   └── COMPANY_SETUP_GUIDE.md
│
├── 🎨 Frontend Application
│   └── frontend/
│
├── 🔧 Backend API
│   └── backend/
│
└── 🗄️ Database Scripts
    └── database/
```

---

## 🔧 Installation & Setup

### Prerequisites
- **Docker Desktop** (required)
- **Git** (required)
- **Company email accounts** for services

### Automated Setup
```bash
# Clone repository
git clone https://github.com/YOUR-COMPANY/ocr-invoice-processor.git
cd ocr-invoice-processor

# Run setup wizard
./company-setup.sh

# Start application
./quick-start.sh
```

### Manual Setup
1. **Copy environment file:**
   ```bash
   cp .env.production .env
   ```

2. **Set up environment configuration:**
   ```bash
   # Copy the unified environment template
   cp environment.template .env
   
   # Edit .env with your credentials
   nano .env
   ```
   - Replace all "your-*" placeholders with actual values
   - Configure Supabase database URL and keys
   - Add SendGrid API key for emails
   - Generate secure JWT secret

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

---

## 🌐 Configuration Services

### 1. Supabase Database
- **Purpose**: Stores all invoice data
- **Setup**: Create project at supabase.com
- **Required**: Project URL and API keys

#### 🏗️ Database Schema Setup

**Option A: Automatic Setup (Recommended)**
The application will automatically set up the database schema when it starts:
1. Configure your `.env` file with Supabase credentials
2. Start the backend: `python backend/main.py`
3. The system will detect missing tables and create them automatically

**Option B: Manual Setup**
If automatic setup fails, manually run the SQL:
1. Go to your Supabase SQL Editor
2. Copy and paste the contents of `COMPLETE_SUPABASE_SETUP.sql`
3. Execute the SQL to create all tables, indexes, and policies

**What Gets Created:**
- `users` table - Authentication and user management
- `invoices_clean` table - Main invoice data storage
- `email_audit_log` table - Email tracking and audit trail
- `approval_tokens` table - Secure approval workflow tokens
- `skonto_tracking` table - Early payment discount tracking
- All necessary indexes, triggers, and security policies

### 2. SendGrid Email
- **Purpose**: Sends workflow notifications
- **Setup**: Create account at sendgrid.com
- **Required**: API key with send permissions

### 3. Google Cloud OCR (Optional)
- **Purpose**: Extracts text from invoice PDFs
- **Setup**: Enable Document AI in Google Cloud
- **Alternative**: Can use mock OCR for testing

---

## 🎯 Usage Guide

### For Invoice Processors
1. **Upload Invoice**: Drag PDF to upload area
2. **Review Data**: Check OCR-extracted information
3. **Edit Fields**: Correct any errors
4. **Complete**: Mark invoice as complete
5. **Send**: Forward to Bauleiter for approval

### For Bauleiter (Managers)
1. **Dashboard**: View pending approvals
2. **Review**: Check invoice details
3. **Approve/Reject**: Make decisions
4. **Skonto**: Monitor early payment opportunities

### For Administrators
1. **Monitor**: Check system health
2. **Manage**: Add users and configure settings
3. **Reports**: View processing statistics
4. **Maintain**: Update dropdown options

---

## � Docker Management

### Smart Docker Manager
The project includes an intelligent Docker management script that simplifies container operations:

**macOS/Linux:**
```bash
./docker-manager.sh [command]
```

**Windows:**
```batch
docker-manager.bat [command]
```

### Available Commands

| Command | Description | Use Case |
|---------|-------------|-----------|
| `start` | Build and start all containers | First-time setup or daily startup |
| `status` | Check health of all services | Verify everything is running |
| `stop` | Stop all containers gracefully | End of day shutdown |
| `restart` | Restart all services | Apply configuration changes |
| `logs` | Show real-time application logs | Debug issues or monitor activity |
| `rebuild` | Clean rebuild all containers | After major code changes |
| `cleanup` | Remove all containers and data | Reset to clean state |
| `open` | Open application in browser | Quick access to UI |

### Example Usage
```bash
# Start the application (recommended)
./docker-manager.sh start

# Check if everything is healthy
./docker-manager.sh status

# View live logs for debugging
./docker-manager.sh logs

# Open the application in your browser
./docker-manager.sh open
```

### Service Health Monitoring
The script automatically checks:
- ✅ **Backend API** (http://localhost:8000) - Invoice processing
- ✅ **Frontend UI** (http://localhost:3000) - User interface
- ✅ **Container Status** - Running/stopped states
- ✅ **Docker Engine** - Available and responding

---

## �🔍 Troubleshooting

### Quick Diagnostics
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f

# Check application health
curl http://localhost:8000/api/health

# Restart everything
docker-compose restart
```

### Common Issues

**❌ "Cannot connect to backend"**
- Check if Docker is running
- Verify ports 3000 and 8000 are available
- Check `.env` file configuration

**❌ "Email not sending"**
- Verify SendGrid API key in `.env`
- Check FROM_EMAIL configuration
- Ensure SendGrid account is verified

**❌ "OCR not working"**
- Enable mock OCR: `USE_MOCK_OCR=true`
- Check Google Cloud credentials
- Verify Document AI is enabled

**❌ "Database connection failed"**
- Check Supabase credentials in `.env`
- Verify database is accessible
- Run database setup script

---

## 🔐 Security & Compliance

### Security Features
- **JWT Authentication** for API access
- **Role-based Access Control** for users
- **Encrypted Environment Variables** for secrets
- **HTTPS Support** for production
- **Input Validation** and sanitization

### Data Protection
- **EU GDPR Compliance** ready
- **Data Encryption** at rest and in transit
- **Audit Logs** for all actions
- **Backup Procedures** for data safety

### Production Considerations
- Change default JWT secret
- Use strong database passwords
- Enable HTTPS with SSL certificates
- Configure firewall rules
- Set up monitoring and alerts

---

## 📊 Monitoring & Analytics

### Health Monitoring
- **Service Health**: http://localhost:8000/api/health
- **Container Status**: `docker-compose ps`
- **Resource Usage**: `docker stats`

### Log Management
- **Application Logs**: `./logs/` directory
- **Container Logs**: `docker-compose logs`
- **Error Tracking**: Built-in error handling

### Performance Metrics
- Invoice processing times
- OCR accuracy rates
- User activity statistics
- System resource usage

---

## 🚀 Deployment Options

### Development
```bash
# Hot reload development
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
# Optimized production build
docker-compose up -d
```

### Cloud Deployment
- **AWS ECS**: Container orchestration
- **Google Cloud Run**: Serverless containers
- **Azure Container Instances**: Managed containers
- **DigitalOcean**: App platform deployment

---

## 📞 Support & Contact

### For Technical Issues
1. **Check Documentation**: This README and guides
2. **Review Logs**: `docker-compose logs -f`
3. **Test Health**: `curl localhost:8000/api/health`
4. **Contact IT**: Your company IT department

### For Business Questions
- **System Administrator**: [Your IT Contact]
- **Business Owner**: [Project Manager]
- **User Training**: [Training Contact]

### Resources
- **Documentation**: All `.md` files in repository
- **API Documentation**: http://localhost:8000/docs
- **Company Repository**: [Your GitHub URL]

---

## 📝 Quick Command Reference

```bash
# Setup & Start
./company-setup.sh     # First-time setup
./quick-start.sh       # Start application
./quick-stop.sh        # Stop application

# Development
docker-compose -f docker-compose.dev.yml up  # Dev mode
docker-compose logs -f                       # View logs
docker-compose restart backend               # Restart service

# Maintenance
docker-compose down -v      # Reset everything
docker-compose pull        # Update images
docker system prune        # Clean up Docker
```

---

## 🏆 Success Criteria

**✅ System is Working When:**
- Frontend loads at http://localhost:3000
- Backend responds at http://localhost:8000/api/health
- File uploads work correctly
- OCR processes invoices (or mock works)
- Emails send successfully
- Database stores data properly

**🎯 Company Benefits:**
- **Faster Processing**: Automated OCR reduces manual entry
- **Better Accuracy**: Digital validation prevents errors
- **Audit Trail**: Complete tracking of all changes
- **Cost Savings**: Skonto tracking maximizes discounts
- **Compliance**: Proper document management
- **Scalability**: Handles growing invoice volumes

---

*This system is designed for company use with enterprise-grade security, scalability, and reliability.*
