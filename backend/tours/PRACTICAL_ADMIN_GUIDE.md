# راهنمای عملی ادمین تور - Practical Tour Admin Guide

## 🎯 **مشکل و راه حل**

### **مشکل:**

شما نمی‌توانید فیلدهای `title`, `description`, `short_description`, `highlights`, `rules`, `required_items` را در تب اصلی ادمین ببینید.

### **راه حل:**

این فیلدها **قابل ترجمه** هستند و در **تب‌های زبان** مدیریت می‌شوند.

## 📋 **مرحله به مرحله - ایجاد تور جدید**

### **مرحله 1: تب اصلی (Basic Information)**

1. روی "Add Tour" کلیک کنید
2. در تب اصلی، این فیلدها را پر کنید:

#### **Basic Information:**

- **Slug**: آدرس URL (خودکار تولید می‌شود)

#### **Category & Type:**

- **Category**: دسته‌بندی تور (اجباری)
- **Tour Type**: نوع تور (روزانه/شبانه)
- **Transport Type**: نوع حمل و نقل

#### **Location:**

- **City**: شهر
- **Country**: کشور
- **Image**: تصویر اصلی

#### **Pricing:**

- **Price**: قیمت پایه
- **Currency**: واحد پول

#### **Timing:**

- **Duration Hours**: مدت زمان
- **Pickup Time**: زمان سرویس
- **Start Time**: زمان شروع
- **End Time**: زمان پایان

#### **Capacity & Booking:**

- **Min Participants**: حداقل شرکت‌کنندگان
- **Max Participants**: حداکثر شرکت‌کنندگان
- **Booking Cutoff Hours**: مهلت رزرو

#### **Cancellation Policy:**

- **Cancellation Hours**: ساعات لغو
- **Refund Percentage**: درصد بازپرداخت

#### **Services Included:**

- **Includes Transfer**: شامل سرویس
- **Includes Guide**: شامل راهنما
- **Includes Meal**: شامل وعده غذایی
- **Includes Photographer**: شامل عکاس

#### **Content:**

- **Gallery**: گالری تصاویر

#### **Status:**

- **Is Featured**: ویژه
- **Is Popular**: محبوب
- **Is Active**: فعال

### **مرحله 2: تب فارسی (fa)**

1. روی تب "فارسی" کلیک کنید
2. این فیلدها را پر کنید:

#### **فیلدهای قابل ترجمه:**

- **Title**: عنوان تور به فارسی
- **Description**: توضیح کامل تور به فارسی
- **Short Description**: توضیح کوتاه تور به فارسی
- **Highlights**: نکات برجسته تور به فارسی
- **Rules**: قوانین و مقررات به فارسی
- **Required Items**: وسایل مورد نیاز به فارسی

### **مرحله 3: تب انگلیسی (en)**

1. روی تب "English" کلیک کنید
2. همان فیلدها را به انگلیسی وارد کنید:

#### **Translatable Fields:**

- **Title**: Tour title in English
- **Description**: Full tour description in English
- **Short Description**: Short tour description in English
- **Highlights**: Tour highlights in English
- **Rules**: Rules and regulations in English
- **Required Items**: Required items in English

### **مرحله 4: تب ترکی (tr)**

1. روی تب "Türkçe" کلیک کنید
2. همان فیلدها را به ترکی وارد کنید:

#### **Çevrilebilir Alanlar:**

- **Title**: Tur başlığı Türkçe
- **Description**: Tam tur açıklaması Türkçe
- **Short Description**: Kısa tur açıklaması Türkçe
- **Highlights**: Tur öne çıkan özellikleri Türkçe
- **Rules**: Kurallar ve düzenlemeler Türkçe
- **Required Items**: Gerekli eşyalar Türkçe

## 🔧 **ویرایش تور موجود**

### **مرحله 1: انتخاب تور**

1. در لیست تورها، تور مورد نظر را انتخاب کنید
2. روی "Change" کلیک کنید

### **مرحله 2: ویرایش فیلدهای غیر قابل ترجمه**

1. در تب اصلی، فیلدهای غیر قابل ترجمه را ویرایش کنید
2. تغییرات را ذخیره کنید

### **مرحله 3: ویرایش فیلدهای قابل ترجمه**

1. به تب زبان مورد نظر بروید
2. فیلدهای قابل ترجمه را ویرایش کنید
3. تغییرات را ذخیره کنید

## ⚠️ **نکات مهم**

### **1. فیلدهای اجباری:**

- **Category**: حتماً انتخاب کنید
- **City**: حتماً وارد کنید
- **Country**: حتماً وارد کنید
- **Price**: حتماً وارد کنید
- **Duration**: حتماً وارد کنید

### **2. فیلدهای قابل ترجمه:**

- در هر تب زبان جداگانه مدیریت می‌شوند
- حداقل یک زبان (فارسی) باید کامل باشد
- سایر زبان‌ها اختیاری هستند

### **3. تصاویر:**

- **Image**: تصویر اصلی در بخش Location
- **Gallery**: گالری تصاویر در بخش Content

### **4. ظرفیت:**

- **Min Participants**: حداقل شرکت‌کنندگان
- **Max Participants**: حداکثر شرکت‌کنندگان
- باید منطقی باشند

### **5. زمان‌بندی:**

- **End Time**: باید بعد از Start Time باشد
- **Pickup Time**: باید قبل از Start Time باشد

## 🔍 **عیب‌یابی**

### **مشکل 1: فیلدهای قابل ترجمه نمایش داده نمی‌شوند**

**راه حل:** به تب‌های زبان بروید

### **مشکل 2: خطای اعتبارسنجی**

**راه حل:** تمام فیلدهای اجباری را پر کنید

### **مشکل 3: تصاویر نمایش داده نمی‌شوند**

**راه حل:** مسیر MEDIA_URL را بررسی کنید

### **مشکل 4: ترجمه‌ها ذخیره نمی‌شوند**

**راه حل:** مطمئن شوید که django-parler نصب شده است

## 📊 **نمایش لیست**

### **ستون‌های نمایش:**

- Title (عنوان)
- Category (دسته‌بندی)
- Tour Type (نوع تور)
- Transport Type (نوع حمل و نقل)
- Duration Hours (مدت زمان)
- Price (قیمت)
- Total Capacity (ظرفیت کل)
- Next Schedule (برنامه بعدی)
- Is Featured (ویژه)
- Is Popular (محبوب)
- Is Active (فعال)
- Booking Count (تعداد رزرو)

### **فیلترها:**

- Category Filter
- Tour Type
- Transport Type
- Is Featured
- Is Popular
- Is Active
- Includes Transfer
- Includes Guide
- Includes Meal
- Created At

## 🎯 **بهترین شیوه‌ها**

1. **همیشه ابتدا فیلدهای غیر قابل ترجمه را پر کنید**
2. **سپس به ترتیب زبان‌ها را تکمیل کنید**
3. **از تصاویر با کیفیت مناسب استفاده کنید**
4. **قوانین و مقررات را واضح و کامل بنویسید**
5. **نکات برجسته را جذاب و مختصر نگه دارید**
6. **وسایل مورد نیاز را دقیق و کامل لیست کنید**
7. **قبل از ذخیره، تمام فیلدهای اجباری را بررسی کنید**

## 📞 **پشتیبانی**

اگر مشکلی دارید:

1. ابتدا این راهنما را مطالعه کنید
2. تنظیمات سیستم را بررسی کنید
3. با تیم توسعه تماس بگیرید

---

**آخرین به‌روزرسانی:** 2025-09-04
**نسخه:** 2.0.0
