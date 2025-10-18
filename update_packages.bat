@echo off
echo 🚀 Starting backend package updates...

REM Update backend packages only
echo 📦 Updating backend packages...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing backend requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements.dev.txt

echo ✅ Backend packages updated successfully!

echo 🎉 Backend update completed!
echo.
echo Next steps:
echo 1. Test the backend to ensure everything works
echo 2. Run migrations if needed: python manage.py migrate
echo 3. Start the backend server: python manage.py runserver

pause
