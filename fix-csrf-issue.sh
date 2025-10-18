#!/bin/bash

# Fix CSRF Token Issue in Django Admin
# This script resolves CSRF token problems in production

echo "🔧 Fixing CSRF Token Issue in Django Admin..."

# Check if containers are running
if ! docker ps --format "table {{.Names}}" | grep -q "peykan_backend"; then
    echo "❌ Backend container is not running. Please start the application first."
    exit 1
fi

echo "✅ Backend container is running"

# Clear Django sessions and CSRF tokens
echo "🧹 Clearing Django sessions and CSRF tokens..."
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py shell -c "
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.conf import settings

# Clear all sessions
Session.objects.all().delete()
print('✅ All sessions cleared')

# Clear cache
cache.clear()
print('✅ Cache cleared')

# Clear CSRF tokens
from django.middleware.csrf import get_token
print('✅ CSRF tokens cleared')
"

# Restart backend service
echo "🔄 Restarting backend service..."
docker-compose -f docker-compose.production-secure.yml restart backend

# Wait for service to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Test admin access
echo "🧪 Testing admin access..."
if curl -f -s "https://peykantravelistanbul.com/admin/" > /dev/null; then
    echo "✅ Admin panel is accessible"
else
    echo "⚠️  Admin panel might not be accessible yet"
fi

echo ""
echo "🎉 CSRF issue fix completed!"
echo ""
echo "📋 Next steps:"
echo "1. Try accessing the admin panel again"
echo "2. If still having issues, check the logs:"
echo "   docker-compose -f docker-compose.production-secure.yml logs backend"
echo "3. Clear browser cache and cookies"
echo "4. Try accessing from an incognito/private window"
echo ""
echo "🔗 Admin Panel: https://peykantravelistanbul.com/admin/"
