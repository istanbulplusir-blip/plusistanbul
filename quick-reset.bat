@echo off
echo 🗑️  Quick Database Reset - Peykan Tourism Platform

REM Stop services
echo [INFO] Stopping services...
docker-compose -f docker-compose.production-secure.yml down

REM Remove database volumes
echo [INFO] Removing database volumes...
docker volume prune -f

REM Remove migration files
echo [INFO] Removing migration files...
cd backend
for /r %%i in (*.py) do (
    if not "%%~ni"=="__init__" (
        if "%%~pi"=="migrations\" (
            del "%%i" 2>nul
        )
    )
)

REM Remove database files
echo [INFO] Removing database files...
del db.sqlite3 2>nul
del *.db 2>nul
del *.sqlite 2>nul

REM Remove cache files
echo [INFO] Removing cache files...
for /d /r %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
del /s /q *.pyc 2>nul

REM Create fresh migrations
echo [INFO] Creating fresh migrations...
python manage.py makemigrations

REM Start database services
echo [INFO] Starting database services...
cd ..
docker-compose -f docker-compose.production-secure.yml up -d postgres redis

REM Wait for database
echo [INFO] Waiting for database to be ready...
timeout /t 15 /nobreak >nul

REM Run migrations
echo [INFO] Running migrations...
cd backend
python manage.py migrate

REM Collect static files
echo [INFO] Collecting static files...
python manage.py collectstatic --noinput

echo ✅ Database reset completed successfully!
echo [INFO] Next steps:
echo 1. Start all services: docker-compose -f ../docker-compose.production-secure.yml up -d
echo 2. Check logs: docker-compose -f ../docker-compose.production-secure.yml logs
echo 3. Test the application

cd ..
pause
