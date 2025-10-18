# 🎭 Events System

> سیستم جامع مدیریت رویدادها و بلیط‌فروشی

---

## 📚 مستندات موجود

### راهنماها
- **[README_EVENT_SYSTEM.md](./README_EVENT_SYSTEM.md)** - راهنمای کامل سیستم
- **[QUICK_EVENT_SETUP.md](./QUICK_EVENT_SETUP.md)** - راه‌اندازی سریع
- **[EVENT_CREATION_GUIDE.md](./EVENT_CREATION_GUIDE.md)** - راهنمای ایجاد رویداد

### خلاصه‌ها
- **[EVENT_FILES_SUMMARY.md](./EVENT_FILES_SUMMARY.md)** - خلاصه فایل‌ها و ساختار

---

## 🎯 قابلیت‌ها

### مدیریت رویدادها
- ✅ ایجاد و ویرایش رویدادها
- ✅ دسته‌بندی رویدادها
- ✅ مکان‌ها (Venues)
- ✅ هنرمندان (Artists)
- ✅ گالری تصاویر

### سیستم بلیط
- ✅ انواع مختلف بلیط
- ✅ قیمت‌گذاری پویا
- ✅ ظرفیت و موجودی
- ✅ نقشه صندلی (Seating)

### اجراها (Performances)
- ✅ زمان‌بندی اجراها
- ✅ مدیریت ظرفیت
- ✅ وضعیت موجودی

### ویژگی‌های پیشرفته
- ✅ سیستم تخفیف
- ✅ محدودیت سنی
- ✅ قوانین لغو
- ✅ آمار و گزارش

---

## 🚀 شروع سریع

### ایجاد رویداد جدید

1. **ایجاد مکان (Venue)**
   ```
   Admin > Events > Venues > Add
   ```

2. **ایجاد رویداد**
   ```
   Admin > Events > Events > Add
   - عنوان و توضیحات
   - مکان
   - تصویر
   - قیمت پایه
   ```

3. **افزودن انواع بلیط**
   ```
   Event Detail > Ticket Types > Add
   - نام (VIP, Regular, etc.)
   - قیمت
   - ظرفیت
   ```

4. **ایجاد اجرا (Performance)**
   ```
   Event Detail > Performances > Add
   - تاریخ و زمان
   - ظرفیت
   ```

### تست سریع

```bash
# استفاده از اسکریپت تست
./test-event-api.sh

# یا دستی
curl http://localhost:8000/api/v1/events/
```

---

## 📊 API Endpoints

### رویدادها
```bash
GET    /api/v1/events/              # لیست رویدادها
GET    /api/v1/events/{slug}/       # جزئیات رویداد
GET    /api/v1/events/featured/     # رویدادهای ویژه
GET    /api/v1/events/upcoming/     # رویدادهای آینده
```

### اجراها
```bash
GET    /api/v1/events/{slug}/performances/     # اجراهای یک رویداد
POST   /api/v1/events/performances/{id}/book/  # رزرو بلیط
```

### دسته‌بندی‌ها
```bash
GET    /api/v1/events/categories/   # لیست دسته‌بندی‌ها
```

---

## 🗂️ ساختار مدل‌ها

```
Event
├── EventCategory
├── Venue
├── Artist (Many-to-Many)
├── EventGallery (Images)
├── TicketType
│   └── TicketPricing
├── Performance
│   └── PerformanceSeat
└── EventOption (Add-ons)
```

---

## 🔧 تنظیمات

### Backend Settings
```python
# backend/events/models.py
- Event model configuration
- Ticket types
- Performance scheduling
```

### Frontend Components
```tsx
// frontend/components/events/
- EventCard.tsx
- EventDetail.tsx
- TicketSelection.tsx
- SeatMap.tsx
```

---

## 📝 نمونه داده

برای ایجاد داده نمونه:

```bash
# استفاده از اسکریپت
./create-sample-event.sh

# یا دستی در Django shell
python manage.py shell
from events.models import Event, Venue
# ...
```

---

## 🔗 لینک‌های مرتبط

- [بازگشت به Features](../)
- [Tours System](../tours/)
- [Invoice System](../invoices/)
- [Cart System](../../development/)

---

## 🐛 مشکلات رایج

### رویداد نمایش داده نمیشود
- بررسی `is_active = True`
- بررسی تاریخ شروع و پایان
- بررسی موجودی بلیط

### خطای ظرفیت
- بررسی `max_capacity` در Performance
- بررسی `capacity` در TicketType

### مشکل قیمت‌گذاری
- بررسی TicketPricing
- بررسی تاریخ‌های اعتبار

---

**آخرین بروزرسانی:** 18 اکتبر 2025
