# راهنمای ایجاد ایونت نمونه با ۳ زبان

## نصب و راه‌اندازی

این دستور یک ایونت کامل با پشتیبانی از ۳ زبان (فارسی، انگلیسی، عربی) ایجاد می‌کند.

### محتویات ایونت نمونه:

1. **دسته‌بندی**: کنسرت موسیقی
2. **مکان**: سالن بزرگ استانبول (ظرفیت ۵۰۰۰ نفر)
3. **هنرمندان**: سامی یوسف و ماهر زین
4. **انواع بلیط**:
   - VIP (۵۰۰ صندلی)
   - عادی (۳۰۰۰ صندلی)
   - اقتصادی (۱۰۰۰ صندلی)
   - ویلچر (۵۰ صندلی)
5. **بخش‌ها**:
   - VIP Section (۵۰۰ صندلی)
   - Section A (۱۵۰۰ صندلی)
   - Section B (۲۰۰۰ صندلی)
   - Section C (۱۰۰۰ صندلی)
6. **اجراها**: ۷ اجرا در ۷ روز آینده
7. **گزینه‌های اضافی**:
   - پارکینگ ($10)
   - بسته غذایی ($25)
8. **سیاست‌های کنسلی**:
   - ۴۸ ساعت قبل: ۸۰٪ بازپرداخت
   - ۲۴ ساعت قبل: ۵۰٪ بازپرداخت
   - کمتر از ۲۴ ساعت: بدون بازپرداخت

## نحوه اجرا

### ۱. فعال‌سازی محیط مجازی

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows
```

### ۲. اجرای دستور

```bash
python manage.py create_sample_event
```

### ۳. بررسی نتیجه

پس از اجرای موفق، خروجی زیر را خواهید دید:

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

## دسترسی به داده‌ها

### از طریق Django Admin

1. وارد پنل ادمین شوید: `http://localhost:8000/admin/`
2. به بخش Events بروید
3. ایونت "Istanbul Music Festival 2025" را پیدا کنید

### از طریق API

#### لیست ایونت‌ها
```bash
GET /api/events/
```

#### جزئیات ایونت
```bash
GET /api/events/istanbul-music-festival-2025/
```

#### اجراها
```bash
GET /api/events/istanbul-music-festival-2025/performances/
```

#### صندلی‌های موجود برای یک اجرا
```bash
GET /api/events/{event_id}/performances/{performance_id}/seats/
```

## تغییر زبان

برای دریافت داده‌ها به زبان‌های مختلف، از هدر `Accept-Language` استفاده کنید:

```bash
# فارسی
curl -H "Accept-Language: fa" http://localhost:8000/api/events/istanbul-music-festival-2025/

# انگلیسی
curl -H "Accept-Language: en" http://localhost:8000/api/events/istanbul-music-festival-2025/

# عربی
curl -H "Accept-Language: ar" http://localhost:8000/api/events/istanbul-music-festival-2025/
```

## ساختار داده‌ها

### Event (ایونت)
- عنوان، توضیحات، توضیحات کوتاه (۳ زبان)
- نکات برجسته، قوانین، موارد مورد نیاز (۳ زبان)
- دسته‌بندی، مکان، هنرمندان
- زمان‌بندی (باز شدن درها، شروع، پایان)
- محدودیت سنی، قیمت پایه، ارز
- گالری تصاویر

### Venue (مکان)
- نام، توضیحات، آدرس (۳ زبان)
- شهر، کشور، مختصات جغرافیایی
- ظرفیت کل، امکانات، وب‌سایت

### Artist (هنرمند)
- نام، بیوگرافی (۳ زبان)
- تصویر، وب‌سایت، شبکه‌های اجتماعی

### TicketType (نوع بلیط)
- نام، توضیحات (۳ زبان)
- نوع بلیط، ضریب قیمت، ظرفیت
- مزایا، محدودیت‌های سنی

