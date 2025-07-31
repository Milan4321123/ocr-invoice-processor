# 🐳 Docker Deployment Guide for OCR Invoice Processor

## 🎯 Quick Start

Your OCR Invoice Processor is now successfully running in Docker! Here's how to manage it:

### ✅ Current Status
- ✅ **Docker Desktop**: Installed and running
- ✅ **Backend Container**: Running on http://localhost:8000
- ✅ **Frontend Container**: Running on http://localhost:3000
- ✅ **Development Mode**: Hot reload enabled

---

## 🚀 Development Commands

### Start the Application
```bash
# Start in development mode (recommended)
docker-compose -f docker-compose.dev.yml up -d

# Or start with logs visible
docker-compose -f docker-compose.dev.yml up
```

### Stop the Application
```bash
# Stop all containers
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes
docker-compose -f docker-compose.dev.yml down -v
```

### View Logs
```bash
# View all logs
docker-compose -f docker-compose.dev.yml logs

# View backend logs only
docker-compose -f docker-compose.dev.yml logs backend

# View frontend logs only
docker-compose -f docker-compose.dev.yml logs frontend

# Follow logs in real-time
docker-compose -f docker-compose.dev.yml logs -f
```

### Rebuild Containers
```bash
# Rebuild and restart (after code changes)
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# Force rebuild without cache
docker-compose -f docker-compose.dev.yml build --no-cache
```

---

## 🌐 Access Your Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application interface |
| **Backend API** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/api/health | Backend health status |

---

## 🔧 Production Deployment

### Option 1: Standard Production
```bash
# Use the standard compose file for production
docker-compose up -d

# With nginx reverse proxy
docker-compose --profile production up -d
```

### Option 2: Simple Production (without nginx)
```bash
# Start with production optimizations
docker-compose -f docker-compose.simple.yml up -d
```

---

## 📁 Docker Configuration Files

### Development Setup
- **`docker-compose.dev.yml`**: Development with hot reload
- **`backend/Dockerfile.dev`**: Development backend image
- **`frontend/Dockerfile.dev`**: Development frontend image

### Production Setup
- **`docker-compose.yml`**: Production deployment
- **`backend/Dockerfile`**: Optimized backend image
- **`frontend/Dockerfile`**: Optimized frontend image

---

## 🔍 Troubleshooting

### Check Container Status
```bash
# See running containers
docker-compose -f docker-compose.dev.yml ps

# See detailed container info
docker ps
```

### Access Container Shell
```bash
# Access backend container
docker-compose -f docker-compose.dev.yml exec backend bash

# Access frontend container
docker-compose -f docker-compose.dev.yml exec frontend sh
```

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill process using port
kill -9 <PID>
```

#### Container Won't Start
```bash
# Check logs for errors
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend
```

#### Environment Variables Not Loading
```bash
# Check if .env file exists and has correct values
cat .env

# Restart containers to reload environment
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

---

## 💾 Data Persistence

### Volumes
- **`./backend/uploads`**: Uploaded invoice files
- **`./logs`**: Application logs
- **`./backend/keys`**: GCP service account keys

### Database
- **Supabase**: External cloud database (configured via environment variables)

---

## 🔧 Development Workflow

### 1. Code Changes
- **Backend**: Changes auto-reload (uvicorn --reload)
- **Frontend**: Changes auto-reload (npm run dev)
- **No rebuild needed** for most code changes

### 2. Dependency Changes
```bash
# If you add new Python packages
docker-compose -f docker-compose.dev.yml build backend
docker-compose -f docker-compose.dev.yml up -d backend

# If you add new npm packages
docker-compose -f docker-compose.dev.yml build frontend
docker-compose -f docker-compose.dev.yml up -d frontend
```

### 3. Environment Changes
```bash
# After modifying .env file
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost:3000

# Container health status
docker-compose -f docker-compose.dev.yml ps
```

### Resource Usage
```bash
# See container resource usage
docker stats

# See container processes
docker-compose -f docker-compose.dev.yml top
```

---

## 🎯 Next Steps

1. **Test the Application**: Visit http://localhost:3000
2. **Login**: Use your existing credentials
3. **Upload Invoices**: Test the complete workflow
4. **Check Logs**: Monitor both services for any issues
5. **Customize**: Modify environment variables as needed

---

## 🆘 Support Commands

### Quick Status Check
```bash
# One command to check everything
echo "=== Docker Status ===" && docker --version && \
echo "=== Containers ===" && docker-compose -f docker-compose.dev.yml ps && \
echo "=== Backend Health ===" && curl -s http://localhost:8000/api/health && \
echo -e "\n=== Frontend Health ===" && curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000
```

### Emergency Reset
```bash
# Complete reset (removes all containers and volumes)
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📝 Environment Variables

Make sure your `.env` file contains all required variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Frontend Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000

# Security
JWT_SECRET=your-secure-jwt-secret

# Email Configuration
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=noreply@yourcompany.com

# Application Settings
DEBUG=true
ENABLE_OCR=true
USE_MOCK_OCR=true
```

---

**🎉 Your OCR Invoice Processor is now running in Docker!**
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
