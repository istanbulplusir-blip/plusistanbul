#!/bin/bash

# Script to deploy iOS map fix
# Date: 2025-10-20

set -e

echo "=========================================="
echo "Deploying iOS Map Fix"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running in plusistanbul directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found. Please run this script from the plusistanbul directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Stopping containers...${NC}"
docker-compose down

echo ""
echo -e "${YELLOW}Step 2: Building frontend with iOS map fixes...${NC}"
docker-compose build frontend

echo ""
echo -e "${YELLOW}Step 3: Starting services...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}Step 4: Waiting for services to be ready...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}Step 5: Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "iOS Map Fix has been deployed successfully."
echo ""
echo "Changes applied:"
echo "  ✓ Improved touch handling for iOS devices"
echo "  ✓ Custom zoom controls for better mobile experience"
echo "  ✓ Fixed zoom control flickering"
echo "  ✓ Enhanced tap detection on maps"
echo ""
echo "Please test on an iOS device:"
echo "  1. Navigate to transfers booking page"
echo "  2. Click 'Select from Map'"
echo "  3. Try clicking on the map to select a location"
echo "  4. Test zoom controls"
echo ""
echo -e "${YELLOW}View logs:${NC} docker-compose logs -f frontend"
echo -e "${YELLOW}Restart:${NC} docker-compose restart frontend"
echo ""
