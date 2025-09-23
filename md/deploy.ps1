# Peykan Tourism Platform - Automated Production Deployment Script (PowerShell)
# This script extracts local environment variables and deploys to production server

param(
    [string]$ServerIP = "167.235.140.125",
    [string]$ServerUser = "djangouser",
    [string]$Domain = "peykantravelistanbul.com"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to generate secure random strings
function Generate-SecretKey {
    $chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    $random = ""
    for ($i = 0; $i -lt 50; $i++) {
        $random += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $random
}

# Function to extract local environment variables
function Extract-LocalEnv {
    Write-Status "Extracting local environment variables..."
    
    # Read local .env file
    $envFile = "backend\.env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^([^=]+)=(.*)$") {
                $varName = $matches[1]
                $varValue = $matches[2]
                Set-Variable -Name $varName -Value $varValue -Scope Script
            }
        }
        Write-Success "Local .env file found and loaded"
    } else {
        Write-Warning "Local .env file not found, using defaults"
        $script:SECRET_KEY = "django-insecure-peykan-tourism-dev-2024"
        $script:DATABASE_URL = "sqlite:///db.sqlite3"
        $script:DEBUG = "True"
        $script:CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:3001"
    }
    
    # Extract email configuration from local settings if available
    $settingsFile = "backend\peykan\settings.py"
    if (Test-Path $settingsFile) {
        $content = Get-Content $settingsFile -Raw
        if ($content -match 'EMAIL_HOST_USER\s*=\s*["'']([^"'']*)["'']') {
            $script:EMAIL_HOST_USER = $matches[1]
        }
        if ($content -match 'EMAIL_HOST_PASSWORD\s*=\s*["'']([^"'']*)["'']') {
            $script:EMAIL_HOST_PASSWORD = $matches[1]
        }
        if ($content -match 'KAVENEGAR_API_KEY\s*=\s*["'']([^"'']*)["'']') {
            $script:KAVENEGAR_API_KEY = $matches[1]
        }
        if ($content -match 'PAYMENT_SECRET_KEY\s*=\s*["'']([^"'']*)["'']') {
            $script:PAYMENT_SECRET_KEY = $matches[1]
        }
    }
}

# Function to create production environment file
function Create-ProductionEnv {
    Write-Status "Creating production environment file..."
    
    # Generate secure production keys
    $prodSecretKey = Generate-SecretKey
    $prodJwtSecretKey = Generate-SecretKey
    
    # Create production .env file
    $emailHostUser = if ($script:EMAIL_HOST_USER) { $script:EMAIL_HOST_USER } else { "your-email@gmail.com" }
    $emailHostPassword = if ($script:EMAIL_HOST_PASSWORD) { $script:EMAIL_HOST_PASSWORD } else { "your-app-password" }
    $defaultFromEmail = if ($script:EMAIL_HOST_USER) { $script:EMAIL_HOST_USER } else { "noreply@$Domain" }
    $kavenegarApiKey = if ($script:KAVENEGAR_API_KEY) { $script:KAVENEGAR_API_KEY } else { "your-kavenegar-api-key" }
    $paymentSecretKey = if ($script:PAYMENT_SECRET_KEY) { $script:PAYMENT_SECRET_KEY } else { "your-stripe-secret-key" }

    $envContent = @"
# Production Environment Variables for Peykan Tourism Platform
# Generated automatically by deploy.ps1

# Django Settings
DEBUG=False
SECRET_KEY=$prodSecretKey
ALLOWED_HOSTS=$Domain,www.$Domain,localhost,127.0.0.1

# Database - PostgreSQL for production
DATABASE_URL=postgresql://peykan_user:peykan_password@postgres:5432/peykan

# Redis Cache
REDIS_URL=redis://redis:6379/1

# CORS - Production settings
CORS_ALLOWED_ORIGINS=https://$Domain,https://www.$Domain,http://localhost:3000

# Internationalization
LANGUAGES=fa,en,tr
DEFAULT_LANGUAGE=fa

# Currency
DEFAULT_CURRENCY=USD
SUPPORTED_CURRENCIES=USD,EUR,TRY,IRR

# Email Configuration - Extract from local if available
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$emailHostUser
EMAIL_HOST_PASSWORD=$emailHostPassword
DEFAULT_FROM_EMAIL=$defaultFromEmail

# Kavenegar SMS - Extract from local if available
KAVENEGAR_API_KEY=$kavenegarApiKey

# File Storage
MEDIA_URL=/media/
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# JWT Settings
JWT_SECRET_KEY=$prodJwtSecretKey
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1440

# Payment Gateway - Extract from local if available
PAYMENT_GATEWAY=stripe
PAYMENT_SECRET_KEY=$paymentSecretKey

# Security Settings - Production
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
"@

    $envContent | Out-File -FilePath "backend\.env.production" -Encoding UTF8
    Write-Success "Production environment file created: backend\.env.production"
}

