# متغیرهای محیطی حالت توسعه - Peykan Tourism Platform

این فایل شامل تمام متغیرهای محیطی مورد نیاز برای حالت توسعه (Development) پروژه Peykan Tourism Platform است.

## 📁 فایل‌های Environment موجود

### 1. `backend/env.development` - محیط توسعه ساده

### 2. `backend/env.example` - نمونه متغیرهای محیطی

### 3. `backend/env.production.dev` - محیط شبیه‌سازی پروداکشن

---

## 🔧 متغیرهای محیطی Development

### **Django Settings**

```bash
# تنظیمات اصلی Django
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

### **Database Configuration**

```bash
# دیتابیس SQLite برای توسعه
DATABASE_URL=sqlite:///db.sqlite3

# یا PostgreSQL برای تست
# DATABASE_URL=postgresql://peykan_user:dev_password_123@postgres:5432/peykan
```

### **Redis Cache**

```bash
# Redis برای Cache
REDIS_URL=redis://localhost:6379/1

# یا با پسورد
# REDIS_URL=redis://:dev_redis_123@redis:6379/1
```

### **CORS Settings**

```bash
# تنظیمات CORS برای توسعه
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002
```

### **Internationalization**

```bash
# تنظیمات زبان
LANGUAGES=fa,en,tr
DEFAULT_LANGUAGE=fa
```

### **Currency Settings**

```bash
# تنظیمات ارز
DEFAULT_CURRENCY=USD
SUPPORTED_CURRENCIES=USD,EUR,TRY,IRR
```

### **Email Configuration**

```bash
# تنظیمات ایمیل برای توسعه
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@peykantravelistanbul.com
```

### **SMS Service**

```bash
# Kavenegar SMS - Mock برای توسعه
KAVENEGAR_API_KEY=mock-api-key-for-development
```

### **File Storage**

```bash
# تنظیمات فایل‌ها
MEDIA_URL=/media/
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
```

### **JWT Settings**

```bash
# تنظیمات JWT
JWT_SECRET_KEY=dev-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### **Payment Gateway**

```bash
# درگاه پرداخت Mock برای توسعه
PAYMENT_GATEWAY=mock
PAYMENT_SECRET_KEY=mock-secret-key
```

### **Google OAuth**

```bash
# Google OAuth - Mock برای توسعه
GOOGLE_CLIENT_ID=mock-google-client-id
GOOGLE_CLIENT_SECRET=mock-google-client-secret
```

### **Security Settings**

```bash
# تنظیمات امنیتی - غیرفعال برای توسعه
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_BROWSER_XSS_FILTER=False
SECURE_CONTENT_TYPE_NOSNIFF=False
```

### **File Upload Settings**

```bash
# تنظیمات آپلود فایل
FILE_UPLOAD_MAX_MEMORY_SIZE=10
DATA_UPLOAD_MAX_MEMORY_SIZE=10
```

### **Image Processing Settings**

```bash
# تنظیمات پردازش تصویر
IMAGE_MAX_SIZE=1920,1080
IMAGE_QUALITY=85
MAX_IMAGE_SIZE_MB=10
```

---

## 🚀 محیط شبیه‌سازی پروداکشن (Production-like Development)

### **Django Settings**

```bash
# تنظیمات شبیه‌سازی پروداکشن
DEBUG=False
SECRET_KEY=dev_secret_key_change_in_production_12345678901234567890
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,peykantravelistanbul.com,www.peykantravelistanbul.com
```

### **Database - PostgreSQL**

```bash
# دیتابیس PostgreSQL با SSL
DATABASE_URL=postgresql://peykan_user:dev_password_123@postgres:5432/peykan
```

### **Redis Cache - با پسورد**

```bash
# Redis با پسورد امن
REDIS_URL=redis://:dev_redis_123@redis:6379/1
```

### **CORS - محدود به دامنه‌های مجاز**

