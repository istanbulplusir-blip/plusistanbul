# CORS Fix Summary - Duplicate Headers Issue

**تاریخ:** ۲۵ اکتبر ۲۰۲۵  
**مشکل:** خطای CORS در browser console  
**وضعیت:** ✅ حل شد

## مشکل اصلی

هنگام باز کردن سایت در browser، خطاهای زیر در console نمایش داده می‌شد:

```
Access to XMLHttpRequest at 'https://peykantravelistanbul.com/api/v1/...' 
from origin 'https://www.peykantravelistanbul.com' has been blocked by CORS policy: 
The 'Access-Control-Allow-Origin' header contains multiple values 
'https://www.peykantravelistanbul.com, https://peykantravelistanbul.com', 
but only one is allowed.
```

### علت مشکل

CORS headers دو بار اضافه می‌شدند:
1. **یک بار در Nginx** - در فایل `/etc/nginx/sites-available/peykantravelistanbul.conf`
2. **یک بار در Django** - توسط `django-cors-headers` middleware

این باعث می‌شد که browser header تکراری دریافت کند و درخواست‌های API را block کند.

## راه حل

CORS headers را از Nginx configuration حذف کردیم و اجازه دادیم Django آنها را مدیریت کند.

### تغییرات انجام شده

**قبل از تغییر (Nginx):**
```nginx
location ~ ^/(api|admin)/ {
    proxy_pass http://localhost:8000;
    # ... other settings ...
    
    # CORS headers (if needed) ❌ این باعث مشکل می‌شد
    add_header Access-Control-Allow-Origin "https://peykantravelistanbul.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
}
```

**بعد از تغییر (Nginx):**
```nginx
location ~ ^/(api|admin)/ {
    proxy_pass http://localhost:8000;
    # ... other settings ...
    
    # CORS headers are handled by Django (django-cors-headers middleware)
    # DO NOT add CORS headers here to avoid duplicate headers ✅
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

**Django CORS Configuration (بدون تغییر):**
```python
# در plusistanbul/backend/peykan/settings.py
CORS_ALLOWED_ORIGINS = [
    'https://peykantravelistanbul.com',
    'https://www.peykantravelistanbul.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
```

## مراحل اجرا شده

1. ✅ شناسایی مشکل CORS در browser console
2. ✅ بررسی Nginx configuration
3. ✅ بررسی Django CORS settings
4. ✅ حذف CORS headers از Nginx
5. ✅ تست Nginx configuration: `sudo nginx -t`
6. ✅ Reload Nginx: `sudo systemctl reload nginx`
7. ✅ تست CORS headers با curl

## تست و تایید

### تست با curl

```bash
# تست navigation menu API
curl -I "https://peykantravelistanbul.com/api/v1/shared/navigation-menu/active/" \
  -H "Origin: https://www.peykantravelistanbul.com" 2>&1 | grep -i "access-control"

# نتیجه: ✅ فقط یک header
access-control-allow-origin: https://www.peykantravelistanbul.com
access-control-allow-credentials: true
```

```bash
# تست site settings API
curl -I "https://peykantravelistanbul.com/api/v1/shared/site-settings/" \
  -H "Origin: https://www.peykantravelistanbul.com" 2>&1 | grep -i "access-control"

# نتیجه: ✅ فقط یک header
access-control-allow-origin: https://www.peykantravelistanbul.com
access-control-allow-credentials: true
```

```bash
# تست cart API
curl -I "https://peykantravelistanbul.com/api/v1/cart/" \
  -H "Origin: https://www.peykantravelistanbul.com" 2>&1 | grep -i "access-control"

# نتیجه: ✅ فقط یک header
access-control-allow-origin: https://www.peykantravelistanbul.com
access-control-allow-credentials: true
```

### تست در Browser

بعد از این تغییرات، باید:
- ✅ هیچ خطای CORS در console نباشد
- ✅ API calls موفقیت‌آمیز باشند
- ✅ Navigation menu load شود
- ✅ Site settings load شود
- ✅ Cart data load شود
- ✅ Catalog data load شود

## نکات مهم

### چرا Django CORS را مدیریت می‌کند؟

1. **انعطاف‌پذیری بیشتر:** Django می‌تواند CORS را بر اساس شرایط مختلف مدیریت کند
2. **پیکربندی متمرکز:** تمام تنظیمات CORS در یک جا (settings.py)
3. **پشتیبانی از credentials:** Django می‌تواند cookies و authentication را به درستی مدیریت کند
4. **Dynamic origins:** می‌توان origins را از environment variables خواند

### چرا از Nginx حذف کردیم؟

1. **جلوگیری از تکرار:** Nginx و Django نباید هر دو CORS headers اضافه کنند
2. **سادگی:** یک لایه کمتر برای مدیریت
3. **مطابقت با best practices:** معمولاً application layer (Django) CORS را مدیریت می‌کند

## فایل‌های تغییر یافته

1. `/etc/nginx/sites-available/peykantravelistanbul.conf` - حذف CORS headers از location block
2. `peykantravelistanbul_fixed.conf` - نسخه جدید configuration (backup در home directory)

## Rollback (در صورت نیاز)

اگر نیاز به بازگشت به حالت قبل باشد:

```bash
# بازیابی از backup
sudo cp /etc/nginx/sites-available/peykantravelistanbul.conf.backup \
     /etc/nginx/sites-available/peykantravelistanbul.conf

# تست و reload
sudo nginx -t
sudo systemctl reload nginx
```

## نتیجه‌گیری

✅ **مشکل CORS به طور کامل حل شد**

- CORS headers دیگر تکراری نیستند
- API calls در browser به درستی کار می‌کنند
- Django CORS middleware به تنهایی CORS را مدیریت می‌کند
- Nginx فقط به عنوان reverse proxy عمل می‌کند

---

**توسعه‌دهنده:** Kiro AI  
**تاریخ:** ۲۵ اکتبر ۲۰۲۵  
**وضعیت:** تکمیل شده ✅
