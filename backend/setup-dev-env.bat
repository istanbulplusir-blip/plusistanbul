@echo off
echo Setting up development environment for Peykan Tourism Platform...

REM Copy development environment file to .env
if not exist .env (
    copy env.development .env
    echo Created .env file from env.development
) else (
    echo .env file already exists
)

echo.
echo CORS Configuration:
echo - Allowed Origins: http://localhost:3000, http://localhost:3001, http://localhost:3002
echo - Also includes: http://127.0.0.1:3000, http://127.0.0.1:3001, http://127.0.0.1:3002
echo.
echo You can now run the Django development server on any of these ports:
echo - Port 3000 (default frontend)
echo - Port 3001 (alternative frontend instance)
echo - Port 3002 (alternative frontend instance)
echo.
echo To start the development server:
echo python manage.py runserver
echo.
echo To start with a specific port:
echo python manage.py runserver 8000
echo.
pause