# Function to update docker-compose.yml for production
function Update-DockerCompose {
    Write-Status "Updating docker-compose.yml for production..."
    
    # Create production docker-compose file
    $composeContent = @"
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: peykan
      POSTGRES_USER: peykan_user
      POSTGRES_PASSWORD: peykan_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U peykan_user -d peykan"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Django Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/.env.production
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://peykan_user:peykan_password@postgres:5432/peykan
      - REDIS_URL=redis://redis:6379/1
      - DJANGO_SETTINGS_MODULE=peykan.settings_production
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./backend/logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn peykan.wsgi:application --bind 0.0.0.0:8000 --workers 3 --worker-class gevent"

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=https://$Domain/api/v1
      - NEXT_PUBLIC_SITE_URL=https://$Domain
      - NODE_ENV=production
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - nginx_logs:/var/log/nginx
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  nginx_logs:

networks:
  default:
    name: peykan_network
"@

    $composeContent | Out-File -FilePath "docker-compose.production.yml" -Encoding UTF8
    Write-Success "Production docker-compose file created: docker-compose.production.yml"
}

# Function to create SSL certificates
function Create-SSLCertificates {
    Write-Status "Creating SSL certificates..."
    
    # Create SSL directory
    if (!(Test-Path "nginx\ssl")) {
        New-Item -ItemType Directory -Path "nginx\ssl" -Force | Out-Null
    }
    
    # Check if OpenSSL is available
    try {
        $null = Get-Command openssl -ErrorAction Stop
        Write-Status "Generating self-signed SSL certificates..."
        $opensslCmd = "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -subj '/C=TR/ST=Istanbul/L=Istanbul/O=PeykanTravel/CN=$Domain'"
        Invoke-Expression $opensslCmd
        Write-Success "SSL certificates created in nginx/ssl/"
    } catch {
        Write-Warning "OpenSSL not found. Please install OpenSSL or provide certificates manually."
        Write-Status "For production, use Let's Encrypt:"
        Write-Status "certbot certonly --standalone -d $Domain -d www.$Domain"
    }
}

# Function to create deployment script for server
function Create-ServerDeployScript {
    Write-Status "Creating server deployment script..."
    
    $serverScript = @'
#!/bin/bash

# Server-side deployment script
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system
print_status "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    sudo apt install docker.io docker-compose -y
    sudo usermod -aG docker $USER
    newgrp docker
fi

# Clone or pull repository
if [ -d "peykan-tourism" ]; then
    print_status "Pulling latest changes..."
    cd peykan-tourism
    git pull origin main
else
    print_status "Cloning repository..."
    git clone https://github.com/PeykanTravel/peykan-tourism.git
    cd peykan-tourism
fi

# Copy production environment file
if [ -f "backend/.env.production" ]; then
    print_status "Setting up environment..."
    cp backend/.env.production backend/.env
else
    print_error "Production environment file not found!"
    exit 1
fi

# Create SSL directory if not exists
mkdir -p nginx/ssl

# Build and start services
print_status "Building containers..."
docker-compose -f docker-compose.production.yml build

print_status "Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T backend python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.production.yml exec -T backend python manage.py collectstatic --noinput

# Create superuser if needed
print_status "Checking for superuser..."
if ! docker-compose -f docker-compose.production.yml exec -T backend python manage.py shell -c "from django.contrib.auth.models import User; print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" 2>/dev/null | grep -q "Superuser exists"; then
    print_status "Creating superuser..."
    docker-compose -f docker-compose.production.yml exec -T backend python manage.py createsuperuser --noinput || true
fi

# Check service status
print_status "Checking service status..."
docker-compose -f docker-compose.production.yml ps

print_success "Deployment completed successfully!"
print_status "Check logs with: docker-compose -f docker-compose.production.yml logs -f"
print_status "Access the application at: https://peykantravelistanbul.com"
'@

    $serverScript | Out-File -FilePath "deploy-server.sh" -Encoding UTF8
    Write-Success "Server deployment script created: deploy-server.sh"
}

