#!/bin/bash

# Test CORS Fix - Verify no duplicate headers

echo "========================================"
echo "  CORS Fix Verification Test"
echo "========================================"
echo ""

DOMAIN="https://peykantravelistanbul.com"
ORIGIN="https://www.peykantravelistanbul.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_cors_header() {
    local endpoint=$1
    local description=$2
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $endpoint"
    
    # Get all access-control-allow-origin headers
    headers=$(curl -s -I "$endpoint" -H "Origin: $ORIGIN" 2>&1 | grep -i "^access-control-allow-origin:" | wc -l)
    
    if [ "$headers" -eq 1 ]; then
        echo -e "${GREEN}✓ PASS${NC} - Single CORS header found"
        
        # Show the header value
        header_value=$(curl -s -I "$endpoint" -H "Origin: $ORIGIN" 2>&1 | grep -i "^access-control-allow-origin:" | cut -d' ' -f2- | tr -d '\r\n')
        echo "  Header value: $header_value"
    elif [ "$headers" -eq 0 ]; then
        echo -e "${RED}✗ FAIL${NC} - No CORS header found"
    else
        echo -e "${RED}✗ FAIL${NC} - Multiple CORS headers found ($headers)"
        curl -s -I "$endpoint" -H "Origin: $ORIGIN" 2>&1 | grep -i "^access-control-allow-origin:"
    fi
    
    echo ""
}

# Test various API endpoints
echo "Testing API Endpoints:"
echo "----------------------------------------"

test_cors_header "$DOMAIN/api/v1/shared/navigation-menu/active/" "Navigation Menu API"
test_cors_header "$DOMAIN/api/v1/shared/site-settings/" "Site Settings API"
test_cors_header "$DOMAIN/api/v1/cart/" "Cart API"
test_cors_header "$DOMAIN/api/v1/shared/catalogs/featured/" "Catalogs API"

echo "========================================"
echo "  Test Complete"
echo "========================================"
echo ""
echo "If all tests passed, the CORS issue is fixed!"
echo "You can now test in the browser at:"
echo "  - https://www.peykantravelistanbul.com/"
echo "  - https://www.peykantravelistanbul.com/catalog"
echo ""
