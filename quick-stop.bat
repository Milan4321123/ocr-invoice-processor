@echo off
REM Quick Stop Script for OCR Invoice Processor (Windows)

echo 🛑 Stopping OCR Invoice Processor...

docker-compose down

echo ✅ OCR Invoice Processor Stopped!
echo.
echo 💡 Start again with: quick-start.bat

pause
