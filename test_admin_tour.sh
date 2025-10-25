#!/bin/bash

echo "🔍 Testing Admin Tour Access..."
echo ""

# Test 1: Check if tour exists
echo "1️⃣ Checking if tour exists..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell << 'EOF'
from tours.models import Tour
tour = Tour.objects.filter(slug='istanbul-bosphorus-cruise').first()
if tour:
    print(f"✅ Tour exists: {tour.slug}")
    print(f"   ID: {tour.id}")
    print(f"   Title (current): {tour.title}")
else:
    print("❌ Tour not found")
EOF

echo ""
echo "2️⃣ Testing tour admin access..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell << 'EOF'
from django.contrib import admin
from tours.models import Tour
from tours.admin import TourAdmin

# Check if TourAdmin is registered
if Tour in admin.site._registry:
    print("✅ TourAdmin is registered")
    tour_admin = admin.site._registry[Tour]
    print(f"   Admin class: {tour_admin.__class__.__name__}")
else:
    print("❌ TourAdmin is NOT registered")
EOF

echo ""
echo "3️⃣ Testing tour translations..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell << 'EOF'
from tours.models import Tour
from django.utils.translation import activate

tour = Tour.objects.first()
if tour:
    print("✅ Testing translations:")
    
    # Get all translations
    translations = tour.translations.all()
    print(f"   Total translations: {translations.count()}")
    
    for trans in translations:
        print(f"   - {trans.language_code}: {trans.title}")
else:
    print("❌ No tour found")
EOF

echo ""
echo "4️⃣ Testing admin URL..."
echo "   Admin URL: https://peykantravelistanbul.com/admin/tours/tour/"
echo "   Tour edit URL: https://peykantravelistanbul.com/admin/tours/tour/$(docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell -c "from tours.models import Tour; t=Tour.objects.first(); print(t.id if t else '')" 2>/dev/null | tail -1 | tr -d '\r')/change/"

echo ""
echo "5️⃣ Checking for any errors in recent logs..."
docker-compose -f docker-compose.production-secure.yml logs --tail=20 backend 2>&1 | grep -i "error\|exception\|traceback" || echo "   ✅ No errors found in recent logs"

echo ""
echo "✅ Test complete!"
