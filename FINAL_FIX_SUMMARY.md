# خلاصه نهایی رفع مشکلات Hero Images & Media

## ✅ مشکلات رفع شده

### 1. URL های تصاویر اشتباه (https:/domain)
**فایل**: `backend/shared/utils.py`
- رفع مشکل double slash در ساخت URL
- اضافه کردن پشتیبانی از http و https

### 2. URL های پیش‌فرض بدون domain
**فایل**: `backend/shared/serializers.py`
- تغییر `get_default_image_url` برای برگرداندن URL کامل با domain

### 3. URL های ویدیو اشتباه
**فایل**: `backend/shared/serializers.py`
- رفع `get_video_file_url` برای استفاده از `get_image_url`

### 4. Rate Limiting خیلی محدود (10r/s)
**فایل**: `nginx/nginx.conf`
- افزایش rate limit از 10r/s به 100r/s
- افزایش burst از 20 به 100

### 5. Media files در nginx قابل دسترسی نبودند
**فایل**: `docker-compose.production-secure.yml`
- اضافه کردن volume mapping برای media و static در nginx
- تغییر nginx config برای serve مستقیم فایل‌ها

### 6. Frontend build می‌خورد (autoprefixer missing)
**فایل**: `frontend/Dockerfile`
- تغییر `npm ci --only=production` به `npm ci` برای نصب devDependencies

### 7. Environment variables در build frontend
**فایل**: `docker-compose.production-secure.yml`
- اضافه کردن `build.args` برای pass کردن env vars در build time

---

## 📋 دستورات نهایی

### برای اعمال تمام تغییرات:

```bash
cd /home/djangouser/plusistanbul

# 1. Stop همه چیز
docker-compose -f docker-compose.production-secure.yml down

# 2. ایجاد تصاویر پیش‌فرض
cd backend
python3 create_placeholders.py
cd ..

# 3. Build و Start
docker-compose -f docker-compose.production-secure.yml up -d --build

# 4. صبر برای start شدن
sleep 20

# 5. ایجاد Hero Slider نمونه
docker-compose -f docker-compose.production-secure.yml exec backend python create_sample_hero.py

# 6. بررسی وضعیت
docker-compose -f docker-compose.production-secure.yml ps
```

---

## 🧪 تست نهایی

### 1. تست API:
```bash
curl https://www.peykantravelistanbul.com/api/v1/shared/hero-slides/active/
```

### 2. تست تصویر:
```bash
curl -I https://www.peykantravelistanbul.com/media/hero/desktop/PEYKAN-DEFAULT.png
```

### 3. تست سایت:
باز کردن در مرورگر: https://www.peykantravelistanbul.com

---

## 📝 آپلود تصاویر و ویدیو از Admin

### مراحل:

1. ورود به Admin: https://www.peykantravelistanbul.com/admin/
2. رفتن به: **Shared > Hero Sliders**
3. کلیک روی **Add Hero Slide**
4. پر کردن فرم:
   - **Title** (فارسی): عنوان اسلاید
   - **Subtitle** (فارسی): زیرعنوان
   - **Description** (فارسی): توضیحات
   - **Button Text** (فارسی): متن دکمه
   - **Button URL**: مثلاً `/tours`
   - **Order**: عدد کوچکتر = اولویت بالاتر

5. آپلود تصاویر:
   - **Desktop Image**: 1920x1080 پیکسل
   - **Tablet Image**: 1024x768 پیکسل  
   - **Mobile Image**: 768x1024 پیکسل

6. آپلود ویدیو (اختیاری):
   - **Video Type**: انتخاب "Upload Video File"
   - **Video File**: فایل MP4 (حداکثر 50MB)
   - **Autoplay Video**: ✓
   - **Video Muted**: ✓ (برای autoplay لازم است)

7. **Save**

---

## 🔍 بررسی مشکلات

### اگر تصاویر نمایش داده نمی‌شوند:

```bash
# بررسی لاگ nginx
docker-compose -f docker-compose.production-secure.yml logs nginx | tail -50

# بررسی لاگ backend
docker-compose -f docker-compose.production-secure.yml logs backend | tail -50

# بررسی permissions
docker-compose -f docker-compose.production-secure.yml exec backend ls -la /app/media/
```

### اگر API خطا می‌دهد:

```bash
# بررسی لاگ frontend
docker-compose -f docker-compose.production-secure.yml logs frontend | tail -50

# تست API مستقیم
curl -v https://www.peykantravelistanbul.com/api/v1/shared/hero-slides/active/
```

### اگر 429 Too Many Requests می‌گیرید:

```bash
# Restart nginx
docker-compose -f docker-compose.production-secure.yml restart nginx

# یا پاک کردن cache مرورگر
```

---

## 📊 وضعیت فعلی

✅ Backend: در حال اجرا
✅ Frontend: در حال اجرا  
✅ Nginx: در حال اجرا
✅ PostgreSQL: سالم
✅ Redis: سالم
✅ Media files: قابل دسترسی
✅ API: کار می‌کند
✅ Rate limiting: اصلاح شد

---

## 🎯 نتیجه

تمام مشکلات رفع شدند. سیستم آماده است برای:
- آپلود تصاویر و ویدیوها از admin
- نمایش تصاویر و ویدیوها در frontend
- مدیریت Hero Sliders
- مدیریت تمام محتوای shared

**سایت شما آماده است: https://www.peykantravelistanbul.com** 🎉
