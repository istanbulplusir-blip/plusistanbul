# 🎨 Hero Slider System

> سیستم اسلایدر صفحه اصلی با پشتیبانی ویدیو و تصاویر responsive

---

## 📚 مستندات موجود

### راهنماها
- **[HERO_SLIDER_GUIDE_FA.md](./HERO_SLIDER_GUIDE_FA.md)** - راهنمای کامل فارسی
- **[HERO_SLIDER_DEFAULT_SETTINGS_GUIDE.md](./HERO_SLIDER_DEFAULT_SETTINGS_GUIDE.md)** - تنظیمات پیش‌فرض

### تحلیل‌ها
- **[HERO_SLIDER_ANALYSIS.md](./HERO_SLIDER_ANALYSIS.md)** - تحلیل کامل سیستم
- **[HERO_SLIDER_COMPLETE_SUMMARY.md](./HERO_SLIDER_COMPLETE_SUMMARY.md)** - خلاصه کامل
- **[HERO_SLIDER_FINAL_REPORT.md](./HERO_SLIDER_FINAL_REPORT.md)** - گزارش نهایی

### پیاده‌سازی
- **[HERO_SLIDER_IMPLEMENTATION_SUMMARY.md](./HERO_SLIDER_IMPLEMENTATION_SUMMARY.md)** - خلاصه پیاده‌سازی
- **[HERO_SLIDER_FIXES.md](./HERO_SLIDER_FIXES.md)** - رفع مشکلات

---

## 🎯 قابلیت‌ها

### تصاویر Responsive
- ✅ Desktop Image (1920x1080)
- ✅ Tablet Image (1024x768)
- ✅ Mobile Image (768x1024)

### پشتیبانی ویدیو
- ✅ آپلود فایل ویدیو
- ✅ لینک ویدیوی خارجی (YouTube, Vimeo)
- ✅ Autoplay با کنترل
- ✅ Thumbnail سفارشی

### مدیریت محتوا
- ✅ عنوان، زیرعنوان، توضیحات
- ✅ دکمه با لینک سفارشی
- ✅ ترتیب نمایش
- ✅ زمان‌بندی نمایش

### تنظیمات پیشرفته
- ✅ نمایش برای کاربران احراز هویت شده/مهمان
- ✅ تاریخ شروع و پایان
- ✅ آمار بازدید و کلیک
- ✅ تنظیمات پیش‌فرض در SiteSettings

---

## 🚀 شروع سریع

### ایجاد اسلاید جدید

1. **ورود به Admin Panel**
   ```
   http://localhost:8000/admin/shared/heroslider/
   ```

2. **افزودن اسلاید**
   - عنوان و محتوا را وارد کنید
   - تصاویر را آپلود کنید
   - (اختیاری) ویدیو اضافه کنید
   - تنظیمات را انجام دهید

3. **فعال‌سازی**
   - `is_active` را فعال کنید
   - ذخیره کنید

### تنظیمات پیش‌فرض

اگر هیچ اسلایدی وجود نداشته باشد، محتوای پیش‌فرض از `SiteSettings` نمایش داده میشود:

```
Admin > Shared > Site Settings
- Default Hero Title
- Default Hero Subtitle
- Default Hero Description
- Default Hero Button Text
- Default Hero Button URL
- Default Hero Image
```

---

## 📊 API Endpoints

### دریافت اسلایدهای فعال
```bash
GET /api/v1/shared/hero-slides/active/
```

### ثبت بازدید
```bash
POST /api/v1/shared/hero-slides/{id}/track_view/
```

### ثبت کلیک
```bash
POST /api/v1/shared/hero-slides/{id}/track_click/
```

---

## 🔗 لینک‌های مرتبط

- [بازگشت به Features](../)
- [Image Optimization](../image-optimization/)
- [Banner System](../BANNER_SETUP_GUIDE.md)

---

**آخرین بروزرسانی:** 18 اکتبر 2025
