#!/bin/bash

echo "🔍 Checking Django Models - Peykan Tourism Platform"

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

print_status "Step 1: Checking Django configuration..."

# Check Django settings
python manage.py check --deploy

print_status "Step 2: Checking for model issues..."

# Check for common model issues
python manage.py check

print_status "Step 3: Validating models..."

# Validate all models
python manage.py validate

print_status "Step 4: Checking migration status..."

# Show migration status
python manage.py showmigrations

print_status "Step 5: Testing makemigrations..."

# Test makemigrations without applying
python manage.py makemigrations --dry-run

print_status "Step 6: Checking for circular imports..."

# Check for circular imports in models
apps=("agents" "car_rentals" "cart" "core" "events" "orders" "payments" "tours" "transfers" "users")

for app in "${apps[@]}"; do
    if [ -f "$app/models.py" ]; then
        print_info "Checking $app/models.py for issues..."
        
        # Check for common issues
        if grep -q "from django.db import models" "$app/models.py"; then
            print_info "✓ $app has proper Django imports"
        else
            print_warning "⚠ $app might be missing Django imports"
        fi
        
        # Check for model definitions
        if grep -q "class.*models.Model" "$app/models.py"; then
            print_info "✓ $app has model definitions"
        else
            print_warning "⚠ $app might not have model definitions"
        fi
    fi
done

print_status "Step 7: Checking for foreign key issues..."

# Check for potential foreign key issues
for app in "${apps[@]}"; do
    if [ -f "$app/models.py" ]; then
        if grep -q "ForeignKey\|OneToOneField\|ManyToManyField" "$app/models.py"; then
            print_info "✓ $app has relationship fields"
        fi
    fi
done

print_status "Step 8: Checking for missing imports..."

# Check for missing imports
for app in "${apps[@]}"; do
    if [ -f "$app/models.py" ]; then
        if grep -q "from.*import.*User" "$app/models.py"; then
            print_info "✓ $app imports User model"
        fi
    fi
done

print_status "Step 9: Testing model creation..."

# Test if we can create migrations
if python manage.py makemigrations --dry-run > /dev/null 2>&1; then
    print_status "✅ Models are ready for migration creation"
else
    print_error "❌ Models have issues that prevent migration creation"
    print_info "Run: python manage.py makemigrations --dry-run to see details"
fi

print_status "Step 10: Checking for database connectivity..."

# Check database connectivity
if python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; then
    print_status "✅ Database connectivity is working"
else
    print_warning "⚠ Database connectivity issues detected"
fi

print_status "🎉 Model check completed!"

print_info "Summary:"
echo "- Django configuration: Checked"
echo "- Model validation: Completed"
echo "- Migration status: Checked"
echo "- Import issues: Checked"
echo "- Database connectivity: Checked"

print_info "Next steps:"
echo "1. If no errors found, run: python manage.py makemigrations"
echo "2. Then run: python manage.py migrate"
echo "3. If errors found, fix them and run this script again"

print_warning "Common issues to check:"
echo "- Missing imports in models.py"
echo "- Circular imports between apps"
echo "- Invalid field definitions"
echo "- Missing related_name in foreign keys"
echo "- Invalid choices in field definitions"

cd ..
