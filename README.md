# OCR Invoice Processor

A modern invoice processing system that handles PDF uploads, OCR extraction, and data management using Next.js and FastAPI.

## 🚀 Quick Start

```bash
# Clone and start the application
git clone <your-repo-url>
cd ocr-invoice-processor
docker-compose up
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 Features

### Sprint 1: Upload UI + File Service ✅
- [x] Drag & drop PDF upload interface
- [x] Filename validation (YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf)
- [x] Supabase storage integration
- [x] Invoice metadata tracking
- [x] Dashboard for uploaded files

### Sprint 2: OCR Processing (Planned)
- [ ] PDF text extraction
- [ ] Invoice field parsing
- [ ] Data validation
- [ ] Error handling

### Sprint 3: Advanced Features (Planned)
- [ ] User authentication
- [ ] Batch processing
- [ ] Export functionality
- [ ] Analytics dashboard

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS | User interface and file upload |
| **Backend** | FastAPI, Python 3.11, Uvicorn | API server and file processing |
| **Storage** | Supabase Storage, PostgreSQL | File storage and metadata |
| **DevOps** | Docker, Docker Compose | Local development environment |

## 📁 Project Structure

```
ocr-invoice-processor/
├── .github/workflows/    # CI/CD pipelines
├── frontend/            # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── upload/page.tsx
│   │   │   └── dashboard/page.tsx
│   │   ├── components/Dropzone.tsx
│   │   └── lib/supabaseClient.ts
│   └── package.json
├── backend/             # FastAPI service
│   ├── main.py         # FastAPI application
│   ├── services/       # Business logic
│   └── requirements.txt
├── docker-compose.yml   # Local development setup
└── README.md
```

## 🔧 Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Variables

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend (.env)
```bash
SUPA_URL=your_supabase_url
SUPA_KEY=your_supabase_service_key
DEBUG=True
```

### Local Development

```bash
# Using Docker (Recommended)
docker-compose up

# Manual setup
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌿 Git Branching Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: Individual feature development

### Workflow
```bash
# Create feature branch
git checkout develop
git checkout -b feature/your-feature-name

# Work on feature
git add .
git commit -m "feat(component): description"

# Push and create PR
git push -u origin feature/your-feature-name
# Create PR to develop branch
```

## 📝 API Documentation

### Upload Endpoint
```http
POST /upload
Content-Type: multipart/form-data

file: <PDF file>
```

**Response:**
```json
{
  "url": "https://storage.url/filename.pdf",
  "status": "uploaded",
  "filename": "20250528_INV001_ACME_SERVICE.pdf",
  "id": "uuid"
}
```

### List Invoices
```http
GET /invoices
```

**Response:**
```json
{
  "invoices": [
    {
      "id": "uuid",
      "filename": "20250528_INV001_ACME_SERVICE.pdf",
      "url": "https://storage.url/filename.pdf",
      "status": "uploaded",
      "created_at": "2025-05-28T10:30:00Z"
    }
  ]
}
```

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run all tests via Docker
docker-compose -f docker-compose.test.yml up
```

## 📦 Deployment

### Production Build
```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD
GitHub Actions automatically:
- Runs tests on PR creation
- Builds Docker images
- Deploys to staging/production

## 🐛 Troubleshooting

### Common Issues

**CORS Errors:**
- Ensure FastAPI CORS middleware is properly configured
- Check that frontend URL is in allowed origins

**File Upload Fails:**
- Verify Supabase credentials
- Check bucket permissions
- Validate filename format

**Docker Issues:**
- Clear Docker cache: `docker-compose down && docker system prune`
- Rebuild images: `docker-compose build --no-cache`

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- Create an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide clear reproduction steps for bugs