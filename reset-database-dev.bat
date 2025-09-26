@echo off
echo 🗑️  Database Reset for Development - Peykan Tourism Platform

REM Check if we're in the right directory
if not exist "backend" (
    echo [ERROR] Please run this script from the project root directory!
    pause
    exit /b 1
)

cd backend

echo [INFO] Step 1: Stopping local services...
REM Stop any running Django development server
taskkill /f /im python.exe 2>nul

echo [INFO] Step 2: Removing local database files...
REM Remove SQLite database
del db.sqlite3 2>nul
del *.db 2>nul
del *.sqlite 2>nul

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

echo [INFO] Step 4: Creating fresh migrations...
python manage.py makemigrations

echo [INFO] Step 5: Running migrations...
python manage.py migrate

echo [INFO] Step 6: Creating superuser (optional)...
echo Do you want to create a superuser? (y/n)
set /p response=
if /i "%response%"=="y" (
    python manage.py createsuperuser
)

echo [INFO] Step 7: Collecting static files...
python manage.py collectstatic --noinput

echo [INFO] Step 8: Loading sample data (optional)...
echo Do you want to load sample data? (y/n)
set /p response=
if /i "%response%"=="y" (
    python manage.py loaddata fixtures/sample_data.json 2>nul || echo No sample data found
)

echo ✅ Development database reset completed successfully!

echo [INFO] Next steps:
echo 1. Start development server: python manage.py runserver
echo 2. Open browser: http://localhost:8000
echo 3. Check admin panel: http://localhost:8000/admin

echo [INFO] Useful commands:
echo - Run server: python manage.py runserver
echo - Check models: python manage.py check
echo - Show migrations: python manage.py showmigrations
echo - Create superuser: python manage.py createsuperuser

cd ..
pause
