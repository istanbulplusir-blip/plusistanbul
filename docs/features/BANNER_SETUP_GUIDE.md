# 🎨 راهنمای کامل تنظیم بنرها

## 🔍 مشکل شناسایی شده

بنرها در فرانت‌اند نمایش داده نمی‌شدند به دلایل زیر:

### ✅ مشکلات اصلاح شده:

1. **نام فیلد اشتباه در TypeScript**
   - ❌ قبلی: `image_url`
   - ✅ اصلاح شده: `image_url_field`

2. **کامپوننت Banner**
   - ✅ اصلاح شد تا از `image_url_field` استفاده کند
   - ✅ Fallback به `image` اضافه شد

3. **تصاویر بنرها**
   - ✅ فقط بنر اول تصویر داشت
   - ⚠️ بنرهای دیگر نیاز به آپلود تصویر دارند

---

## 📋 وضعیت فعلی بنرها

### بنر 1: Homepage Top ✅
- **نوع:** `homepage_top`
- **موقعیت:** `top`
- **تصویر دسکتاپ:** ✅ دارد (`banners/Banka_Kart_combo.jpg`)
- **تصویر موبایل:** ✅ دارد (`banners/mobile/Banka_Kart_combo.jpg`)
- **وضعیت:** آماده نمایش

### بنر 2: Homepage Bottom ❌
- **نوع:** `homepage_bottom`
- **موقعیت:** `bottom`
- **تصویر دسکتاپ:** ❌ ندارد
- **تصویر موبایل:** ❌ ندارد
- **وضعیت:** نیاز به آپلود تصویر

### بنر 3: Sidebar ❌
- **نوع:** `sidebar`
- **موقعیت:** `sidebar`
- **تصویر دسکتاپ:** ❌ ندارد
- **تصویر موبایل:** ❌ ندارد
- **وضعیت:** نیاز به آپلود تصویر

---

## 🚀 راهنمای آپلود تصاویر بنر

### روش 1: از طریق Django Admin (توصیه می‌شود)

#### مرحله 1: ورود به Admin
```
http://localhost:8000/admin/shared/banner/
```

#### مرحله 2: انتخاب بنر
- روی بنر مورد نظر کلیک کنید (مثلاً Homepage Bottom)

#### مرحله 3: آپلود تصاویر
1. **Desktop Image:**
   - کلیک روی "Choose File" در قسمت "Banner Image"
   - تصویر با سایز توصیه شده: **1200x400 پیکسل**
   - فرمت: JPG, PNG, WebP
   - حجم: حداکثر 2MB

2. **Mobile Image (اختیاری):**
   - کلیک روی "Choose File" در قسمت "Mobile Banner Image"
   - تصویر با سایز توصیه شده: **768x400 پیکسل**
   - فرمت: JPG, PNG, WebP
   - حجم: حداکثر 1MB

#### مرحله 4: ذخیره
- کلیک روی "Save" یا "Save and continue editing"

---

### روش 2: از طریق API

```bash
# آپلود تصویر برای بنر
curl -X PATCH http://localhost:8000/api/shared/banners/{banner_id}/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@/path/to/desktop-image.jpg" \
  -F "mobile_image=@/path/to/mobile-image.jpg"
```

---

## 📐 سایزهای توصیه شده تصاویر

### بنرهای Homepage (Top & Bottom)
- **Desktop:** 1200x400 پیکسل (نسبت 3:1)
- **Mobile:** 768x400 پیکسل
- **فرمت:** JPG (بهینه شده)
- **کیفیت:** 80-85%

### بنر Sidebar
- **Desktop:** 400x600 پیکسل (نسبت 2:3)
- **Mobile:** 768x400 پیکسل
- **فرمت:** JPG (بهینه شده)
- **کیفیت:** 80-85%

---

## 🎨 نکات طراحی بنر

### 1. محتوای بصری
- ✅ استفاده از تصاویر با کیفیت بالا
- ✅ رنگ‌های متناسب با برند
- ✅ متن خوانا با کنتراست مناسب
- ❌ اجتناب از تصاویر شلوغ

