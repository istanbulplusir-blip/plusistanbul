#!/bin/bash

# Script to rebuild and restart services for catalog feature

echo "🔄 Rebuilding services for catalog feature..."

# Stop services
echo "⏸️  Stopping services..."
docker-compose -f docker-compose.production-dev.yml stop frontend backend

# Rebuild backend (for new model, views, serializers)
echo "🔨 Rebuilding backend..."
docker-compose -f docker-compose.production-dev.yml build --no-cache backend

# Rebuild frontend (for new page and component)
echo "🔨 Rebuilding frontend..."
docker-compose -f docker-compose.production-dev.yml build --no-cache frontend

# Start services
echo "▶️  Starting services..."
docker-compose -f docker-compose.production-dev.yml up -d backend frontend

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check backend health
echo "🔍 Checking backend..."
if curl -f http://localhost:8000/api/shared/catalogs/featured/ > /dev/null 2>&1; then
    echo "✅ Backend API is working"
else
    echo "⚠️  Backend API not responding yet, checking logs..."
    docker-compose -f docker-compose.production-dev.yml logs --tail=20 backend
fi

# Check frontend health
echo "🔍 Checking frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is working"
else
    echo "⚠️  Frontend not responding yet, checking logs..."
    docker-compose -f docker-compose.production-dev.yml logs --tail=20 frontend
fi

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "📋 Test URLs:"
echo "   Backend API: http://localhost:8000/api/shared/catalogs/featured/"
echo "   Frontend (fa): http://localhost:3000/fa/catalog"
echo "   Frontend (en): http://localhost:3000/en/catalog"
echo "   Frontend (tr): http://localhost:3000/tr/catalog"
echo "   Admin: http://localhost:8000/admin/shared/catalogfile/"
echo ""
echo "📊 View logs:"
echo "   Backend: docker-compose -f docker-compose.production-dev.yml logs -f backend"
echo "   Frontend: docker-compose -f docker-compose.production-dev.yml logs -f frontend"
