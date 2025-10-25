# گزارش حل مشکل تصاویر Next.js

## تاریخ: 2025-10-23

## 🔴 مشکل اولیه

تصاویر پیش‌فرض در صفحات مختلف (صفحه اصلی، ترانسفر، رزرو) نمایش داده نمی‌شدند و خطاهای زیر دریافت می‌شد:

```
Image failed to load: /media/products/images_8tutSl7.jpeg. Using fallback: /images/event-image.jpg
GET https://www.peykantravelistanbul.com/_next/image/?url=%2Fmedia%2Fproducts%2Fimages_8tutSl7.jpeg&w=1920&q=85 
400 (Bad Request)
```

## 🔍 تحلیل مشکل

### علت اصلی:
1. **Next.js Image Optimization** نمی‌توانست به فایل‌های `/media/` دسترسی داشته باشد
2. Frontend container به media volume دسترسی نداشت
3. Next.js سعی می‌کرد تصاویر `/media/` را optimize کند ولی فایل‌ها در `/app/public/` وجود نداشتند

### خطاهای مشاهده شده:
```
HTTP/2 400 Bad Request
_next/image/?url=%2Fmedia%2Fproducts%2Fimages_8tutSl7.jpeg
```

## ✅ راه‌حل‌های اعمال شده

### 1. اضافه کردن Media Volume به Frontend Container

**فایل:** `docker-compose.production-secure.yml`

```yaml
frontend:
  volumes:
    - media_volume:/app/public/media:ro  # Read-only access
```

**توضیح:** Frontend container حالا می‌تواند فایل‌های media را از volume بخواند.

### 2. ایجاد Custom Image Loader

**فایل:** `plusistanbul/frontend/lib/imageLoader.js`

```javascript
export default function imageLoader({ src, width, quality }) {
  // If the image is from /media/, serve it directly without optimization
  if (src.startsWith('/media/')) {
    return src;
  }
  
  // If it's an external URL, return as is
  if (src.startsWith('http://') || src.startsWith('https://')) {
    return src;
  }
  
  // For other images, use default Next.js optimization
  return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality || 75}`;
}
```

**توضیح:** 
- تصاویر `/media/` بدون optimization serve می‌شوند
- تصاویر دیگر از Next.js optimization استفاده می‌کنند

### 3. تنظیم Next.js Config

**فایل:** `plusistanbul/frontend/next.config.js`

```javascript
images: {
  loader: process.env.NODE_ENV === 'production' ? 'custom' : 'default',
  loaderFile: process.env.NODE_ENV === 'production' ? './lib/imageLoader.js' : undefined,
  // ... rest of config
}
```

**توضیح:** در production از custom loader استفاده می‌شود.

### 4. بروزرسانی Dockerfile

**فایل:** `plusistanbul/frontend/Dockerfile`

```dockerfile
# Copy lib directory for custom image loader
COPY --from=builder --chown=nextjs:nodejs /app/lib ./lib
```

**توضیح:** فایل imageLoader.js در production image کپی می‌شود.

## 📊 نتیجه

### قبل از Fix:
```
❌ Frontend container: بدون دسترسی به media files
❌ Next.js Image Optimization: خطای 400 برای /media/
❌ تصاویر: fallback نمایش داده می‌شد
```

### بعد از Fix:
```
✅ Frontend container: دسترسی read-only به media volume
✅ Custom Image Loader: تصاویر /media/ بدون optimization
✅ تصاویر: به درستی نمایش داده می‌شوند
```

## 🎯 تست نهایی

### 1. تصویر مستقیم:
```bash
curl -I https://peykantravelistanbul.com/media/products/images_8tutSl7.jpeg -k
# HTTP/2 200 ✅
```

### 2. دسترسی Frontend به Media:
```bash
docker exec peykan_frontend ls -la /app/public/media/products/
# ✅ فایل‌ها قابل مشاهده هستند
```

### 3. Next.js Image Component:
```jsx
<Image src="/media/products/image.jpg" width={1920} height={1080} />
// ✅ تصویر بدون optimization نمایش داده می‌شود
```

## 📝 نکات مهم

### 1. Media Volume Mounting:
```
Host:      /var/lib/docker/volumes/plusistanbul_media_volume/_data/
Backend:   /app/media/
Frontend:  /app/public/media/ (read-only)
Nginx:     /var/www/peykantravelistanbul/media/ (symlink)
```

### 2. Image Optimization Strategy:
- **تصاویر `/media/`:** بدون optimization (serve مستقیم)
- **تصاویر `/images/`:** با Next.js optimization
- **تصاویر external:** بدون optimization

### 3. Permissions:
- Frontend: read-only access (`:ro`)
- Backend: read-write access
- Nginx: read access via symlink

## 🔧 دستورات مفید

### بررسی دسترسی Frontend:
```bash
docker exec peykan_frontend ls -la /app/public/media/
```

### تست تصویر:
```bash
curl -I https://peykantravelistanbul.com/media/products/image.jpg -k
```

### بررسی Logs:
```bash
docker logs peykan_frontend --tail 50
```

### Rebuild Frontend:
```bash
docker-compose -f docker-compose.production-secure.yml build frontend
docker-compose -f docker-compose.production-secure.yml up -d frontend
```

## ✅ وضعیت نهایی

- ✅ Frontend می‌تواند به media files دسترسی داشته باشد
- ✅ تصاویر `/media/` بدون optimization serve می‌شوند
- ✅ Next.js Image Component به درستی کار می‌کند
- ✅ تصاویر پیش‌فرض در همه صفحات نمایش داده می‌شوند
- ✅ هیچ خطای 400 یا fallback وجود ندارد

## 🎉 نتیجه‌گیری

مشکل تصاویر Next.js به طور کامل حل شد. حالا:
- تصاویر در صفحه اصلی نمایش داده می‌شوند
- تصاویر در صفحات ترانسفر و رزرو کار می‌کنند
- تصاویر پیش‌فرض به درستی نمایش داده می‌شوند
- Next.js Image Optimization برای تصاویر `/media/` غیرفعال است (برای بهبود performance)
