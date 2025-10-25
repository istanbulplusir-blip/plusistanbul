# خلاصه دیپلوی تور نمونه استانبول

## ✅ تور با موفقیت ایجاد و دیپلوی شد!

### 📋 اطلاعات تور

**نام تور:** کروز بسفر استانبول و تور دو قاره  
**Slug:** `istanbul-bosphorus-cruise`  
**قیمت:** $45 (شروع از)  
**مدت زمان:** 6 ساعت  
**شهر:** Istanbul  
**کشور:** Turkey  

### 🌐 لینک‌های دسترسی

#### سایت اصلی:
- **صفحه اصلی:** https://peykantravelistanbul.com
- **لیست تورها:** https://peykantravelistanbul.com/tours
- **صفحه تور:** https://peykantravelistanbul.com/tours/istanbul-bosphorus-cruise

#### API Endpoints:
- **لیست تورها:** https://peykantravelistanbul.com/api/v1/tours/
- **جزئیات تور:** https://peykantravelistanbul.com/api/v1/tours/istanbul-bosphorus-cruise/
- **برنامه تور:** https://peykantravelistanbul.com/api/v1/tours/istanbul-bosphorus-cruise/itinerary/
- **نظرات:** https://peykantravelistanbul.com/api/v1/tours/istanbul-bosphorus-cruise/reviews/
- **گزینه‌ها:** https://peykantravelistanbul.com/api/v1/tours/istanbul-bosphorus-cruise/options/

#### پنل مدیریت:
- **Admin Panel:** https://peykantravelistanbul.com/admin/
- **مدیریت تورها:** https://peykantravelistanbul.com/admin/tours/tour/
- **مدیریت نظرات:** https://peykantravelistanbul.com/admin/tours/tourreview/

### 📊 آمار تور

- **تعداد Variants:** 4 (ECONOMY, STANDARD, PREMIUM, VIP)
- **تعداد Schedules:** 14 روز آینده
- **تعداد Options:** 5 گزینه اضافی
- **تعداد Itinerary Items:** 9 مرحله
- **تعداد Cancellation Policies:** 5 سیاست
- **تعداد نظرات:** 15 نظر (میانگین: 4.8⭐)

### 🎯 ویژگی‌های تور

#### Variants (انواع بسته):
1. **ECONOMY** - $45
   - صندلی استاندارد قایق
   - ظرفیت: 60 نفر

2. **STANDARD** - $65
   - صندلی عرشه بالایی
   - ظرفیت: 50 نفر

3. **PREMIUM** - $95
   - دسترسی به لانژ VIP
   - عکاس حرفه‌ای
   - ظرفیت: 30 نفر

4. **VIP** - $150
   - کابین خصوصی
   - خدمات انحصاری
   - غذای ویژه
   - ظرفیت: 10 نفر

#### Options (گزینه‌های اضافی):
1. **Professional Photography Package** - $35
2. **Premium Lunch Upgrade** - $25
3. **Private Guide** - $80
4. **Sunset Cruise Upgrade** - $20
5. **Turkish Tea & Snacks** - $10

#### Itinerary (برنامه تور):
1. پیکاپ از هتل (30 دقیقه)
2. بازدید از کاخ دلمه‌باغچه (60 دقیقه)
3. کروز بسفر (120 دقیقه)
4. عبور از پل بسفر (15 دقیقه)
5. ناهار ترکی (75 دقیقه)
6. توقف عکس در قلعه روملی (30 دقیقه)
7. منظره برج دختر (20 دقیقه)
8. بازدید از میدان اورتاکوی (30 دقیقه)
9. بازگشت به هتل (30 دقیقه)

### 🌍 پشتیبانی از زبان‌ها

تور به صورت کامل به 3 زبان ترجمه شده است:
- ✅ **انگلیسی** (English)
- ✅ **ترکی** (Türkçe)
- ✅ **فارسی** (Persian)

### 💬 نظرات کاربران

- **تعداد کل نظرات:** 15
- **میانگین امتیاز:** 4.8 از 5
- **5 ستاره:** 12 نظر
- **4 ستاره:** 3 نظر
- **نظرات به 3 زبان:** انگلیسی، ترکی، فارسی

