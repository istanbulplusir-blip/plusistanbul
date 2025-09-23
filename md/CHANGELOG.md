# تاریخچه تغییرات پروژه Peykan Tourism

این فایل شامل تمام تغییرات مهم، ویژگی‌های جدید، رفع مشکلات و بهبودهای پروژه است.

## [Unreleased]

### Added
- راهنمای توسعه جامع با Docker
- اسکریپت‌های راه‌اندازی خودکار
- چک‌لیست استقرار تولید
- مستندات مشارکت و امنیت

### Changed
- بهبود ساختار مستندات
- به‌روزرسانی README اصلی

## [1.2.0] - 2024-01-15

### Added
- سیستم احراز هویت OTP با Kavenegar
- پشتیبانی از چندین ارز (USD, EUR, TRY, IRR)
- سیستم رزرو موقت برای مدیریت موجودی
- API برای مدیریت تورها و رویدادها
- سیستم سبد خرید پیشرفته

### Changed
- بهبود عملکرد API با caching
- بهینه‌سازی queries پایگاه داده
- بهبود UI/UX فرانت‌اند

### Fixed
- رفع مشکل CORS در API
- رفع مشکل timezone در تاریخ‌ها
- رفع مشکل encoding در فایل‌های فارسی

## [1.1.0] - 2024-01-01

### Added
- سیستم مدیریت کاربران با نقش‌های مختلف
- پنل مدیریت برای ادمین‌ها
- سیستم آپلود فایل با validation
- API برای مدیریت پروفایل کاربران

### Changed
- بهبود امنیت با JWT tokens
- بهینه‌سازی تصاویر
- بهبود responsive design

### Fixed
- رفع مشکل session management
- رفع مشکل file upload در Docker
- رفع مشکل RTL در فرانت‌اند

## [1.0.0] - 2023-12-15

### Added
- پیاده‌سازی کامل MVP
- سیستم تورها با variants و options
- سیستم رزرو و پرداخت
- پشتیبانی از سه زبان (فارسی، انگلیسی، ترکی)
- Docker containerization
- PostgreSQL و Redis integration

### Features
- **Frontend**: Next.js 14 با TypeScript
- **Backend**: Django 5 با DRF
- **Database**: PostgreSQL با UUID primary keys
- **Cache**: Redis برای session و caching
- **Deployment**: Docker Compose برای production

---

## نحوه نگارش

### انواع تغییرات
- **Added**: ویژگی‌های جدید
- **Changed**: تغییرات در ویژگی‌های موجود
- **Deprecated**: ویژگی‌هایی که در آینده حذف می‌شوند
- **Removed**: ویژگی‌های حذف شده
- **Fixed**: رفع مشکلات
- **Security**: بهبودهای امنیتی

### نسخه‌گذاری
از [Semantic Versioning](https://semver.org/) استفاده می‌کنیم:
- **MAJOR**: تغییرات ناسازگار با نسخه‌های قبلی
- **MINOR**: اضافه کردن ویژگی‌های جدید (سازگار)
- **PATCH**: رفع مشکلات (سازگار)

### مثال
```markdown
## [2.1.0] - 2024-02-01

### Added
- ویژگی جدید A
- ویژگی جدید B

### Changed
- بهبود ویژگی C
- تغییر در API endpoint D

### Fixed
- رفع مشکل در E
- رفع bug در F
```

---

## لینک‌های مفید

- [GitHub Releases](https://github.com/PeykanTravel/peykan-tourism/releases)
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) 