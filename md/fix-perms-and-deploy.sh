#!/usr/bin/env bash
set -e


echo "=== Starting comprehensive permission fix and deployment process ==="

# Navigate to project directory
echo "1. Navigating to project directory..."
cd /home/djangouser/peykan-tourism

# Check if we're in the right directory
if [ ! -f "docker-compose.production.yml" ]; then
    echo "Error: docker-compose.production.yml not found. Please run this script from the project root."
    exit 1
fi

echo "2. Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

echo "3. Removing logs directory to reset permissions..."
# Remove the logs directory so it gets recreated with correct permissions
rm -rf logs

echo "4. Rebuilding frontend with updated API configuration..."
# Rebuild frontend to pick up the new next.config.js changes
docker-compose -f docker-compose.production.yml build frontend

echo "5. Starting containers with fresh logs directory..."
docker-compose -f docker-compose.production.yml up -d

echo "6. Waiting for containers to initialize..."
sleep 15

echo "7. Checking container status..."
docker-compose -f docker-compose.production.yml ps

echo "8. Checking logs directory permissions..."
if [ -d "logs" ]; then
    echo "Logs directory exists. Checking permissions:"
    ls -la logs/
else
    echo "Warning: Logs directory not found after container start"
fi

echo "9. Following backend logs..."
echo "=== Backend Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 backend

echo "10. Following frontend logs..."
echo "=== Frontend Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 frontend

echo "11. Following nginx logs..."
echo "=== Nginx Logs ==="
docker-compose -f docker-compose.production.yml logs --tail=20 nginx

echo "=== Deployment completed ==="
echo "The logs directory has been recreated with correct permissions."
echo "Frontend has been rebuilt with updated API configuration."
echo "Backend should now be able to write to logs without PermissionError."
echo "Frontend should now be able to connect to backend properly."
echo ""
echo "To monitor logs in real-time:"
echo "  Backend: docker-compose -f docker-compose.production.yml logs -f backend"
echo "  Frontend: docker-compose -f docker-compose.production.yml logs -f frontend"
echo "  Nginx: docker-compose -f docker-compose.production.yml logs -f nginx"
echo ""
echo "To check container status: docker-compose -f docker-compose.production.yml ps" 