### 🔧 دستورات مفید

#### مشاهده لاگ‌ها:
```bash
# لاگ backend
docker-compose -f docker-compose.production-secure.yml logs -f backend

# لاگ frontend
docker-compose -f docker-compose.production-secure.yml logs -f frontend

# لاگ nginx
docker-compose -f docker-compose.production-secure.yml logs -f nginx
```

#### بررسی وضعیت:
```bash
# وضعیت کانتینرها
docker-compose -f docker-compose.production-secure.yml ps

# تست API
curl https://peykantravelistanbul.com/api/v1/tours/
```

#### مدیریت تور:
```bash
# ورود به shell Django
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py shell

# مشاهده تورها
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py shell -c "from tours.models import Tour; print(Tour.objects.all())"
```

### 📝 نکات مهم

1. **تصاویر:** تور فعلاً از تصویر پیش‌فرض استفاده می‌کند. می‌توانید از پنل Admin تصاویر واقعی آپلود کنید.

2. **Schedules:** 14 روز آینده به صورت خودکار ایجاد شده است. می‌توانید از پنل Admin schedules بیشتری اضافه کنید.

3. **Capacity:** ظرفیت هر variant به صورت خودکار مدیریت می‌شود.

4. **Pricing:** قیمت‌ها به دلار آمریکا هستند. می‌توانید از پنل Admin تغییر دهید.

### 🎨 آپلود تصاویر

برای آپلود تصاویر تور:

1. وارد Admin Panel شوید
2. به `Tours > Tours` بروید
3. روی تور "Istanbul Bosphorus Cruise" کلیک کنید
4. در بخش Image، تصویر اصلی را آپلود کنید
5. برای گالری، به `Tour Gallery Images` بروید و تصاویر بیشتری اضافه کنید

**سایز توصیه شده تصاویر:**
- تصویر اصلی: 1200x800 پیکسل
- تصاویر گالری: 1920x1080 پیکسل
- فرمت: JPG یا PNG
- حداکثر حجم: 5MB

### 🔄 به‌روزرسانی تور

اگر می‌خواهید تور را به‌روزرسانی کنید:

```bash
# اجرای مجدد command
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py create_istanbul_bosphorus_tour

# Restart frontend
docker-compose -f docker-compose.production-secure.yml restart frontend
```

### 🆘 عیب‌یابی

#### مشکل: تور در سایت نمایش داده نمی‌شود
**راه‌حل:**
```bash
# Restart frontend
docker-compose -f docker-compose.production-secure.yml restart frontend

# پاک کردن cache مرورگر
```

#### مشکل: تصاویر نمایش داده نمی‌شوند
**راه‌حل:**
```bash
# بررسی permissions
chmod -R 755 /home/djangouser/plusistanbul/backend/media

# Restart nginx
docker-compose -f docker-compose.production-secure.yml restart nginx
```

#### مشکل: API خطا می‌دهد
**راه‌حل:**
```bash
# بررسی لاگ backend
docker-compose -f docker-compose.production-secure.yml logs backend

# Restart backend
docker-compose -f docker-compose.production-secure.yml restart backend
```

### 📞 پشتیبانی

اگر مشکلی پیش آمد:

1. لاگ‌ها را بررسی کنید
2. وضعیت کانتینرها را چک کنید
3. در صورت نیاز، تمام سرویس‌ها را restart کنید:

```bash
docker-compose -f docker-compose.production-secure.yml restart
```

---

## ✅ خلاصه

تور نمونه "کروز بسفر استانبول" با موفقیت ایجاد و در پروداکشن دیپلوی شد. تور به صورت کامل به 3 زبان (انگلیسی، ترکی، فارسی) ترجمه شده و شامل 4 variant، 14 schedule، 5 option، 9 itinerary item و 15 نظر کاربر است.

**تور در آدرس زیر قابل مشاهده است:**
https://peykantravelistanbul.com/tours/istanbul-bosphorus-cruise

**موفق باشید! 🎉**
