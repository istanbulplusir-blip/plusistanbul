# 🎉 سیستم مدیریت ایونت سه‌زبانه

<div dir="rtl">

## 🌟 معرفی

یک سیستم کامل و حرفه‌ای برای مدیریت ایونت‌ها با پشتیبانی از **۳ زبان** (فارسی، انگلیسی، عربی).

این سیستم برای مدیریت کنسرت‌ها، رویدادها، جشنواره‌ها و هر نوع ایونت دیگری طراحی شده است.

</div>

---

## ✨ ویژگی‌ها

<div dir="rtl">

### 🌍 چندزبانه
- ✅ پشتیبانی کامل از فارسی، انگلیسی و عربی
- ✅ تغییر زبان با یک هدر ساده
- ✅ ترجمه خودکار تمام محتوا

### 🎫 مدیریت بلیط
- ✅ انواع مختلف بلیط (VIP، عادی، اقتصادی، ویلچر)
- ✅ قیمت‌گذاری پویا با ضریب قیمت
- ✅ مدیریت ظرفیت و موجودی

### 🪑 مدیریت صندلی
- ✅ تقسیم‌بندی به بخش‌ها (Sections)
- ✅ شماره‌گذاری صندلی‌ها (ردیف و شماره)
- ✅ وضعیت صندلی (موجود، رزرو، فروخته شده)
- ✅ صندلی‌های ویژه (پرمیوم، ویلچر)

### 📅 مدیریت اجرا
- ✅ چندین اجرا برای هر ایونت
- ✅ تاریخ و زمان‌بندی دقیق
- ✅ اجراهای ویژه

### 🏛️ مدیریت مکان
- ✅ اطلاعات کامل مکان
- ✅ مختصات جغرافیایی
- ✅ امکانات و تسهیلات

### 🎤 مدیریت هنرمندان
- ✅ بیوگرافی کامل
- ✅ شبکه‌های اجتماعی
- ✅ تصاویر و گالری

### 🎁 گزینه‌های اضافی
- ✅ پارکینگ
- ✅ بسته غذایی
- ✅ خدمات ویژه

### 🔄 سیاست کنسلی
- ✅ چندین سطح بازپرداخت
- ✅ بر اساس زمان باقی‌مانده
- ✅ قابل تنظیم

### 🔌 API کامل
- ✅ RESTful API
- ✅ مستندات Swagger
- ✅ Postman Collection

</div>

---

## 🚀 شروع سریع

<div dir="rtl">

### ۱. نصب وابستگی‌ها

```bash
cd backend
pip install -r requirements.txt
```

### ۲. راه‌اندازی پایگاه داده

```bash
python manage.py migrate
```

### ۳. ایجاد ایونت نمونه

**ویندوز:**
```bash
create-sample-event.bat
```

**لینوکس/مک:**
```bash
./create-sample-event.sh
```

### ۴. اجرای سرور

```bash
python manage.py runserver
```

### ۵. مشاهده نتیجه

- **پنل ادمین**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/events/
- **ایونت نمونه**: http://localhost:8000/api/events/istanbul-music-festival-2025/

</div>

---

## 📖 مستندات

<div dir="rtl">

### راهنماهای موجود:

1. **[راهنمای کامل](EVENT_CREATION_GUIDE.md)** - مستندات جامع
2. **[راهنمای سریع](QUICK_EVENT_SETUP.md)** - شروع در ۳ مرحله
3. **[مستندات تفصیلی](backend/events/SAMPLE_EVENT_README.md)** - جزئیات فنی
4. **[خلاصه فایل‌ها](EVENT_FILES_SUMMARY.md)** - لیست تمام فایل‌ها

</div>

---

## 🌐 API Examples

### دریافت لیست ایونت‌ها

```bash
curl http://localhost:8000/api/events/
```

### دریافت ایونت به زبان فارسی

```bash
curl -H "Accept-Language: fa" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

### دریافت ایونت به زبان انگلیسی

```bash
curl -H "Accept-Language: en" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

### دریافت ایونت به زبان عربی

```bash
curl -H "Accept-Language: ar" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

### جستجوی ایونت‌ها

```bash
curl "http://localhost:8000/api/events/search/?q=music"
```

---

## 💻 نمونه کد JavaScript

```javascript
// دریافت ایونت به زبان فارسی
const response = await fetch(
  'http://localhost:8000/api/events/istanbul-music-festival-2025/',
  {
    headers: {
      'Accept-Language': 'fa'
    }
  }
);

