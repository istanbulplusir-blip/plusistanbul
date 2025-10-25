# راهنمای مدیریت تور در Admin Panel

## ✅ تور با موفقیت ایجاد شد!

تور "کروز بسفر استانبول" با موفقیت در سیستم ایجاد شده و آماده استفاده است.

### 🔗 لینک‌های دسترسی

#### Admin Panel:
- **لیست تورها:** https://peykantravelistanbul.com/admin/tours/tour/
- **ویرایش تور:** https://peykantravelistanbul.com/admin/tours/tour/d087b619-c777-4ae1-b1d4-df4d5666cc07/change/
- **افزودن تور جدید:** https://peykantravelistanbul.com/admin/tours/tour/add/

#### مدیریت اجزای تور:
- **Variants:** https://peykantravelistanbul.com/admin/tours/tourvariant/
- **Schedules:** https://peykantravelistanbul.com/admin/tours/tourschedule/
- **Options:** https://peykantravelistanbul.com/admin/tours/touroption/
- **Itinerary:** https://peykantravelistanbul.com/admin/tours/touritinerary/
- **Reviews:** https://peykantravelistanbul.com/admin/tours/tourreview/
- **Categories:** https://peykantravelistanbul.com/admin/tours/tourcategory/

### 📝 نحوه ویرایش تور

#### 1. ورود به Admin Panel
```
URL: https://peykantravelistanbul.com/admin/
Username: [admin username]
Password: [admin password]
```

#### 2. رفتن به بخش Tours
- از منوی سمت چپ، روی **Tours** کلیک کنید
- سپس روی **Tours** کلیک کنید
- تور "Istanbul Bosphorus Cruise" را پیدا کنید

#### 3. ویرایش محتوای چندزبانه

در صفحه ویرایش تور، در بالای هر فیلد قابل ترجمه، تب‌های زبان را خواهید دید:

```
[فارسی] [English] [Türkçe]
```

**مراحل ویرایش:**

1. روی تب زبان مورد نظر کلیک کنید
2. محتوای آن زبان را ویرایش کنید
3. روی تب زبان دیگر کلیک کنید و محتوای آن را ویرایش کنید
4. در پایان صفحه، روی **Save** کلیک کنید

**فیلدهای قابل ترجمه:**
- ✅ Title (عنوان)
- ✅ Description (توضیحات کامل)
- ✅ Short Description (توضیحات کوتاه)
- ✅ Highlights (نکات برجسته)
- ✅ Rules (قوانین)
- ✅ Required Items (وسایل ضروری)

**فیلدهای غیرقابل ترجمه:**
- Price (قیمت)
- Duration (مدت زمان)
- City/Country (شهر/کشور)
- Dates (تاریخ‌ها)
- Capacity (ظرفیت)

### 🖼️ آپلود تصاویر

#### تصویر اصلی تور:
1. در صفحه ویرایش تور، به بخش **Image** بروید
2. روی **Choose File** کلیک کنید
3. تصویر را انتخاب کنید (توصیه: 1200x800 پیکسل)
4. **Save** کنید

#### تصاویر گالری:
1. به **Tour Gallery Images** بروید
2. روی **Add Tour Gallery Image** کلیک کنید
3. تور را انتخاب کنید
4. تصویر را آپلود کنید
5. Title و Description را وارد کنید
6. Order را تنظیم کنید (عدد کوچکتر = اولویت بالاتر)
7. **Save** کنید

**مشخصات تصاویر:**
- فرمت: JPG, PNG, WebP
- سایز توصیه شده: 1920x1080 پیکسل
- حداکثر حجم: 5MB
- نسبت تصویر: 16:9 (برای نمایش بهتر)

### 📅 مدیریت Schedules

#### افزودن Schedule جدید:
1. به **Tour Schedules** بروید
2. روی **Add Tour Schedule** کلیک کنید
3. فیلدها را پر کنید:
   - **Tour:** تور را انتخاب کنید
   - **Start Date:** تاریخ شروع
   - **End Date:** تاریخ پایان (معمولاً همان روز)
   - **Start Time:** ساعت شروع (مثلاً 10:00)
   - **End Time:** ساعت پایان (مثلاً 16:00)
   - **Is Available:** ✓ فعال
4. **Save** کنید

**نکته مهم:** بعد از ذخیره، ظرفیت‌های variant به صورت خودکار ایجاد می‌شوند.

### 💰 مدیریت Variants و قیمت‌ها

#### ویرایش Variant:
1. به **Tour Variants** بروید
2. Variant مورد نظر را انتخاب کنید
3. فیلدها را ویرایش کنید:
   - **Name:** نام variant (ECONOMY, STANDARD, PREMIUM, VIP)
   - **Description:** توضیحات
   - **Base Price:** قیمت پایه (به دلار)
   - **Capacity:** ظرفیت
   - **Services:** خدمات شامل شده (✓ یا ✗)
4. **Save** کنید

#### تنظیم قیمت بر اساس سن:
1. در صفحه ویرایش Variant، به بخش **Pricing** بروید
2. برای هر گروه سنی (Adult, Child, Infant):
   - **Age Group:** گروه سنی
   - **Base Price:** قیمت پایه
   - **Discount Percentage:** درصد تخفیف (اختیاری)
   - **Final Price:** قیمت نهایی (محاسبه خودکار)
