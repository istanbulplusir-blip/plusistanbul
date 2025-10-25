# 📸 راهنمای آپلود تصاویر و ویدیو Hero

## ✅ وضعیت فعلی
- ✅ Backend: کار می‌کند
- ✅ Frontend: کار می‌کند
- ✅ API: کار می‌کند
- ✅ Media files: قابل دسترسی
- ✅ Admin Panel: آماده برای آپلود

---

## 🎯 مراحل آپلود تصاویر و ویدیو

### مرحله 1: ورود به Admin Panel

1. باز کردن: https://www.peykantravelistanbul.com/admin/
2. وارد شدن با username و password admin

### مرحله 2: رفتن به Hero Sliders

1. در منوی سمت چپ، روی **Shared** کلیک کنید
2. روی **Hero Sliders** کلیک کنید
3. لیست Hero Sliders فعلی را می‌بینید

### مرحله 3: ایجاد Hero Slider جدید

1. روی دکمه **Add Hero Slide** (بالا سمت راست) کلیک کنید
2. فرم باز می‌شود

### مرحله 4: پر کردن اطلاعات

#### بخش Basic Information:
- **Order**: عدد ترتیب نمایش (1, 2, 3, ...) - عدد کوچکتر اول نمایش داده می‌شود
- **Is Active**: ✓ (تیک بزنید)
- **Display Duration**: 5000 (5 ثانیه)

#### بخش Content (محتوا):
برای هر زبان (فارسی، انگلیسی، ترکی):

**زبان فارسی:**
- **Title**: عنوان اصلی (مثال: "به استانبول خوش آمدید")
- **Subtitle**: زیرعنوان (مثال: "بهترین تورهای استانبول")
- **Description**: توضیحات کامل
- **Button Text**: متن دکمه (مثال: "مشاهده تورها")

**Button URL**: `/tours` یا هر لینک دیگر
**Button Type**: Primary (آبی) یا Secondary (خاکستری)

#### بخش Images (تصاویر):
**مهم**: حتماً هر سه تصویر را آپلود کنید:

1. **Desktop Image**: 
   - سایز توصیه شده: 1920x1080 پیکسل
   - فرمت: JPG یا PNG
   - حداکثر حجم: 10MB

2. **Tablet Image**:
   - سایز توصیه شده: 1024x768 پیکسل
   - فرمت: JPG یا PNG
   - حداکثر حجم: 10MB

3. **Mobile Image**:
   - سایز توصیه شده: 768x1024 پیکسل
   - فرمت: JPG یا PNG
   - حداکثر حجم: 10MB

#### بخش Video Settings (اختیاری):

اگر می‌خواهید ویدیو داشته باشید:

1. **Video Type**: انتخاب کنید:
   - **No Video**: بدون ویدیو (فقط تصویر)
   - **Upload Video File**: آپلود فایل ویدیو
   - **External Video URL**: لینک ویدیو (YouTube, Vimeo)

2. اگر "Upload Video File" انتخاب کردید:
   - **Video File**: فایل MP4 (حداکثر 50MB)
   - **Video Thumbnail**: تصویر پیش‌نمایش (اختیاری)

3. اگر "External Video URL" انتخاب کردید:
   - **Video URL**: لینک کامل ویدیو

#### بخش Video Controls:

- **Autoplay Video**: ✓ (پخش خودکار)
- **Video Muted**: ✓ (بی‌صدا - برای autoplay لازم است)
- **Show Video Controls**: □ (نمایش کنترل‌ها)
- **Loop Video**: ✓ (تکرار)

#### بخش Targeting:
- **Show for Authenticated**: ✓ (نمایش برای کاربران لاگین شده)
- **Show for Anonymous**: ✓ (نمایش برای مهمان‌ها)

#### بخش Schedule (اختیاری):
- **Start Date**: تاریخ شروع نمایش (خالی = همیشه)
- **End Date**: تاریخ پایان نمایش (خالی = همیشه)

### مرحله 5: ذخیره

روی دکمه **Save** کلیک کنید.

---

## 🔍 بررسی نتیجه

### 1. بررسی در Admin:
- به لیست Hero Sliders برگردید
- باید Hero Slider جدید را ببینید
- روی آن کلیک کنید و تصاویر را ببینید

### 2. بررسی API:
```bash
curl https://www.peykantravelistanbul.com/api/v1/shared/hero-slides/active/
```

باید JSON با URL های کامل ببینید:
```json
{
  "desktop_image_url": "https://www.peykantravelistanbul.com/media/hero/desktop/...",
  "video_file_url": "https://www.peykantravelistanbul.com/media/hero/videos/..."
}
```

### 3. بررسی در سایت:
- باز کردن: https://www.peykantravelistanbul.com
- باید تصاویر Hero را ببینید
- اگر ویدیو آپلود کردید، باید پخش شود

### 4. بررسی Console مرورگر:
- F12 > Console
- نباید خطای 404 یا 429 ببینید
- نباید خطای "getHomeTours is not a function" ببینید

---

## ⚠️ نکات مهم

### تصاویر:
- ✅ حتماً هر سه سایز (Desktop, Tablet, Mobile) را آپلود کنید
- ✅ از تصاویر با کیفیت بالا استفاده کنید
- ✅ سایز فایل را کم نگه دارید (زیر 2MB توصیه می‌شود)
- ✅ از فرمت WebP برای کیفیت بهتر و حجم کمتر استفاده کنید

### ویدیوها:
- ✅ فقط فرمت MP4 استفاده کنید (سازگاری بیشتر)
- ✅ حجم را زیر 20MB نگه دارید
- ✅ برای autoplay، حتماً Muted را فعال کنید
- ⚠️ ویدیوهای بزرگ سرعت سایت را کم می‌کنند

### ترتیب نمایش:
- عدد **Order** کوچکتر = اولویت بالاتر
- مثال: Order=1 قبل از Order=2 نمایش داده می‌شود

---

## 🐛 مشکلات احتمالی

### مشکل: تصاویر در سایت نمایش داده نمی‌شوند

**راه‌حل 1**: پاک کردن cache مرورگر
- Ctrl+Shift+Delete
- یا باز کردن در حالت Incognito

**راه‌حل 2**: بررسی لاگ‌ها
```bash
docker-compose -f docker-compose.production-secure.yml logs nginx | grep media
```

**راه‌حل 3**: Restart nginx
```bash
docker-compose -f docker-compose.production-secure.yml restart nginx
```

### مشکل: ویدیو پخش نمی‌شود

**راه‌حل**:
- مطمئن شوید فرمت MP4 است
- مطمئن شوید Video Muted فعال است
- مطمئن شوید حجم زیر 50MB است

### مشکل: خطای 429 Too Many Requests

**راه‌حل**:
```bash
# Restart nginx
docker-compose -f docker-compose.production-secure.yml restart nginx

# یا صبر کنید 1 دقیقه
```

---

## 📞 پشتیبانی

اگر مشکلی پیش آمد:

1. لاگ‌ها را بررسی کنید:
```bash
docker-compose -f docker-compose.production-secure.yml logs -f
```

2. وضعیت کانتینرها را بررسی کنید:
```bash
docker-compose -f docker-compose.production-secure.yml ps
```

3. Restart کامل:
```bash
docker-compose -f docker-compose.production-secure.yml restart
```

---

**موفق باشید! 🚀**
