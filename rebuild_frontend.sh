#!/bin/bash

echo "🔄 Rebuilding Frontend with Correct Environment Variables"
echo "=========================================================="

cd /home/djangouser/plusistanbul

# 1. Stop containers
echo "1️⃣ Stopping containers..."
docker-compose -f docker-compose.production-secure.yml down

# 2. Remove old frontend image to force rebuild
echo "2️⃣ Removing old frontend image..."
docker rmi plusistanbul_frontend 2>/dev/null || echo "No old image to remove"

# 3. Build frontend with correct env vars
echo "3️⃣ Building frontend..."
docker-compose -f docker-compose.production-secure.yml build --no-cache frontend

# 4. Start all services
echo "4️⃣ Starting all services..."
docker-compose -f docker-compose.production-secure.yml up -d

# 5. Wait for services
echo "5️⃣ Waiting for services to start..."
sleep 15

# 6. Check status
echo "6️⃣ Checking container status..."
docker-compose -f docker-compose.production-secure.yml ps

echo ""
echo "✅ Frontend rebuilt successfully!"
echo ""
echo "🔍 Test the site:"
echo "   https://www.peykantravelistanbul.com"
echo ""
echo "📊 Check logs:"
echo "   docker-compose -f docker-compose.production-secure.yml logs -f frontend"
echo ""
