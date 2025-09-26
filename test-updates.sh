#!/bin/bash
set -e

echo "🧪 Testing Updated Dependencies..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test Backend Dependencies
print_status "Testing Backend Dependencies..."

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_warning "Creating virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source backend/venv/bin/activate

# Install backend dependencies
print_info "Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Test Django
print_info "Testing Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Test other key packages
print_info "Testing key packages..."
python -c "import rest_framework; print('DRF: OK')"
python -c "import celery; print('Celery: OK')"
python -c "import redis; print('Redis: OK')"
python -c "import psycopg2; print('PostgreSQL: OK')"

cd ..

# Test Frontend Dependencies
print_status "Testing Frontend Dependencies..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    npm install
else
    print_info "Updating frontend dependencies..."
    npm update
fi

# Test Next.js
print_info "Testing Next.js installation..."
npx next --version

# Test build
print_info "Testing frontend build..."
npm run build

cd ..

print_status "✅ All dependency tests passed!"
print_info "Next steps:"
echo "1. Run: docker-compose -f docker-compose.production-secure.yml build"
echo "2. Run: docker-compose -f docker-compose.production-secure.yml up -d"
echo "3. Test the application in browser"
echo "4. Run any existing tests to ensure compatibility"

print_warning "Remember to:"
echo "• Update your .env.production file with new configurations"
echo "• Test all functionality after deployment"
echo "• Monitor logs for any compatibility issues"
