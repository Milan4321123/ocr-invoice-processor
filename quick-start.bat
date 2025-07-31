@echo off
REM Quick Start Script for OCR Invoice Processor (Windows)

echo 🚀 Starting OCR Invoice Processor...

REM Check if .env exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Run company-setup.sh first or copy .env.example to .env
    pause
    exit /b 1
)

REM Start with Docker Compose
docker-compose up -d

echo.
echo ✅ OCR Invoice Processor Started!
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo 📋 API Docs: http://localhost:8000/docs
echo.
echo 💡 Stop with: quick-stop.bat
echo 💡 View logs: docker-compose logs -f

pause
