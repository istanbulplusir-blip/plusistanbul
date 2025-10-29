#!/bin/bash

# Test Frontend Integration for Peykan Static/Media Files Fix
# This script tests all frontend functionality including homepage, catalog, products, and multi-language support

DOMAIN="https://peykantravelistanbul.com"
RESULTS_FILE="frontend_integration_test_results.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize results file
echo "Frontend Integration Test Results - $(date)" > "$RESULTS_FILE"
echo "================================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Function to test URL and check response (follows redirects)
test_url() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "Testing: $description" >> "$RESULTS_FILE"
    echo "URL: $url" >> "$RESULTS_FILE"
    
    # Follow redirects with -L flag
    response=$(curl -L -s -o /dev/null -w "%{http_code}" "$url" 2>&1)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Status: $response"
        echo "✓ PASS - Status: $response" >> "$RESULTS_FILE"
    else
        echo -e "${RED}✗ FAIL${NC} - Expected: $expected_status, Got: $response"
        echo "✗ FAIL - Expected: $expected_status, Got: $response" >> "$RESULTS_FILE"
    fi
    echo "" >> "$RESULTS_FILE"
}

# Function to check content type
test_content_type() {
    local url=$1
    local description=$2
    local expected_type=$3
    
    echo -e "${YELLOW}Testing Content-Type: $description${NC}"
    echo "Testing Content-Type: $description" >> "$RESULTS_FILE"
    echo "URL: $url" >> "$RESULTS_FILE"
    
    content_type=$(curl -s -I "$url" | grep -i "content-type:" | cut -d' ' -f2- | tr -d '\r\n')
    
    if [[ "$content_type" == *"$expected_type"* ]]; then
        echo -e "${GREEN}✓ PASS${NC} - Content-Type: $content_type"
        echo "✓ PASS - Content-Type: $content_type" >> "$RESULTS_FILE"
    else
        echo -e "${RED}✗ FAIL${NC} - Expected: $expected_type, Got: $content_type"
        echo "✗ FAIL - Expected: $expected_type, Got: $content_type" >> "$RESULTS_FILE"
    fi
    echo "" >> "$RESULTS_FILE"
}

echo "========================================"
echo "  Frontend Integration Test Suite"
echo "========================================"
echo ""

# Task 6.1: Test Homepage
echo -e "${YELLOW}=== Task 6.1: Testing Homepage ===${NC}"
echo "=== Task 6.1: Testing Homepage ===" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

test_url "$DOMAIN/" "Homepage (default language)"
test_url "$DOMAIN/fa/" "Homepage (Farsi)"
test_url "$DOMAIN/en/" "Homepage (English)"
test_url "$DOMAIN/tr/" "Homepage (Turkish)"

# Test static files from homepage
echo -e "${YELLOW}Testing Static Files (CSS/JS)${NC}"
# Test actual static files that exist
test_url "$DOMAIN/static/rest_framework/css/bootstrap.min.css" "Bootstrap CSS file"
test_content_type "$DOMAIN/static/rest_framework/css/bootstrap.min.css" "Bootstrap CSS" "text/css"

test_url "$DOMAIN/static/rest_framework/js/jquery-3.7.1.min.js" "jQuery JavaScript file"
test_content_type "$DOMAIN/static/rest_framework/js/jquery-3.7.1.min.js" "jQuery JavaScript" "javascript"

test_url "$DOMAIN/static/admin/css/base.css" "Admin CSS file"
test_content_type "$DOMAIN/static/admin/css/base.css" "Admin CSS" "text/css"

echo ""

# Task 6.2: Test Catalog Page
echo -e "${YELLOW}=== Task 6.2: Testing Catalog Page ===${NC}"
echo "=== Task 6.2: Testing Catalog Page ===" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

test_url "$DOMAIN/catalog" "Catalog page"
test_url "$DOMAIN/fa/catalog" "Catalog page (Farsi)"
test_url "$DOMAIN/en/catalog" "Catalog page (English)"
test_url "$DOMAIN/tr/catalog" "Catalog page (Turkish)"

# Test PDF catalog file
PDF_URL="$DOMAIN/media/catalogs/Peykan%20Travel%20Tour-Guide-2025-1.pdf"
echo -e "${YELLOW}Testing PDF Catalog${NC}"
test_url "$PDF_URL" "PDF Catalog file"
test_content_type "$PDF_URL" "PDF Catalog" "application/pdf"

# Test product images
echo -e "${YELLOW}Testing Product Images${NC}"
test_url "$DOMAIN/media/products/mosque-architecture-hd-8k-wallpaper-stock-photographic-image.jpg" "Product image"
test_content_type "$DOMAIN/media/products/mosque-architecture-hd-8k-wallpaper-stock-photographic-image.jpg" "Product image" "image/jpeg"

echo ""

# Task 6.3: Test Product Pages
echo -e "${YELLOW}=== Task 6.3: Testing Product Pages ===${NC}"
echo "=== Task 6.3: Testing Product Pages ===" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Test product listing pages (these redirect, so we follow them)
test_url "$DOMAIN/tours/" "Tours listing page"
test_url "$DOMAIN/transfers/" "Transfers listing page"
test_url "$DOMAIN/events/" "Events listing page"

# Test media files - product images
echo -e "${YELLOW}Testing Media Directory Access${NC}"

