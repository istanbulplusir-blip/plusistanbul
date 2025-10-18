@echo off
REM Setup script for production-like development environment
REM This script prepares the project for deployment testing

echo Setting up production-like development environment...
echo.

REM Check if Docker is running
echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop and start it.
    pause
    exit /b 1
)

echo Docker is available.
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist backend\logs mkdir backend\logs
if not exist nginx\ssl mkdir nginx\ssl
if not exist postgres mkdir postgres
if not exist redis mkdir redis

echo Directories created.
echo.

REM Copy environment template if it doesn't exist
if not exist backend\.env.production.dev (
    echo Creating production development environment file...
    copy backend\env.production.dev backend\.env.production.dev
    echo Environment file created.
) else (
    echo Environment file already exists.
)

echo.

REM Generate SSL certificates for development
echo Generating SSL certificates for development...
if not exist nginx\ssl\cert.pem (
    echo Creating self-signed SSL certificates...
    docker run --rm -v "%cd%\nginx\ssl:/ssl" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /ssl/key.pem -out /ssl/cert.pem -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=localhost"
    echo SSL certificates generated.
) else (
    echo SSL certificates already exist.
)

echo.

REM Build and start the services
echo Building and starting services...
echo This may take several minutes on first run...
echo.

docker-compose -f docker-compose.production-dev.yml down
docker-compose -f docker-compose.production-dev.yml build --no-cache
docker-compose -f docker-compose.production-dev.yml up -d

echo.
echo Services are starting up...
echo.

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service status
echo Checking service status...
docker-compose -f docker-compose.production-dev.yml ps

echo.
echo ========================================
echo Production-like development environment is ready!
echo.
echo Services:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - Nginx Proxy: http://localhost:80
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379
echo.
echo To view logs:
echo docker-compose -f docker-compose.production-dev.yml logs -f
echo.
echo To stop services:
echo docker-compose -f docker-compose.production-dev.yml down
echo.
echo To restart services:
echo docker-compose -f docker-compose.production-dev.yml restart
echo ========================================

pause
