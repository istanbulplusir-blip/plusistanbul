# 🎉 راهنمای کامل ایجاد ایونت سه‌زبانه

## 📋 فهرست مطالب
1. [معرفی](#معرفی)
2. [پیش‌نیازها](#پیش‌نیازها)
3. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
4. [ایجاد ایونت نمونه](#ایجاد-ایونت-نمونه)
5. [دسترسی به داده‌ها](#دسترسی-به-داده‌ها)
6. [API Endpoints](#api-endpoints)
7. [نمونه‌های کد](#نمونه‌های-کد)
8. [عیب‌یابی](#عیب‌یابی)

---

## 🎯 معرفی

این سیستم یک راه‌حل کامل برای مدیریت ایونت‌ها با پشتیبانی از **۳ زبان** (فارسی، انگلیسی، عربی) است.

### ویژگی‌های کلیدی:
- ✅ پشتیبانی کامل از ۳ زبان (فارسی، انگلیسی، عربی)
- ✅ مدیریت دسته‌بندی‌ها، مکان‌ها و هنرمندان
- ✅ انواع مختلف بلیط (VIP، عادی، اقتصادی، ویلچر)
- ✅ مدیریت بخش‌ها و صندلی‌ها
- ✅ سیستم رزرو و فروش بلیط
- ✅ گزینه‌های اضافی (پارکینگ، غذا، و...)
- ✅ سیاست‌های کنسلی قابل تنظیم
- ✅ API کامل برای فرانت‌اند

---

## 📦 پیش‌نیازها

### نرم‌افزارهای مورد نیاز:
- Python 3.8+
- Django 4.0+
- PostgreSQL (یا SQLite برای توسعه)
- django-parler (برای چندزبانه‌سازی)

### بررسی نصب:
```bash
python --version
django-admin --version
```

---

## 🚀 نصب و راه‌اندازی

### ۱. فعال‌سازی محیط مجازی

**ویندوز:**
```bash
cd backend
venv\Scripts\activate
```

**لینوکس/مک:**
```bash
cd backend
source venv/bin/activate
```

### ۲. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۳. تنظیمات پایگاه داده

```bash
python manage.py makemigrations
python manage.py migrate
```

### ۴. ایجاد سوپریوزر (اختیاری)

```bash
python manage.py createsuperuser
```

---

## 🎪 ایجاد ایونت نمونه

### روش ۱: استفاده از اسکریپت (توصیه می‌شود)

**ویندوز:**
```bash
create-sample-event.bat
```

**لینوکس/مک:**
```bash
chmod +x create-sample-event.sh
./create-sample-event.sh
```

### روش ۲: اجرای دستی

```bash
cd backend
python manage.py create_sample_event
```

### خروجی موفق:
```
Creating sample event with 3 languages...
Creating event category...
Creating venue...
Creating artists...
Creating event...
Creating ticket types...
Creating event options...
Creating cancellation policies...
Creating performances...
Creating sections and seats...

✅ Successfully created event: istanbul-music-festival-2025
Event ID: [UUID]
Total Performances: 7

You can now view this event in the admin panel or API.
```

---

## 🔍 دسترسی به داده‌ها

### Django Admin Panel

1. اجرای سرور:
```bash
python manage.py runserver
```

2. ورود به پنل ادمین:
```
http://localhost:8000/admin/
```

3. مسیر ایونت‌ها:
```
Admin > Events > Events
```

### مشاهده ایونت نمونه:
- **Slug**: `istanbul-music-festival-2025`
- **عنوان (فارسی)**: جشنواره موسیقی استانبول ۲۰۲۵
- **عنوان (انگلیسی)**: Istanbul Music Festival 2025
- **عنوان (عربی)**: مهرجان اسطنبول الموسيقي ٢٠٢٥

---

## 🌐 API Endpoints

### لیست ایونت‌ها
```http
GET /api/events/
```

### جزئیات ایونت (با Slug)
```http
GET /api/events/istanbul-music-festival-2025/
```

### جزئیات ایونت (با ID)
```http
GET /api/events/{event_id}/
```

### اجراهای ایونت
```http
GET /api/events/{event_id}/performances/
```

### صندلی‌های موجود برای یک اجرا
```http
GET /api/events/{event_id}/performances/{performance_id}/seats/
```

### فیلتر بر اساس دسته‌بندی
```http
GET /api/events/?category=music-concert
```

### فیلتر بر اساس مکان
```http
GET /api/events/?venue=grand-hall-istanbul
```

### جستجو
```http
GET /api/events/search/?q=music
```

---

## 💻 نمونه‌های کد

### ۱. دریافت ایونت به زبان فارسی

**cURL:**
```bash
curl -H "Accept-Language: fa" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

**JavaScript (Fetch):**
```javascript
fetch('http://localhost:8000/api/events/istanbul-music-festival-2025/', {
  headers: {
    'Accept-Language': 'fa'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Python (Requests):**
```python
import requests

response = requests.get(
    'http://localhost:8000/api/events/istanbul-music-festival-2025/',
    headers={'Accept-Language': 'fa'}
)
print(response.json())
```

### ۲. دریافت ایونت به زبان انگلیسی

**cURL:**
```bash
curl -H "Accept-Language: en" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

**JavaScript (Axios):**
```javascript
import axios from 'axios';

const response = await axios.get(
  'http://localhost:8000/api/events/istanbul-music-festival-2025/',
  {
    headers: {
      'Accept-Language': 'en'
    }
  }
);
console.log(response.data);
```

### ۳. دریافت ایونت به زبان عربی

**cURL:**
```bash
curl -H "Accept-Language: ar" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

### ۴. دریافت صندلی‌های موجود

**JavaScript:**
```javascript
const eventId = 'your-event-id';
const performanceId = 'your-performance-id';

fetch(`http://localhost:8000/api/events/${eventId}/performances/${performanceId}/seats/`, {
  headers: {
    'Accept-Language': 'fa'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Available sections:', data.sections);
  data.sections.forEach(section => {
    console.log(`Section: ${section.name}`);
    console.log(`Available seats: ${section.available_capacity}`);
    console.log(`Price: ${section.base_price} ${section.currency}`);
  });
});
```

### ۵. فیلتر ایونت‌ها بر اساس تاریخ

**cURL:**
```bash
curl "http://localhost:8000/api/events/?date_from=2025-10-19&date_to=2025-10-25"
```

### ۶. جستجوی ایونت‌ها

**JavaScript:**
```javascript
const searchQuery = 'music';

fetch(`http://localhost:8000/api/events/search/?q=${searchQuery}`, {
  headers: {
    'Accept-Language': 'fa'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Search results:', data);
});
```

---

## 🎨 ساختار داده

### Event Object (نمونه پاسخ API)

```json
{
  "id": "uuid-here",
  "slug": "istanbul-music-festival-2025",
  "title": "جشنواره موسیقی استانبول ۲۰۲۵",
  "short_description": "شبی فراموش‌نشدنی با بهترین خوانندگان جهان",
  "description": "جشنواره موسیقی استانبول...",
  "highlights": "• اجرای زنده توسط سامی یوسف و ماهر زین...",
  "rules": "• ورود با بلیط معتبر الزامی است...",
  "required_items": "• بلیط چاپی یا الکترونیکی...",
  "image": "/media/events/event.jpg",
  "gallery": ["/media/events/gallery1.jpg"],
  "style": "music",
  "door_open_time": "18:00:00",
  "start_time": "20:00:00",
  "end_time": "23:00:00",
  "age_restriction": 12,
  "price": 150.00,
  "currency": "USD",
  "category": {
    "id": "uuid-here",
    "name": "کنسرت موسیقی",
    "slug": "music-concert",
    "icon": "music",
    "color": "#FF6B6B"
  },
  "venue": {
    "id": "uuid-here",
    "name": "سالن بزرگ استانبول",
    "address": "میدان تقسیم، خیابان استقلال، استانبول، ترکیه",
    "city": "Istanbul",
    "country": "Turkey",
    "total_capacity": 5000,
    "coordinates": {"lat": 41.0082, "lng": 28.9784}
  },
  "artists": [
    {
      "id": "uuid-here",
      "name": "سامی یوسف",
      "bio": "خواننده و آهنگساز بریتانیایی-ایرانی...",
      "website": "https://samiyusuf.com"
    }
  ],
  "ticket_types": [
    {
      "id": "uuid-here",
      "name": "بلیط VIP",
      "description": "بلیط ویژه با امکانات اختصاصی...",
      "ticket_type": "vip",
      "price_modifier": 2.0,
      "capacity": 500,
      "benefits": ["Front row seats", "VIP lounge access"]
    }
  ],
  "performances": [
    {
      "id": "uuid-here",
      "date": "2025-10-19",
      "start_time": "20:00:00",
      "end_time": "23:00:00",
      "is_available": true,
      "max_capacity": 5000,
      "available_capacity": 5000
    }
  ],
  "is_active": true,
  "is_featured": true,
  "is_popular": true,
  "is_special": true
}
```

---

## 🔧 عیب‌یابی

### مشکل: ایونت ایجاد نمی‌شود

**راه‌حل:**
1. بررسی کنید که django-parler نصب شده باشد:
```bash
pip install django-parler
```

2. مطمئن شوید که migrations اجرا شده‌اند:
```bash
python manage.py migrate
```

### مشکل: زبان‌ها نمایش داده نمی‌شوند

**راه‌حل:**
1. بررسی تنظیمات LANGUAGES در `settings.py`:
```python
LANGUAGES = [
    ('fa', 'Persian'),
    ('en', 'English'),
    ('ar', 'Arabic'),
]
```

2. بررسی PARLER_LANGUAGES:
```python
PARLER_LANGUAGES = {
    None: (
        {'code': 'fa'},
        {'code': 'en'},
        {'code': 'ar'},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}
```

### مشکل: API خطای 404 می‌دهد

**راه‌حل:**
1. مطمئن شوید که سرور در حال اجراست:
```bash
python manage.py runserver
```

2. بررسی کنید که URL صحیح است:
```
http://localhost:8000/api/events/
```

### مشکل: صندلی‌ها ایجاد نمی‌شوند

**راه‌حل:**
1. بررسی لاگ‌های Django
2. اجرای مجدد دستور:
```bash
python manage.py create_sample_event
```

---

## 📚 منابع اضافی

### فایل‌های مرتبط:
- `backend/events/SAMPLE_EVENT_README.md` - راهنمای تفصیلی
- `backend/events/sample_event_structure.json` - ساختار JSON کامل
- `backend/events/management/commands/create_sample_event.py` - کد منبع

### مستندات API:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

---

## 🎯 مراحل بعدی

1. **تست API**: از Postman یا cURL برای تست استفاده کنید
2. **یکپارچه‌سازی فرانت‌اند**: API را با React/Vue/Angular یکپارچه کنید
3. **سفارشی‌سازی**: ایونت‌های خود را با داده‌های واقعی ایجاد کنید
4. **استقرار**: برنامه را روی سرور مستقر کنید

---

## 💡 نکات مهم

1. **زبان پیش‌فرض**: اگر هدر `Accept-Language` ارسال نشود، زبان پیش‌فرض سیستم استفاده می‌شود
2. **Slug**: برای دسترسی سریع‌تر از slug به جای UUID استفاده کنید
3. **کش**: برای بهبود عملکرد، از کش استفاده کنید
4. **امنیت**: در محیط تولید، CORS و احراز هویت را پیکربندی کنید

---

## 📞 پشتیبانی

در صورت بروز مشکل:
1. لاگ‌های Django را بررسی کنید
2. مستندات django-parler را مطالعه کنید
3. از تیم توسعه کمک بگیرید

---

**موفق باشید! 🚀**
