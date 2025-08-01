@echo off
title OCR Invoice Processor - Stop

echo.
echo 🛑 Stopping OCR Invoice Processor...
echo.

docker-compose down

if errorlevel 0 (
    echo.
    echo ✅ Application stopped successfully!
    echo.
    echo 💡 To start again: run start-company.bat
    echo.
) else (
    echo.
    echo ❌ Error stopping application
    echo 💡 Try: docker-compose down --remove-orphans
    echo.
)

pause