```bash
# CORS برای دامنه‌های مجاز
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://peykantravelistanbul.com,https://www.peykantravelistanbul.com
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://peykantravelistanbul.com,https://www.peykantravelistanbul.com
```

### **Email Configuration - SMTP**

```bash
# تنظیمات ایمیل SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-secure-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@peykantravelistanbul.com
```

### **Security Settings - فعال**

```bash
# تنظیمات امنیتی فعال
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

### **Additional Security Headers**

```bash
# هدرهای امنیتی اضافی
SECURE_REFERRER_POLICY=strict-origin-when-cross-origin
SECURE_CROSS_ORIGIN_OPENER_POLICY=same-origin
```

### **Database Security**

```bash
# امنیت دیتابیس
DATABASE_CONNECTION_MAX_AGE=600
DATABASE_CONNECTION_HEALTH_CHECKS=True
```

### **Cache Security**

```bash
# امنیت Cache
CACHE_KEY_PREFIX=peykan_dev_
CACHE_TIMEOUT=300
```

### **Rate Limiting**

```bash
# محدودیت نرخ درخواست
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### **Logging**

```bash
# تنظیمات Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log
```

### **Docker Secrets**

```bash
# رمزهای عبور Docker
POSTGRES_PASSWORD=dev_password_123
REDIS_PASSWORD=dev_redis_123
```

---

## 🎯 نحوه استفاده

### **1. محیط توسعه ساده:**

```bash
# کپی کردن فایل
cp backend/env.development backend/.env

# اجرای پروژه
python manage.py runserver
```

### **2. محیط شبیه‌سازی پروداکشن:**

```bash
# کپی کردن فایل
cp backend/env.production.dev backend/.env

# اجرای با Docker
docker-compose -f docker-compose.production-dev.yml up -d
```

### **3. استفاده از نمونه:**

```bash
# کپی کردن فایل نمونه
cp backend/env.example backend/.env

# ویرایش متغیرها
nano backend/.env
```

---

## ⚠️ نکات مهم

### **امنیت:**

- هرگز کلیدهای واقعی را در فایل‌های توسعه قرار ندهید
- از کلیدهای Mock برای سرویس‌های خارجی استفاده کنید
- پسوردهای پیش‌فرض را در پروداکشن تغییر دهید

### **توسعه:**

- از SQLite برای توسعه سریع استفاده کنید
- از Console Email Backend برای تست ایمیل استفاده کنید
- Debug mode را در پروداکشن غیرفعال کنید

### **تست:**

- از محیط شبیه‌سازی پروداکشن برای تست نهایی استفاده کنید
- تمام تنظیمات امنیتی را قبل از Deploy تست کنید
- از Docker برای شبیه‌سازی محیط پروداکشن استفاده کنید

---

## 📋 چک‌لیست تنظیمات

### **✅ Development Environment:**

- [ ] فایل `.env` ایجاد شده
- [ ] متغیرهای Django تنظیم شده
- [ ] دیتابیس SQLite پیکربندی شده
- [ ] CORS برای localhost تنظیم شده
- [ ] ایمیل Console Backend فعال
- [ ] Debug mode فعال

### **✅ Production-like Environment:**

- [ ] فایل `env.production.dev` ایجاد شده
- [ ] PostgreSQL پیکربندی شده
- [ ] Redis با پسورد تنظیم شده
- [ ] CORS برای دامنه اصلی تنظیم شده
- [ ] تنظیمات امنیتی فعال
- [ ] Docker Compose آماده

---

## 🔗 لینک‌های مفید

- **Django Settings**: `backend/peykan/settings.py`
- **Production Settings**: `backend/peykan/settings_production.py`
- **Docker Compose Dev**: `docker-compose.production-dev.yml`
- **Docker Compose Prod**: `docker-compose.production-secure.yml`

---

**نکته**: این فایل شامل تمام متغیرهای محیطی مورد نیاز برای توسعه است. برای پروداکشن، از فایل‌های مخصوص پروداکشن استفاده کنید.
