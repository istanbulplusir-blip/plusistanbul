@echo off
REM Fix CSRF Token Issue in Django Admin (Windows)
REM This script resolves CSRF token problems in production

echo 🔧 Fixing CSRF Token Issue in Django Admin...

REM Check if containers are running
docker ps --format "table {{.Names}}" | findstr "peykan_backend" >nul
if errorlevel 1 (
    echo ❌ Backend container is not running. Please start the application first.
    pause
    exit /b 1
)

echo ✅ Backend container is running

REM Clear Django sessions and CSRF tokens
echo 🧹 Clearing Django sessions and CSRF tokens...
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py shell -c "from django.contrib.sessions.models import Session; from django.core.cache import cache; Session.objects.all().delete(); cache.clear(); print('✅ Sessions and cache cleared')"

REM Restart backend service
echo 🔄 Restarting backend service...
docker-compose -f docker-compose.production-secure.yml restart backend

REM Wait for service to be ready
echo ⏳ Waiting for backend to be ready...
timeout /t 10 /nobreak >nul

REM Test admin access
echo 🧪 Testing admin access...
curl -f -s "https://peykantravelistanbul.com/admin/" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Admin panel is accessible
) else (
    echo ⚠️  Admin panel might not be accessible yet
)

echo.
echo 🎉 CSRF issue fix completed!
echo.
echo 📋 Next steps:
echo 1. Try accessing the admin panel again
echo 2. If still having issues, check the logs:
echo    docker-compose -f docker-compose.production-secure.yml logs backend
echo 3. Clear browser cache and cookies
echo 4. Try accessing from an incognito/private window
echo.
echo 🔗 Admin Panel: https://peykantravelistanbul.com/admin/

pause
