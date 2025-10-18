#!/bin/bash

# Setup script for production-like development environment
# This script prepares the project for deployment testing

echo "Setting up production-like development environment..."
echo

# Check if Docker is running
echo "Checking Docker..."
if ! docker --version >/dev/null 2>&1; then
    echo "ERROR: Docker is not installed or not running!"
    echo "Please install Docker and start it."
    exit 1
fi

echo "Docker is available."
echo

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p backend/logs
mkdir -p nginx/ssl
mkdir -p postgres
mkdir -p redis

echo "Directories created."
echo

# Copy environment template if it doesn't exist
if [ ! -f "backend/.env.production.dev" ]; then
    echo "Creating production development environment file..."
    cp backend/env.production.dev backend/.env.production.dev
    echo "Environment file created."
else
    echo "Environment file already exists."
fi

echo

# Generate SSL certificates for development
echo "Generating SSL certificates for development..."
if [ ! -f "nginx/ssl/cert.pem" ]; then
    echo "Creating self-signed SSL certificates..."
    docker run --rm -v "$(pwd)/nginx/ssl:/ssl" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /ssl/key.pem -out /ssl/cert.pem -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=localhost"
    echo "SSL certificates generated."
else
    echo "SSL certificates already exist."
fi

echo

# Build and start the services
echo "Building and starting services..."
echo "This may take several minutes on first run..."
echo

docker-compose -f docker-compose.production-dev.yml down
docker-compose -f docker-compose.production-dev.yml build --no-cache
docker-compose -f docker-compose.production-dev.yml up -d

echo
echo "Services are starting up..."
echo

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.production-dev.yml ps

echo
echo "========================================"
echo "Production-like development environment is ready!"
echo
echo "Services:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- Nginx Proxy: http://localhost:80"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"
echo
echo "To view logs:"
echo "docker-compose -f docker-compose.production-dev.yml logs -f"
echo
echo "To stop services:"
echo "docker-compose -f docker-compose.production-dev.yml down"
echo
echo "To restart services:"
echo "docker-compose -f docker-compose.production-dev.yml restart"
echo "========================================"
