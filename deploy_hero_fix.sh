#!/bin/bash

echo "========================================="
echo "Deploying Hero Images Fix to Production"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop on error
set -e

echo ""
echo "${YELLOW}Step 1: Stopping containers...${NC}"
cd /home/djangouser/plusistanbul
docker-compose down

echo ""
echo "${YELLOW}Step 2: Creating placeholder images...${NC}"
cd /home/djangouser/plusistanbul/backend
python3 create_placeholders.py

echo ""
echo "${YELLOW}Step 3: Running migrations...${NC}"
docker-compose run --rm backend python manage.py migrate shared

echo ""
echo "${YELLOW}Step 4: Creating sample hero slider...${NC}"
docker-compose run --rm backend python manage.py shell << EOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')

from shared.models import HeroSlider
from django.core.files import File

# Check if hero slider already exists
if not HeroSlider.objects.filter(is_active=True).exists():
    print("Creating sample Hero Slider...")
    
    hero = HeroSlider.objects.create(
        order=1,
        is_active=True,
        display_duration=5000,
        button_url='/tours',
        button_type='primary',
        show_for_authenticated=True,
        show_for_anonymous=True,
        video_type='none',
        autoplay_video=False,
        video_muted=True,
        show_video_controls=False,
        video_loop=True
    )
    
    # Set translatable fields
    hero.set_current_language('fa')
    hero.title = 'به پیکان توریسم خوش آمدید'
    hero.subtitle = 'بهترین تورهای استانبول'
    hero.description = 'تجربه‌ای فراموش‌نشدنی در استانبول'
    hero.button_text = 'مشاهده تورها'
    hero.save()
    
    hero.set_current_language('en')
    hero.title = 'Welcome to Peykan Tourism'
    hero.subtitle = 'Best Istanbul Tours'
    hero.description = 'Unforgettable experience in Istanbul'
    hero.button_text = 'View Tours'
    hero.save()
    
    print(f"✓ Created Hero Slider: {hero.title}")
else:
    print("Hero slider already exists!")
EOF

echo ""
echo "${YELLOW}Step 5: Collecting static files...${NC}"
docker-compose run --rm backend python manage.py collectstatic --noinput

echo ""
echo "${YELLOW}Step 6: Building and starting containers...${NC}"
docker-compose up -d --build

echo ""
echo "${YELLOW}Step 7: Waiting for services to start...${NC}"
sleep 10

echo ""
echo "${YELLOW}Step 8: Checking container status...${NC}"
docker-compose ps

echo ""
echo "${GREEN}=========================================${NC}"
echo "${GREEN}Deployment Complete!${NC}"
echo "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Check logs: docker-compose logs -f backend"
echo "2. Visit admin: https://peykantravelistanbul.com/admin/"
echo "3. Visit site: https://peykantravelistanbul.com/"
echo ""
echo "To test API:"
echo "curl https://peykantravelistanbul.com/api/shared/hero-sliders/active/"
echo ""