# Function to create SSH deployment script
function Create-SSHDeployScript {
    Write-Status "Creating SSH deployment script..."
    
    $sshScript = @"
# SSH deployment script
# Run this script to deploy via SSH

Write-Host "Connecting to server and deploying..." -ForegroundColor Blue

# Copy files to server
Write-Host "Copying deployment files to server..." -ForegroundColor Blue
scp -r backend\.env.production ${ServerUser}@${ServerIP}:~/peykan-tourism/backend/.env.production
scp docker-compose.production.yml ${ServerUser}@${ServerIP}:~/peykan-tourism/
scp deploy-server.sh ${ServerUser}@${ServerIP}:~/peykan-tourism/

# Execute deployment on server
Write-Host "Executing deployment on server..." -ForegroundColor Blue
ssh ${ServerUser}@${ServerIP} "cd ~/peykan-tourism && chmod +x deploy-server.sh && ./deploy-server.sh"

Write-Host "SSH deployment completed!" -ForegroundColor Green
Write-Host "Check server status: ssh ${ServerUser}@${ServerIP}" -ForegroundColor Blue
Write-Host "View logs: ssh ${ServerUser}@${ServerIP} 'cd peykan-tourism && docker-compose -f docker-compose.production.yml logs -f'" -ForegroundColor Blue
"@

    $sshScript | Out-File -FilePath "deploy-ssh.ps1" -Encoding UTF8
    Write-Success "SSH deployment script created: deploy-ssh.ps1"
}

# Function to create environment variable prompt script
function Create-EnvPromptScript {
    Write-Status "Creating environment variable prompt script..."
    
    $envPromptScript = @'
# Interactive environment setup script
# Run this script to set up environment variables interactively

Write-Host "Setting up production environment variables..." -ForegroundColor Blue
Write-Host "This script will prompt for sensitive information. Make sure you're in a secure environment." -ForegroundColor Yellow

# Start with basic template
$envContent = @"
# Production Environment Variables for Peykan Tourism Platform
# Generated by setup-env.ps1

# Django Settings
DEBUG=False
SECRET_KEY=django-insecure-peykan-tourism-prod-2024
ALLOWED_HOSTS=peykantravelistanbul.com,www.peykantravelistanbul.com,localhost,127.0.0.1

# Database - PostgreSQL for production
DATABASE_URL=postgresql://peykan_user:peykan_password@postgres:5432/peykan

# Redis Cache
REDIS_URL=redis://redis:6379/1

# CORS - Production settings
CORS_ALLOWED_ORIGINS=https://peykantravelistanbul.com,https://www.peykantravelistanbul.com,http://localhost:3000

# Internationalization
LANGUAGES=fa,en,tr
DEFAULT_LANGUAGE=fa

# Currency
DEFAULT_CURRENCY=USD
SUPPORTED_CURRENCIES=USD,EUR,TRY,IRR

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@peykantravelistanbul.com

# File Storage
MEDIA_URL=/media/
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# JWT Settings
JWT_SECRET_KEY=jwt-secret-key-change-this
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1440

# Payment Gateway
PAYMENT_GATEWAY=stripe

# Security Settings - Production
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True

"@

$envContent | Out-File -FilePath "backend\.env.production" -Encoding UTF8

# Prompt for sensitive values
Write-Host ""
$emailUser = Read-Host "Enter EMAIL_HOST_USER (e.g., your-email@gmail.com)"
$emailPass = Read-Host "Enter EMAIL_HOST_PASSWORD (for Gmail, use App Password)" -AsSecureString
$kavenegarKey = Read-Host "Enter KAVENEGAR_API_KEY" -AsSecureString
$paymentKey = Read-Host "Enter PAYMENT_SECRET_KEY (starts with sk_)" -AsSecureString

# Convert secure strings to plain text
$emailPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($emailPass))
$kavenegarKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($kavenegarKey))
$paymentKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($paymentKey))

