# 🚀 Complete Company Setup Guide for OCR Invoice Processor

## Overview
This guide will help you set up the complete OCR Invoice Processor system for your company, including GitHub, Supabase database, SendGrid email, and Azure deployment.

---

## 1. 📁 GitHub Repository Setup

### Create Company Repository
1. **Ask your manager/IT** for access to company GitHub organization
2. **Create new repository**: `ocr-invoice-processor`
3. **Push your code**:
   ```bash
   git remote set-url origin https://github.com/COMPANY/ocr-invoice-processor.git
   git push -u origin main
   ```

### Repository Structure
```
ocr-invoice-processor/
├── frontend/          # Next.js React app
├── backend/          # FastAPI Python backend
├── database/         # Migration scripts
├── .env.example      # Environment template
├── README.md         # Setup instructions
└── COMPLETE_SUPABASE_SETUP.sql  # Database schema
```

---

## 2. 🗄️ Supabase Database Setup

### A. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) with **company email**
2. Click **New Project**
3. Choose organization: **Your Company**
4. Project name: `ocr-invoice-processor`
5. Database password: **Save this securely!**
6. Region: Choose closest to your location

### B. Run Database Setup
1. In Supabase dashboard, go to **SQL Editor**
2. Copy entire contents of `COMPLETE_SUPABASE_SETUP.sql`
3. Paste and click **Run**
4. ✅ All tables and data should be created

### C. Create Storage Buckets
1. Go to **Storage** in Supabase dashboard
2. Click **New Bucket**
3. Create these buckets:
   - **Name**: `invoices` | **Public**: ✅ | **Description**: Manual uploads
   - **Name**: `folderwatcher` | **Public**: ✅ | **Description**: Folder watcher uploads

### D. Get Supabase Credentials
Go to **Project Settings > API** and save:
- **Project URL**: `https://xxx.supabase.co`
- **Anon Key**: `eyJhbGc...` (for frontend)
- **Service Role Key**: `eyJhbGc...` (for backend, keep secret!)

---

## 3. 📧 SendGrid Email Setup

### A. Create SendGrid Account
1. Go to [sendgrid.com](https://sendgrid.com)
2. Sign up with **company email**
3. Complete verification process

### B. Create API Key
1. Go to **Settings > API Keys**
2. Click **Create API Key**
3. Name: `OCR Invoice Processor`
4. Permissions: **Full Access** (or **Mail Send** minimum)
5. **Save the API key securely!**

### C. Verify Sender Domain (Optional but Recommended)
1. Go to **Settings > Sender Authentication**
2. **Authenticate Your Domain**
3. Follow DNS setup instructions

---

## 4. ⚙️ Environment Configuration

### A. Backend Environment (.env)
Create `backend/.env`:
```env
# Supabase Configuration
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@yourcompany.com

# Security
JWT_SECRET=your-super-secure-jwt-secret-here

# Application
ENVIRONMENT=production
CORS_ORIGINS=["http://localhost:3000","https://yourcompany-ocr.azurewebsites.net"]
```

### B. Frontend Environment (.env.local)
Create `frontend/.env.local`:
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 5. 🧪 Local Testing

### A. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### B. Start Services
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### C. Test Application
1. Open http://localhost:3000
2. Login with: `admin` / `admin123`
3. Upload a test invoice
4. Verify data extraction and workflow

---

## 6. ☁️ Azure Deployment

### A. Azure App Service (Backend)
1. **Create Azure App Service**:
   - Runtime: Python 3.11
   - Operating System: Linux
   - Region: Same as your users

2. **Configure Environment Variables** in Azure portal:
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   JWT_SECRET=your-jwt-secret
   ```

3. **Deploy Code**:
   ```bash
   # Using Azure CLI
   az webapp up --name your-company-ocr-backend --resource-group your-rg
   ```

### B. Azure Static Web Apps (Frontend)
1. **Create Static Web App** connected to your GitHub repo
2. **Build Configuration**:
   - App location: `/frontend`
   - Output location: `out` (for Next.js export)

3. **Environment Variables**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
   NEXT_PUBLIC_API_URL=https://your-backend.azurewebsites.net
   ```

---

## 7. 👥 Team Access & Testing

### A. Share Access
- **GitHub Repository**: Add team members as collaborators
- **Supabase Project**: Invite team to organization
- **Azure Resources**: Add team to resource group

### B. Testing Guide for Team
Create this guide for your team:

```markdown
# OCR Invoice Processor - Testing Guide

## Access
- **Live App**: https://your-company-ocr.azurewebsites.net
- **Test Login**: admin / admin123

## Test Scenarios
1. **Upload Invoice**: Try PDF, JPG, PNG files
2. **Data Extraction**: Verify extracted fields are accurate
3. **Edit Invoice**: Test form editing and validation
4. **Approval Workflow**: Send to Bauleiter, test approval emails
5. **Skonto Features**: Test discount reminders and tracking

## Report Issues
- **GitHub Issues**: https://github.com/COMPANY/ocr-invoice-processor/issues
- **Email**: your.email@company.com
```

---

## 8. 📊 Monitoring & Maintenance

### A. Application Monitoring
- **Azure Application Insights**: Monitor performance and errors
- **Supabase Dashboard**: Monitor database performance
- **SendGrid Dashboard**: Track email delivery

### B. Regular Tasks
- **Weekly**: Check error logs and user feedback
- **Monthly**: Review storage usage and costs
- **Quarterly**: Update dependencies and security patches

---

## 9. 🔒 Security Checklist

- ✅ **Environment Variables**: Never commit secrets to Git
- ✅ **Database RLS**: Row Level Security enabled
- ✅ **HTTPS Only**: All endpoints use SSL
- ✅ **JWT Tokens**: Secure token generation and validation
- ✅ **Email Links**: Time-limited approval tokens
- ✅ **File Upload**: Size and type restrictions

---

## 10. 🚀 Go-Live Checklist

### Before Company Demo:
- [ ] Database schema created and tested
- [ ] Sample data inserted
- [ ] Email sending working
- [ ] File upload/download working
- [ ] All major workflows tested
- [ ] Team access configured
- [ ] Documentation complete

### For Production:
- [ ] Azure deployment working
- [ ] Custom domain configured
- [ ] SSL certificates installed
- [ ] Monitoring setup
- [ ] Backup strategy defined
- [ ] Support procedures documented

---

## 📞 Need Help?

If you run into any issues during setup:

1. **Check the error logs** in Azure/Supabase dashboards
2. **Review environment variables** - most issues are config related
3. **Test locally first** before deploying to cloud
4. **Ask team members** or IT for company-specific guidance

---

**🎉 You're ready to demonstrate the OCR Invoice Processor to your company!**