### 2. متن روی بنر
- ✅ عنوان کوتاه و جذاب (حداکثر 50 کاراکتر)
- ✅ فونت واضح و خوانا
- ✅ سایز مناسب برای موبایل
- ❌ متن طولانی و پیچیده

### 3. دکمه CTA
- ✅ رنگ متمایز از پس‌زمینه
- ✅ متن واضح و عمل‌گرا
- ✅ سایز مناسب برای کلیک
- ❌ دکمه‌های کوچک یا نامشخص

---

## 🔧 تست و بررسی

### 1. بررسی در Admin
```bash
# مشاهده لیست بنرها
http://localhost:8000/admin/shared/banner/

# بررسی تصاویر آپلود شده
http://localhost:8000/media/banners/
```

### 2. بررسی API
```bash
# دریافت لیست بنرها
curl http://localhost:8000/api/shared/banners/

# دریافت یک بنر خاص
curl http://localhost:8000/api/shared/banners/{banner_id}/
```

### 3. بررسی در Frontend
```bash
# صفحه اصلی
http://localhost:3000/

# بررسی Console برای خطاها
F12 > Console
```

---

## 🐛 عیب‌یابی

### مشکل: تصویر نمایش داده نمی‌شود

#### بررسی 1: فایل تصویر وجود دارد؟
```bash
cd backend
ls media/banners/
```

#### بررسی 2: مسیر تصویر در دیتابیس صحیح است؟
```bash
python manage.py shell
>>> from shared.models import Banner
>>> banner = Banner.objects.get(banner_type='homepage_bottom')
>>> print(banner.image)
>>> print(banner.mobile_image)
```

#### بررسی 3: API تصویر را برمی‌گرداند؟
```bash
curl http://localhost:8000/api/shared/banners/ | jq '.[] | {type: .banner_type, image: .image_url_field}'
```

#### بررسی 4: مجوزهای فایل
```bash
# در Windows
icacls media\banners\

# در Linux/Mac
ls -la media/banners/
```

---

## 📊 بررسی عملکرد بنرها

### آمار بنرها در Admin
```
http://localhost:8000/admin/shared/banner/
```

هر بنر شامل:
- **View Count:** تعداد نمایش
- **Click Count:** تعداد کلیک
- **Click Rate:** نرخ کلیک (CTR)

### API آمار
```bash
# ثبت نمایش بنر
POST /api/shared/banners/{banner_id}/track-view/

# ثبت کلیک بنر
POST /api/shared/banners/{banner_id}/track-click/
```

---

## ✅ چک‌لیست نهایی

قبل از انتشار، مطمئن شوید:

- [ ] تمام بنرها تصویر دسکتاپ دارند
- [ ] تصاویر موبایل آپلود شده (یا از دسکتاپ استفاده می‌شود)
- [ ] عنوان و Alt Text برای SEO تنظیم شده
- [ ] لینک‌ها صحیح هستند
- [ ] بنرها در صفحات مناسب نمایش داده می‌شوند
- [ ] تصاویر بهینه شده و حجم مناسب دارند
- [ ] بنرها در موبایل و دسکتاپ تست شده‌اند
- [ ] آمارگیری فعال است

---

## 🎯 نتیجه

با اصلاحات انجام شده:

1. ✅ **مشکل نام فیلد** اصلاح شد
2. ✅ **کامپوننت Banner** به‌روز شد
3. ✅ **Type Definition** اصلاح شد
4. ⚠️ **تصاویر بنرها** نیاز به آپلود دارند

### اقدامات بعدی:

1. آپلود تصاویر برای بنرهای `homepage_bottom` و `sidebar`
2. تست نمایش بنرها در فرانت‌اند
3. بررسی responsive بودن در موبایل
4. تنظیم لینک‌ها و CTA ها

---

**تاریخ:** ۱۸ اکتبر ۲۰۲۵  
**وضعیت:** ✅ آماده برای آپلود تصاویر
