@echo off
REM Production Deployment Script for Peykan Tourism Platform (Windows)
REM This script deploys the application to production with all necessary configurations

echo 🚀 Starting production deployment for Peykan Tourism Platform...

REM Check if Docker is installed and running
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker first.
    exit /b 1
)

echo [INFO] Docker is available

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo [INFO] Docker Compose is available

REM Check if production environment file exists
if not exist "backend\env.production" (
    echo [ERROR] Production environment file not found: backend\env.production
    echo [INFO] Please create the production environment file first
    exit /b 1
)

REM Check if SSL certificates exist
if not exist "nginx\ssl\cert.pem" (
    echo [WARNING] SSL certificates not found. Generating self-signed certificates...
    call generate-ssl-certs-production.bat
)

REM Backup existing data if containers exist
docker ps -a --format "table {{.Names}}" | findstr "peykan_" >nul
if not errorlevel 1 (
    echo [INFO] Backing up existing data...
    
    REM Create backup directory
    set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set BACKUP_DIR=%BACKUP_DIR: =0%
    mkdir "%BACKUP_DIR%"
    
    REM Backup database
    docker ps --format "table {{.Names}}" | findstr "peykan_postgres" >nul
    if not errorlevel 1 (
        echo [INFO] Backing up database...
        docker exec peykan_postgres pg_dump -U peykan_user peykan > "%BACKUP_DIR%\database.sql"
    )
    
    REM Backup media files
    docker ps --format "table {{.Names}}" | findstr "peykan_backend" >nul
    if not errorlevel 1 (
        echo [INFO] Backing up media files...
        docker cp peykan_backend:/app/media "%BACKUP_DIR%\"
    )
    
    echo [SUCCESS] Backup completed: %BACKUP_DIR%
)

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f docker-compose.production-secure.yml down

REM Pull latest images
echo [INFO] Pulling latest images...
docker-compose -f docker-compose.production-secure.yml pull

REM Build and start services
echo [INFO] Building and starting services...
docker-compose -f docker-compose.production-secure.yml up -d --build

REM Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo [INFO] Checking service status...
docker-compose -f docker-compose.production-secure.yml ps

REM Run database migrations
echo [INFO] Running database migrations...
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py migrate

REM Collect static files
echo [INFO] Collecting static files...
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py collectstatic --noinput

REM Create superuser if it doesn't exist
echo [INFO] Creating superuser (if not exists)...
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@peykantravelistanbul.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')"

REM Test health endpoints
echo [INFO] Testing health endpoints...

REM Test backend health
curl -f -s http://localhost/api/v1/health/ >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Backend health check passed
) else (
    echo [WARNING] Backend health check failed
)

REM Test frontend
curl -f -s http://localhost/ >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Frontend health check passed
) else (
    echo [WARNING] Frontend health check failed
)

REM Display deployment information
echo [SUCCESS] 🎉 Production deployment completed!
echo.
echo 📋 Deployment Information:
echo   🌐 Frontend: https://peykantravelistanbul.com
echo   🔧 Backend API: https://peykantravelistanbul.com/api/v1/
echo   👨‍💼 Admin Panel: https://peykantravelistanbul.com/admin/
echo   📊 Health Check: https://peykantravelistanbul.com/health
echo.
echo 🔐 Admin Credentials:
echo   Username: admin
echo   Password: admin123
echo   ⚠️  Please change the admin password immediately!
echo.
echo 📝 Next Steps:
echo   1. Update admin password
echo   2. Configure email settings
echo   3. Set up monitoring
echo   4. Configure backup strategy
echo.
echo 📊 View logs: docker-compose -f docker-compose.production-secure.yml logs -f
echo 🛑 Stop services: docker-compose -f docker-compose.production-secure.yml down

pause
