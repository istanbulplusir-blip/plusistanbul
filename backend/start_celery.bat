@echo off
echo Starting Celery Services for Peykan Tourism Platform...
echo.

REM Start Redis (if not already running)
echo Starting Redis...
start "Redis" redis-server
timeout /t 3 /nobreak >nul

REM Start Celery Worker
echo Starting Celery Worker...
start "Celery Worker" python manage.py start_celery_worker --loglevel=info --concurrency=2

REM Wait a moment for worker to start
timeout /t 5 /nobreak >nul

REM Start Celery Beat Scheduler
echo Starting Celery Beat Scheduler...
start "Celery Beat" python manage.py start_celery_beat --loglevel=info

echo.
echo Celery services started successfully!
echo.
echo Services running:
echo - Redis Server
echo - Celery Worker (2 processes)
echo - Celery Beat Scheduler
echo.
echo Press any key to stop all services...
pause >nul

REM Stop all services
echo Stopping services...
taskkill /f /im redis-server.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

echo All services stopped.
pause
