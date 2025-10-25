# راهنمای عیب‌یابی تصاویر

## تاریخ: 2025-10-23

## ✅ تغییرات اعمال شده

### 1. Custom Image Loader بهبود یافته
**فایل:** `plusistanbul/frontend/lib/imageLoader.js`

```javascript
export default function imageLoader({ src, width, quality }) {
    // 1. Relative paths from /media/
    if (src.startsWith('/media/')) {
        return src;
    }

    // 2. Full URLs from our domain with /media/
    if (src.includes('/media/')) {
        try {
            const url = new URL(src);
            if (url.hostname === 'peykantravelistanbul.com' || 
                url.hostname === 'www.peykantravelistanbul.com' ||
                url.hostname === 'localhost') {
                return url.pathname; // Extract path only
            }
        } catch (e) {
            // URL parsing failed
        }
    }

    // 3. External URLs
    if (src.startsWith('http://') || src.startsWith('https://')) {
        return src;
    }

    // 4. Other images (use Next.js optimization)
    return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality || 75}`;
}
```

### قابلیت‌های Image Loader:
- ✅ `/media/products/image.jpg` → `/media/products/image.jpg`
- ✅ `https://peykantravelistanbul.com/media/products/image.jpg` → `/media/products/image.jpg`
- ✅ `https://www.peykantravelistanbul.com/media/products/image.jpg` → `/media/products/image.jpg`
- ✅ `https://external.com/image.jpg` → `https://external.com/image.jpg`
- ✅ `/images/local.jpg` → `/_next/image?url=%2Fimages%2Flocal.jpg&w=1920&q=85`

## 🔍 چگونه صفحات را چک کنیم؟

### 1. بررسی Console در Browser

**مراحل:**
1. صفحه را در Chrome/Firefox باز کنید
2. F12 را بزنید (Developer Tools)
3. به تب Console بروید
4. به دنبال خطاهای زیر بگردید:

```
❌ خطاهای رایج:
- Image failed to load: ...
- GET ... 404 (Not Found)
- GET ... 400 (Bad Request)
```

### 2. بررسی Network Tab

**مراحل:**
1. F12 → Network Tab
2. Filter: Img
3. صفحه را Refresh کنید
4. تصاویر قرمز (404/400) را پیدا کنید

**چک کنید:**
- ✅ Status Code: 200 (موفق)
- ❌ Status Code: 404 (فایل وجود ندارد)
- ❌ Status Code: 400 (درخواست اشتباه)

### 3. بررسی URL تصاویر

**URL های صحیح:**
```
✅ https://peykantravelistanbul.com/media/products/image.jpg
✅ https://www.peykantravelistanbul.com/media/products/image.jpg
✅ /media/products/image.jpg
```

**URL های اشتباه:**
```
❌ https:/www.peykantravelistanbul.com/media/... (یک / کم)
❌ https://peykantravelistanbul.com//media/... (دو / اضافی)
❌ http://peykantravelistanbul.com/media/... (http به جای https)
```

## 🧪 تست صفحات مختلف

### صفحات اصلی برای تست:

#### 1. صفحه اصلی
```
URL: https://peykantravelistanbul.com/
تصاویر: Hero images, Featured tours, Events
```

#### 2. لیست تورها
```
URL: https://peykantravelistanbul.com/fa/tours/
تصاویر: Tour cards, Tour thumbnails
```

#### 3. جزئیات تور
```
URL: https://peykantravelistanbul.com/fa/tours/istanbul-bosphorus-cruise/
تصاویر: Tour main image, Gallery images
```

#### 4. لیست Events
```
URL: https://peykantravelistanbul.com/fa/events/
تصاویر: Event cards, Event thumbnails
```

#### 5. صفحه Transfers
```
URL: https://peykantravelistanbul.com/fa/transfers/
تصاویر: Transfer vehicle images
```

#### 6. صفحه رزرو
```
URL: https://peykantravelistanbul.com/fa/booking/
تصاویر: Product images در سبد خرید
```

## 🔧 دستورات تست

### 1. تست تصویر مستقیم:
```bash
curl -I https://peykantravelistanbul.com/media/products/IMAGE_NAME.jpg -k
# باید 200 برگرداند
```

### 2. تست API:
```bash
curl -s https://peykantravelistanbul.com/api/v1/tours/TOUR_SLUG/ -k | grep image_url
# بررسی کنید URL صحیح است
```

