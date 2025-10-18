@echo off
REM Test Event API Script for Windows
REM This script tests the created sample event API endpoints

set BASE_URL=http://localhost:8000/api
set EVENT_SLUG=istanbul-music-festival-2025

echo ==========================================
echo Testing Event API Endpoints
echo ==========================================
echo.

REM Test 1: List all events
echo 1. Testing: GET /api/events/
echo ---
curl -s "%BASE_URL%/events/"
echo.
echo.

REM Test 2: Get event details in Persian
echo 2. Testing: GET /api/events/%EVENT_SLUG%/ (Persian)
echo ---
curl -s -H "Accept-Language: fa" "%BASE_URL%/events/%EVENT_SLUG%/"
echo.
echo.

REM Test 3: Get event details in English
echo 3. Testing: GET /api/events/%EVENT_SLUG%/ (English)
echo ---
curl -s -H "Accept-Language: en" "%BASE_URL%/events/%EVENT_SLUG%/"
echo.
echo.

REM Test 4: Get event details in Arabic
echo 4. Testing: GET /api/events/%EVENT_SLUG%/ (Arabic)
echo ---
curl -s -H "Accept-Language: ar" "%BASE_URL%/events/%EVENT_SLUG%/"
echo.
echo.

REM Test 5: Get event categories
echo 5. Testing: GET /api/categories/
echo ---
curl -s -H "Accept-Language: fa" "%BASE_URL%/categories/"
echo.
echo.

REM Test 6: Get venues
echo 6. Testing: GET /api/venues/
echo ---
curl -s -H "Accept-Language: fa" "%BASE_URL%/venues/"
echo.
echo.

REM Test 7: Get artists
echo 7. Testing: GET /api/artists/
echo ---
curl -s -H "Accept-Language: fa" "%BASE_URL%/artists/"
echo.
echo.

REM Test 8: Search events
echo 8. Testing: GET /api/events/search/?q=music
echo ---
curl -s -H "Accept-Language: fa" "%BASE_URL%/events/search/?q=music"
echo.
echo.

echo ==========================================
echo All tests completed!
echo ==========================================
echo.
echo To test performances and seats, you need to get the event ID first
echo.

pause