# Add the values to the file
Add-Content -Path "backend\.env.production" -Value "EMAIL_HOST_USER=$emailUser"
Add-Content -Path "backend\.env.production" -Value "EMAIL_HOST_PASSWORD=$emailPassPlain"
Add-Content -Path "backend\.env.production" -Value "KAVENEGAR_API_KEY=$kavenegarKeyPlain"
Add-Content -Path "backend\.env.production" -Value "PAYMENT_SECRET_KEY=$paymentKeyPlain"

Write-Host "Environment file created: backend\.env.production" -ForegroundColor Green
Write-Host "Please review the file and update SECRET_KEY and JWT_SECRET_KEY with secure values if needed." -ForegroundColor Yellow
'@

    $envPromptScript | Out-File -FilePath "setup-env.ps1" -Encoding UTF8
    Write-Success "Environment setup script created: setup-env.ps1"
}

# Function to validate server environment
function Test-ServerEnvironment {
    Write-Status "Validating server environment..."
    
    $errors = @()
    $warnings = @()
    
    # Test SSH connectivity
    Write-Status "Testing SSH connectivity to server..."
    try {
        $sshTest = ssh -o ConnectTimeout=10 -o BatchMode=yes ${ServerUser}@${ServerIP} "echo 'SSH connection successful'" 2>&1
        if ($LASTEXITCODE -ne 0) {
            $errors += "SSH connection failed to ${ServerUser}@${ServerIP}. Please check SSH keys and connectivity."
        } else {
            Write-Success "SSH connectivity: OK"
        }
    } catch {
        $errors += "SSH connection failed: $($_.Exception.Message)"
    }
    
    # Test server requirements via SSH
    if ($errors.Count -eq 0) {
        Write-Status "Checking server requirements..."
        
        # Check Docker
        $dockerCheck = ssh ${ServerUser}@${ServerIP} "command -v docker >/dev/null 2>&1 && docker --version || echo 'DOCKER_MISSING'"
        if ($dockerCheck -match "DOCKER_MISSING") {
            $warnings += "Docker not installed on server. Will install during deployment."
        } else {
            Write-Success "Docker: $dockerCheck"
        }
        
        # Check Docker Compose
        $composeCheck = ssh ${ServerUser}@${ServerIP} "command -v docker-compose >/dev/null 2>&1 && docker-compose --version || echo 'COMPOSE_MISSING'"
        if ($composeCheck -match "COMPOSE_MISSING") {
            $warnings += "Docker Compose not installed on server. Will install during deployment."
        } else {
            Write-Success "Docker Compose: $composeCheck"
        }
        
        # Check Git
        $gitCheck = ssh ${ServerUser}@${ServerIP} "command -v git >/dev/null 2>&1 && git --version || echo 'GIT_MISSING'"
        if ($gitCheck -match "GIT_MISSING") {
            $errors += "Git not installed on server. Required for deployment."
        } else {
            Write-Success "Git: $gitCheck"
        }
        
        # Check disk space (need at least 5GB free)
        $diskCheck = ssh ${ServerUser}@${ServerIP} "df -h / | tail -1 | awk '{print \$4}' | sed 's/G//'"
        if ($diskCheck -match "^\d+$" -and [int]$diskCheck -lt 5) {
            $errors += "Insufficient disk space. Need at least 5GB free, found ${diskCheck}GB"
        } else {
            Write-Success "Disk space: ${diskCheck}GB available"
        }
        
        # Check memory (need at least 2GB free)
        $memoryCheck = ssh ${ServerUser}@${ServerIP} "free -m | grep Mem | awk '{print \$7}'"
        if ($memoryCheck -match "^\d+$" -and [int]$memoryCheck -lt 2048) {
            $warnings += "Low memory available: ${memoryCheck}MB. Recommended: 2GB+ free"
        } else {
            Write-Success "Memory: ${memoryCheck}MB available"
        }
        
        # Check if ports 80, 443, 8000, 3000 are available
        Write-Status "Checking port availability..."
        $ports = @(80, 443, 8000, 3000)
        foreach ($port in $ports) {
            $portCheck = ssh ${ServerUser}@${ServerIP} "netstat -tuln | grep ':$port ' || echo 'PORT_FREE'"
            if ($portCheck -notmatch "PORT_FREE") {
                $errors += "Port $port is already in use. Please free up the port before deployment."
            } else {
                Write-Success "Port $port`: Available"
            }
        }
        
        # Check domain DNS resolution
        Write-Status "Checking domain DNS resolution..."
        $dnsCheck = ssh ${ServerUser}@${ServerIP} "nslookup $Domain 2>/dev/null | grep -q 'Address:' && echo 'DNS_OK' || echo 'DNS_FAIL'"
        if ($dnsCheck -match "DNS_FAIL") {
            $warnings += "Domain $Domain does not resolve to this server. SSL certificates may fail."
        } else {
            Write-Success "Domain DNS: $Domain resolves correctly"
        }
        
        # Check if project directory exists and has proper permissions
        $dirCheck = ssh ${ServerUser}@${ServerIP} "test -d ~/peykan-tourism && echo 'DIR_EXISTS' || echo 'DIR_MISSING'"
        if ($dirCheck -match "DIR_MISSING") {
            Write-Success "Project directory will be created during deployment"
        } else {
            $permCheck = ssh ${ServerUser}@${ServerIP} "test -w ~/peykan-tourism && echo 'WRITE_OK' || echo 'WRITE_FAIL'"
            if ($permCheck -match "WRITE_FAIL") {
                $errors += "No write permission to ~/peykan-tourism directory"
            } else {
                Write-Success "Project directory: Write permissions OK"
            }
        }
    }
    
    # Display results
    if ($errors.Count -gt 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Red
        Write-Host "CRITICAL ERRORS FOUND:" -ForegroundColor Red
        Write-Host "==========================================" -ForegroundColor Red
        foreach ($err in $errors) {
            Write-Host "❌ $err" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Please fix these issues before proceeding with deployment." -ForegroundColor Red
        Write-Host "==========================================" -ForegroundColor Red
        return $false
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Yellow
        Write-Host "WARNINGS:" -ForegroundColor Yellow
        Write-Host "==========================================" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "⚠️  $warning" -ForegroundColor Yellow
        }
        Write-Host ""
        $continue = Read-Host "Do you want to continue with deployment? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "Deployment cancelled by user." -ForegroundColor Yellow
            return $false
        }
    }
    
    Write-Success "Server environment validation completed successfully!"
    return $true
}

