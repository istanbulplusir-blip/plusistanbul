#!/bin/bash
set -e

# Modern Production Deployment Script for Peykan Tourism Platform
# Usage: ./deploy-production.sh

echo "🚀 Starting Modern Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if .env.production exists
if [ ! -f "backend/.env.production" ]; then
    print_error ".env.production file not found!"
    print_warning "Please copy env.production.template to .env.production and update the values"
    print_info "Run: cp backend/env.production.template backend/.env.production"
    exit 1
fi

# Check if required environment variables are set
print_status "Checking environment variables..."
source backend/.env.production

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE_THIS_TO_A_STRONG_SECRET_KEY_MINIMUM_50_CHARACTERS" ]; then
    print_error "SECRET_KEY is not set or is using default value!"
    print_warning "Please generate a strong SECRET_KEY"
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    print_error "POSTGRES_PASSWORD is not set!"
    exit 1
fi

if [ -z "$REDIS_PASSWORD" ]; then
    print_error "REDIS_PASSWORD is not set!"
    exit 1
fi

print_status "Environment variables check passed!"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p postgres redis nginx/ssl backend/logs

# Generate SSL certificates if they don't exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/CN=yourdomain.com"
    print_status "Self-signed SSL certificates generated!"
    print_warning "⚠️  IMPORTANT: For production, replace with real SSL certificates from Let's Encrypt"
    print_info "Run: sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.production-secure.yml down

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.production-secure.yml up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service health..."
if ! docker-compose -f docker-compose.production-secure.yml ps | grep -q "Up"; then
    print_error "Some services failed to start!"
    docker-compose -f docker-compose.production-secure.yml logs
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py migrate --noinput

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py collectstatic --noinput

# Create superuser if needed
print_status "Checking for superuser..."
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually.')
    print('Run: docker-compose -f docker-compose.production-secure.yml exec backend python manage.py createsuperuser')
else:
    print('Superuser exists.')
"

# Final health check
print_status "Performing final health check..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_status "✅ Deployment successful! Application is running at http://localhost"
else
    print_warning "Health check failed. Please check the logs:"
    docker-compose -f docker-compose.production-secure.yml logs
fi

print_status "🎉 Modern Production Deployment completed!"
print_info "Next steps:"
echo "1. Create a superuser: docker-compose -f docker-compose.production-secure.yml exec backend python manage.py createsuperuser"
echo "2. Replace self-signed SSL certificates with Let's Encrypt certificates"
echo "3. Configure your domain DNS to point to this server"
echo "4. Set up monitoring and automated backups"
echo "5. Configure log rotation and monitoring alerts"
echo "6. Test all functionality in production environment"
echo ""
print_warning "Security reminders:"
echo "• Ensure all passwords are strong and unique"
echo "• Regularly update dependencies and security patches"
echo "• Monitor logs for suspicious activity"
echo "• Set up automated backups"
