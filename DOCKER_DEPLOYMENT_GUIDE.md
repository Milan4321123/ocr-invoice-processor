# 🏢 OCR Invoice Processor - Company Deployment Guide

## Overview
This guide helps you deploy the OCR Invoice Processor in your company environment using Docker. The system processes invoice PDFs using OCR technology and manages the complete invoice workflow.

## 🚀 Quick Start for Company IT

### 1. Prerequisites
- **Docker Desktop** installed and running
- **Git** for cloning the repository
- **Company email accounts** for Supabase and SendGrid setup

### 2. One-Command Setup
```bash
# Clone and setup (replace with your company repository)
git clone https://github.com/YOUR-COMPANY/ocr-invoice-processor.git
cd ocr-invoice-processor

# Run company setup
./company-setup.sh

# Start the application
./docker-start.sh
```

### 3. Quick Commands
```bash
# Start application
./quick-start.sh

# Stop application  
./quick-stop.sh

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
```

---

## 📋 Detailed Setup Instructions

### Step 1: Environment Configuration

1. **Copy environment template:**
   ```bash
   cp .env.production .env
   ```

2. **Edit `.env` file with company credentials:**
   ```env
   # Supabase Database
   SUPABASE_URL=https://your-company-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

   # Email Service
   SENDGRID_API_KEY=your_company_sendgrid_key
   FROM_EMAIL=noreply@yourcompany.com

   # Security (generate unique secret)
   JWT_SECRET=your-unique-company-secret-here
   ```

### Step 2: Supabase Database Setup

1. **Create Supabase project** with company email
2. **Run database setup:**
   - Go to Supabase SQL Editor
   - Copy contents of `COMPLETE_SUPABASE_SETUP.sql`
   - Execute the script

3. **Create storage buckets:**
   - Bucket: `invoices` (public)
   - Bucket: `folderwatcher` (public)

### Step 3: Email Service Setup

1. **Create SendGrid account** with company email
2. **Generate API key** with Mail Send permissions
3. **Configure sender domain** (recommended)

### Step 4: OCR Configuration (Optional)

If using Google Cloud Document AI:
1. **Create GCP project**
2. **Enable Document AI API**
3. **Create service account** and download JSON key
4. **Place key file** in `backend/keys/gcp-service-account.json`

---

## 🐳 Docker Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   (Next.js)     │    │   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │   Nginx         │
         │   (Production)  │
         │   Port: 80      │
         └─────────────────┘
```

### Services
- **Frontend**: React/Next.js application
- **Backend**: FastAPI Python service
- **Database**: Supabase (cloud) or PostgreSQL (local)
- **Nginx**: Reverse proxy (production only)

---

## 🔧 Configuration Files

### Docker Compose Files
- `docker-compose.yml` - Production configuration
- `docker-compose.dev.yml` - Development with hot reload

### Environment Files
- `.env` - Main configuration (create from template)
- `.env.production` - Production template
- `.env.example` - Basic template

### Scripts
- `docker-start.sh` - Full setup and start with health checks
- `company-setup.sh` - Initial company setup wizard
- `quick-start.sh` - Simple start command
- `quick-stop.sh` - Simple stop command

---

## 🌐 Access Points

Once running, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3000 | Invoice management interface |
| **API** | http://localhost:8000 | Backend API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/api/health | Service status |

---

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using ports
   lsof -i :3000
   lsof -i :8000
   
   # Change ports in docker-compose.yml if needed
   ```

2. **Docker not running:**
   ```bash
   # Start Docker Desktop
   # On macOS: Applications > Docker Desktop
   # On Windows: Start Menu > Docker Desktop
   ```

3. **Environment variables:**
   ```bash
   # Check if .env file exists and has correct values
   cat .env
   ```

4. **Database connection:**
   ```bash
   # Check backend logs
   docker-compose logs backend
   ```

### Health Checks
```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs frontend
docker-compose logs backend

# Check application health
curl http://localhost:8000/api/health
```

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down

# Remove all data (careful!)
docker-compose down -v

# Rebuild and start fresh
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔐 Security Considerations

### For Production Deployment

1. **Change default passwords:**
   - Generate unique JWT_SECRET
   - Use strong database passwords

2. **Enable HTTPS:**
   - Configure SSL certificates in Nginx
   - Update BASE_URL to use https://

3. **Network security:**
   - Use Docker secrets for sensitive data
   - Configure firewall rules
   - Limit database access

4. **Monitoring:**
   - Set up log aggregation
   - Configure health monitoring
   - Set up backup procedures

---

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Log Files
- Application logs: `./logs/`
- Container logs: `docker-compose logs`

### Health Monitoring
- Backend health: `http://localhost:8000/api/health`
- Frontend health: `http://localhost:3000` (should load)

---

## 🚀 Production Deployment

### Option 1: Company Servers
1. **Install Docker** on company servers
2. **Clone repository** to server
3. **Configure environment** for production
4. **Run with production compose:**
   ```bash
   docker-compose -f docker-compose.yml --profile production up -d
   ```

### Option 2: Cloud Deployment
- **AWS ECS** with Docker containers
- **Google Cloud Run** 
- **Azure Container Instances**
- **DigitalOcean App Platform**

---

## 📞 Support

### For Company IT Teams

1. **Check logs first:**
   ```bash
   docker-compose logs -f
   ```

2. **Verify environment:**
   ```bash
   docker-compose config
   ```

3. **Test connectivity:**
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **Restart services:**
   ```bash
   docker-compose restart
   ```

### Contact Information
- **System Administrator**: [Your IT Team]
- **Documentation**: This README file
- **Repository**: [Your Company Repository URL]

---

## 📝 Quick Reference

```bash
# Setup
./company-setup.sh

# Start/Stop
./quick-start.sh
./quick-stop.sh

# Full control
./docker-start.sh
docker-compose down

# Logs
docker-compose logs -f

# Health
curl localhost:8000/api/health
```

**Access:** http://localhost:3000
