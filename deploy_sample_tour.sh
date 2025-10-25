#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   دیپلوی تور نمونه استانبول${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# بررسی اینکه در مسیر صحیح هستیم
if [ ! -f "docker-compose.production-secure.yml" ]; then
    echo -e "${RED}❌ خطا: فایل docker-compose.production-secure.yml یافت نشد${NC}"
    echo -e "${YELLOW}لطفاً این اسکریپت را از پوشه اصلی پروژه اجرا کنید${NC}"
    exit 1
fi

# مرحله 1: بررسی وضعیت کانتینرها
echo -e "${BLUE}📋 مرحله 1: بررسی وضعیت کانتینرها...${NC}"
docker-compose -f docker-compose.production-secure.yml ps

# مرحله 2: اجرای تور نمونه
echo ""
echo -e "${BLUE}🚀 مرحله 2: ایجاد تور نمونه استانبول...${NC}"
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py create_istanbul_bosphorus_tour

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ تور با موفقیت ایجاد شد${NC}"
else
    echo -e "${RED}❌ خطا در ایجاد تور${NC}"
    exit 1
fi

# مرحله 3: اضافه کردن نظرات
echo ""
echo -e "${BLUE}💬 مرحله 3: اضافه کردن نظرات کاربران...${NC}"
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py add_istanbul_bosphorus_reviews

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ نظرات با موفقیت اضافه شدند${NC}"
else
    echo -e "${YELLOW}⚠️  هشدار: مشکل در اضافه کردن نظرات${NC}"
fi

# مرحله 4: Restart کردن frontend برای اعمال تغییرات
echo ""
echo -e "${BLUE}🔄 مرحله 4: Restart کردن frontend...${NC}"
docker-compose -f docker-compose.production-secure.yml restart frontend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend با موفقیت restart شد${NC}"
else
    echo -e "${YELLOW}⚠️  هشدار: مشکل در restart کردن frontend${NC}"
fi

# مرحله 5: نمایش اطلاعات تور
echo ""
echo -e "${BLUE}📊 مرحله 5: اطلاعات تور ایجاد شده...${NC}"
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py shell << 'EOF'
from tours.models import Tour

tour = Tour.objects.filter(slug='istanbul-bosphorus-cruise').first()
if tour:
    print("\n" + "="*60)
    print("✅ تور با موفقیت ایجاد شد!")
    print("="*60)
    print(f"نام تور: {tour.title}")
    print(f"Slug: {tour.slug}")
    print(f"قیمت: ${tour.price}")
    print(f"مدت زمان: {tour.duration_hours} ساعت")
    print(f"شهر: {tour.city}")
    print(f"کشور: {tour.country}")
    print(f"تعداد Variants: {tour.variants.count()}")
    print(f"تعداد Schedules: {tour.schedules.count()}")
    print(f"تعداد Options: {tour.options.count()}")
    print(f"تعداد Itinerary Items: {tour.itinerary.count()}")
    print(f"تعداد نظرات: {tour.reviews.count()}")
    print("="*60)
else:
    print("❌ تور یافت نشد!")
EOF

# خلاصه نهایی
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ دیپلوی با موفقیت انجام شد!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}🌐 لینک‌های مفید:${NC}"
echo -e "   • سایت: ${YELLOW}https://peykantravelistanbul.com${NC}"
echo -e "   • تور: ${YELLOW}https://peykantravelistanbul.com/tours/istanbul-bosphorus-cruise${NC}"
echo -e "   • API: ${YELLOW}https://peykantravelistanbul.com/api/tours/tours/istanbul-bosphorus-cruise/${NC}"
echo -e "   • Admin: ${YELLOW}https://peykantravelistanbul.com/admin/tours/tour/${NC}"
echo ""
echo -e "${BLUE}📝 دستورات مفید:${NC}"
echo -e "   • مشاهده لاگ backend: ${YELLOW}docker-compose -f docker-compose.production-secure.yml logs -f backend${NC}"
echo -e "   • مشاهده لاگ frontend: ${YELLOW}docker-compose -f docker-compose.production-secure.yml logs -f frontend${NC}"
echo -e "   • بررسی وضعیت: ${YELLOW}docker-compose -f docker-compose.production-secure.yml ps${NC}"
echo ""
echo -e "${GREEN}موفق باشید! 🎉${NC}"
