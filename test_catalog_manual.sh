#!/bin/bash

# Manual test script for PDF Catalog feature
# Run this when both backend and frontend servers are running

echo "=========================================="
echo "PDF Catalog Manual Test Script"
echo "=========================================="
echo ""

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_url() {
    local url=$1
    local name=$2
    
    echo -n "Testing $name... "
    
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10)
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Status: $status_code)"
        return 1
    fi
}

echo "Configuration:"
echo "  Backend URL: $BACKEND_URL"
echo "  Frontend URL: $FRONTEND_URL"
echo ""

# Check if servers are running
echo "Checking if servers are running..."
echo ""

# Test backend
if curl -s "$BACKEND_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend server is running"
else
    echo -e "${RED}✗${NC} Backend server is NOT running"
    echo "  Start with: cd backend && python3 manage.py runserver"
    BACKEND_DOWN=1
fi

# Test frontend
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend server is running"
else
    echo -e "${RED}✗${NC} Frontend server is NOT running"
    echo "  Start with: cd frontend && npm run dev"
    FRONTEND_DOWN=1
fi

echo ""

if [ "$BACKEND_DOWN" = "1" ] || [ "$FRONTEND_DOWN" = "1" ]; then
    echo -e "${YELLOW}Please start the required servers and run this script again.${NC}"
    exit 1
fi

echo "=========================================="
echo "Backend API Tests"
echo "=========================================="
echo ""

# Test backend endpoints
test_url "$BACKEND_URL/api/shared/catalogs/" "Catalog list endpoint"
test_url "$BACKEND_URL/api/shared/catalogs/featured/" "Featured catalog endpoint"
test_url "$BACKEND_URL/media/catalogs/Peykan%20Travel%20Tour-Guide-2025-1.pdf" "Direct PDF access"

echo ""
echo "=========================================="
echo "Frontend Page Tests"
echo "=========================================="
echo ""

# Test frontend pages
test_url "$FRONTEND_URL/fa/catalog" "Catalog page (Persian)"
test_url "$FRONTEND_URL/en/catalog" "Catalog page (English)"
test_url "$FRONTEND_URL/tr/catalog" "Catalog page (Turkish)"

echo ""
echo "=========================================="
echo "Manual Verification Checklist"
echo "=========================================="
echo ""
echo "Please manually verify the following:"
echo ""
echo "1. PDF Viewer:"
echo "   - Open: $FRONTEND_URL/fa/catalog"
echo "   - Verify PDF displays in iframe"
echo "   - Check loading state appears briefly"
echo ""
echo "2. Download Button:"
echo "   - Click download button"
echo "   - Verify file downloads with correct name"
echo ""
echo "3. Mobile Responsiveness:"
echo "   - Open Chrome DevTools (F12)"
echo "   - Toggle device toolbar (Ctrl+Shift+M)"
echo "   - Test on iPhone and Android viewports"
echo "   - Verify fixed download button on mobile"
echo ""
echo "4. Multi-language:"
echo "   - Test all three languages (fa, en, tr)"
echo "   - Verify translations are correct"
echo ""
echo "5. Error Handling:"
echo "   - Stop backend server"
echo "   - Reload catalog page"
echo "   - Verify error message displays"
echo ""
echo "6. Analytics:"
echo "   - Open Django admin: $BACKEND_URL/admin/shared/catalogfile/"
echo "   - Note current view_count and download_count"
echo "   - View catalog page (increments view_count)"
echo "   - Download catalog (increments download_count)"
echo "   - Refresh admin and verify counters increased"
echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
