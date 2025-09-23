# راهنمای ادمین تور - Tour Admin Guide

## 📋 **معرفی**

ادمین تور در Peykan Tourism Platform از `django-parler` برای مدیریت چندزبانه استفاده می‌کند. این راهنما توضیح می‌دهد که چگونه از تمام ویژگی‌های ادمین استفاده کنید.

## 🌐 **مدیریت چندزبانه**

### **زبان‌های پشتیبانی شده:**

- **فارسی (fa)** - زبان پیش‌فرض
- **انگلیسی (en)** - زبان بین‌المللی
- **ترکی (tr)** - زبان محلی

### **فیلدهای قابل ترجمه:**

فیلدهای زیر در تب‌های زبان جداگانه مدیریت می‌شوند:

#### **Basic Information:**

- **Title** - عنوان تور
- **Description** - توضیح کامل تور
- **Short description** - توضیح کوتاه تور
- **Slug** - آدرس URL تور

#### **Content:**

- **Highlights** - نکات برجسته تور
- **Rules and regulations** - قوانین و مقررات
- **Required items** - وسایل مورد نیاز

## 📝 **نحوه استفاده از ادمین**

### **1. ایجاد تور جدید:**

1. روی "Add Tour" کلیک کنید
2. ابتدا فیلدهای غیر قابل ترجمه را پر کنید:

   - Category (دسته‌بندی)
   - City (شهر)
   - Country (کشور)
   - Image (تصویر)
   - Price (قیمت)
   - Duration (مدت زمان)
   - Timing (زمان‌بندی)
   - Capacity (ظرفیت)
   - Services (خدمات)

3. سپس به تب‌های زبان بروید:
   - **فارسی**: عنوان، توضیح، و سایر فیلدهای قابل ترجمه را به فارسی وارد کنید
   - **English**: همان اطلاعات را به انگلیسی وارد کنید
   - **Türkçe**: همان اطلاعات را به ترکی وارد کنید

### **2. ویرایش تور موجود:**

1. تور مورد نظر را انتخاب کنید
2. در هر تب زبان، فیلدهای مربوط به آن زبان را ویرایش کنید
3. فیلدهای Content (Highlights, Rules, Required Items) در هر تب زبان جداگانه مدیریت می‌شوند

## 🔧 **بخش‌های ادمین**

### **Basic Information:**

- **ID**: شناسه یکتا تور
- **Slug**: آدرس URL (خودکار از عنوان تولید می‌شود)

### **Category & Type:**

- **Category**: دسته‌بندی تور (اجباری)
- **Tour Type**: نوع تور (روزانه/شبانه)
- **Transport Type**: نوع حمل و نقل (زمینی/هوایی/دریایی)

### **Location:**

- **City**: شهر
- **Country**: کشور
- **Image**: تصویر اصلی تور

### **Pricing:**

- **Price**: قیمت پایه (USD)
- **Currency**: واحد پول

### **Timing:**

- **Duration Hours**: مدت زمان تور (ساعت)
- **Pickup Time**: زمان سرویس
- **Start Time**: زمان شروع
- **End Time**: زمان پایان

### **Capacity & Booking:**

- **Min Participants**: حداقل شرکت‌کنندگان
- **Max Participants**: حداکثر شرکت‌کنندگان
- **Booking Cutoff Hours**: مهلت رزرو (ساعت)

### **Cancellation Policy:**

- **Cancellation Hours**: ساعات لغو
- **Refund Percentage**: درصد بازپرداخت

### **Services Included:**

- **Includes Transfer**: شامل سرویس
- **Includes Guide**: شامل راهنما
- **Includes Meal**: شامل وعده غذایی
- **Includes Photographer**: شامل عکاس

### **Content:**

- **Highlights**: نکات برجسته (قابل ترجمه)
- **Rules**: قوانین و مقررات (قابل ترجمه)
- **Required Items**: وسایل مورد نیاز (قابل ترجمه)
- **Gallery**: گالری تصاویر

### **Status:**

- **Is Featured**: ویژه
- **Is Popular**: محبوب
- **Is Active**: فعال

## 🌐 **مدیریت زبان‌ها**

### **تب‌های زبان:**

1. **فارسی (fa)**: زبان پیش‌فرض
2. **English (en)**: زبان بین‌المللی
3. **Türkçe (tr)**: زبان محلی

### **فیلدهای قابل ترجمه در هر تب:**

- Title (عنوان)
- Description (توضیح)
- Short Description (توضیح کوتاه)
- Highlights (نکات برجسته)
- Rules (قوانین)
- Required Items (وسایل مورد نیاز)

## ⚠️ **نکات مهم**

1. **فیلدهای اجباری**: Category، City، Country، Price، Duration باید حتماً پر شوند
2. **ترجمه**: فیلدهای قابل ترجمه در تب‌های زبان جداگانه مدیریت می‌شوند
3. **تصاویر**: تصویر اصلی در بخش Location و گالری در بخش Content قرار دارد
4. **ظرفیت**: حداقل و حداکثر شرکت‌کنندگان باید منطقی باشند
5. **زمان‌بندی**: زمان پایان باید بعد از زمان شروع باشد

## 🔄 **عملیات ادمین**

### **Actions موجود:**

- **Initialize Schedule Capacities**: تنظیم ظرفیت‌های برنامه
- **Validate Tour Schedules**: بررسی برنامه‌های تور
- **Validate Tour Variants**: بررسی انواع تور

### **Inline Models:**

- **Tour Variants**: انواع تور
- **Tour Schedules**: برنامه‌های تور
- **Tour Itinerary**: مسیر تور
- **Tour Pricing**: قیمت‌گذاری
- **Tour Options**: گزینه‌های اضافی
- **Cancellation Policies**: سیاست‌های لغو

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
