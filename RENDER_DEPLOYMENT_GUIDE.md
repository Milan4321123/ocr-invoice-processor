# 🚀 Render Deployment Guide - OCR Invoice Processor

## Overview
This guide helps you deploy your OCR Invoice Processor to Render while keeping your localhost setup intact.

## 🔧 What We've Set Up

### 1. **Environment Separation**
- ✅ **Local Development**: Uses `localhost:3000` and `localhost:8000`
- ✅ **Production**: Uses Render URLs with proper CORS settings
- ✅ **Environment Variables**: Separate configs for local vs production

### 2. **Docker Optimization**
- ✅ **Backend**: Production-ready Python container with health checks
- ✅ **Frontend**: Multi-stage Next.js build with standalone output
- ✅ **Security**: Non-root users, proper dependency management

### 3. **Configuration Updates**
- ✅ **CORS**: Added production URLs to allowed origins
- ✅ **Next.js**: Conditional API proxying (dev only)
- ✅ **Health Checks**: Monitoring endpoints for both services

## 🚀 Quick Deployment

### Step 1: Run the Deployment Script
```bash
cd /Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor
./deploy-to-render.sh
```

This script will:
- Create a `deployy` branch for deployment
- Push your code to GitHub
- Preserve your local development setup

### Step 2: Set Up on Render
1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo: `Milan4321123/ocr-invoice-processor`
4. Select branch: **`deployy`**
5. Render auto-detects `render.yaml`

### Step 3: Configure Environment Variables

#### Backend Service (`ocr-invoice-backend`)
```
SUPABASE_SERVICE_ROLE_KEY = [Your Supabase Service Role Key]
SUPABASE_ANON_KEY = [Your Supabase Anonymous Key]
SENDGRID_API_KEY = [Your SendGrid API Key]
JWT_SECRET = [64-character random string]
```

#### Frontend Service (`ocr-invoice-frontend`)
```
NEXT_PUBLIC_SUPABASE_ANON_KEY = [Same as backend SUPABASE_ANON_KEY]
```

## 🔑 Getting Your Keys

### Supabase Keys
1. Visit: https://supabase.com/dashboard/project/bdtcfypvadryfeabqnlc/settings/api
2. Copy:
   - **anon/public key** → `SUPABASE_ANON_KEY`
   - **service_role/secret key** → `SUPABASE_SERVICE_ROLE_KEY`

### SendGrid API Key
1. Visit: https://app.sendgrid.com/settings/api_keys
2. Create new API key with **Full Access**
3. Copy key → `SENDGRID_API_KEY`

### JWT Secret
Generate a secure random string:
```bash
openssl rand -hex 32
```

## 🌐 Production URLs
- **Frontend**: https://ocr-invoice-frontend.onrender.com
- **Backend**: https://ocr-invoice-backend.onrender.com
- **Health Check**: https://ocr-invoice-backend.onrender.com/api/health

## 🔧 Local Development (Unchanged)
Your localhost setup continues to work exactly as before:
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend  
cd frontend && npm run dev
```

## 📊 Monitoring
- Render provides logs and metrics in the dashboard
- Health checks run every 30 seconds
- First deployment takes 10-15 minutes

## 🆘 Troubleshooting

### Build Failures
- Check Render logs for specific error messages
- Ensure all environment variables are set
- Verify your GitHub repo has the `deployy` branch

### Runtime Issues
- Check health endpoints: `/api/health`
- Review application logs in Render dashboard
- Verify Supabase connection and API keys

### CORS Errors
- Frontend and backend are configured for cross-origin requests
- Check if production URLs match your Render service names

## 🔄 Future Updates
To update your deployment:
```bash
# Make your changes locally
git add .
git commit -m "Your updates"

# Re-run deployment script
./deploy-to-render.sh
```

## 🛡️ Security Notes
- Environment variables are stored securely in Render
- No secrets are committed to your repository
- Production uses HTTPS for all communications
- Docker containers run as non-root users

---

**Need Help?** 
- Check Render documentation: https://render.com/docs
- Review logs in Render dashboard for detailed error messages
