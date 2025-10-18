#!/bin/bash

# Production Deployment Script for Peykan Tourism Platform
# This script deploys the application to production with all necessary configurations

set -e

echo "🚀 Starting production deployment for Peykan Tourism Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Check if production environment file exists
if [ ! -f "backend/env.production" ]; then
    print_error "Production environment file not found: backend/env.production"
    print_status "Please create the production environment file first"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    ./generate-ssl-certs-production.sh
fi

# Backup existing data if containers exist
if docker ps -a --format "table {{.Names}}" | grep -q "peykan_"; then
    print_status "Backing up existing data..."
    
    # Create backup directory
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if docker ps --format "table {{.Names}}" | grep -q "peykan_postgres"; then
        print_status "Backing up database..."
        docker exec peykan_postgres pg_dump -U peykan_user peykan > "$BACKUP_DIR/database.sql"
    fi
    
    # Backup media files
    if docker ps --format "table {{.Names}}" | grep -q "peykan_backend"; then
        print_status "Backing up media files..."
        docker cp peykan_backend:/app/media "$BACKUP_DIR/"
    fi
    
    print_success "Backup completed: $BACKUP_DIR"
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.production-secure.yml down || true

# Pull latest images
print_status "Pulling latest images..."
docker-compose -f docker-compose.production-secure.yml pull

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.production-secure.yml up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service status..."
docker-compose -f docker-compose.production-secure.yml ps

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_status "Creating superuser (if not exists)..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@peykantravelistanbul.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Test health endpoints
print_status "Testing health endpoints..."

# Test backend health
if curl -f -s http://localhost/api/v1/health/ > /dev/null; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed"
fi

# Test frontend
if curl -f -s http://localhost/ > /dev/null; then
    print_success "Frontend health check passed"
else
    print_warning "Frontend health check failed"
fi

# Display deployment information
print_success "🎉 Production deployment completed!"
echo ""
echo "📋 Deployment Information:"
echo "  🌐 Frontend: https://peykantravelistanbul.com"
echo "  🔧 Backend API: https://peykantravelistanbul.com/api/v1/"
echo "  👨‍💼 Admin Panel: https://peykantravelistanbul.com/admin/"
echo "  📊 Health Check: https://peykantravelistanbul.com/health"
echo ""
echo "🔐 Admin Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  ⚠️  Please change the admin password immediately!"
echo ""
echo "📝 Next Steps:"
echo "  1. Update admin password"
echo "  2. Configure email settings"
echo "  3. Set up monitoring"
echo "  4. Configure backup strategy"
echo ""
echo "📊 View logs: docker-compose -f docker-compose.production-secure.yml logs -f"
echo "🛑 Stop services: docker-compose -f docker-compose.production-secure.yml down"
