# 📁 خلاصه فایل‌های ایجاد شده برای سیستم ایونت سه‌زبانه

## 🎯 فایل‌های اصلی

### 1. کد منبع (Source Code)
📄 **`backend/events/management/commands/create_sample_event.py`**
- دستور Django برای ایجاد ایونت نمونه
- شامل تمام داده‌های نمونه با ۳ زبان
- ایجاد خودکار دسته‌بندی، مکان، هنرمندان، بلیط‌ها، اجراها و صندلی‌ها

### 2. فایل‌های __init__
📄 **`backend/events/management/__init__.py`**
📄 **`backend/events/management/commands/__init__.py`**
- فایل‌های مورد نیاز برای ماژول‌های Python

---

## 📚 مستندات

### 1. راهنمای کامل
📖 **`EVENT_CREATION_GUIDE.md`**
- راهنمای جامع و کامل
- شامل تمام جزئیات نصب، راه‌اندازی و استفاده
- نمونه‌های کد به زبان‌های مختلف
- راهنمای عیب‌یابی

### 2. راهنمای سریع
⚡ **`QUICK_EVENT_SETUP.md`**
- راه‌اندازی در ۳ مرحله ساده
- برای شروع سریع

### 3. مستندات تفصیلی
📄 **`backend/events/SAMPLE_EVENT_README.md`**
- توضیحات تفصیلی محتویات ایونت
- ساختار داده‌ها
- نحوه دسترسی به API

### 4. ساختار JSON
🗂️ **`backend/events/sample_event_structure.json`**
- نمونه کامل ساختار JSON ایونت
- شامل تمام فیلدها و روابط
- مفید برای توسعه‌دهندگان فرانت‌اند

### 5. خلاصه فایل‌ها (این فایل)
📋 **`EVENT_FILES_SUMMARY.md`**
- لیست تمام فایل‌های ایجاد شده
- توضیح مختصر هر فایل

---

## 🚀 اسکریپت‌های اجرایی

### 1. ایجاد ایونت نمونه

#### ویندوز
🪟 **`create-sample-event.bat`**
```bash
create-sample-event.bat
```

#### لینوکس/مک
🐧 **`create-sample-event.sh`**
```bash
chmod +x create-sample-event.sh
./create-sample-event.sh
```

### 2. تست API

#### ویندوز
🪟 **`test-event-api.bat`**
```bash
test-event-api.bat
```

#### لینوکس/مک
🐧 **`test-event-api.sh`**
```bash
chmod +x test-event-api.sh
./test-event-api.sh
```

---

## 🧪 فایل‌های تست

### Postman Collection
📮 **`Event_API_Tests.postman_collection.json`**
- مجموعه کامل تست‌های API
- شامل تمام endpoint‌ها
- تست با ۳ زبان (فارسی، انگلیسی، عربی)
- قابل import در Postman

**نحوه استفاده:**
1. Postman را باز کنید
2. Import > Upload Files
3. فایل `Event_API_Tests.postman_collection.json` را انتخاب کنید
4. متغیرها را تنظیم کنید:
   - `base_url`: http://localhost:8000
   - `event_slug`: istanbul-music-festival-2025
   - `event_id`: UUID ایونت
   - `performance_id`: UUID اجرا

---

## 📊 ساختار دایرکتوری

```
project-root/
│
├── backend/
│   └── events/
│       ├── management/
│       │   ├── __init__.py
│       │   └── commands/
│       │       ├── __init__.py
│       │       └── create_sample_event.py
│       ├── SAMPLE_EVENT_README.md
│       └── sample_event_structure.json
│
├── EVENT_CREATION_GUIDE.md
├── QUICK_EVENT_SETUP.md
├── EVENT_FILES_SUMMARY.md
├── create-sample-event.bat
├── create-sample-event.sh
├── test-event-api.bat
├── test-event-api.sh
└── Event_API_Tests.postman_collection.json
```

---

## 🎯 نحوه استفاده

### مرحله ۱: ایجاد ایونت نمونه
```bash
# ویندوز
create-sample-event.bat

# لینوکس/مک
./create-sample-event.sh
```

### مرحله ۲: اجرای سرور
```bash
cd backend
python manage.py runserver
```

### مرحله ۳: تست API
```bash
# ویندوز
test-event-api.bat

# لینوکس/مک
./test-event-api.sh
```

### مرحله ۴: تست با Postman
1. Import کردن `Event_API_Tests.postman_collection.json`
2. تنظیم متغیرها
3. اجرای تست‌ها

---

## 🌍 پشتیبانی از زبان‌ها

تمام فایل‌های ایجاد شده از **۳ زبان** پشتیبانی می‌کنند:

