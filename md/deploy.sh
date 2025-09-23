#!/bin/bash

# Peykan Tourism Platform - Automated Production Deployment Script
# This script extracts local environment variables and deploys to production server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="peykan-tourism"
SERVER_IP="167.235.140.125"
SERVER_USER="djangouser"
DOMAIN="peykantravelistanbul.com"
GITHUB_REPO="https://github.com/PeykanTravel/peykan-tourism.git"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to generate secure random strings
generate_secret_key() {
    python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
}

# Function to extract local environment variables
extract_local_env() {
    print_status "Extracting local environment variables..."
    
    # Read local .env file
    if [ -f "backend/.env" ]; then
        source backend/.env
        print_success "Local .env file found and loaded"
    else
        print_warning "Local .env file not found, using defaults"
        # Set default values
        SECRET_KEY="django-insecure-peykan-tourism-dev-2024"
        DATABASE_URL="sqlite:///db.sqlite3"
        DEBUG="True"
        CORS_ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001"
    fi
    
    # Extract email configuration from local settings if available
    if [ -f "backend/peykan/settings.py" ]; then
        EMAIL_HOST_USER=$(grep -o 'EMAIL_HOST_USER\s*=\s*["'"'"'][^"'"'"']*["'"'"']' backend/peykan/settings.py | cut -d'"' -f2 || echo "")
        EMAIL_HOST_PASSWORD=$(grep -o 'EMAIL_HOST_PASSWORD\s*=\s*["'"'"'][^"'"'"']*["'"'"']' backend/peykan/settings.py | cut -d'"' -f2 || echo "")
        KAVENEGAR_API_KEY=$(grep -o 'KAVENEGAR_API_KEY\s*=\s*["'"'"'][^"'"'"']*["'"'"']' backend/peykan/settings.py | cut -d'"' -f2 || echo "")
        PAYMENT_SECRET_KEY=$(grep -o 'PAYMENT_SECRET_KEY\s*=\s*["'"'"'][^"'"'"']*["'"'"']' backend/peykan/settings.py | cut -d'"' -f2 || echo "")
    fi
}

# Function to create production environment file
create_production_env() {
    print_status "Creating production environment file..."
    
    # Generate secure production keys
    PROD_SECRET_KEY=$(generate_secret_key)
    PROD_JWT_SECRET_KEY=$(generate_secret_key)
    
    # Create production .env file
    cat > backend/.env.production << EOF
# Production Environment Variables for Peykan Tourism Platform
# Generated automatically by deploy.sh

# Django Settings
DEBUG=False
SECRET_KEY=${PROD_SECRET_KEY}
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost,127.0.0.1

# Database - PostgreSQL for production
DATABASE_URL=postgresql://peykan_user:peykan_password@postgres:5432/peykan

# Redis Cache
REDIS_URL=redis://redis:6379/1

# CORS - Production settings
CORS_ALLOWED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN},http://localhost:3000

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
EMAIL_HOST_USER=${EMAIL_HOST_USER:-your-email@gmail.com}
EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD:-your-app-password}
DEFAULT_FROM_EMAIL=${EMAIL_HOST_USER:-noreply@${DOMAIN}}

# Kavenegar SMS - Extract from local if available
KAVENEGAR_API_KEY=${KAVENEGAR_API_KEY:-your-kavenegar-api-key}

# File Storage
MEDIA_URL=/media/
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# JWT Settings
JWT_SECRET_KEY=${PROD_JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1440

# Payment Gateway - Extract from local if available
PAYMENT_GATEWAY=stripe
PAYMENT_SECRET_KEY=${PAYMENT_SECRET_KEY:-your-stripe-secret-key}

# Security Settings - Production
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
EOF

    print_success "Production environment file created: backend/.env.production"
}

# Function to update docker-compose.yml for production
update_docker_compose() {
    print_status "Updating docker-compose.yml for production..."
    
    # Create production docker-compose file
    cat > docker-compose.production.yml << EOF
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
      - NEXT_PUBLIC_API_URL=https://${DOMAIN}/api/v1
      - NEXT_PUBLIC_SITE_URL=https://${DOMAIN}
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
EOF

    print_success "Production docker-compose file created: docker-compose.production.yml"
}

# Function to create SSL certificates
create_ssl_certificates() {
    print_status "Creating SSL certificates..."
    
    # Create SSL directory
    mkdir -p nginx/ssl
    
    # Generate self-signed certificates for testing
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=TR/ST=Istanbul/L=Istanbul/O=PeykanTravel/CN=${DOMAIN}" \
        2>/dev/null || {
        print_warning "Could not generate SSL certificates. Please install OpenSSL or provide certificates manually."
        print_status "For production, use Let's Encrypt:"
        print_status "certbot certonly --standalone -d ${DOMAIN} -d www.${DOMAIN}"
    }
    
    print_success "SSL certificates created in nginx/ssl/"
}

