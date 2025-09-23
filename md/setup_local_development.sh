#!/bin/bash

# Local Development Setup Script for Peykan Tourism
# Generated from server backup

set -e

echo "🚀 Setting up local development environment..."
echo "=============================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Backend setup
print_status "Setting up backend environment..."

if [ ! -d "backend/venv" ]; then
    print_status "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

print_status "Activating virtual environment and installing dependencies..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Frontend setup
print_status "Setting up frontend environment..."
cd frontend
npm install
cd ..

# Database setup
print_status "Setting up database..."
cd backend
source venv/bin/activate

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from example..."
    cp env.example .env
    print_warning "Please edit backend/.env with your local database settings"
fi

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

# Create superuser if needed
read -p "Do you want to create a superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

cd ..

print_success "Local development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your local database settings"
echo "2. Start backend: cd backend && source venv/bin/activate && python manage.py runserver"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Access admin panel: http://localhost:8000/admin"
echo "5. Access frontend: http://localhost:3000"
