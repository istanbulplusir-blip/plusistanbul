@echo off
echo 🗑️  Resetting Database - Peykan Tourism Platform

REM Check if we're in the right directory
if not exist "backend" (
    echo [ERROR] Please run this script from the project root directory!
    exit /b 1
)

cd backend

echo [INFO] Step 1: Stopping all services...
docker-compose -f ../docker-compose.production-secure.yml down 2>nul

echo [INFO] Step 2: Removing database volumes...
for /f "tokens=*" %%i in ('docker volume ls -q ^| findstr /E "postgres redis"') do docker volume rm %%i 2>nul

echo [INFO] Step 3: Cleaning up migration files...

REM Remove all migration files except __init__.py
for /r %%i in (*.py) do (
    if not "%%~ni"=="__init__" (
        if "%%~pi"=="migrations\" (
            del "%%i" 2>nul
        )
    )
)

REM Remove Python cache files
for /d /r %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
del /s /q *.pyc 2>nul

echo [INFO] Step 4: Removing database files...
del db.sqlite3 2>nul
del *.db 2>nul
del *.sqlite 2>nul

echo [INFO] Step 5: Creating fresh migrations...
python manage.py makemigrations

echo [INFO] Step 6: Starting database services...
cd ..
docker-compose -f docker-compose.production-secure.yml up -d postgres redis

echo [INFO] Waiting for database to be ready...
timeout /t 15 /nobreak >nul

cd backend

echo [INFO] Step 7: Running migrations...
python manage.py migrate

echo [INFO] Step 8: Collecting static files...
python manage.py collectstatic --noinput

echo ✅ Database reset completed successfully!

echo [INFO] Next steps:
echo 1. Start all services: docker-compose -f ../docker-compose.production-secure.yml up -d
echo 2. Check logs: docker-compose -f ../docker-compose.production-secure.yml logs
echo 3. Test the application

echo [WARNING] Important notes:
echo - All data has been permanently deleted
echo - You may need to recreate test data
echo - Check your models for any issues

cd ..
pause
