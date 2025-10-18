# 🚀 راه‌اندازی سریع ایونت سه‌زبانه

## در ۳ مرحله ساده!

### ۱️⃣ اجرای اسکریپت

**ویندوز:**
```bash
create-sample-event.bat
```

**لینوکس/مک:**
```bash
./create-sample-event.sh
```

### ۲️⃣ اجرای سرور

```bash
cd backend
python manage.py runserver
```

### ۳️⃣ مشاهده نتیجه

**پنل ادمین:**
```
http://localhost:8000/admin/events/event/
```

**API:**
```
http://localhost:8000/api/events/istanbul-music-festival-2025/
```

---

## 🌍 تغییر زبان

### فارسی:
```bash
curl -H "Accept-Language: fa" http://localhost:8000/api/events/istanbul-music-festival-2025/
```

### انگلیسی:
```bash
curl -H "Accept-Language: en" http://localhost:8000/api/events/istanbul-music-festival-2025/
```

### عربی:
```bash
curl -H "Accept-Language: ar" http://localhost:8000/api/events/istanbul-music-festival-2025/
```

---

## 📊 محتویات ایونت نمونه

✅ **جشنواره موسیقی استانبول ۲۰۲۵**
- 🎤 هنرمندان: سامی یوسف، ماهر زین
- 🏛️ مکان: سالن بزرگ استانبول (۵۰۰۰ نفر)
- 🎫 ۴ نوع بلیط: VIP، عادی، اقتصادی، ویلچر
- 📅 ۷ اجرا در ۷ روز آینده
- 🪑 ۵۰۰۰ صندلی در ۴ بخش
- 🅿️ گزینه‌های اضافی: پارکینگ، بسته غذایی

---

## 🔗 لینک‌های مفید

- 📖 [راهنمای کامل](EVENT_CREATION_GUIDE.md)
- 📄 [مستندات تفصیلی](backend/events/SAMPLE_EVENT_README.md)
- 🗂️ [ساختار JSON](backend/events/sample_event_structure.json)

---

**تمام! حالا می‌تونی از API استفاده کنی 🎉**
