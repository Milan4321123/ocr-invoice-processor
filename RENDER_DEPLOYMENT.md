# OCR Invoice Processor - Render Deployment Guide

## 🚀 Quick Render Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Deploy Backend on Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `ocr-invoice-backend`
   - **Environment:** `Python 3`
   - **Region:** `Frankfurt` (or closest)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python render_start.py`

5. Add Environment Variables:
```
SUPABASE_URL=https://bdtcfypvadryfeabqnlc.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SENDGRID_API_KEY=SG.7vElBB30TFG9V4eZ1IVLTA...
FROM_EMAIL=adhikarimilan4321@gmail.com
FROM_NAME=Invoice Processing System
JWT_SECRET=aZ-Z7oWl2S2_rB0yFMmRfQ7RRLE3DvqLqNP3w45ulxk
ENABLE_OCR=false
USE_MOCK_OCR=true
DEBUG=false
```

### Step 3: Deploy Frontend on Render

1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Name:** `ocr-invoice-frontend`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `.next`

4. Add Environment Variables:
```
NEXT_PUBLIC_SUPABASE_URL=https://bdtcfypvadryfeabqnlc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-NAME.onrender.com
NODE_VERSION=18
```

### Step 4: Update URLs

After deployment, update the frontend environment variable:
- **NEXT_PUBLIC_API_URL:** Use your actual backend URL from Render

## 🎯 Your Deployed URLs

- **Frontend:** `https://ocr-invoice-frontend.onrender.com`
- **Backend:** `https://ocr-invoice-backend.onrender.com`
- **Login:** `admin / admin123`

## ✅ Features Ready for Demo

- ✅ File upload and processing
- ✅ Invoice management
- ✅ Email notifications (SendGrid)
- ✅ Authentication system
- ✅ Professional UI
- ✅ Database integration (Supabase)

## 📱 For Company Demo

1. Share frontend URL with company
2. Demo login: `admin / admin123`
3. Show file upload functionality
4. Demonstrate invoice workflow
5. Test email notifications

## ⚠️ Important Notes

- Free tier sleeps after 15 minutes of inactivity
- First request may be slow (cold start)
- All environment variables are secure in Render dashboard
- Automatic deployments on every GitHub push

Your OCR Invoice Processor is now ready for company demonstration! 🎉
