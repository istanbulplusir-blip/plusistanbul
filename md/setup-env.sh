#!/bin/bash

# Environment Setup Script for Peykan Tourism Platform
# This script helps you configure environment variables interactively

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    error "Environment file not found. Please run the deployment script first."
fi

log "Setting up environment variables for Peykan Tourism Platform"
echo ""

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        echo "${var_name}=${input:-$default}"
    else
        read -p "$prompt: " input
        echo "${var_name}=$input"
    fi
}

# Function to prompt for secret input
prompt_secret() {
    local prompt="$1"
    local var_name="$2"
    
    read -s -p "$prompt: " input
    echo ""
    echo "${var_name}=$input"
}

# Generate secure secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(50))"
}

# Backup existing .env file
if [ -f "backend/.env" ]; then
    cp backend/.env backend/.env.backup.$(date +%Y%m%d_%H%M%S)
    log "Backed up existing .env file"
fi

# Create new .env file
log "Configuring environment variables..."

# Django Settings
echo "# Django Settings" > backend/.env
echo "$(prompt_with_default "DEBUG mode" "False" "DEBUG")" >> backend/.env
echo "$(prompt_secret "Django Secret Key (leave empty to generate)" "SECRET_KEY")" >> backend/.env

# If secret key is empty, generate one
if grep -q "SECRET_KEY=$" backend/.env; then
    SECRET_KEY=$(generate_secret_key)
    sed -i "s/SECRET_KEY=/SECRET_KEY=$SECRET_KEY/" backend/.env
    log "Generated secure Django secret key"
fi

echo "$(prompt_with_default "Allowed Hosts (comma-separated)" "localhost,127.0.0.1" "ALLOWED_HOSTS")" >> backend/.env
echo "" >> backend/.env

# Database
echo "# Database" >> backend/.env
echo "$(prompt_with_default "Database URL" "postgresql://peykan_user:peykan_password@postgres:5432/peykan" "DATABASE_URL")" >> backend/.env
echo "" >> backend/.env

# Redis
echo "# Redis" >> backend/.env
echo "$(prompt_with_default "Redis URL" "redis://redis:6379/1" "REDIS_URL")" >> backend/.env
echo "" >> backend/.env

# CORS
echo "# CORS" >> backend/.env
echo "$(prompt_with_default "CORS Allowed Origins (comma-separated)" "http://localhost:3000,http://127.0.0.1:3000" "CORS_ALLOWED_ORIGINS")" >> backend/.env
echo "" >> backend/.env

# Internationalization
echo "# Internationalization" >> backend/.env
echo "$(prompt_with_default "Languages (comma-separated)" "fa,en,tr" "LANGUAGES")" >> backend/.env
echo "$(prompt_with_default "Default Language" "fa" "DEFAULT_LANGUAGE")" >> backend/.env
echo "" >> backend/.env

# Currency
echo "# Currency" >> backend/.env
echo "$(prompt_with_default "Default Currency" "USD" "DEFAULT_CURRENCY")" >> backend/.env
echo "$(prompt_with_default "Supported Currencies (comma-separated)" "USD,EUR,TRY,IRR" "SUPPORTED_CURRENCIES")" >> backend/.env
echo "" >> backend/.env

# Email Configuration
echo "# Email Configuration" >> backend/.env
echo "$(prompt_with_default "Email Backend" "django.core.mail.backends.smtp.EmailBackend" "EMAIL_BACKEND")" >> backend/.env
echo "$(prompt_with_default "Email Host" "smtp.gmail.com" "EMAIL_HOST")" >> backend/.env
echo "$(prompt_with_default "Email Port" "587" "EMAIL_PORT")" >> backend/.env
echo "$(prompt_with_default "Email Use TLS" "True" "EMAIL_USE_TLS")" >> backend/.env
echo "$(prompt_with_default "Email Host User" "" "EMAIL_HOST_USER")" >> backend/.env
echo "$(prompt_secret "Email Host Password" "EMAIL_HOST_PASSWORD")" >> backend/.env
echo "$(prompt_with_default "Default From Email" "" "DEFAULT_FROM_EMAIL")" >> backend/.env
echo "" >> backend/.env

# SMS Configuration
echo "# SMS Configuration" >> backend/.env
echo "$(prompt_with_default "Kavenegar API Key" "" "KAVENEGAR_API_KEY")" >> backend/.env
echo "" >> backend/.env

# File Storage
echo "# File Storage" >> backend/.env
echo "$(prompt_with_default "Media URL" "/media/" "MEDIA_URL")" >> backend/.env
echo "$(prompt_with_default "Static URL" "/static/" "STATIC_URL")" >> backend/.env
echo "$(prompt_with_default "Static Root" "staticfiles/" "STATIC_ROOT")" >> backend/.env
echo "" >> backend/.env

# JWT Settings
echo "# JWT Settings" >> backend/.env
echo "$(prompt_secret "JWT Secret Key (leave empty to generate)" "JWT_SECRET_KEY")" >> backend/.env

# If JWT secret key is empty, generate one
if grep -q "JWT_SECRET_KEY=$" backend/.env; then
    JWT_SECRET_KEY=$(generate_secret_key)
    sed -i "s/JWT_SECRET_KEY=/JWT_SECRET_KEY=$JWT_SECRET_KEY/" backend/.env
    log "Generated secure JWT secret key"
fi

echo "$(prompt_with_default "JWT Access Token Lifetime (minutes)" "30" "JWT_ACCESS_TOKEN_LIFETIME")" >> backend/.env
echo "$(prompt_with_default "JWT Refresh Token Lifetime (minutes)" "1440" "JWT_REFRESH_TOKEN_LIFETIME")" >> backend/.env
echo "" >> backend/.env

# Payment Gateway
echo "# Payment Gateway" >> backend/.env
echo "$(prompt_with_default "Payment Gateway" "stripe" "PAYMENT_GATEWAY")" >> backend/.env
echo "$(prompt_secret "Payment Secret Key" "PAYMENT_SECRET_KEY")" >> backend/.env
echo "" >> backend/.env

# Security Settings
echo "# Security Settings" >> backend/.env
echo "$(prompt_with_default "Session Cookie Secure" "True" "SESSION_COOKIE_SECURE")" >> backend/.env
echo "$(prompt_with_default "CSRF Cookie Secure" "True" "CSRF_COOKIE_SECURE")" >> backend/.env
echo "$(prompt_with_default "Secure SSL Redirect" "True" "SECURE_SSL_REDIRECT")" >> backend/.env
echo "$(prompt_with_default "HSTS Seconds" "31536000" "SECURE_HSTS_SECONDS")" >> backend/.env
echo "$(prompt_with_default "HSTS Include Subdomains" "True" "SECURE_HSTS_INCLUDE_SUBDOMAINS")" >> backend/.env
echo "$(prompt_with_default "Browser XSS Filter" "True" "SECURE_BROWSER_XSS_FILTER")" >> backend/.env
echo "$(prompt_with_default "Content Type Nosniff" "True" "SECURE_CONTENT_TYPE_NOSNIFF")" >> backend/.env

log "Environment configuration completed!"
echo ""
warn "Important: Review the generated backend/.env file and update any values as needed."
echo ""
log "Next steps:"
echo "1. Review: nano backend/.env"
echo "2. Restart services: docker-compose restart"
echo "3. Test application: https://your-domain.com"
echo ""

# Set proper permissions
chmod 600 backend/.env
log "Set secure permissions on .env file" 