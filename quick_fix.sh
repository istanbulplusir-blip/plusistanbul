#!/bin/bash

echo "🚀 Quick Fix for Hero Images"
echo "=============================="

cd /home/djangouser/plusistanbul

# 1. Create placeholder images
echo "📸 Creating placeholder images..."
cd backend
python3 create_placeholders.py
cd ..

# 2. Rebuild and restart containers
echo "🔄 Rebuilding containers..."
docker-compose -f docker-compose.production-secure.yml up -d --build backend

# 3. Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# 4. Run migrations inside container
echo "📦 Running migrations..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py migrate shared

# 5. Create sample hero if needed
echo "🎨 Creating sample hero slider..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell << 'EOF'
from shared.models import HeroSlider
if not HeroSlider.objects.filter(is_active=True).exists():
    hero = HeroSlider.objects.create(
        order=1, is_active=True, display_duration=5000,
        button_url='/tours', button_type='primary',
        show_for_authenticated=True, show_for_anonymous=True,
        video_type='none'
    )
    hero.set_current_language('fa')
    hero.title = 'به پیکان توریسم خوش آمدید'
    hero.subtitle = 'بهترین تورهای استانبول'
    hero.button_text = 'مشاهده تورها'
    hero.save()
    print("✓ Hero slider created!")
else:
    print("✓ Hero slider already exists!")
EOF

# 6. Restart frontend
echo "🎨 Restarting frontend..."
docker-compose -f docker-compose.production-secure.yml restart frontend

echo ""
echo "✅ Done! Check your site at:"
echo "   https://peykantravelistanbul.com"
echo ""
echo "📊 Check logs with:"
echo "   docker-compose -f docker-compose.production-secure.yml logs -f backend"
echo "   docker-compose -f docker-compose.production-secure.yml logs -f frontend"
