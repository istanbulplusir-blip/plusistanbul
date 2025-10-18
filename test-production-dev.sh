#!/bin/bash

# Test script for production-like development environment
# This script tests all services and endpoints

echo "Testing production-like development environment..."
echo

# Check if services are running
echo "Checking if services are running..."
docker-compose -f docker-compose.production-dev.yml ps

echo
echo "Testing service endpoints..."
echo

# Test Nginx health check
echo "Testing Nginx health check..."
curl -s http://localhost/health || echo "Nginx health check failed"

echo
echo "Testing Backend API health check..."
curl -s http://localhost:8000/api/v1/health/ || echo "Backend health check failed"

echo
echo "Testing Frontend..."
curl -s -I http://localhost:3000 | grep "200 OK" || echo "Frontend check failed"

echo
echo "Testing database connection..."
docker-compose -f docker-compose.production-dev.yml exec -T postgres pg_isready -U peykan_user -d peykan || echo "Database connection failed"

echo
echo "Testing Redis connection..."
docker-compose -f docker-compose.production-dev.yml exec -T redis redis-cli -a dev_redis_123 ping || echo "Redis connection failed"

echo
echo "Testing API endpoints..."
echo

# Test API endpoints
echo "Testing tours API..."
curl -s http://localhost:8000/api/v1/tours/ | grep "results" || echo "Tours API failed"

echo
echo "Testing events API..."
curl -s http://localhost:8000/api/v1/events/ | grep "results" || echo "Events API failed"

echo
echo "Testing shared API..."
curl -s http://localhost:8000/api/v1/shared/ | grep "results" || echo "Shared API failed"

echo
echo "========================================"
echo "Test Summary:"
echo
echo "Services Status:"
docker-compose -f docker-compose.production-dev.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo
echo "Available Endpoints:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- Nginx Proxy: http://localhost:80"
echo "- API Documentation: http://localhost:8000/api/docs/"
echo "- Admin Panel: http://localhost:8000/admin/"
echo "========================================"
