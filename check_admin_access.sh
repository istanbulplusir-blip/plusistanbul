#!/bin/bash

echo "🔍 بررسی دسترسی به Admin Panel..."
echo ""

# Test admin page
echo "1️⃣ تست صفحه اصلی Admin..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://peykantravelistanbul.com/admin/)
if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
    echo "   ✅ Admin در دسترس است (HTTP $STATUS)"
else
    echo "   ❌ مشکل در دسترسی به Admin (HTTP $STATUS)"
fi

echo ""
echo "2️⃣ تست صفحه لیست تورها..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://peykantravelistanbul.com/admin/tours/tour/)
if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
    echo "   ✅ صفحه تورها در دسترس است (HTTP $STATUS)"
else
    echo "   ❌ مشکل در دسترسی به صفحه تورها (HTTP $STATUS)"
fi

echo ""
echo "3️⃣ بررسی وضعیت backend..."
docker-compose -f docker-compose.production-secure.yml ps backend | grep -q "Up"
if [ $? -eq 0 ]; then
    echo "   ✅ Backend در حال اجرا است"
else
    echo "   ❌ Backend در حال اجرا نیست"
fi

echo ""
echo "4️⃣ تست API..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://peykantravelistanbul.com/api/v1/tours/)
if [ "$STATUS" = "200" ]; then
    echo "   ✅ API کار می‌کند (HTTP $STATUS)"
else
    echo "   ⚠️  API مشکل دارد (HTTP $STATUS)"
fi

echo ""
echo "5️⃣ بررسی تور در دیتابیس..."
docker-compose -f docker-compose.production-secure.yml exec -T backend python manage.py shell << 'EOF' 2>/dev/null
from tours.models import Tour
count = Tour.objects.count()
print(f"   ✅ تعداد تورها در دیتابیس: {count}")
if count > 0:
    tour = Tour.objects.first()
    print(f"   📋 آخرین تور: {tour.slug}")
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 لینک‌های مفید:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔐 Admin Panel:"
echo "   https://peykantravelistanbul.com/admin/"
echo ""
echo "📋 مدیریت تورها:"
echo "   https://peykantravelistanbul.com/admin/tours/tour/"
echo ""
echo "🌐 سایت:"
echo "   https://peykantravelistanbul.com"
echo ""
echo "🎯 تور نمونه:"
echo "   https://peykantravelistanbul.com/tours/istanbul-bosphorus-cruise"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 نکته: اگر خطای 500 می‌بینید، لاگ‌ها را بررسی کنید:"
echo "   docker-compose -f docker-compose.production-secure.yml logs backend"
echo ""
echo "✅ بررسی تکمیل شد!"
