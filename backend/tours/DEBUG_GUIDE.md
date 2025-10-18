# راهنمای عیب‌یابی فیلدهای قابل ترجمه

## 🎯 **مشکل فعلی**

شما در تب انگلیسی (`http://127.0.0.1:8000/admin/tours/tour/add/?language=en`) فیلدهای قابل ترجمه را نمی‌بینید.

## 🔍 **مراحل عیب‌یابی**

### **مرحله 1: بررسی تنظیمات Parler**

بیایید تنظیمات `django-parler` را بررسی کنیم:

```python
# در settings.py
PARLER_LANGUAGES = {
    SITE_ID: (
        {'code': 'fa', 'name': 'فارسی', 'fallback': True},
        {'code': 'en', 'name': 'English'},
        {'code': 'tr', 'name': 'Türkçe'},
    ),
    'default': {
        'fallback': 'fa',
        'hide_untranslated': False,
        'redirect_on_fallback': False,
    }
}

PARLER_DEFAULT_LANGUAGE_CODE = 'fa'
PARLER_SHOW_EXCLUDED_LANGUAGE_TABS = True
PARLER_ENABLE_CACHING = False
```

### **مرحله 2: بررسی مدل Tour**

فیلدهای قابل ترجمه در مدل درست تعریف شده‌اند:

```python
# در models.py
translations = TranslatedFields(
    title=models.CharField(max_length=255, verbose_name=_('Title')),
    description=models.TextField(verbose_name=_('Description')),
    short_description=models.TextField(max_length=500, verbose_name=_('Short description')),
    highlights=models.TextField(blank=True, verbose_name=_('Highlights')),
    rules=models.TextField(blank=True, verbose_name=_('Rules and regulations')),
    required_items=models.TextField(blank=True, verbose_name=_('Required items')),
)
```

### **مرحله 3: بررسی ادمین**

ادمین از `TranslatableAdmin` و `TranslatableModelForm` استفاده می‌کند:

```python
@admin.register(Tour)
class TourAdmin(TranslatableAdmin):
    form = TourAdminForm
    # ...
```

## 🚨 **مشکلات احتمالی و راه حل**

### **مشکل 1: کش مرورگر**

**راه حل:** کش مرورگر را پاک کنید و صفحه را رفرش کنید.

### **مشکل 2: تنظیمات SITE_ID**

**راه حل:** مطمئن شوید که `SITE_ID = 1` در `settings.py` تنظیم شده است.

### **مشکل 3: مشکل در فرم**

**راه حل:** `get_prepopulated_fields` را خالی کردیم تا مشکل KeyError حل شود.

### **مشکل 4: مشکل در دیتابیس**

**راه حل:** دیتابیس را بررسی کنید.

## 🔧 **تست عملی**

### **مرحله 1: تست سرور**

1. به آدرس `http://127.0.0.1:8000/admin/` بروید
2. وارد ادمین شوید
3. به بخش Tours بروید
4. روی "Add Tour" کلیک کنید

### **مرحله 2: بررسی تب‌های زبان**

1. در بالای صفحه، تب‌های زبان را ببینید:
   - **فارسی** (فارسی)
   - **English** (انگلیسی)
   - **Türkçe** (ترکی)

### **مرحله 3: بررسی فیلدهای قابل ترجمه**

1. روی تب "English" کلیک کنید
2. فیلدهای زیر باید نمایش داده شوند:
   - **Title** - عنوان تور
   - **Description** - توضیح کامل تور
   - **Short Description** - توضیح کوتاه تور
   - **Highlights** - نکات برجسته تور
   - **Rules** - قوانین و مقررات
   - **Required Items** - وسایل مورد نیاز

## ⚠️ **اگر فیلدها هنوز نمایش داده نمی‌شوند**

### **راه حل 1: بررسی تنظیمات**

```bash
python manage.py shell -c "from django.contrib.sites.models import Site; print('Sites:', Site.objects.all())"
```

### **راه حل 2: بررسی فیلدهای قابل ترجمه**

```bash
python manage.py shell -c "from tours.models import Tour; print('Translatable fields:', list(Tour._parler_meta.get_translated_fields()))"
```

### **راه حل 3: ری‌استارت سرور**

```bash
# سرور را متوقف کنید
taskkill /f /im python.exe

# دوباره شروع کنید
python manage.py runserver
```

### **راه حل 4: بررسی لاگ‌ها**

در کنسول سرور، خطاها را بررسی کنید.

## 📋 **چک‌لیست**

- [ ] سرور در حال اجرا است
- [ ] تنظیمات `PARLER_LANGUAGES` درست است
- [ ] `SITE_ID = 1` تنظیم شده است
- [ ] مدل `Tour` از `TranslatableModel` ارث‌بری می‌کند
- [ ] ادمین از `TranslatableAdmin` استفاده می‌کند
- [ ] فرم از `TranslatableModelForm` استفاده می‌کند
- [ ] کش مرورگر پاک شده است
- [ ] صفحه رفرش شده است

## 🆘 **اگر مشکل حل نشد**

1. **لاگ‌های سرور را بررسی کنید**
2. **خطاهای مرورگر را بررسی کنید** (F12 → Console)
3. **تنظیمات را دوباره بررسی کنید**
4. **با تیم توسعه تماس بگیرید**

---

**آخرین به‌روزرسانی:** 2025-09-04
**وضعیت:** در حال عیب‌یابی
