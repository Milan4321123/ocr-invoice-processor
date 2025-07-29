@echo off
REM OCR Invoice Processor - Docker Management Script (Windows)

setlocal EnableDelayedExpansion

REM Project name
set PROJECT_NAME=ocr-invoice-processor

REM Print header
:print_header
echo ================================
echo   OCR Invoice Processor Docker
echo ================================
goto :eof

REM Print status
:print_status
echo [INFO] %~1
goto :eof

REM Print error
:print_error
echo [ERROR] %~1
goto :eof

REM Print warning
:print_warning
echo [WARNING] %~1
goto :eof

REM Check if Docker is running
:check_docker
docker info >nul 2>&1
if !errorlevel! neq 0 (
    call :print_error "Docker is not running. Please start Docker Desktop and try again."
    pause
    exit /b 1
)
goto :eof

REM Show status
:show_status
call :print_header
call :print_status "Checking Docker status..."
call :check_docker
call :print_status "Docker is running"

echo.
call :print_status "Container Status:"
docker-compose -f docker-compose.dev.yml ps 2>nul

echo.
call :print_status "Service Health Checks:"

REM Check backend
curl -s http://localhost:8000/api/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Backend (http://localhost:8000) - Healthy
) else (
    echo ❌ Backend (http://localhost:8000) - Not responding
)

REM Check frontend
curl -s http://localhost:3000 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Frontend (http://localhost:3000) - Healthy
) else (
    echo ❌ Frontend (http://localhost:3000) - Not responding
)
pause
goto :eof

REM Start services
:start_services
call :print_header
call :print_status "Starting OCR Invoice Processor..."
call :check_docker

if not exist ".env" (
    call :print_warning "No .env file found. Creating from .env.example..."
    if exist ".env.example" (
        copy .env.example .env >nul
        call :print_status "Created .env file. Please edit it with your configuration."
    ) else (
        call :print_error "No .env.example file found. Please create .env manually."
        pause
        exit /b 1
    )
)

call :print_status "Building and starting containers..."
docker-compose -f docker-compose.dev.yml up -d --build

call :print_status "Waiting for services to start..."
timeout /t 10 /nobreak >nul

call :show_status

echo.
call :print_status "🎉 OCR Invoice Processor is now running!"
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
pause
goto :eof

REM Stop services
:stop_services
call :print_header
call :print_status "Stopping OCR Invoice Processor..."
docker-compose -f docker-compose.dev.yml down
call :print_status "Services stopped."
pause
goto :eof

REM Restart services
:restart_services
call :print_header
call :print_status "Restarting OCR Invoice Processor..."
docker-compose -f docker-compose.dev.yml restart
call :print_status "Services restarted."
call :show_status
pause
goto :eof

REM Show logs
:show_logs
call :print_header
call :print_status "Showing application logs..."
docker-compose -f docker-compose.dev.yml logs -f
pause
goto :eof

REM Clean up
:cleanup
call :print_header
call :print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
set /p response="Enter your choice: "
if /i "!response!"=="y" (
    call :print_status "Cleaning up Docker resources..."
    docker-compose -f docker-compose.dev.yml down -v
    docker system prune -f
    call :print_status "Cleanup complete."
) else (
    call :print_status "Cleanup cancelled."
)
pause
goto :eof

REM Rebuild
:rebuild
call :print_header
call :print_status "Rebuilding containers..."
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
call :print_status "Rebuild complete."
call :show_status
pause
goto :eof

REM Open browser
:open_browser
call :print_status "Opening application in browser..."
start http://localhost:3000
pause
goto :eof

REM Show help
:show_help
call :print_header
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   start     Start the application containers
echo   stop      Stop the application containers
echo   restart   Restart the application containers
echo   status    Show current status
echo   logs      Show application logs (follow mode)
echo   rebuild   Rebuild containers from scratch
echo   cleanup   Remove all containers and volumes
echo   open      Open application in browser
echo   help      Show this help message
echo.
echo Examples:
echo   %0 start    # Start the application
echo   %0 status   # Check if everything is running
echo   %0 logs     # View real-time logs
pause
goto :eof

REM Main script logic
if "%1"=="" goto show_help
if "%1"=="start" goto start_services
if "%1"=="stop" goto stop_services
if "%1"=="restart" goto restart_services
if "%1"=="status" goto show_status
if "%1"=="logs" goto show_logs
if "%1"=="rebuild" goto rebuild
if "%1"=="cleanup" goto cleanup
if "%1"=="open" goto open_browser
if "%1"=="help" goto show_help
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

call :print_error "Unknown command: %1"
echo.
goto show_help