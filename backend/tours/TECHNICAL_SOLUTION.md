# راهنمای تخصصی حل مشکل فیلدهای قابل ترجمه

## 🎯 **مشکل دقیق**

شما در تب‌های زبان (فارسی، انگلیسی، ترکی) فقط فیلد `Gallery` را می‌بینید و فیلدهای قابل ترجمه (`title`, `description`, `short_description`, `highlights`, `rules`, `required_items`) نمایش داده نمی‌شوند.

## 🔍 **تحلیل تخصصی مشکل**

### **1. بررسی فیلدهای قابل ترجمه:**

```bash
python manage.py shell -c "from tours.models import Tour; print('Translatable fields:', list(Tour._parler_meta.get_translated_fields()))"
```

**نتیجه:** فیلدهای قابل ترجمه درست تعریف شده‌اند.

### **2. بررسی فرم ادمین:**

```bash
python manage.py shell -c "from tours.admin import TourAdminForm; form = TourAdminForm(); print('Form fields:', list(form.fields.keys()))"
```

**نتیجه:** فیلدهای قابل ترجمه در فرم وجود دارند.

### **3. بررسی تنظیمات Parler:**

```bash
python manage.py shell -c "from django.conf import settings; print('PARLER_LANGUAGES:', settings.PARLER_LANGUAGES)"
```

**نتیجه:** تنظیمات Parler درست است.

## 🚨 **علت اصلی مشکل**

مشکل احتمالاً در یکی از موارد زیر است:

1. **مشکل در تنظیمات `fieldsets`**: فیلدهای قابل ترجمه نباید در `fieldsets` قرار بگیرند
2. **مشکل در `get_form`**: متد `get_form` باید درست تنظیم شود
3. **مشکل در کش مرورگر**: کش مرورگر باید پاک شود

## 🔧 **راه حل‌های اعمال شده**

### **1. فرم اصلاح شد:**

```python
class TourAdminForm(TranslatableModelForm):  # تغییر از forms.ModelForm
    """Custom form for Tour admin with enhanced validation."""

    class Meta:
        model = Tour
        fields = '__all__'
```

### **2. تنظیمات Parler بهبود یافت:**

```python
PARLER_ENABLE_CACHING = False  # اضافه شد
```

### **3. متد get_form اضافه شد:**

```python
def get_form(self, request, obj=None, **kwargs):
    """Get form with proper field configuration."""
    form = super().get_form(request, obj, **kwargs)
    return form
```

### **4. get_prepopulated_fields خالی شد:**

```python
def get_prepopulated_fields(self, request, obj=None):
    """Get prepopulated fields for slug generation."""
    return {}
```

## 📋 **مراحل تست**

### **مرحله 1: پاک کردن کش**

1. مرورگر را کاملاً ببندید
2. کش مرورگر را پاک کنید (Ctrl+Shift+Delete)
3. مرورگر را دوباره باز کنید

### **مرحله 2: تست ادمین**

1. به آدرس `http://127.0.0.1:8000/admin/` بروید
2. وارد ادمین شوید
3. به بخش Tours بروید
4. روی "Add Tour" کلیک کنید

### **مرحله 3: بررسی تب‌های زبان**

1. در بالای صفحه، تب‌های زبان را ببینید:
   - **فارسی** (فارسی)
   - **English** (انگلیسی)
   - **Türkçe** (ترکی)

### **مرحله 4: بررسی فیلدهای قابل ترجمه**

1. روی تب "English" کلیک کنید
2. فیلدهای زیر باید نمایش داده شوند:
   - **Title** - عنوان تور
   - **Description** - توضیح کامل تور
   - **Short Description** - توضیح کوتاه تور
   - **Highlights** - نکات برجسته تور
   - **Rules** - قوانین و مقررات
   - **Required Items** - وسایل مورد نیاز

## ⚠️ **اگر مشکل حل نشد**

### **راه حل 1: بررسی لاگ‌ها**

```bash
# در کنسول سرور، خطاها را بررسی کنید
```

### **راه حل 2: بررسی خطاهای مرورگر**

1. F12 را فشار دهید
2. به تب Console بروید
3. خطاها را بررسی کنید

### **راه حل 3: تست با مرورگر دیگر**

1. از مرورگر دیگری استفاده کنید
2. یا از حالت incognito/private استفاده کنید

### **راه حل 4: بررسی تنظیمات Django**

```bash
python manage.py check
```

## 🎯 **نتیجه مورد انتظار**

بعد از اعمال تغییرات، شما باید:

1. **در تب اصلی**: فیلدهای غیر قابل ترجمه را ببینید
2. **در تب‌های زبان**: فیلدهای قابل ترجمه را ببینید
3. **در بخش Content**: فقط فیلد Gallery را ببینید

## 📞 **پشتیبانی فنی**

اگر مشکل حل نشد:

1. لاگ‌های سرور را بررسی کنید
2. خطاهای مرورگر را بررسی کنید
3. تنظیمات را دوباره بررسی کنید
4. با تیم توسعه تماس بگیرید

---

**آخرین به‌روزرسانی:** 2025-09-04
**وضعیت:** در حال حل
**مشکل:** فیلدهای قابل ترجمه در تب‌های زبان نمایش داده نمی‌شوند
