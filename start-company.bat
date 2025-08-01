@echo off
title OCR Invoice Processor - Company Edition

echo.
echo ========================================
echo    OCR INVOICE PROCESSOR - COMPANY
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed!
    echo.
    echo 📥 Please install Docker Desktop from:
    echo    https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo.
    echo 🚀 Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo ✅ Docker is ready
echo.

REM Check if .env exists
if not exist ".env" (
    echo 📝 Setting up environment file...
    copy environment.template .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file with your company settings:
    echo    - Database URLs (Supabase)
    echo    - Email configuration (SendGrid)  
    echo    - Company information
    echo    - Admin credentials
    echo.
    echo Press any key after editing .env file...
    pause
)

echo 🚀 Starting OCR Invoice Processor...
echo    This may take a few minutes on first start (downloading images)
echo.

REM Build and start containers
docker-compose up --build -d

if errorlevel 0 (
    echo.
    echo ========================================
    echo ✅ SUCCESS! APPLICATION IS RUNNING
    echo ========================================
    echo.
    echo 🌐 Access your application:
    echo.
    echo    📊 Main Application: http://localhost:3000
    echo    🔧 API Backend:     http://localhost:8000  
    echo    📖 API Documentation: http://localhost:8000/docs
    echo.
    echo 💡 What to do next:
    echo    1. Open http://localhost:3000 in your browser
    echo    2. Login with admin credentials from .env file
    echo    3. Start processing invoices!
    echo.
    echo 🛑 To stop: run stop-company.bat
    echo 📊 To view logs: docker-compose logs -f
    echo.
    echo Opening application in browser...
    timeout /t 3 /nobreak >nul
    start http://localhost:3000
) else (
    echo.
    echo ❌ FAILED TO START APPLICATION
    echo.
    echo 🔍 Troubleshooting:
    echo    1. Check Docker is running properly
    echo    2. Check ports 3000 and 8000 are available
    echo    3. Check .env file is configured correctly
    echo    4. Run: docker-compose logs
    echo.
)

echo.
echo Press any key to exit...
pause >nul