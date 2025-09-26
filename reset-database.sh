#!/bin/bash

echo "🗑️  Resetting Database - Peykan Tourism Platform"

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

print_status "Step 1: Stopping all services..."

# Stop all services
docker-compose -f ../docker-compose.production-secure.yml down 2>/dev/null || true

print_status "Step 2: Removing database volumes..."

# Remove database volumes
docker volume rm $(docker volume ls -q | grep -E "(postgres|redis)") 2>/dev/null || true

print_status "Step 3: Cleaning up migration files..."

# Remove all migration files except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete 2>/dev/null || true

# Remove migration files from each app
apps=("agents" "car_rentals" "cart" "core" "events" "orders" "payments" "tours" "transfers" "users")

for app in "${apps[@]}"; do
    if [ -d "$app/migrations" ]; then
        print_info "Cleaning migrations for $app..."
        find "$app/migrations" -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true
        find "$app/migrations" -name "*.pyc" -delete 2>/dev/null || true
    fi
done

print_status "Step 4: Removing database files..."

# Remove SQLite database if exists
rm -f db.sqlite3 2>/dev/null || true

# Remove any other database files
rm -f *.db 2>/dev/null || true
rm -f *.sqlite 2>/dev/null || true

print_status "Step 5: Cleaning Python cache..."

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

print_status "Step 6: Creating fresh migrations..."

# Create fresh migrations for all apps
for app in "${apps[@]}"; do
    if [ -d "$app" ]; then
        print_info "Creating migration for $app..."
        python manage.py makemigrations "$app" --empty 2>/dev/null || true
    fi
done

# Create initial migrations
print_info "Creating initial migrations..."
python manage.py makemigrations

print_status "Step 7: Starting database services..."

# Start only database services
cd ..
docker-compose -f docker-compose.production-secure.yml up -d postgres redis

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 15

print_status "Step 8: Running migrations..."

cd backend

# Run migrations
python manage.py migrate

print_status "Step 9: Creating superuser (optional)..."

print_warning "Do you want to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

print_status "Step 10: Collecting static files..."

python manage.py collectstatic --noinput

print_status "✅ Database reset completed successfully!"

print_info "Next steps:"
echo "1. Start all services: docker-compose -f ../docker-compose.production-secure.yml up -d"
echo "2. Check logs: docker-compose -f ../docker-compose.production-secure.yml logs"
echo "3. Test the application"

print_warning "Important notes:"
echo "- All data has been permanently deleted"
echo "- You may need to recreate test data"
echo "- Check your models for any issues"

cd ..