### 3. بررسی Frontend Logs:
```bash
docker logs peykan_frontend --tail 100 | grep -i "error\|failed"
```

### 4. بررسی Backend Logs:
```bash
docker logs peykan_backend --tail 100 | grep -i "error\|media"
```

## ⚠️ مشکلات رایج و راه‌حل

### مشکل 1: تصویر 404
**علت:** فایل در media directory وجود ندارد

**راه‌حل:**
```bash
# بررسی وجود فایل
docker exec peykan_backend ls -la /app/media/products/

# یا در host
sudo ls -la /var/lib/docker/volumes/plusistanbul_media_volume/_data/products/
```

### مشکل 2: تصویر 403
**علت:** مشکل permission

**راه‌حل:**
```bash
# تنظیم permissions
sudo chown -R 1001:33 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
sudo chmod -R 775 /var/lib/docker/volumes/plusistanbul_media_volume/_data/
```

### مشکل 3: URL اشتباه (https:/www)
**علت:** مشکل در تولید URL در Backend یا Frontend

**راه‌حل:**
- بررسی کنید API چه URL برمی‌گرداند
- بررسی کنید Frontend چطور URL را استفاده می‌کند
- imageLoader ما این مشکل را حل می‌کند

### مشکل 4: تصویر در بعضی صفحات کار نمی‌کند
**علت:** Component های مختلف ممکن است URL را متفاوت استفاده کنند

**راه‌حل:**
1. Console را باز کنید
2. خطا را پیدا کنید
3. URL اشتباه را شناسایی کنید
4. Component مربوطه را پیدا کنید و اصلاح کنید

## 📊 چک‌لیست تست کامل

### Backend:
- [ ] فایل در `/app/media/` وجود دارد
- [ ] Permissions صحیح است (775, owner: django:www-data)
- [ ] API URL صحیح برمی‌گرداند
- [ ] Django MEDIA_URL = '/media/'

### Frontend:
- [ ] Media volume mount شده است
- [ ] imageLoader.js وجود دارد
- [ ] next.config.js loader را تنظیم کرده
- [ ] Container بدون خطا start می‌شود

### Nginx:
- [ ] Symlink به media volume درست است
- [ ] www-data می‌تواند فایل‌ها را بخواند
- [ ] `/media/` location در config وجود دارد

### Browser:
- [ ] تصاویر در صفحه اصلی نمایش داده می‌شوند
- [ ] تصاویر در لیست تورها نمایش داده می‌شوند
- [ ] تصاویر در جزئیات تور نمایش داده می‌شوند
- [ ] تصاویر در Events نمایش داده می‌شوند
- [ ] تصاویر در Transfers نمایش داده می‌شوند
- [ ] هیچ خطای 404/400 در Console نیست

## 🎯 اگر هنوز مشکل دارید

### گام 1: شناسایی صفحه مشکل‌دار
```
کدام صفحه؟ _________________
URL کامل: _________________
```

### گام 2: شناسایی تصویر مشکل‌دار
```
نام فایل: _________________
URL در Console: _________________
Status Code: _________________
```

### گام 3: تست مستقیم
```bash
# تست فایل
curl -I https://peykantravelistanbul.com/media/products/FILE_NAME.jpg -k

# تست در container
docker exec peykan_frontend ls -la /app/public/media/products/FILE_NAME.jpg
```

### گام 4: بررسی Logs
```bash
# Frontend
docker logs peykan_frontend --tail 50

# Backend
docker logs peykan_backend --tail 50
```

## 📝 گزارش مشکل

اگر مشکل ادامه دارد، این اطلاعات را جمع‌آوری کنید:

1. **URL صفحه مشکل‌دار:**
2. **خطای Console (screenshot):**
3. **URL تصویر اشتباه:**
4. **نتیجه `curl -I` برای تصویر:**
5. **Frontend logs:**
6. **Backend logs:**

## ✅ نتیجه‌گیری

با تغییرات اعمال شده:
- ✅ imageLoader می‌تواند URL های کامل را handle کند
- ✅ تصاویر `/media/` بدون optimization serve می‌شوند
- ✅ مشکلات URL اشتباه (مثل `https:/www`) حل می‌شوند

اگر هنوز مشکل دارید، مراحل بالا را دنبال کنید و مشکل را شناسایی کنید.
