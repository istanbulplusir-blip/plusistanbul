#!/bin/bash

# Test Event API Script
# This script tests the created sample event API endpoints

BASE_URL="http://localhost:8000/api"
EVENT_SLUG="istanbul-music-festival-2025"

echo "=========================================="
echo "Testing Event API Endpoints"
echo "=========================================="
echo ""

# Test 1: List all events
echo "1️⃣  Testing: GET /api/events/"
echo "---"
curl -s "${BASE_URL}/events/" | python -m json.tool | head -20
echo ""
echo ""

# Test 2: Get event details in Persian
echo "2️⃣  Testing: GET /api/events/${EVENT_SLUG}/ (Persian)"
echo "---"
curl -s -H "Accept-Language: fa" "${BASE_URL}/events/${EVENT_SLUG}/" | python -m json.tool | head -30
echo ""
echo ""

# Test 3: Get event details in English
echo "3️⃣  Testing: GET /api/events/${EVENT_SLUG}/ (English)"
echo "---"
curl -s -H "Accept-Language: en" "${BASE_URL}/events/${EVENT_SLUG}/" | python -m json.tool | head -30
echo ""
echo ""

# Test 4: Get event details in Arabic
echo "4️⃣  Testing: GET /api/events/${EVENT_SLUG}/ (Arabic)"
echo "---"
curl -s -H "Accept-Language: ar" "${BASE_URL}/events/${EVENT_SLUG}/" | python -m json.tool | head -30
echo ""
echo ""

# Test 5: Get event categories
echo "5️⃣  Testing: GET /api/categories/"
echo "---"
curl -s -H "Accept-Language: fa" "${BASE_URL}/categories/" | python -m json.tool
echo ""
echo ""

# Test 6: Get venues
echo "6️⃣  Testing: GET /api/venues/"
echo "---"
curl -s -H "Accept-Language: fa" "${BASE_URL}/venues/" | python -m json.tool
echo ""
echo ""

# Test 7: Get artists
echo "7️⃣  Testing: GET /api/artists/"
echo "---"
curl -s -H "Accept-Language: fa" "${BASE_URL}/artists/" | python -m json.tool
echo ""
echo ""

# Test 8: Search events
echo "8️⃣  Testing: GET /api/events/search/?q=music"
echo "---"
curl -s -H "Accept-Language: fa" "${BASE_URL}/events/search/?q=music" | python -m json.tool | head -30
echo ""
echo ""

echo "=========================================="
echo "✅ All tests completed!"
echo "=========================================="
echo ""
echo "To test performances and seats, you need to get the event ID first:"
echo "curl -s '${BASE_URL}/events/${EVENT_SLUG}/' | python -m json.tool | grep '\"id\"'"
echo ""