1. **فارسی (fa)** - زبان اصلی
2. **انگلیسی (en)** - زبان بین‌المللی
3. **عربی (ar)** - زبان منطقه‌ای

### تغییر زبان در API:
```bash
# فارسی
curl -H "Accept-Language: fa" http://localhost:8000/api/events/...

# انگلیسی
curl -H "Accept-Language: en" http://localhost:8000/api/events/...

# عربی
curl -H "Accept-Language: ar" http://localhost:8000/api/events/...
```

---

## 📦 محتویات ایونت نمونه

### جشنواره موسیقی استانبول ۲۰۲۵

#### 🎤 هنرمندان
- سامی یوسف (Sami Yusuf)
- ماهر زین (Maher Zain)

#### 🏛️ مکان
- سالن بزرگ استانبول
- ظرفیت: ۵۰۰۰ نفر
- آدرس: میدان تقسیم، استانبول

#### 🎫 انواع بلیط
1. **VIP** (۵۰۰ صندلی) - ضریب قیمت: ۲.۰
2. **عادی** (۳۰۰۰ صندلی) - ضریب قیمت: ۱.۰
3. **اقتصادی** (۱۰۰۰ صندلی) - ضریب قیمت: ۰.۷
4. **ویلچر** (۵۰ صندلی) - ضریب قیمت: ۱.۰

#### 🪑 بخش‌ها
1. **VIP Section** - ۵۰۰ صندلی - $300
2. **Section A** - ۱۵۰۰ صندلی - $150
3. **Section B** - ۲۰۰۰ صندلی - $100
4. **Section C** - ۱۰۰۰ صندلی - $70

#### 📅 اجراها
- ۷ اجرا در ۷ روز آینده
- زمان: ۲۰:۰۰ - ۲۳:۰۰
- باز شدن درها: ۱۸:۰۰

#### 🅿️ گزینه‌های اضافی
- پارکینگ: $10
- بسته غذایی: $25

#### 🔄 سیاست‌های کنسلی
- ۴۸ ساعت قبل: ۸۰٪ بازپرداخت
- ۲۴ ساعت قبل: ۵۰٪ بازپرداخت
- کمتر از ۲۴ ساعت: بدون بازپرداخت

---

## 🔗 لینک‌های مفید

### API Endpoints
- لیست ایونت‌ها: `GET /api/events/`
- جزئیات ایونت: `GET /api/events/istanbul-music-festival-2025/`
- دسته‌بندی‌ها: `GET /api/categories/`
- مکان‌ها: `GET /api/venues/`
- هنرمندان: `GET /api/artists/`
- اجراها: `GET /api/events/{id}/performances/`
- صندلی‌ها: `GET /api/events/{id}/performances/{id}/seats/`

### پنل ادمین
- ایونت‌ها: `http://localhost:8000/admin/events/event/`
- دسته‌بندی‌ها: `http://localhost:8000/admin/events/eventcategory/`
- مکان‌ها: `http://localhost:8000/admin/events/venue/`
- هنرمندان: `http://localhost:8000/admin/events/artist/`

---

## 💡 نکات مهم

1. **اجرای اولیه**: حتماً ابتدا migrations را اجرا کنید
2. **زبان پیش‌فرض**: اگر هدر زبان ارسال نشود، زبان پیش‌فرض استفاده می‌شود
3. **UUID vs Slug**: می‌توانید از slug یا UUID برای دسترسی به ایونت استفاده کنید
4. **Postman**: برای تست راحت‌تر از Postman Collection استفاده کنید
5. **مستندات**: برای جزئیات بیشتر به `EVENT_CREATION_GUIDE.md` مراجعه کنید

---

## 🆘 پشتیبانی

در صورت بروز مشکل:

1. **لاگ‌ها را بررسی کنید**
   ```bash
   python manage.py runserver
   ```

2. **مستندات را مطالعه کنید**
   - `EVENT_CREATION_GUIDE.md`
   - `backend/events/SAMPLE_EVENT_README.md`

3. **تست‌ها را اجرا کنید**
   ```bash
   ./test-event-api.sh
   ```

4. **Postman Collection را امتحان کنید**
   - Import کنید
   - تست‌ها را اجرا کنید

---

## ✅ چک‌لیست

- [ ] فایل‌های ایجاد شده را بررسی کردم
- [ ] اسکریپت ایجاد ایونت را اجرا کردم
- [ ] سرور Django را راه‌اندازی کردم
- [ ] API را تست کردم
- [ ] Postman Collection را import کردم
- [ ] تمام ۳ زبان را تست کردم
- [ ] مستندات را مطالعه کردم

---

**موفق باشید! 🎉**

برای سوالات بیشتر، به مستندات مراجعه کنید یا با تیم توسعه تماس بگیرید.
