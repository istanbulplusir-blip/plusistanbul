#!/bin/bash

echo "🗑️  Database Reset for Development - Peykan Tourism Platform"

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

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory!"
    exit 1
fi

cd backend

print_status "Step 1: Stopping local services..."

# Stop any running Django development server
pkill -f "python manage.py runserver" 2>/dev/null || true

print_status "Step 2: Removing local database files..."

# Remove SQLite database
rm -f db.sqlite3
rm -f *.db
rm -f *.sqlite

print_status "Step 3: Cleaning up migration files..."

# Remove all migration files except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete 2>/dev/null || true

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

print_status "Step 4: Creating fresh migrations..."

# Create fresh migrations
python manage.py makemigrations

print_status "Step 5: Running migrations..."

# Run migrations
python manage.py migrate

print_status "Step 6: Creating superuser (optional)..."

print_warning "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

print_status "Step 7: Collecting static files..."

# Collect static files
python manage.py collectstatic --noinput

print_status "Step 8: Loading sample data (optional)..."

print_warning "Do you want to load sample data? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    python manage.py loaddata fixtures/sample_data.json 2>/dev/null || print_info "No sample data found"
fi

print_status "✅ Development database reset completed successfully!"

print_info "Next steps:"
echo "1. Start development server: python manage.py runserver"
echo "2. Open browser: http://localhost:8000"
echo "3. Check admin panel: http://localhost:8000/admin"

print_info "Useful commands:"
echo "- Run server: python manage.py runserver"
echo "- Check models: python manage.py check"
echo "- Show migrations: python manage.py showmigrations"
echo "- Create superuser: python manage.py createsuperuser"

cd ..
