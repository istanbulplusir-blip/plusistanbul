#!/bin/bash

# Peykan Tourism Platform - Production Deployment Script
set -e

echo "🚀 Starting Peykan Tourism Platform Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if .env.production exists
if [ ! -f "backend/.env.production" ]; then
    print_error ".env.production file not found!"
    print_warning "Please copy env.production.template to .env.production and configure it."
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    print_warning "SSL certificates not found!"
    print_warning "Generating self-signed certificates for testing..."
    
    mkdir -p nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan/CN=localhost"
    
    print_status "Self-signed certificates generated."
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.production-secure.yml down

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.production-secure.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check backend
if curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
    print_status "✅ Backend is healthy"
else
    print_error "❌ Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "✅ Frontend is healthy"
else
    print_error "❌ Frontend health check failed"
fi

# Check nginx
if curl -f http://localhost > /dev/null 2>&1; then
    print_status "✅ Nginx is healthy"
else
    print_error "❌ Nginx health check failed"
fi

# Show running containers
print_status "Running containers:"
docker-compose -f docker-compose.production-secure.yml ps

print_status "🎉 Deployment completed!"
print_warning "Don't forget to:"
print_warning "1. Update DNS records to point to your server"
print_warning "2. Configure real SSL certificates"
print_warning "3. Set up monitoring and backups"
print_warning "4. Configure firewall rules"
