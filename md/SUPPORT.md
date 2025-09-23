# راهنمای پشتیبانی پروژه Peykan Tourism

## 📋 فهرست مطالب
- [کانال‌های پشتیبانی](#کانال‌های-پشتیبانی)
- [مشکلات رایج](#مشکلات-رایج)
- [زمان‌بندی پاسخ](#زمان‌بندی-پاسخ)
- [فرآیند پشتیبانی](#فرآیند-پشتیبانی)
- [تماس‌های اضطراری](#تماس‌های-اضطراری)
- [منابع خودآموز](#منابع-خودآموز)

## 📞 کانال‌های پشتیبانی

### پشتیبانی فنی
- **GitHub Issues**: [ایجاد Issue جدید](https://github.com/PeykanTravel/peykan-tourism/issues/new)
- **GitHub Discussions**: [بحث‌های عمومی](https://github.com/PeykanTravel/peykan-tourism/discussions)
- **ایمیل فنی**: tech-support@peykantravelistanbul.com
- **تلگرام فنی**: @PeykanTech

### پشتیبانی کاربری
- **ایمیل کاربری**: support@peykantravelistanbul.com
- **تلگرام کاربری**: @PeykanSupport
- **چت زنده**: [لینک چت زنده](https://peykantravelistanbul.com/chat)
- **فرم تماس**: [فرم تماس](https://peykantravelistanbul.com/contact)

### پشتیبانی تجاری
- **ایمیل تجاری**: business@peykantravelistanbul.com
- **تلگرام تجاری**: @PeykanBusiness
- **شماره تماس**: +90 XXX XXX XXXX

## 🔧 مشکلات رایج

### مشکلات راه‌اندازی

#### مشکل: Docker services راه‌اندازی نمی‌شوند
```bash
# راه‌حل 1: بررسی وضعیت Docker
docker --version
docker-compose --version

# راه‌حل 2: پاک کردن و rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# راه‌حل 3: بررسی لاگ‌ها
docker-compose logs -f
```

#### مشکل: اتصال به پایگاه داده
```bash
# راه‌حل 1: بررسی وضعیت PostgreSQL
docker-compose ps postgres
docker-compose logs postgres

# راه‌حل 2: تست اتصال
docker-compose exec backend python manage.py dbshell

# راه‌حل 3: تنظیم مجدد متغیرهای محیطی
# بررسی فایل backend/.env
```

#### مشکل: Frontend بارگذاری نمی‌شود
```bash
# راه‌حل 1: بررسی وضعیت Next.js
docker-compose ps frontend
docker-compose logs frontend

# راه‌حل 2: پاک کردن cache
docker-compose exec frontend npm run clean
docker-compose restart frontend

# راه‌حل 3: بررسی متغیرهای محیطی
# بررسی فایل frontend/.env.local
```

### مشکلات API

#### مشکل: خطای CORS
```javascript
// راه‌حل: بررسی تنظیمات CORS در backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### مشکل: خطای 500 در API
```bash
# راه‌حل 1: بررسی لاگ‌های backend
docker-compose logs -f backend

# راه‌حل 2: اجرای migration ها
docker-compose exec backend python manage.py migrate

# راه‌حل 3: جمع‌آوری فایل‌های استاتیک
docker-compose exec backend python manage.py collectstatic --noinput
```

#### مشکل: خطای احراز هویت
```bash
# راه‌حل 1: بررسی تنظیمات JWT
# بررسی JWT_SECRET_KEY در backend/.env

# راه‌حل 2: پاک کردن cache
docker-compose exec redis redis-cli FLUSHALL

# راه‌حل 3: بررسی لاگ‌های احراز هویت
docker-compose logs backend | grep -i auth
```

### مشکلات عملکرد

#### مشکل: کندی بارگذاری صفحات
```bash
# راه‌حل 1: بررسی استفاده از منابع
docker stats

# راه‌حل 2: بهینه‌سازی تصاویر
# استفاده از WebP format
# فشرده‌سازی تصاویر

# راه‌حل 3: فعال‌سازی cache
# بررسی تنظیمات Redis
```

#### مشکل: خطای حافظه
```bash
# راه‌حل 1: افزایش حافظه Docker
# تنظیم Docker Desktop memory limit

# راه‌حل 2: بهینه‌سازی queries
# بررسی slow queries در PostgreSQL

# راه‌حل 3: پاک کردن cache
docker system prune -a
```

## ⏰ زمان‌بندی پاسخ

### سطوح اولویت
| سطح | زمان پاسخ | زمان حل |
|------|-----------|---------|
| Critical | 2 ساعت | 24 ساعت |
| High | 4 ساعت | 48 ساعت |
| Medium | 8 ساعت | 72 ساعت |
| Low | 24 ساعت | 1 هفته |

### ساعات کاری
- **شنبه تا چهارشنبه**: 9:00 - 18:00 (GMT+3)
- **پنجشنبه**: 9:00 - 17:00 (GMT+3)
- **جمعه**: تعطیل (فقط موارد اضطراری)

### خارج از ساعات کاری
برای موارد اضطراری خارج از ساعات کاری:
1. ارسال ایمیل با موضوع "URGENT"
2. تماس تلگرامی با @PeykanEmergency
3. در صورت عدم پاسخ، تماس تلفنی

## 🔄 فرآیند پشتیبانی

### مرحله 1: دریافت درخواست
- **ثبت**: درخواست در سیستم ثبت می‌شود
- **اولویت‌بندی**: تعیین اولویت بر اساس نوع مشکل
- **تخصیص**: تخصیص به متخصص مناسب

### مرحله 2: بررسی اولیه
- **تشخیص**: تشخیص اولیه مشکل
- **جمع‌آوری اطلاعات**: جمع‌آوری اطلاعات بیشتر
- **راه‌حل سریع**: ارائه راه‌حل سریع در صورت امکان

### مرحله 3: حل مشکل
- **تحلیل**: تحلیل دقیق مشکل
- **توسعه راه‌حل**: توسعه راه‌حل مناسب
- **تست**: تست راه‌حل
- **استقرار**: استقرار راه‌حل

### مرحله 4: پیگیری
- **تأیید**: تأیید حل مشکل
- **مستندسازی**: مستندسازی راه‌حل
- **بازخورد**: جمع‌آوری بازخورد کاربر

## 🚨 تماس‌های اضطراری

### مشکلات بحرانی
- **ایمیل اضطراری**: emergency@peykantravelistanbul.com
- **تلگرام اضطراری**: @PeykanEmergency
- **شماره اضطراری**: +90 XXX XXX XXXX

### تعریف مشکلات بحرانی
- **Downtime کامل**: سایت کاملاً غیرقابل دسترسی
- **نشت داده**: نشت اطلاعات حساس
- **مشکلات امنیتی**: آسیب‌پذیری‌های امنیتی
- **مشکلات پرداخت**: اختلال در سیستم پرداخت

### فرآیند اضطراری
1. **تشخیص**: تشخیص سریع مشکل
2. **اعلام**: اعلام به تیم اضطراری
3. **کنترل**: کنترل و محدود کردن آسیب
4. **حل**: حل سریع مشکل
5. **بازسازی**: بازسازی کامل سیستم

## 📚 منابع خودآموز

### مستندات رسمی
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - راهنمای کامل توسعه
- [CONTRIBUTING.md](CONTRIBUTING.md) - راهنمای مشارکت
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - چک‌لیست استقرار
- [API Documentation](https://api.peykantravelistanbul.com/docs) - مستندات API

### آموزش‌های ویدیویی
- [راه‌اندازی محیط توسعه](https://youtube.com/playlist?list=...)
- [استفاده از API](https://youtube.com/playlist?list=...)
- [عیب‌یابی مشکلات رایج](https://youtube.com/playlist?list=...)

### مقالات آموزشی
- [بهترین شیوه‌های Docker](https://blog.peykantravelistanbul.com/docker-best-practices)
- [بهینه‌سازی عملکرد](https://blog.peykantravelistanbul.com/performance-optimization)
- [امنیت در Django](https://blog.peykantravelistanbul.com/django-security)

### ابزارهای مفید
- **Postman**: تست API
- **pgAdmin**: مدیریت پایگاه داده
- **Redis Commander**: مدیریت Redis
- **Docker Desktop**: مدیریت کانتینرها

## 🎯 انواع پشتیبانی

### پشتیبانی فنی
- **راه‌اندازی محیط**: کمک در راه‌اندازی محیط توسعه
- **عیب‌یابی**: کمک در رفع مشکلات فنی
- **بهینه‌سازی**: کمک در بهبود عملکرد
- **امنیت**: کمک در مسائل امنیتی

### پشتیبانی کاربری
- **راهنمایی**: راهنمایی در استفاده از سیستم
- **آموزش**: آموزش ویژگی‌های جدید
- **پیکربندی**: کمک در تنظیمات
- **انتقال داده**: کمک در انتقال داده‌ها

### پشتیبانی تجاری
- **مشاوره**: مشاوره در انتخاب راه‌حل‌ها
- **قیمت‌گذاری**: اطلاعات قیمت‌ها
- **قرارداد**: کمک در تنظیم قراردادها
- **ادغام**: کمک در ادغام با سیستم‌های موجود

## 📊 آمار پشتیبانی

### آمار پاسخ‌دهی
- **زمان پاسخ متوسط**: 4 ساعت
- **زمان حل متوسط**: 24 ساعت
- **رضایت کاربران**: 95%
- **مشکلات حل شده**: 98%

### حوزه‌های پشتیبانی
- **راه‌اندازی**: 30%
- **عیب‌یابی**: 40%
- **بهینه‌سازی**: 20%
- **آموزش**: 10%

## 🤝 مشارکت در بهبود

### پیشنهادات بهبود
- **ایجاد Issue**: [ایجاد Issue جدید](https://github.com/PeykanTravel/peykan-tourism/issues/new)
- **ایمیل**: feedback@peykantravelistanbul.com
- **فرم بازخورد**: [فرم بازخورد](https://peykantravelistanbul.com/feedback)

### مشارکت در مستندات
- **بهبود راهنماها**: مشارکت در بهبود مستندات
- **ترجمه**: کمک در ترجمه مستندات
- **مثال‌ها**: اضافه کردن مثال‌های کاربردی
- **ویدیو**: ایجاد ویدیوهای آموزشی

---

## 📞 اطلاعات تماس

### تیم پشتیبانی
- **مدیر پشتیبانی**: support-manager@peykantravelistanbul.com
- **تیم فنی**: tech-team@peykantravelistanbul.com
- **تیم کاربری**: user-support@peykantravelistanbul.com

### ساعات کاری
- **شنبه تا چهارشنبه**: 9:00 - 18:00 (GMT+3)
- **پنجشنبه**: 9:00 - 17:00 (GMT+3)
- **جمعه**: تعطیل (فقط موارد اضطراری)

### کانال‌های ارتباطی
- **GitHub**: [PeykanTravel/peykan-tourism](https://github.com/PeykanTravel/peykan-tourism)
- **تلگرام**: @PeykanSupport
- **ایمیل**: support@peykantravelistanbul.com
- **وب‌سایت**: [peykantravelistanbul.com](https://peykantravelistanbul.com)

---

*تیم پشتیبانی Peykan Tourism آماده کمک به شما در هر مرحله از توسعه و استفاده از پروژه است.* 