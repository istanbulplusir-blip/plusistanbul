#!/bin/bash

echo "📁 Copying translation files to production..."

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

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found!"
    exit 1
fi

# Check if messages directory exists
if [ ! -d "frontend/messages" ]; then
    print_error "Messages directory not found!"
    exit 1
fi

# Check if i18n directory exists
if [ ! -d "frontend/i18n" ]; then
    print_error "i18n directory not found!"
    exit 1
fi

print_status "Checking translation files..."

# Check if all required translation files exist
required_files=(
    "frontend/messages/fa.json"
    "frontend/messages/en.json"
    "frontend/messages/tr.json"
    "frontend/i18n/config.js"
    "frontend/i18n/request.js"
    "frontend/middleware.ts"
    "frontend/next.config.js"
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

print_status "All translation files found!"

# Check file sizes
print_info "Checking file sizes..."
for file in "${required_files[@]}"; do
    size=$(wc -c < "$file")
    if [ "$size" -lt 100 ]; then
        print_warning "File $file is very small ($size bytes) - might be empty or corrupted"
    else
        print_info "✓ $file ($size bytes)"
    fi
done

# Check if files are valid JSON (for .json files)
print_info "Validating JSON files..."
for file in frontend/messages/*.json; do
    if [ -f "$file" ]; then
        if jq empty "$file" 2>/dev/null; then
            print_info "✓ $file is valid JSON"
        else
            print_error "✗ $file is not valid JSON"
            exit 1
        fi
    fi
done

print_status "✅ All translation files are valid and ready for production!"

print_info "Files that will be included in Docker build:"
echo "  - frontend/messages/fa.json"
echo "  - frontend/messages/en.json" 
echo "  - frontend/messages/tr.json"
echo "  - frontend/i18n/config.js"
echo "  - frontend/i18n/request.js"
echo "  - frontend/middleware.ts"
echo "  - frontend/next.config.js"

print_warning "Make sure these files are included in your Docker build context!"
print_info "You can verify this by checking the .dockerignore file in the frontend directory."
