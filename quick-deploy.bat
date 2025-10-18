@echo off
REM Quick Production Deployment Script (Windows)
REM This script provides a simplified deployment process

echo 🚀 Quick Production Deployment for Peykan Tourism Platform
echo ==========================================================

REM Check if we're in the right directory
if not exist "docker-compose.production-secure.yml" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if production environment exists
if not exist "backend\env.production" (
    echo ❌ Error: Production environment file not found
    echo Please create backend\env.production first
    pause
    exit /b 1
)

echo ✅ Production environment file found

REM Generate SSL certificates if they don't exist
if not exist "nginx\ssl\cert.pem" (
    echo 🔐 Generating SSL certificates...
    call generate-ssl-certs-production.bat
) else (
    echo ✅ SSL certificates already exist
)

REM Deploy the application
echo 🚀 Deploying application...
call deploy-production.bat

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📋 Your application is now available at:
echo    🌐 Frontend: https://peykantravelistanbul.com
echo    🔧 Backend: https://peykantravelistanbul.com/api/v1/
echo    👨‍💼 Admin: https://peykantravelistanbul.com/admin/
echo.
echo 🔐 Admin credentials:
echo    Username: admin
echo    Password: admin123
echo    ⚠️  Please change the password immediately!
echo.
echo 📊 To view logs: docker-compose -f docker-compose.production-secure.yml logs -f
echo 🛑 To stop: docker-compose -f docker-compose.production-secure.yml down

pause
