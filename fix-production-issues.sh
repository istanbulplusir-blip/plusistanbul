#!/bin/bash

echo "🚀 Fixing Production Issues - Peykan Tourism Platform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed!"
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed!"
    exit 1
fi

if ! command_exists jq; then
    print_warning "jq is not installed. Installing..."
    if command_exists apt-get; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command_exists yum; then
        sudo yum install -y jq
    elif command_exists brew; then
        brew install jq
    else
        print_error "Cannot install jq automatically. Please install it manually."
        exit 1
    fi
fi

print_status "Prerequisites check completed!"

# Step 1: Check translation files
print_status "Step 1: Checking translation files..."

if [ ! -d "frontend/messages" ]; then
    print_error "Messages directory not found!"
    exit 1
fi

if [ ! -d "frontend/i18n" ]; then
    print_error "i18n directory not found!"
    exit 1
fi

# Check if all translation files exist and are valid
translation_files=("frontend/messages/fa.json" "frontend/messages/en.json" "frontend/messages/tr.json")
for file in "${translation_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Translation file not found: $file"
        exit 1
    fi
    
    if ! jq empty "$file" 2>/dev/null; then
        print_error "Invalid JSON in translation file: $file"
        exit 1
    fi
    
    print_info "✓ $file is valid"
done

# Step 2: Check next-intl configuration
print_status "Step 2: Checking next-intl configuration..."

config_files=("frontend/i18n/config.js" "frontend/i18n/request.js" "frontend/middleware.ts" "frontend/next.config.js")
for file in "${config_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Configuration file not found: $file"
        exit 1
    fi
    print_info "✓ $file exists"
done

# Step 3: Check if next-intl is installed
print_status "Step 3: Checking next-intl installation..."

cd frontend
if ! npm list next-intl > /dev/null 2>&1; then
    print_warning "next-intl is not installed. Installing..."
    npm install next-intl@latest
fi
cd ..

# Step 4: Test Next.js build locally
print_status "Step 4: Testing Next.js build locally..."

cd frontend
if npm run build > build.log 2>&1; then
    print_status "✅ Local Next.js build successful!"
    rm -f build.log
else
    print_error "❌ Local Next.js build failed. Check build.log for details:"
    cat build.log
    cd ..
    exit 1
fi
cd ..

# Step 5: Clean up Docker resources
print_status "Step 5: Cleaning up Docker resources..."

docker-compose -f docker-compose.production-secure.yml down 2>/dev/null || true
docker system prune -f

# Step 6: Build Docker images
print_status "Step 6: Building Docker images..."

if docker-compose -f docker-compose.production-secure.yml build --no-cache; then
    print_status "✅ Docker build successful!"
else
    print_error "❌ Docker build failed!"
    exit 1
fi

# Step 7: Start services
print_status "Step 7: Starting services..."

if docker-compose -f docker-compose.production-secure.yml up -d; then
    print_status "✅ Services started successfully!"
else
    print_error "❌ Failed to start services!"
    exit 1
fi

# Step 8: Wait for services to be ready
print_status "Step 8: Waiting for services to be ready..."

sleep 30

# Step 9: Check service health
print_status "Step 9: Checking service health..."

# Check if containers are running
if docker-compose -f docker-compose.production-secure.yml ps | grep -q "Up"; then
    print_status "✅ Services are running!"
else
    print_error "❌ Some services are not running!"
    docker-compose -f docker-compose.production-secure.yml ps
    exit 1
fi

# Step 10: Test frontend
print_status "Step 10: Testing frontend..."

# Wait a bit more for frontend to be ready
sleep 10

# Check if frontend is responding
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    print_status "✅ Frontend is responding!"
else
    print_warning "⚠️  Frontend might not be ready yet. Checking logs..."
    docker-compose -f docker-compose.production-secure.yml logs --tail=20 frontend
fi

# Step 11: Test backend
print_status "Step 11: Testing backend..."

if curl -f -s http://localhost:8000/api/health > /dev/null 2>&1; then
    print_status "✅ Backend is responding!"
else
    print_warning "⚠️  Backend might not be ready yet. Checking logs..."
    docker-compose -f docker-compose.production-secure.yml logs --tail=20 backend
fi

# Final status
print_status "🎉 Production setup completed!"

print_info "Services status:"
docker-compose -f docker-compose.production-secure.yml ps

print_info "Next steps:"
echo "1. Open your browser and go to: http://localhost:3000"
echo "2. Check the application functionality"
echo "3. Monitor logs: docker-compose -f docker-compose.production-secure.yml logs -f"

print_warning "If you encounter any issues:"
echo "1. Check logs: docker-compose -f docker-compose.production-secure.yml logs"
echo "2. Restart services: docker-compose -f docker-compose.production-secure.yml restart"
echo "3. Check the troubleshooting guide: NEXTINTL-TROUBLESHOOTING.md"

print_info "Useful commands:"
echo "- View logs: docker-compose -f docker-compose.production-secure.yml logs -f"
echo "- Restart frontend: docker-compose -f docker-compose.production-secure.yml restart frontend"
echo "- Stop services: docker-compose -f docker-compose.production-secure.yml down"
echo "- Rebuild: docker-compose -f docker-compose.production-secure.yml build --no-cache"
