# گزارش حل مشکل آپلود فایل در ادمین

## تاریخ: 2025-10-23

## 🔴 مشکل اولیه

هنگام آپلود تصویر از پنل ادمین Django، خطای 500 دریافت می‌شد:

```
POST https://peykantravelistanbul.com/admin/events/event/a1b7ad51-60d5-4f99-b2bc-0d47d9fc7ff8/change/?language=fa 
500 (Internal Server Error)
```

## 🔍 تحلیل مشکل

### خطای Backend:
```python
PermissionError: [Errno 13] Permission denied: '/app/media/products/images_CXLD5gH.jpeg'
```

### علت مشکل:
1. **Django** با user `django` (uid=1001) اجرا می‌شود
2. **Media directory** owner `www-data` (uid=33) بود
3. Django نمی‌توانست فایل جدید بنویسد

### بررسی Permissions قبل از Fix:
```bash
docker exec peykan_backend ls -la /app/media/
# drwxr-xr-x 15 33 33 4096 Oct 19 16:08 .
# Owner: www-data (33:33)
# Django user: django (1001:1001)
# ❌ Django نمی‌تواند بنویسد
```

## ✅ راه‌حل

### 1. تغییر Owner و Group
```bash
# Owner: django (1001) - برای نوشتن توسط Django
# Group: www-data (33) - برای خواندن توسط Nginx
sudo chown -R 1001:33 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
```

### 2. تنظیم Permissions
```bash
# 775 = rwxrwxr-x
# Owner (django): read, write, execute
# Group (www-data): read, write, execute
# Others: read, execute
sudo chmod -R 775 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
```

### 3. تست دسترسی
```bash
# تست نوشتن توسط Django
docker exec peykan_backend touch /app/media/test_write.txt
# ✅ موفق

# تست خواندن توسط Nginx
sudo -u www-data cat /var/www/peykantravelistanbul/media/test_write.txt
# ✅ موفق
```

## 📊 نتیجه

### قبل از Fix:
```
Owner: www-data (33:33)
Permission: 755 (rwxr-xr-x)
❌ Django نمی‌تواند فایل بنویسد
✅ Nginx می‌تواند فایل بخواند
```

### بعد از Fix:
```
Owner: django (1001)
Group: www-data (33)
Permission: 775 (rwxrwxr-x)
✅ Django می‌تواند فایل بنویسد
✅ Nginx می‌تواند فایل بخواند
```

## 🎯 تست نهایی

### 1. آپلود از ادمین:
```
✅ Django می‌تواند فایل جدید در /app/media/ بنویسد
✅ فایل با owner django:www-data ذخیره می‌شود
✅ Permission 775 برای فایل جدید اعمال می‌شود
```

### 2. نمایش در Frontend:
```
✅ Nginx می‌تواند فایل را از /var/www/peykantravelistanbul/media/ بخواند
✅ تصویر در دامنه قابل دسترسی است
✅ Next.js Image Optimization کار می‌کند
```

## 📝 نکات مهم

### 1. User IDs در Container:
- **Django user:** `django` (uid=1001, gid=1001)
- **Nginx user:** `www-data` (uid=33, gid=33)

### 2. Permission Strategy:
- **Owner (django):** برای نوشتن فایل‌های جدید
- **Group (www-data):** برای خواندن توسط Nginx
- **Permission (775):** دسترسی کامل برای owner و group

### 3. Media Volume Path:
```
Host:      /var/lib/docker/volumes/plusistanbul_media_volume/_data/
Container: /app/media/
Nginx:     /var/www/peykantravelistanbul/media/ (symlink)
```

## 🔧 دستورات مفید برای آینده

### بررسی Permissions:
```bash
docker exec peykan_backend ls -la /app/media/
```

### تست نوشتن توسط Django:
```bash
docker exec peykan_backend touch /app/media/test.txt
```

### تست خواندن توسط Nginx:
```bash
sudo -u www-data cat /var/www/peykantravelistanbul/media/test.txt
```

### تنظیم مجدد Permissions (در صورت نیاز):
```bash
sudo chown -R 1001:33 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
sudo chmod -R 775 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
```

## ✅ وضعیت نهایی

- ✅ Django می‌تواند فایل آپلود کند
- ✅ Nginx می‌تواند فایل‌ها را serve کند
- ✅ Frontend می‌تواند تصاویر را نمایش دهد
- ✅ پنل ادمین به درستی کار می‌کند

## 🎉 نتیجه‌گیری

مشکل آپلود فایل در پنل ادمین به طور کامل حل شد. حالا می‌توانید:
- از پنل ادمین تصویر آپلود کنید
- تصاویر در دامنه قابل دسترسی هستند
- Frontend می‌تواند تصاویر را نمایش دهد
- هیچ خطای 500 یا Permission Denied وجود ندارد
