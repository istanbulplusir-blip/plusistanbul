#!/bin/bash

# Quick Production Deployment Script
# This script provides a simplified deployment process

set -e

echo "🚀 Quick Production Deployment for Peykan Tourism Platform"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.production-secure.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if production environment exists
if [ ! -f "backend/env.production" ]; then
    echo "❌ Error: Production environment file not found"
    echo "Please create backend/env.production first"
    exit 1
fi

echo "✅ Production environment file found"

# Generate SSL certificates if they don't exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "🔐 Generating SSL certificates..."
    ./generate-ssl-certs-production.sh
else
    echo "✅ SSL certificates already exist"
fi

# Deploy the application
echo "🚀 Deploying application..."
./deploy-production.sh

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Your application is now available at:"
echo "   🌐 Frontend: https://peykantravelistanbul.com"
echo "   🔧 Backend: https://peykantravelistanbul.com/api/v1/"
echo "   👨‍💼 Admin: https://peykantravelistanbul.com/admin/"
echo ""
echo "🔐 Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  Please change the password immediately!"
echo ""
echo "📊 To view logs: docker-compose -f docker-compose.production-secure.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.production-secure.yml down"
