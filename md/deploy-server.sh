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
