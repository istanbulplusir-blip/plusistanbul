# خلاصه کامل مشکلات و راه‌حل‌ها - پروژه Peykan Travel Istanbul

**تاریخ:** ۲۶ اکتبر ۲۰۲۵  
**وضعیت:** ✅ همه مشکلات حل شد

## مشکلات اصلی

### 1. ❌ CORS Headers تکراری
**علت:** هم Nginx و هم Django CORS headers اضافه می‌کردند  
**خطا:**
```
The 'Access-Control-Allow-Origin' header contains multiple values 
'https://www.peykantravelistanbul.com, https://peykantravelistanbul.com', 
but only one is allowed.
```

**راه حل:** ✅ CORS headers را از Nginx حذف کردیم و Django آنها را مدیریت می‌کند

### 2. ❌ CSP frame-ancestors 'none'
**علت:** CSP در middleware تنظیم شده بود که سایت نمی‌توانست در iframe قرار بگیرد  
**خطا:**
```
Refused to frame 'https://peykantravelistanbul.com/' because it violates 
the following Content Security Policy directive: "frame-ancestors 'none'".
```

**راه حل:** ✅ `frame-ancestors` را از `'none'` به `'self'` تغییر دادیم

### 3. ❌ Static/Media Files 404
**علت:** Symlinks به Docker volumes اشتباه اشاره می‌کردند  
**مشکل:**
- Backend از `plusistanbul_media_volume` استفاده می‌کرد
- اما symlink به `plusistanbul_media_volume_dev` اشاره می‌کرد

**راه حل:** ✅ Symlinks را به volumes صحیح تغییر دادیم

### 4. ❌ API Endpoint 404
**علت:** هیچ catalog با `is_featured=True` وجود نداشت  
**راه حل:** ✅ Catalog را به صورت دستی featured کردیم

## ساختار پروژه

### Docker Containers
```
peykan_frontend    - Next.js (port 3000)
peykan_backend     - Django (port 8000)
peykan_postgres    - PostgreSQL
peykan_redis       - Redis
peykan_nginx       - Nginx (NOT RUNNING - using system Nginx instead)
```

### Nginx Configuration
- **System Nginx** (خارج از Docker) در حال اجرا است
- Config: `/etc/nginx/sites-available/peykantravelistanbul.conf`
- Ports: 80, 443

### Docker Volumes
```
plusistanbul_static_volume  -> /var/www/peykantravelistanbul/static/
plusistanbul_media_volume   -> /var/www/peykantravelistanbul/media/
```

### پروژه‌های موازی
⚠️ **توجه:** دو پروژه جداگانه در حال اجرا هستند:
1. **peykantravelistanbul** (peykan) - port 8000
2. **istanbulplus** - port 8001

## تغییرات انجام شده

### 1. Nginx Configuration
**فایل:** `/etc/nginx/sites-available/peykantravelistanbul.conf`

**قبل:**
```nginx
location ~ ^/(api|admin)/ {
    # CORS headers (if needed) ❌
    add_header Access-Control-Allow-Origin "https://peykantravelistanbul.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
}
```

**بعد:**
```nginx
location ~ ^/(api|admin)/ {
    # CORS headers are handled by Django (django-cors-headers middleware)
    # DO NOT add CORS headers here to avoid duplicate headers ✅
    
    proxy_pass http://localhost:8000;
    # ... other settings
}
```

### 2. Next.js Middleware
**فایل:** `plusistanbul/frontend/middleware.ts`

**قبل:**
```typescript
frame-ancestors 'none';  ❌
```

**بعد:**
```typescript
frame-ancestors 'self' https://peykantravelistanbul.com https://www.peykantravelistanbul.com;  ✅
```

### 3. Docker Volumes Symlinks
**قبل:**
```bash
/var/www/peykantravelistanbul/media -> plusistanbul_media_volume_dev  ❌
/var/www/peykantravelistanbul/static -> plusistanbul_static_volume_dev  ❌
```

**بعد:**
```bash
/var/www/peykantravelistanbul/media -> plusistanbul_media_volume  ✅
/var/www/peykantravelistanbul/static -> plusistanbul_static_volume  ✅
```

**دستورات:**
```bash
sudo rm /var/www/peykantravelistanbul/media
sudo ln -s /var/lib/docker/volumes/plusistanbul_media_volume/_data /var/www/peykantravelistanbul/media

sudo rm /var/www/peykantravelistanbul/static
sudo ln -s /var/lib/docker/volumes/plusistanbul_static_volume/_data /var/www/peykantravelistanbul/static
```

### 4. Frontend Container Rebuild
```bash
cd plusistanbul
sudo docker-compose -f docker-compose.production-secure.yml build frontend
sudo docker restart peykan_frontend
```

### 5. Nginx Reload
```bash
sudo systemctl reload nginx
```

## تست‌های نهایی

### ✅ CORS Headers
```bash
curl -I "https://peykantravelistanbul.com/api/v1/shared/navigation-menu/active/" \
  -H "Origin: https://www.peykantravelistanbul.com" | grep -i "access-control"

# نتیجه: فقط یک header
access-control-allow-origin: https://www.peykantravelistanbul.com
access-control-allow-credentials: true
```

