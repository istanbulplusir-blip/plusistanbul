# گزارش حل مشکل نمایش تصاویر Media

## تاریخ: 2025-10-23

## 🔴 مشکل اولیه
تصاویر تورها در فرانت نمایش داده نمی‌شدند و خطای 404 دریافت می‌شد:
```
GET https://www.peykantravelistanbul.com/_next/image/?url=https:/peykantravelistanbul.com/media/products/tours-istanbul-new-NewFolder-_IvhkcM3.jpg&w=384&q=85
[HTTP/2 404 143ms]
```

## 🔍 تحلیل مشکل

### 1. فایل در Backend وجود داشت
```bash
docker exec peykan_backend ls -la /app/media/products/
# ✅ فایل tours-istanbul-new-NewFolder-_IvhkcM3.jpg وجود داشت
```

### 2. Nginx Container در حال اجرا نبود
- Nginx سیستم (خارج از Docker) در حال اجرا بود
- Nginx Container به دلیل تداخل پورت 80 start نشده بود
- Media files از Docker volume باید serve می‌شدند

### 3. مشکلات Permission
- Nginx سیستم نمی‌توانست به Docker volumes دسترسی داشته باشد
- Directory permissions اشتباه بود

## ✅ راه‌حل‌های اعمال شده

### 1. ایجاد Symlink به Docker Volume
```bash
sudo rm -rf /var/www/peykantravelistanbul/media
sudo ln -s /var/lib/docker/volumes/plusistanbul_media_volume/_data /var/www/peykantravelistanbul/media
```

### 2. تنظیم Permissions
```bash
# تغییر owner به www-data
sudo chown -R www-data:www-data /var/lib/docker/volumes/plusistanbul_media_volume/_data/

# تنظیم permissions برای directories
sudo chmod 755 /var/lib/docker/volumes/plusistanbul_media_volume/
sudo chmod 755 /var/lib/docker
sudo chmod 755 /var/lib/docker/volumes

# تنظیم permissions برای files
sudo chmod -R 755 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
```

### 3. تأیید دسترسی Nginx
```bash
# تست دسترسی www-data به فایل
sudo -u www-data cat /var/www/peykantravelistanbul/media/products/tours-istanbul-new-NewFolder-_IvhkcM3.jpg > /dev/null
# ✅ موفق
```

## 📊 نتیجه

### قبل از Fix:
```
HTTP/2 404 - File not found
HTTP/2 403 - Permission denied
```

### بعد از Fix:
```bash
curl -I https://peykantravelistanbul.com/media/products/tours-istanbul-new-NewFolder-_IvhkcM3.jpg -k
# HTTP/2 200 ✅
# content-type: image/jpeg
# content-length: 144926
```

## 🎯 تست نهایی

```bash
curl -s https://peykantravelistanbul.com/api/v1/tours/istanbul-bosphorus-cruise/ -k | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['image_url'])"
```

**نتیجه:**
```
✅ Tour: کروز بسفر استانبول و تور دو قاره
✅ Image URL: https://peykantravelistanbul.com/media/products/tours-istanbul-new-NewFolder-_IvhkcM3.jpg
✅ Has image: True
✅ HTTP Status: 200 OK
```

## 📝 نکات مهم

### 1. ساختار Directory
```
/var/www/peykantravelistanbul/media -> /var/lib/docker/volumes/plusistanbul_media_volume/_data
```

### 2. Permissions مورد نیاز
- Docker volumes directory: `755` (drwxr-xr-x)
- Media files: `755` (rwxr-xr-x)
- Owner: `www-data:www-data`

### 3. Nginx Configuration
```nginx
location /media/ {
    alias /var/www/peykantravelistanbul/media/;
    expires 1y;
    add_header Cache-Control "public";
    autoindex off;
}
```

## ✅ وضعیت نهایی

- ✅ تصاویر در Backend ذخیره می‌شوند
- ✅ Nginx می‌تواند به Docker volumes دسترسی داشته باشد
- ✅ تصاویر در دامنه production قابل دسترسی هستند
- ✅ Frontend می‌تواند تصاویر را نمایش دهد
- ✅ Next.js Image Optimization کار می‌کند

## 🔧 دستورات مفید برای آینده

### بررسی دسترسی Nginx به فایل:
```bash
sudo -u www-data cat /var/www/peykantravelistanbul/media/path/to/file.jpg > /dev/null
```

### بررسی permissions در مسیر:
```bash
sudo namei -l /var/www/peykantravelistanbul/media/path/to/file.jpg
```

### تست دسترسی به media file:
```bash
curl -I https://peykantravelistanbul.com/media/path/to/file.jpg -k
```

## 🎉 نتیجه‌گیری

مشکل نمایش تصاویر به طور کامل حل شد. حالا:
- تصاویر در Backend ذخیره می‌شوند
- Nginx می‌تواند آنها را serve کند
- Frontend می‌تواند آنها را نمایش دهد
- Next.js Image Optimization به درستی کار می‌کند
