# Invoice Management System

A manual invoice processing system with searchable dropdowns and workflow management.

## Overview

This system provides a complete invoice management workflow:

1. **PDF Upload** - Upload invoices via web interface or folder watching
2. **Supabase Storage** - Secure storage of invoice PDFs
3. **Manual Editing** - Dashboard with searchable dropdowns for data entry
4. **Database Storage** - Save invoice data to Supabase
5. **Review Workflow** - Approval process with email notifications
6. **Prüfbericht Generation** - Final report generation

## Features

- Manual invoice data entry with searchable dropdowns
- PDF viewing and editing interface
- Folder watching for automatic upload detection
- Multi-step approval workflow
- Email notifications
- Prüfbericht (audit report) generation
- Multi-language support (German/English)

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React/TypeScript)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Email**: SendGrid
- **Deployment**: Docker

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Supabase account
- SendGrid account (for email functionality)

### Environment Setup

1. Copy environment files:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. Configure your environment variables:
   - Supabase URL and API keys
   - SendGrid API key
   - Database connection details

### Run with Docker

```bash
docker-compose up --build
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000

### Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Core Endpoints
- `POST /api/upload` - Upload invoice PDF
- `GET /api/invoices` - List invoices
- `GET /api/invoices/{id}` - Get invoice details
- `PUT /api/invoices/{id}` - Update invoice
- `POST /api/approval/submit` - Submit for approval
- `GET /api/dropdowns/{field}` - Get dropdown options

### Workflow Endpoints
- `POST /api/approval/bauleiter` - Bauleiter approval
- `POST /api/approval/buero` - Büro approval
- `GET /api/reports/prufbericht/{id}` - Generate Prüfbericht

## Database Schema

The system uses the following main tables:
- `invoices` - Invoice data and metadata
- `dropdown_options` - Searchable dropdown values
- `approval_workflow` - Approval process tracking
- `email_workflow` - Email notification tracking

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── api/
│   │   └── routes/      # API route handlers
│   ├── services/        # Business logic services
│   ├── config/          # Configuration
│   └── main.py          # Application entry point
├── frontend/            # Next.js frontend
│   └── src/
│       ├── app/         # Next.js app directory
│       ├── components/  # React components
│       └── services/    # API services
├── docker-compose.yml   # Docker configuration
└── README.md           # This file
```

## Development Guidelines

### Manual Workflow
This system is designed for manual invoice processing. All data entry is done through the web interface with assistance from searchable dropdowns.

### No OCR Dependencies
The system does not include OCR (Optical Character Recognition) functionality. All invoice data must be entered manually.

### Searchable Dropdowns
The system provides searchable dropdowns for:
- Vendors (Lieferanten)
- Cost centers (Kostenstellen)
- Accounts (Konten)
- Projects (Projekte)

## Contributing

1. Follow the existing code structure
2. Maintain the manual workflow approach
3. Use TypeScript for frontend development
4. Follow Python best practices for backend
5. Ensure all changes are tested

## License

[Your License Here]