### ✅ CSP Headers
```bash
curl -I "https://peykantravelistanbul.com/" | grep -i "content-security-policy"

# نتیجه:
frame-src 'self' https://accounts.google.com https://peykantravelistanbul.com https://www.peykantravelistanbul.com;
frame-ancestors 'self' https://peykantravelistanbul.com https://www.peykantravelistanbul.com;
```

### ✅ Media Files
```bash
curl -I "https://peykantravelistanbul.com/media/defaults/meta/Logo-3D-highQ_-_Copy_ybHvHwj.png"

# نتیجه: HTTP/2 200
```

### ✅ Static Files
```bash
curl -I "https://peykantravelistanbul.com/static/rest_framework/css/bootstrap.min.css"

# نتیجه: HTTP/2 200
```

### ✅ API Endpoints
```bash
curl "https://peykantravelistanbul.com/api/v1/shared/catalogs/featured/"

# نتیجه: JSON با catalog data
```

## چرا این مشکلات به وجود آمد؟

### 1. Docker Volumes مختلف
پروژه چندین بار rebuild شده و volumes جدید ایجاد شده‌اند:
- `plusistanbul_media_volume_dev` (قدیمی)
- `plusistanbul_media_volume` (جدید)

اما symlinks به volumes قدیمی اشاره می‌کردند.

### 2. Nginx خارج از Docker
Nginx سیستم (خارج از Docker) در حال اجرا است، نه Nginx container. این باعث می‌شود که:
- تغییرات در Docker compose تأثیری نداشته باشند
- باید Nginx سیستم را reload کنیم
- Symlinks باید به مسیرهای صحیح Docker volumes اشاره کنند

### 3. چند پروژه موازی
دو پروژه جداگانه در حال اجرا هستند که می‌تواند باعث confusion شود:
- `peykantravelistanbul` (peykan)
- `istanbulplus`

### 4. Frontend Build Cache
بعد از تغییر middleware، باید frontend را rebuild کنیم تا تغییرات اعمال شوند.

## توصیه‌ها برای آینده

### 1. استفاده از یک Nginx
یا از Nginx سیستم استفاده کنید یا از Nginx container، نه هر دو.

**گزینه A: فقط Nginx سیستم (فعلی)**
```bash
# Nginx container را disable کنید
# در docker-compose.yml، nginx service را comment کنید
```

**گزینه B: فقط Nginx container**
```bash
# Nginx سیستم را stop کنید
sudo systemctl stop nginx
sudo systemctl disable nginx

# Nginx container را start کنید
docker-compose up -d nginx
```

### 2. Volume Management
یک naming convention ثابت برای volumes استفاده کنید:
```yaml
volumes:
  peykan_static:
    driver: local
  peykan_media:
    driver: local
```

### 3. Symlinks را در یک اسکریپت مدیریت کنید
```bash
#!/bin/bash
# setup-symlinks.sh

MEDIA_VOLUME="plusistanbul_media_volume"
STATIC_VOLUME="plusistanbul_static_volume"

sudo rm -f /var/www/peykantravelistanbul/media
sudo rm -f /var/www/peykantravelistanbul/static

sudo ln -s /var/lib/docker/volumes/${MEDIA_VOLUME}/_data /var/www/peykantravelistanbul/media
sudo ln -s /var/lib/docker/volumes/${STATIC_VOLUME}/_data /var/www/peykantravelistanbul/static

echo "✅ Symlinks created successfully"
```

### 4. Health Checks
اسکریپت تست برای بررسی سلامت سیستم:
```bash
#!/bin/bash
# health-check.sh

echo "🔍 Checking system health..."

# Check Docker containers
echo "📦 Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check Nginx
echo "🌐 Nginx status:"
systemctl status nginx --no-pager | head -3

# Check symlinks
echo "🔗 Symlinks:"
ls -la /var/www/peykantravelistanbul/ | grep -E "media|static"

# Test endpoints
echo "🧪 Testing endpoints:"
curl -s -o /dev/null -w "Static: %{http_code}\n" https://peykantravelistanbul.com/static/rest_framework/css/bootstrap.min.css
curl -s -o /dev/null -w "Media: %{http_code}\n" https://peykantravelistanbul.com/media/catalogs/Peykan_Travel_Tour-Guide-2025-1.pdf
curl -s -o /dev/null -w "API: %{http_code}\n" https://peykantravelistanbul.com/api/v1/shared/catalogs/featured/
```

### 5. Documentation
یک README.md در root پروژه با:
- ساختار پروژه
- دستورات deployment
- troubleshooting guide

## نتیجه‌گیری

✅ **همه مشکلات حل شدند:**
1. ✅ CORS headers دیگر تکراری نیستند
2. ✅ CSP به درستی تنظیم شده است
3. ✅ Static files به درستی serve می‌شوند
4. ✅ Media files به درستی serve می‌شوند
5. ✅ API endpoints کار می‌کنند
6. ✅ Multi-language support فعال است

**سایت حالا به طور کامل functional است! 🎉**

---

**توسعه‌دهنده:** Kiro AI  
**تاریخ:** ۲۶ اکتبر ۲۰۲۵  
**وضعیت:** تکمیل شده ✅