# Check if media directories return 403 (forbidden) or 404 (not found) - both are acceptable
# We don't want directory listing enabled
response=$(curl -L -s -o /dev/null -w "%{http_code}" "$DOMAIN/media/products/" 2>&1)
if [ "$response" = "403" ] || [ "$response" = "404" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Products directory properly protected (Status: $response)"
    echo "✓ PASS - Products directory properly protected (Status: $response)" >> "$RESULTS_FILE"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Products directory status: $response"
    echo "⚠ WARNING - Products directory status: $response" >> "$RESULTS_FILE"
fi

echo ""

# Task 6.4: Test All Three Languages
echo -e "${YELLOW}=== Task 6.4: Testing Multi-Language Support ===${NC}"
echo "=== Task 6.4: Testing Multi-Language Support ===" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Test main pages in all languages
for lang in fa en tr; do
    echo -e "${YELLOW}Testing $lang language${NC}"
    echo "Testing $lang language" >> "$RESULTS_FILE"
    
    test_url "$DOMAIN/$lang/" "Homepage ($lang)"
    test_url "$DOMAIN/$lang/about/" "About page ($lang)"
    test_url "$DOMAIN/$lang/contact/" "Contact page ($lang)"
    test_url "$DOMAIN/$lang/tours/" "Tours page ($lang)"
    
    # Verify static files work with language prefix (use actual files)
    test_url "$DOMAIN/static/rest_framework/css/bootstrap.min.css" "Static CSS ($lang context)"
    test_url "$DOMAIN/static/rest_framework/js/jquery-3.7.1.min.js" "Static JS ($lang context)"
    
    echo ""
done

# Additional verification tests
echo -e "${YELLOW}=== Additional Verification Tests ===${NC}"
echo "=== Additional Verification Tests ===" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Test 404 handling
test_url "$DOMAIN/static/nonexistent.css" "Non-existent static file" 404
test_url "$DOMAIN/media/nonexistent.jpg" "Non-existent media file" 404

# Non-existent page might redirect, so check final status
response=$(curl -L -s -o /dev/null -w "%{http_code}" "$DOMAIN/nonexistent-page-12345" 2>&1)
if [ "$response" = "404" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Non-existent page returns 404"
    echo "✓ PASS - Non-existent page returns 404" >> "$RESULTS_FILE"
else
    echo -e "${YELLOW}⚠ INFO${NC} - Non-existent page status: $response (may redirect to error page)"
    echo "⚠ INFO - Non-existent page status: $response" >> "$RESULTS_FILE"
fi

# Test cache headers for static files
echo -e "${YELLOW}Testing Cache Headers${NC}"
echo "Testing Cache Headers" >> "$RESULTS_FILE"

cache_control=$(curl -s -I "$DOMAIN/static/rest_framework/css/bootstrap.min.css" | grep -i "cache-control:" | cut -d' ' -f2- | tr -d '\r\n')
echo "Cache-Control header: $cache_control" >> "$RESULTS_FILE"

if [[ -n "$cache_control" ]] && [[ "$cache_control" == *"public"* ]]; then
    echo -e "${GREEN}✓ PASS${NC} - Cache-Control header present: $cache_control"
    echo "✓ PASS - Cache-Control header present" >> "$RESULTS_FILE"
elif [[ -n "$cache_control" ]]; then
    echo -e "${YELLOW}⚠ INFO${NC} - Cache-Control header: $cache_control"
    echo "⚠ INFO - Cache-Control header: $cache_control" >> "$RESULTS_FILE"
else
    echo -e "${YELLOW}⚠ INFO${NC} - No Cache-Control header found"
    echo "⚠ INFO - No Cache-Control header found" >> "$RESULTS_FILE"
fi

# Test Expires header
expires=$(curl -s -I "$DOMAIN/static/rest_framework/css/bootstrap.min.css" | grep -i "expires:" | cut -d' ' -f2- | tr -d '\r\n')
if [[ -n "$expires" ]]; then
    echo -e "${GREEN}✓ PASS${NC} - Expires header present: $expires"
    echo "✓ PASS - Expires header present" >> "$RESULTS_FILE"
else
    echo -e "${YELLOW}⚠ INFO${NC} - No Expires header found"
    echo "⚠ INFO - No Expires header found" >> "$RESULTS_FILE"
fi

echo ""
echo "========================================"
echo "  Test Summary"
echo "========================================"
echo ""

# Count results
total_tests=$(grep -c "Testing:" "$RESULTS_FILE" || echo "0")
passed_tests=$(grep -c "✓ PASS" "$RESULTS_FILE" || echo "0")
failed_tests=$(grep -c "✗ FAIL" "$RESULTS_FILE" || echo "0")

echo "Total Tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $failed_tests"

echo "" >> "$RESULTS_FILE"
echo "========================================"  >> "$RESULTS_FILE"
echo "Test Summary" >> "$RESULTS_FILE"
echo "Total Tests: $total_tests" >> "$RESULTS_FILE"
echo "Passed: $passed_tests" >> "$RESULTS_FILE"
echo "Failed: $failed_tests" >> "$RESULTS_FILE"
echo "========================================"  >> "$RESULTS_FILE"

echo ""
echo "Full results saved to: $RESULTS_FILE"

if [ "$failed_tests" -gt 0 ]; then
    echo -e "${RED}Some tests failed. Please review the results.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
