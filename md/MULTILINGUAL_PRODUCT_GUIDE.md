# راهنمای ایجاد محصولات چندزبانه برای ادمین‌ها

## 🎯 هدف

این راهنما به شما آموزش می‌دهد که چگونه محصولات تور را با پشتیبانی کامل از چند زبان (فارسی، انگلیسی، ترکی) ایجاد کنید تا کاربران بتوانند محتوا را به زبان دلخواه خود مشاهده کنند.

## 🌐 زبان‌های پشتیبانی شده

- **فارسی (fa)**: زبان اصلی سایت
- **انگلیسی (en)**: زبان بین‌المللی
- **ترکی (tr)**: زبان اضافی (اختیاری)

## 📋 مراحل ایجاد محصول چندزبانه

### مرحله 1: ایجاد محصول پایه

```bash
# ایجاد محصول تور
python manage.py create_tour_x
```

### مرحله 2: اضافه کردن ترجمه‌های فارسی

```bash
# اضافه کردن ترجمه‌های فارسی برای محصول
python manage.py update_tour_x_features

# اضافه کردن ترجمه‌های فارسی برای برنامه سفر
python manage.py update_tour_x_itinerary_translations
```

### مرحله 3: تأیید ترجمه‌ها

```bash
# بررسی کامل ترجمه‌ها
python verify_tour_x_translations.py
```

## 🏗️ ساختار ترجمه‌ها

### 1. فیلدهای قابل ترجمه در مدل Tour

```python
# فیلدهای قابل ترجمه
- title: عنوان تور
- description: توضیحات تور
- highlights: نکات برجسته
- rules: قوانین تور
- required_items: موارد مورد نیاز
```

### 2. فیلدهای قابل ترجمه در مدل TourCategory

```python
# فیلدهای قابل ترجمه
- name: نام دسته‌بندی
- description: توضیحات دسته‌بندی
```

### 3. فیلدهای قابل ترجمه در مدل TourItinerary

```python
# فیلدهای قابل ترجمه
- title: عنوان مرحله
- description: توضیحات مرحله
```

## 💻 نحوه تنظیم ترجمه‌ها در کد

### مثال 1: تنظیم ترجمه فارسی برای تور

```python
from tours.models import Tour

# پیدا کردن تور
tour = Tour.objects.filter(slug='tour-x').first()

# تنظیم ترجمه فارسی
tour.set_current_language('fa')
tour.title = "تور ایکس - تجربه فرهنگی"
tour.description = "یک تجربه فرهنگی غنی در تهران، ایران."
tour.save()
```

### مثال 2: تنظیم ترجمه انگلیسی برای تور

```python
# تنظیم ترجمه انگلیسی
tour.set_current_language('en')
tour.title = "Tour X - Cultural Experience"
tour.description = "A rich cultural experience in Tehran, Iran."
tour.save()
```

### مثال 3: تنظیم ترجمه برای برنامه سفر

```python
from tours.models import TourItinerary

# پیدا کردن آیتم برنامه سفر
item = TourItinerary.objects.get(tour=tour, order=1)

# ترجمه فارسی
item.set_current_language('fa')
item.title = "خوش‌آمدگویی و راهنمایی"
item.description = "با راهنمای تور و همسفران خود آشنا شوید."
item.save()

# ترجمه انگلیسی
item.set_current_language('en')
item.title = "Welcome & Orientation"
item.description = "Meet your guide and fellow travelers."
item.save()
```

## 🔧 دستورات مدیریتی برای ترجمه

### دستور ایجاد ترجمه‌های فارسی برای محصول جدید

```python
# در فایل management/commands/create_multilingual_tour.py

class Command(BaseCommand):
    def handle(self, *args, **options):
        # ایجاد تور
        tour = Tour.objects.create(...)

        # تنظیم ترجمه فارسی
        tour.set_current_language('fa')
        tour.title = "عنوان فارسی"
        tour.description = "توضیحات فارسی"
        tour.save()

        # تنظیم ترجمه انگلیسی
        tour.set_current_language('en')
        tour.title = "English Title"
        tour.description = "English Description"
        tour.save()
```

### دستور ایجاد ترجمه‌های فارسی برای برنامه سفر

