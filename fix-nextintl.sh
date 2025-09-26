#!/bin/bash

echo "🔧 Fixing Next.js Internationalization (next-intl) Configuration..."

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
if [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory!"
    exit 1
fi

cd frontend

print_status "Checking Next.js internationalization setup..."

# 1. Check if next-intl is installed
if ! npm list next-intl > /dev/null 2>&1; then
    print_warning "next-intl is not installed. Installing..."
    npm install next-intl@latest
fi

# 2. Check if required directories exist
required_dirs=("i18n" "messages")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        print_error "Required directory '$dir' not found!"
        exit 1
    fi
done

# 3. Check if required files exist
required_files=(
    "i18n/config.js"
    "i18n/request.js"
    "messages/fa.json"
    "messages/en.json"
    "messages/tr.json"
    "middleware.ts"
    "next.config.js"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    print_error "Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

print_status "All required files found!"

# 4. Validate JSON files
print_info "Validating translation files..."
for file in messages/*.json; do
    if [ -f "$file" ]; then
        if jq empty "$file" 2>/dev/null; then
            print_info "✓ $file is valid JSON"
        else
            print_error "✗ $file is not valid JSON"
            exit 1
        fi
    fi
done

# 5. Check next.config.js for next-intl plugin
if grep -q "next-intl/plugin" next.config.js; then
    print_info "✓ next-intl plugin is configured in next.config.js"
else
    print_warning "next-intl plugin not found in next.config.js"
fi

# 6. Check middleware.ts for next-intl middleware
if grep -q "next-intl/middleware" middleware.ts; then
    print_info "✓ next-intl middleware is configured in middleware.ts"
else
    print_warning "next-intl middleware not found in middleware.ts"
fi

# 7. Check if locales are properly configured
if grep -q "locales.*fa.*en.*tr" i18n/config.js; then
    print_info "✓ Locales (fa, en, tr) are configured"
else
    print_warning "Locales might not be properly configured"
fi

# 8. Create a test build to check for errors
print_info "Testing Next.js build..."
if npm run build > build.log 2>&1; then
    print_status "✅ Next.js build successful!"
    rm -f build.log
else
    print_error "❌ Next.js build failed. Check build.log for details:"
    cat build.log
    exit 1
fi

# 9. Check if .next directory was created properly
if [ -d ".next" ]; then
    print_info "✓ .next directory created successfully"
    
    # Check if server chunks exist
    if [ -d ".next/server/chunks" ]; then
        print_info "✓ Server chunks directory exists"
    else
        print_warning "Server chunks directory not found"
    fi
else
    print_error "❌ .next directory not created"
    exit 1
fi

print_status "🎉 Next.js internationalization setup is working correctly!"

print_info "Next steps:"
echo "1. Run: docker-compose -f docker-compose.production-secure.yml build frontend"
echo "2. Run: docker-compose -f docker-compose.production-secure.yml up -d"
echo "3. Check the application in browser"

print_warning "If you still get errors in production:"
echo "1. Check Docker logs: docker-compose logs frontend"
echo "2. Verify all translation files are copied to the container"
echo "3. Check if the build process includes all required files"

cd ..
