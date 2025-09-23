#!/bin/bash

# Peykan Tourism Platform - Production Deployment Script
# This script should be run when SSH access is restored

set -e  # Exit on any error

echo "🚀 Starting Peykan Tourism Platform Deployment..."

# Configuration
SERVER_IP="185.27.134.10"
SERVER_USER="root"
PROJECT_DIR="/opt/peykan-tourism"

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

# Check if SSH is available
print_status "Checking SSH connection..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes ${SERVER_USER}@${SERVER_IP} "echo 'SSH connection successful'" 2>/dev/null; then
    print_error "SSH connection failed. Please ensure SSH service is running on the server."
    print_warning "You may need to restart SSH service through your server control panel."
    exit 1
fi

print_status "SSH connection successful!"

# Connect to server and deploy
print_status "Connecting to server and deploying..."

ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
set -e

echo "📁 Navigating to project directory..."
cd /opt/peykan-tourism

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo "🐳 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

echo "🔨 Building new images..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "📊 Checking service status..."
docker-compose -f docker-compose.production.yml ps

echo "📋 Checking logs for any errors..."
echo "=== Backend Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 backend

echo "=== Frontend Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 frontend

echo "✅ Deployment completed successfully!"
echo "🌐 Your site should be available at: https://peykantravelistanbul.com"
EOF

print_status "Deployment script completed!"
print_status "Check the output above for any errors."
print_status "If everything looks good, your site should be live at: https://peykantravelistanbul.com" 