# گزارش حل مشکل آپلود ویدیو

## تاریخ: 2025-10-23

## 🔴 مشکل اولیه

هنگام آپلود ویدیو در پنل ادمین (Hero Slider)، خطای 413 دریافت می‌شد:

```
POST https://peykantravelistanbul.com/admin/shared/heroslider/.../change/?language=fa
413 (Content Too Large)
```

## 🔍 تحلیل مشکل

### علت:
محدودیت حجم فایل در Nginx و Django خیلی کم بود:
- **Nginx:** بدون تنظیم `client_max_body_size` (پیش‌فرض: 1MB)
- **Django:** `DATA_UPLOAD_MAX_MEMORY_SIZE = 10MB`

### نتیجه:
فایل‌های ویدیو که معمولاً بزرگ‌تر از 10MB هستند، رد می‌شدند.

## ✅ راه‌حل

### 1. افزایش محدودیت Nginx

**فایل:** `/etc/nginx/sites-available/peykantravelistanbul.conf`

```nginx
server {
    listen 443 ssl http2;
    server_name peykantravelistanbul.com www.peykantravelistanbul.com;
    
    # Allow large file uploads (videos)
    client_max_body_size 500M;
    
    # ... rest of config
}
```

**دستورات:**
```bash
sudo sed -i '/server_name peykantravelistanbul.com/a\    \n    # Allow large file uploads\n    client_max_body_size 500M;' /etc/nginx/sites-available/peykantravelistanbul.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 2. افزایش محدودیت Django

**فایل:** `plusistanbul/backend/peykan/settings_production.py`

```python
# File Upload Settings for Production
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB (for videos)
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB (for videos)
```

**قبل:**
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

**بعد:**
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
```

### 3. Restart Backend

```bash
docker-compose -f docker-compose.production-secure.yml restart backend
```

## 📊 نتیجه

### قبل از Fix:
```
❌ Nginx: محدودیت 1MB (پیش‌فرض)
❌ Django: محدودیت 10MB
❌ ویدیوها: رد می‌شدند با خطای 413
```

### بعد از Fix:
```
✅ Nginx: محدودیت 500MB
✅ Django: محدودیت 500MB
✅ ویدیوها: قابل آپلود تا 500MB
```

## 🎯 تست

### آپلود ویدیو در Hero Slider:
1. برید به: https://peykantravelistanbul.com/admin/shared/heroslider/
2. یک Hero Slider باز کنید
3. ویدیو آپلود کنید (تا 500MB)
4. ✅ باید بدون خطا ذخیره شود

### تست با curl:
```bash
# تست محدودیت Nginx
curl -I -X POST https://peykantravelistanbul.com/admin/ \
  -H "Content-Length: 524288000" -k
# باید 200 یا 302 برگرداند (نه 413)
```

## 📝 نکات مهم

### 1. محدودیت‌های تنظیم شده:
- **Nginx:** 500MB
- **Django:** 500MB
- **توصیه:** برای ویدیوهای بزرگ‌تر، این مقادیر را افزایش دهید

### 2. توصیه‌های بهینه‌سازی:
- ویدیوها را قبل از آپلود فشرده کنید
- از فرمت‌های بهینه مثل MP4 (H.264) استفاده کنید
- رزولوشن ویدیو را متناسب با نیاز تنظیم کنید

### 3. Timeout Settings:
اگر آپلود ویدیوهای بزرگ timeout می‌شود، این تنظیمات را هم اضافه کنید:

```nginx
# در Nginx config
proxy_connect_timeout 600;
proxy_send_timeout 600;
proxy_read_timeout 600;
send_timeout 600;
```

### 4. PHP-FPM (اگر استفاده می‌کنید):
```ini
upload_max_filesize = 500M
post_max_size = 500M
max_execution_time = 600
```

## 🔧 دستورات مفید

### بررسی محدودیت Nginx:
```bash
sudo nginx -T | grep client_max_body_size
```

### بررسی محدودیت Django:
```bash
docker exec peykan_backend python manage.py shell -c "from django.conf import settings; print('Max upload:', settings.DATA_UPLOAD_MAX_MEMORY_SIZE / 1024 / 1024, 'MB')"
```

### تست آپلود:
```bash
# ساخت فایل تست 100MB
dd if=/dev/zero of=test_video.mp4 bs=1M count=100

# آپلود با curl
curl -X POST https://peykantravelistanbul.com/admin/shared/heroslider/.../change/ \
  -F "video=@test_video.mp4" \
  -H "Cookie: sessionid=..." -k
```

## ✅ وضعیت نهایی

- ✅ Nginx: محدودیت 500MB تنظیم شد
- ✅ Django: محدودیت 500MB تنظیم شد
- ✅ Backend: Restart شد
- ✅ ویدیوها: قابل آپلود تا 500MB

## 🎉 نتیجه‌گیری

مشکل آپلود ویدیو حل شد. حالا می‌توانید:
- ویدیوهای تا 500MB آپلود کنید
- در Hero Slider ویدیو اضافه کنید
- بدون خطای 413 کار کنید

**توجه:** برای ویدیوهای بزرگ‌تر از 500MB، محدودیت‌ها را افزایش دهید.