const event = await response.json();
console.log(event.title); // جشنواره موسیقی استانبول ۲۰۲۵
```

---

## 🧪 تست API

<div dir="rtl">

### استفاده از اسکریپت تست

**ویندوز:**
```bash
test-event-api.bat
```

**لینوکس/مک:**
```bash
./test-event-api.sh
```

### استفاده از Postman

1. Postman را باز کنید
2. Import > Upload Files
3. فایل `Event_API_Tests.postman_collection.json` را انتخاب کنید
4. متغیرها را تنظیم کنید
5. تست‌ها را اجرا کنید

</div>

---

## 📊 ساختار داده

<div dir="rtl">

### مدل‌های اصلی:

- **Event** - ایونت اصلی
- **EventCategory** - دسته‌بندی ایونت
- **Venue** - مکان برگزاری
- **Artist** - هنرمندان
- **TicketType** - انواع بلیط
- **EventPerformance** - اجراها
- **EventSection** - بخش‌های صندلی
- **Seat** - صندلی‌های تک‌تک
- **EventOption** - گزینه‌های اضافی
- **EventCancellationPolicy** - سیاست‌های کنسلی

برای مشاهده ساختار کامل JSON، فایل `backend/events/sample_event_structure.json` را ببینید.

</div>

---

## 🎯 ایونت نمونه

<div dir="rtl">

### جشنواره موسیقی استانبول ۲۰۲۵

#### مشخصات:
- **هنرمندان**: سامی یوسف، ماهر زین
- **مکان**: سالن بزرگ استانبول
- **ظرفیت**: ۵۰۰۰ نفر
- **اجراها**: ۷ اجرا در ۷ روز آینده

#### انواع بلیط:
1. VIP (۵۰۰ صندلی) - $600
2. عادی (۳۰۰۰ صندلی) - $150
3. اقتصادی (۱۰۰۰ صندلی) - $105
4. ویلچر (۵۰ صندلی) - $150

#### بخش‌ها:
1. VIP Section - ۵۰۰ صندلی
2. Section A - ۱۵۰۰ صندلی
3. Section B - ۲۰۰۰ صندلی
4. Section C - ۱۰۰۰ صندلی

#### گزینه‌های اضافی:
- پارکینگ: $10
- بسته غذایی: $25

</div>

---

## 🛠️ تکنولوژی‌ها

<div dir="rtl">

- **Backend**: Django 4.0+
- **API**: Django REST Framework
- **چندزبانه**: django-parler
- **پایگاه داده**: PostgreSQL / SQLite
- **مستندات**: Swagger / ReDoc

</div>

---

## 📁 ساختار پروژه

```
project-root/
│
├── backend/
│   └── events/
│       ├── models.py              # مدل‌های دیتابیس
│       ├── serializers.py         # سریالایزرها
│       ├── views.py               # ویوها
│       ├── urls.py                # URLها
│       ├── admin.py               # پنل ادمین
│       └── management/
│           └── commands/
│               └── create_sample_event.py
│
├── EVENT_CREATION_GUIDE.md        # راهنمای کامل
├── QUICK_EVENT_SETUP.md           # راهنمای سریع
├── EVENT_FILES_SUMMARY.md         # خلاصه فایل‌ها
├── README_EVENT_SYSTEM.md         # این فایل
│
├── create-sample-event.bat        # اسکریپت ویندوز
├── create-sample-event.sh         # اسکریپت لینوکس
├── test-event-api.bat             # تست ویندوز
├── test-event-api.sh              # تست لینوکس
│
└── Event_API_Tests.postman_collection.json
```

---

## 🔐 امنیت

<div dir="rtl">

### نکات امنیتی:

- ✅ احراز هویت برای عملیات حساس
- ✅ مجوزها برای دسترسی به API
- ✅ CORS برای محیط تولید
- ✅ Rate limiting برای جلوگیری از سوء استفاده
- ✅ Validation برای تمام ورودی‌ها

</div>

---

## 🚀 استقرار (Deployment)

<div dir="rtl">

### مراحل استقرار:

1. تنظیم متغیرهای محیطی
2. پیکربندی پایگاه داده تولید
3. جمع‌آوری فایل‌های استاتیک
4. اجرای migrations
5. راه‌اندازی سرور (Gunicorn/uWSGI)
6. پیکربندی Nginx/Apache
7. تنظیم SSL

</div>

---

## 🤝 مشارکت

<div dir="rtl">

برای مشارکت در این پروژه:

1. Fork کنید
2. یک branch جدید بسازید
3. تغییرات خود را commit کنید
4. Push کنید
5. Pull Request ایجاد کنید

</div>

---

## 📝 لایسنس

<div dir="rtl">

این پروژه تحت لایسنس MIT منتشر شده است.

</div>

---

## 📞 پشتیبانی

<div dir="rtl">

### راه‌های ارتباطی:

- **مستندات**: فایل‌های راهنما را مطالعه کنید
- **Issues**: در GitHub issue ایجاد کنید
- **Email**: به تیم توسعه ایمیل بزنید

</div>

---

## 🎓 آموزش

<div dir="rtl">

### منابع یادگیری:

1. **[راهنمای کامل](EVENT_CREATION_GUIDE.md)** - شروع از اینجا
2. **[نمونه‌های کد](EVENT_CREATION_GUIDE.md#نمونه‌های-کد)** - کدهای آماده
3. **[API Endpoints](EVENT_CREATION_GUIDE.md#api-endpoints)** - لیست APIها
4. **[Postman Collection](Event_API_Tests.postman_collection.json)** - تست‌های آماده

</div>

---

## ✅ چک‌لیست شروع

<div dir="rtl">

- [ ] وابستگی‌ها را نصب کردم
- [ ] پایگاه داده را راه‌اندازی کردم
- [ ] ایونت نمونه را ایجاد کردم
- [ ] سرور را اجرا کردم
- [ ] API را تست کردم
- [ ] تمام ۳ زبان را امتحان کردم
- [ ] Postman Collection را import کردم
- [ ] مستندات را خواندم

</div>

---

## 🌟 ویژگی‌های آینده

<div dir="rtl">

- [ ] سیستم پرداخت آنلاین
- [ ] نقشه تعاملی صندلی‌ها
- [ ] اعلان‌های Push
- [ ] تخفیف‌ها و کوپن‌ها
- [ ] سیستم نظرات و امتیازدهی
- [ ] گزارش‌گیری پیشرفته
- [ ] یکپارچه‌سازی با تقویم
- [ ] اپلیکیشن موبایل

</div>

---

<div align="center">

## 💖 ساخته شده با عشق

**موفق باشید! 🚀**

[مستندات](EVENT_CREATION_GUIDE.md) | [API](http://localhost:8000/api/) | [Admin](http://localhost:8000/admin/)

</div>