# Function to validate local environment
function Test-LocalEnvironment {
    Write-Status "Validating local environment..."
    
    $errors = @()
    
    # Check if we're in the right directory
    if (!(Test-Path "docker-compose.yml")) {
        $errors += "docker-compose.yml not found. Please run this script from the project root directory."
    }
    if (!(Test-Path "backend")) {
        $errors += "backend directory not found. Please run this script from the project root directory."
    }
    if (!(Test-Path "frontend")) {
        $errors += "frontend directory not found. Please run this script from the project root directory."
    }
    
    # Check if required files exist
    if (!(Test-Path "backend\Dockerfile")) {
        $errors += "backend\Dockerfile not found."
    }
    if (!(Test-Path "frontend\Dockerfile")) {
        $errors += "frontend\Dockerfile not found."
    }
    if (!(Test-Path "nginx\Dockerfile")) {
        $errors += "nginx\Dockerfile not found."
    }
    
    # Check if SSH key exists
    if (!(Test-Path "$env:USERPROFILE\.ssh\id_rsa")) {
        $errors += "SSH private key not found at $env:USERPROFILE\.ssh\id_rsa. Please set up SSH authentication."
    }
    
    # Check if Git is available
    try {
        $null = git --version
        Write-Success "Git: Available"
    } catch {
        $errors += "Git not found. Please install Git."
    }
    
    # Check if we can connect to GitHub
    try {
        $gitTest = git ls-remote https://github.com/PeykanTravel/peykan-tourism.git 2>&1
        if ($LASTEXITCODE -ne 0) {
            $errors += "Cannot connect to GitHub repository. Please check your internet connection."
        } else {
            Write-Success "GitHub repository: Accessible"
        }
    } catch {
        $errors += "GitHub connectivity test failed: $($_.Exception.Message)"
    }
    
    # Check if OpenSSL is available (optional)
    try {
        $null = Get-Command openssl -ErrorAction Stop
        Write-Success "OpenSSL: Available for SSL certificate generation"
    } catch {
        Write-Warning "OpenSSL not found. SSL certificates will need to be generated manually or using Let's Encrypt."
    }
    
    # Display results
    if ($errors.Count -gt 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Red
        Write-Host "LOCAL ENVIRONMENT ERRORS:" -ForegroundColor Red
        Write-Host "==========================================" -ForegroundColor Red
        foreach ($err in $errors) {
            Write-Host "❌ $err" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Please fix these issues before proceeding with deployment." -ForegroundColor Red
        Write-Host "==========================================" -ForegroundColor Red
        return $false
    }
    
    Write-Success "Local environment validation completed successfully!"
    return $true
}

# Main deployment function
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Peykan Tourism Platform - Production Deployment" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Validate local environment first
    if (!(Test-LocalEnvironment)) {
        exit 1
    }
    
    # Validate server environment
    if (!(Test-ServerEnvironment)) {
        exit 1
    }
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "ENVIRONMENT VALIDATION PASSED!" -ForegroundColor Green
    Write-Host "Proceeding with deployment preparation..." -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    
    # Extract local environment variables
    Extract-LocalEnv
    
    # Create production environment file
    Create-ProductionEnv
    
    # Update docker-compose for production
    Update-DockerCompose
    
    # Create SSL certificates
    Create-SSLCertificates
    
    # Create server deployment script
    Create-ServerDeployScript
    
    # Create SSH deployment script
    Create-SSHDeployScript
    
    # Create environment setup script
    Create-EnvPromptScript
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Success "Deployment files created successfully!"
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Review and update backend\.env.production with actual values" -ForegroundColor White
    Write-Host "2. Run: .\setup-env.ps1 (for interactive environment setup)" -ForegroundColor White
    Write-Host "3. Run: .\deploy-ssh.ps1 (to deploy via SSH)" -ForegroundColor White
    Write-Host "4. Or manually copy files to server and run: ./deploy-server.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "Files created:" -ForegroundColor White
    Write-Host "- backend\.env.production (production environment)" -ForegroundColor White
    Write-Host "- docker-compose.production.yml (production compose)" -ForegroundColor White
    Write-Host "- deploy-server.sh (server deployment script)" -ForegroundColor White
    Write-Host "- deploy-ssh.ps1 (SSH deployment script)" -ForegroundColor White
    Write-Host "- setup-env.ps1 (interactive environment setup)" -ForegroundColor White
    Write-Host "- nginx\ssl\ (SSL certificates)" -ForegroundColor White
    Write-Host ""
    Write-Warning "IMPORTANT: Update backend\.env.production with real API keys and credentials before deployment!"
}

# Run main function
Main 