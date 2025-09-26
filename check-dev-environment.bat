@echo off
echo 🔍 Checking Development Environment - Peykan Tourism Platform

echo [INFO] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [INFO] Checking Django installation...
cd backend
python -c "import django; print('Django version:', django.get_version())"
if %errorlevel% neq 0 (
    echo [ERROR] Django is not installed
    pause
    exit /b 1
)

echo [INFO] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment found
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found
    echo [INFO] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [INFO] Installing requirements...
    pip install -r requirements.txt
)

echo [INFO] Checking Django configuration...
python manage.py check
if %errorlevel% neq 0 (
    echo [ERROR] Django configuration has issues
    pause
    exit /b 1
)

echo [INFO] Checking database...
if exist "db.sqlite3" (
    echo [INFO] SQLite database found
) else (
    echo [INFO] No database found - will be created during migration
)

echo [INFO] Checking migrations...
python manage.py showmigrations

echo [INFO] Checking static files...
if exist "static" (
    echo [INFO] Static files directory found
) else (
    echo [INFO] Static files directory will be created
)

echo ✅ Development environment check completed!

echo [INFO] Next steps:
echo 1. Run: reset-database-dev.bat (to reset database)
echo 2. Run: python manage.py runserver (to start development server)
echo 3. Open: http://localhost:8000

cd ..
pause