# Function to create deployment script for server
create_server_deploy_script() {
    print_status "Creating server deployment script..."
    
    cat > deploy-server.sh << 'EOF'
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
EOF

    chmod +x deploy-server.sh
    print_success "Server deployment script created: deploy-server.sh"
}

# Function to create SSH deployment script
create_ssh_deploy_script() {
    print_status "Creating SSH deployment script..."
    
    cat > deploy-ssh.sh << EOF
#!/bin/bash

# SSH deployment script
set -e

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m \$1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m \$1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m \$1"
}

# Check if SSH key is available
if [ ! -f ~/.ssh/id_rsa ]; then
    print_error "SSH key not found. Please set up SSH authentication first."
    exit 1
fi

print_status "Connecting to server and deploying..."

# Copy files to server
print_status "Copying deployment files to server..."
scp -r backend/.env.production ${SERVER_USER}@${SERVER_IP}:~/peykan-tourism/backend/.env.production
scp docker-compose.production.yml ${SERVER_USER}@${SERVER_IP}:~/peykan-tourism/
scp deploy-server.sh ${SERVER_USER}@${SERVER_IP}:~/peykan-tourism/

# Execute deployment on server
print_status "Executing deployment on server..."
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd ~/peykan-tourism
chmod +x deploy-server.sh
./deploy-server.sh
ENDSSH

print_success "SSH deployment completed!"
print_status "Check server status: ssh ${SERVER_USER}@${SERVER_IP}"
print_status "View logs: ssh ${SERVER_USER}@${SERVER_IP} 'cd peykan-tourism && docker-compose -f docker-compose.production.yml logs -f'"
EOF

    chmod +x deploy-ssh.sh
    print_success "SSH deployment script created: deploy-ssh.sh"
}

# Function to create environment variable prompt script
create_env_prompt_script() {
    print_status "Creating environment variable prompt script..."
    
    cat > setup-env.sh << 'EOF'
#!/bin/bash

# Interactive environment setup script
set -e

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

# Function to prompt for sensitive data
prompt_for_value() {
    local var_name=$1
    local description=$2
    local is_secret=$3
    
    echo ""
    print_status "$description"
    if [ "$is_secret" = "true" ]; then
        read -s -p "Enter $var_name: " value
        echo ""
    else
        read -p "Enter $var_name: " value
    fi
    
    echo "$var_name=$value" >> backend/.env.production
}

print_status "Setting up production environment variables..."
print_warning "This script will prompt for sensitive information. Make sure you're in a secure environment."

# Start with basic template
cat > backend/.env.production << 'TEMPLATE'
# Production Environment Variables for Peykan Tourism Platform
# Generated by setup-env.sh

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

TEMPLATE

# Prompt for sensitive values
prompt_for_value "EMAIL_HOST_USER" "Email address for SMTP (e.g., your-email@gmail.com)" false
prompt_for_value "EMAIL_HOST_PASSWORD" "Email app password (for Gmail, use App Password)" true
prompt_for_value "KAVENEGAR_API_KEY" "Kavenegar SMS API key" true
prompt_for_value "PAYMENT_SECRET_KEY" "Stripe secret key (starts with sk_)" true

print_success "Environment file created: backend/.env.production"
print_warning "Please review the file and update SECRET_KEY and JWT_SECRET_KEY with secure values if needed."
EOF

    chmod +x setup-env.sh
    print_success "Environment setup script created: setup-env.sh"
}

# Main deployment function
main() {
    echo "=========================================="
    echo "Peykan Tourism Platform - Production Deployment"
    echo "=========================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Extract local environment variables
    extract_local_env
    
    # Create production environment file
    create_production_env
    
    # Update docker-compose for production
    update_docker_compose
    
    # Create SSL certificates
    create_ssl_certificates
    
    # Create server deployment script
    create_server_deploy_script
    
    # Create SSH deployment script
    create_ssh_deploy_script
    
    # Create environment setup script
    create_env_prompt_script
    
    echo ""
    echo "=========================================="
    print_success "Deployment files created successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Review and update backend/.env.production with actual values"
    echo "2. Run: ./setup-env.sh (for interactive environment setup)"
    echo "3. Run: ./deploy-ssh.sh (to deploy via SSH)"
    echo "4. Or manually copy files to server and run: ./deploy-server.sh"
    echo ""
    echo "Files created:"
    echo "- backend/.env.production (production environment)"
    echo "- docker-compose.production.yml (production compose)"
    echo "- deploy-server.sh (server deployment script)"
    echo "- deploy-ssh.sh (SSH deployment script)"
    echo "- setup-env.sh (interactive environment setup)"
    echo "- nginx/ssl/ (SSL certificates)"
    echo ""
    print_warning "IMPORTANT: Update backend/.env.production with real API keys and credentials before deployment!"
}

# Run main function
main "$@" 