```python
# در فایل management/commands/create_multilingual_itinerary.py

class Command(BaseCommand):
    def handle(self, *args, **options):
        # ترجمه‌های فارسی برای برنامه سفر
        persian_translations = {
            1: {
                'title': 'خوش‌آمدگویی و راهنمایی',
                'description': 'با راهنمای تور آشنا شوید.'
            },
            # ... سایر آیتم‌ها
        }

        for order, translations in persian_translations.items():
            item = TourItinerary.objects.get(tour=tour, order=order)

            # تنظیم ترجمه فارسی
            item.set_current_language('fa')
            item.title = translations['title']
            item.description = translations['description']
            item.save()
```

## 🌐 نحوه کارکرد ترجمه‌ها در فرانت‌اند

### 1. API Response

```json
{
  "title": "تور ایکس - تجربه فرهنگی",
  "description": "یک تجربه فرهنگی غنی...",
  "itinerary": [
    {
      "title": "خوش‌آمدگویی و راهنمایی",
      "description": "با راهنمای تور آشنا شوید..."
    }
  ]
}
```

### 2. تغییر زبان در فرانت‌اند

```javascript
// تغییر زبان به فارسی
setLanguage("fa");

// تغییر زبان به انگلیسی
setLanguage("en");
```

### 3. نمایش محتوا بر اساس زبان

```javascript
// نمایش عنوان تور
const tourTitle = tour.title; // بر اساس زبان انتخاب شده

// نمایش برنامه سفر
itinerary.map((item) => (
  <div>
    <h3>{item.title}</h3>
    <p>{item.description}</p>
  </div>
));
```

## ✅ چک‌لیست ایجاد محصول چندزبانه

### قبل از انتشار محصول:

- [ ] عنوان تور در فارسی تنظیم شده
- [ ] عنوان تور در انگلیسی تنظیم شده
- [ ] توضیحات تور در فارسی تنظیم شده
- [ ] توضیحات تور در انگلیسی تنظیم شده
- [ ] دسته‌بندی در فارسی تنظیم شده
- [ ] دسته‌بندی در انگلیسی تنظیم شده
- [ ] برنامه سفر در فارسی تنظیم شده
- [ ] برنامه سفر در انگلیسی تنظیم شده
- [ ] ترجمه‌ها تأیید شده‌اند
- [ ] تست تغییر زبان انجام شده

### تست‌های ضروری:

```bash
# تست ترجمه‌ها
python verify_tour_x_translations.py

# تست کامل محصول
python verify_tour_x_all.py
```

## 🚀 بهترین شیوه‌ها

### 1. همیشه هر دو زبان را تنظیم کنید

```python
# ✅ درست
tour.set_current_language('fa')
tour.title = "عنوان فارسی"
tour.save()

tour.set_current_language('en')
tour.title = "English Title"
tour.save()

# ❌ اشتباه - فقط یک زبان
tour.title = "عنوان فارسی"
tour.save()
```

### 2. از ترجمه‌های با کیفیت استفاده کنید

```python
# ✅ ترجمه با کیفیت
tour.description = "یک تجربه فرهنگی غنی و منحصر به فرد در قلب تهران"

# ❌ ترجمه ضعیف
tour.description = "تور خوب"
```

### 3. همیشه ترجمه‌ها را تأیید کنید

```bash
# قبل از انتشار، حتماً تست کنید
python verify_tour_x_translations.py
```

## 🔍 عیب‌یابی مشکلات رایج

### مشکل 1: ترجمه فارسی نمایش داده نمی‌شود

**علت**: ترجمه فارسی تنظیم نشده
**راه‌حل**:

```python
tour.set_current_language('fa')
tour.title = "عنوان فارسی"
tour.save()
```

### مشکل 2: برنامه سفر فقط انگلیسی است

**علت**: ترجمه‌های برنامه سفر تنظیم نشده
**راه‌حل**:

```bash
python manage.py update_tour_x_itinerary_translations
```

### مشکل 3: دسته‌بندی ترجمه ندارد

**علت**: ترجمه دسته‌بندی تنظیم نشده
**راه‌حل**:

```python
category.set_current_language('fa')
category.name = "نام دسته‌بندی فارسی"
category.save()
```

## 📚 منابع اضافی

- [Django Modeltranslation Documentation](https://django-modeltranslation.readthedocs.io/)
- [Frontend Language Switching Guide](frontend-language-guide.md)
- [API Language Headers Documentation](api-language-guide.md)

---

**نکته مهم**: همیشه قبل از انتشار محصول جدید، ترجمه‌های فارسی و انگلیسی را کامل کنید تا تجربه کاربری بهتری ارائه دهید.