3. **Save** کنید

### 🎯 مدیریت Options (گزینه‌های اضافی)

#### افزودن Option جدید:
1. به **Tour Options** بروید
2. روی **Add Tour Option** کلیک کنید
3. فیلدها را پر کنید:
   - **Tour:** تور را انتخاب کنید
   - **Name:** نام گزینه (مثلاً "Professional Photography")
   - **Description:** توضیحات
   - **Price:** قیمت اضافی
   - **Option Type:** نوع (equipment, food, service, etc.)
   - **Max Quantity:** حداکثر تعداد
   - **Is Available:** ✓ فعال
4. **Save** کنید

### 🗺️ مدیریت Itinerary (برنامه تور)

#### ویرایش Itinerary Item:
1. به **Tour Itineraries** بروید
2. Item مورد نظر را انتخاب کنید
3. محتوا را به 3 زبان ویرایش کنید:
   - **Title:** عنوان مرحله
   - **Description:** توضیحات
   - **Duration:** مدت زمان (دقیقه)
   - **Location:** مکان
   - **Order:** ترتیب نمایش
4. **Save** کنید

### 💬 مدیریت Reviews (نظرات)

#### تأیید/رد نظرات:
1. به **Tour Reviews** بروید
2. نظر مورد نظر را انتخاب کنید
3. **Status** را تغییر دهید:
   - **Pending:** در انتظار بررسی
   - **Approved:** تأیید شده
   - **Rejected:** رد شده
4. **Save** کنید

#### پاسخ به نظرات:
1. نظر را باز کنید
2. به بخش **Responses** بروید
3. پاسخ خود را بنویسید
4. **Save** کنید

### 🔧 نکات مهم

#### 1. ذخیره تغییرات
همیشه بعد از ویرایش، روی **Save** یا **Save and continue editing** کلیک کنید.

#### 2. ترجمه‌ها
- هر فیلد قابل ترجمه باید به هر 3 زبان پر شود
- اگر ترجمه‌ای خالی باشد، از زبان پیش‌فرض (فارسی) استفاده می‌شود

#### 3. تصاویر
- تصاویر با کیفیت بالا آپلود کنید
- از نسبت 16:9 استفاده کنید
- نام فایل را معنی‌دار انتخاب کنید

#### 4. Schedules
- همیشه ظرفیت را بررسی کنید
- تاریخ‌های گذشته را غیرفعال کنید
- برای روزهای خاص، قیمت adjustment تنظیم کنید

#### 5. SEO
- عنوان‌ها را واضح و جذاب بنویسید
- توضیحات کوتاه را برای نمایش در لیست‌ها بهینه کنید
- از کلمات کلیدی مناسب استفاده کنید

### 🆘 عیب‌یابی

#### مشکل: تغییرات در سایت نمایش داده نمی‌شوند
**راه‌حل:**
```bash
# Restart frontend
docker-compose -f docker-compose.production-secure.yml restart frontend

# پاک کردن cache مرورگر (Ctrl+Shift+R)
```

#### مشکل: خطای 500 در admin
**راه‌حل:**
```bash
# بررسی لاگ‌ها
docker-compose -f docker-compose.production-secure.yml logs backend

# Restart backend
docker-compose -f docker-compose.production-secure.yml restart backend
```

#### مشکل: تصاویر نمایش داده نمی‌شوند
**راه‌حل:**
```bash
# بررسی permissions
chmod -R 755 /home/djangouser/plusistanbul/backend/media

# Restart nginx
docker-compose -f docker-compose.production-secure.yml restart nginx
```

#### مشکل: ترجمه‌ها کار نمی‌کنند
**راه‌حل:**
1. مطمئن شوید که تمام تب‌های زبان را پر کرده‌اید
2. روی Save کلیک کنید
3. صفحه را Refresh کنید

### 📞 دستورات مفید

#### بررسی وضعیت تور:
```bash
cd /home/djangouser/plusistanbul
./test_admin_tour.sh
```

#### مشاهده لاگ‌ها:
```bash
docker-compose -f docker-compose.production-secure.yml logs -f backend
```

#### Restart سرویس‌ها:
```bash
docker-compose -f docker-compose.production-secure.yml restart backend
docker-compose -f docker-compose.production-secure.yml restart frontend
```

### ✅ چک‌لیست تکمیل تور

قبل از انتشار تور، این موارد را بررسی کنید:

- [ ] تصویر اصلی آپلود شده
- [ ] حداقل 5 تصویر در گالری
- [ ] محتوای هر 3 زبان کامل است
- [ ] حداقل 2 هفته schedule فعال
- [ ] تمام variants قیمت‌گذاری شده‌اند
- [ ] Options مفید اضافه شده‌اند
- [ ] Itinerary کامل است (حداقل 5 مرحله)
- [ ] Cancellation policies تنظیم شده‌اند
- [ ] تور در سایت قابل مشاهده است
- [ ] لینک‌ها کار می‌کنند
- [ ] تصاویر به درستی نمایش داده می‌شوند

---

## 🎉 موفق باشید!

تور شما آماده است. می‌توانید از Admin Panel تمام جزئیات را مدیریت کنید.

**لینک Admin:** https://peykantravelistanbul.com/admin/tours/tour/

**لینک تور در سایت:** https://peykantravelistanbul.com/tours/istanbul-bosphorus-cruise