### EventPerformance (اجرا)
- تاریخ، زمان شروع، زمان پایان
- وضعیت در دسترس بودن، اجرای ویژه
- ظرفیت کل، ظرفیت فعلی، ظرفیت موجود

### EventSection (بخش)
- نام، توضیحات
- ظرفیت کل، قیمت پایه، ارز
- ویژگی‌ها (پرمیوم، دسترسی ویلچر)

### Seat (صندلی)
- شماره صندلی، شماره ردیف، بخش
- وضعیت (موجود، رزرو شده، فروخته شده، مسدود)
- قیمت، ارز
- ویژگی‌ها (پرمیوم، دسترسی ویلچر)

## نکات مهم

1. **زبان پیش‌فرض**: اگر زبان مشخص نشود، زبان پیش‌فرض سیستم استفاده می‌شود
2. **Slug**: برای دسترسی به ایونت از slug استفاده کنید: `istanbul-music-festival-2025`
3. **UUID**: هر ایونت یک UUID منحصر به فرد دارد
4. **Parler**: این پروژه از django-parler برای چندزبانه‌سازی استفاده می‌کند

## حذف داده‌های نمونه

اگر می‌خواهید داده‌های نمونه را حذف کنید:

```python
from events.models import Event
event = Event.objects.get(slug='istanbul-music-festival-2025')
event.delete()  # این همه موارد مرتبط را نیز حذف می‌کند
```

## پشتیبانی

در صورت بروز مشکل:
1. لاگ‌های Django را بررسی کنید
2. مطمئن شوید که django-parler نصب شده است
3. تنظیمات LANGUAGES در settings.py را بررسی کنید

---

# Sample Event Creation Guide (3 Languages)

## Installation & Setup

This command creates a complete event with support for 3 languages (Persian, English, Arabic).

### Sample Event Contents:

1. **Category**: Music Concert
2. **Venue**: Grand Hall Istanbul (5000 capacity)
3. **Artists**: Sami Yusuf and Maher Zain
4. **Ticket Types**:
   - VIP (500 seats)
   - Normal (3000 seats)
   - Economy (1000 seats)
   - Wheelchair (50 seats)
5. **Sections**:
   - VIP Section (500 seats)
   - Section A (1500 seats)
   - Section B (2000 seats)
   - Section C (1000 seats)
6. **Performances**: 7 performances over the next 7 days
7. **Additional Options**:
   - Parking ($10)
   - Food Package ($25)
8. **Cancellation Policies**:
   - 48 hours before: 80% refund
   - 24 hours before: 50% refund
   - Less than 24 hours: No refund

## How to Run

### 1. Activate Virtual Environment

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Run Command

```bash
python manage.py create_sample_event
```

### 3. Check Results

After successful execution, you will see:

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

## Accessing Data

### Via Django Admin

1. Login to admin panel: `http://localhost:8000/admin/`
2. Go to Events section
3. Find "Istanbul Music Festival 2025" event

### Via API

#### List Events
```bash
GET /api/events/
```

#### Event Details
```bash
GET /api/events/istanbul-music-festival-2025/
```

#### Performances
```bash
GET /api/events/istanbul-music-festival-2025/performances/
```

#### Available Seats for a Performance
```bash
GET /api/events/{event_id}/performances/{performance_id}/seats/
```

## Language Switching

To get data in different languages, use the `Accept-Language` header:

```bash
# Persian
curl -H "Accept-Language: fa" http://localhost:8000/api/events/istanbul-music-festival-2025/

# English
curl -H "Accept-Language: en" http://localhost:8000/api/events/istanbul-music-festival-2025/

# Arabic
curl -H "Accept-Language: ar" http://localhost:8000/api/events/istanbul-music-festival-2025/
```

## Support

If you encounter any issues:
1. Check Django logs
2. Ensure django-parler is installed
3. Verify LANGUAGES settings in settings.py
