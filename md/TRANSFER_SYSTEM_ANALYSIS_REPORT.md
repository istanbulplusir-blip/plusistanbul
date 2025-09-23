# تحلیل و مستندسازی کامل سیستم ترانسفر

## خلاصه اجرایی

این گزارش شامل تحلیل کامل ساختار فعلی سیستم ترانسفر در پلتفرم Peykan Tourism است که شامل بک‌اند (Django) و فرانت‌اند (Next.js) می‌باشد. هدف از این تحلیل، شناسایی نقاط ضعف، بهبود ساختار داده‌ای و اطمینان از عملکرد صحیح سیستم قیمت‌گذاری است.

## ۱. ساختار مدل‌های داده‌ای (Backend Models)

### ۱.۱ مدل‌های اصلی

#### TransferRoute
- **وظیفه**: تعریف مسیرهای ترانسفر با مبدا و مقصد
- **فیلدهای کلیدی**:
  - `origin`, `destination`: مبدا و مقصد
  - `distance_km`, `estimated_duration_minutes`: اطلاعات مسیر
  - `peak_hour_surcharge`, `off_peak_surcharge`, `midnight_surcharge`: سورشارژهای زمانی
  - `round_trip_discount_enabled`, `round_trip_discount_percentage`: تنظیمات رفت و برگشت
- **مشکلات شناسایی شده**:
  - عدم وجود `slug` field برای URLهای SEO-friendly
  - عدم وجود validation برای unique بودن ترکیب origin+destination

#### TransferRoutePricing
- **وظیفه**: قیمت‌گذاری برای هر ترکیب مسیر+نوع خودرو
- **فیلدهای کلیدی**:
  - `route`, `vehicle_type`: کلیدهای خارجی
  - `base_price`: قیمت پایه
  - `max_passengers`, `max_luggage`: ظرفیت
- **مشکلات شناسایی شده**:
  - عدم وجود validation برای اطمینان از وجود pricing برای همه vehicle types
  - عدم وجود field برای dynamic pricing

#### TransferVehicle
- **وظیفه**: تعریف انواع خودروها با اطلاعات عمومی
- **فیلدهای کلیدی**:
  - `vehicle_type`: نوع خودرو (sedan, suv, van, etc.)
  - `features`, `amenities`: امکانات و ویژگی‌ها
  - `images`: تصاویر خودرو
- **مشکلات شناسایی شده**:
  - عدم ارتباط مستقیم با pricing
  - عدم وجود validation برای unique بودن vehicle_type

#### TransferOption
- **وظیفه**: تعریف آپشن‌ها و خدمات اضافی
- **فیلدهای کلیدی**:
  - `available_pricings`: ManyToMany با TransferRoutePricing
  - `price_type`: fixed یا percentage
  - `price`, `price_percentage`: قیمت آپشن
- **مشکلات شناسایی شده**:
  - پیچیدگی در مدیریت available_pricings
  - عدم وجود validation برای consistency

### ۱.۲ مدل‌های پشتیبانی

#### TransferSchedule
- **وظیفه**: مدیریت زمان‌بندی و ظرفیت
- **مشکلات شناسایی شده**:
  - عدم استفاده موثر در سیستم فعلی

#### TransferBooking
- **وظیفه**: ثبت رزروهای ترانسفر
- **مشکلات شناسایی شده**:
  - عدم validation کامل برای capacity
  - عدم محاسبه خودکار قیمت نهایی

## ۲. ساختار APIها (Backend Views)

### ۲.۱ APIهای اصلی

#### TransferRouteViewSet
- **Endpoints**:
  - `GET /api/v1/transfers/routes/`: لیست مسیرهای محبوب
  - `GET /api/v1/transfers/routes/{id}/`: جزئیات مسیر
  - `GET /api/v1/transfers/routes/{id}/pricing/`: قیمت‌های مسیر
  - `GET /api/v1/transfers/routes/{id}/options/`: آپشن‌های مسیر
  - `GET /api/v1/transfers/routes/{id}/available_options/`: آپشن‌های معتبر برای vehicle
  - `POST /api/v1/transfers/routes/{id}/calculate_price/`: محاسبه قیمت

#### TransferRouteViewSet - Public APIs
- `GET /api/v1/transfers/routes/available_vehicles/`: خودروهای موجود
- `POST /api/v1/transfers/routes/calculate_price_public/`: محاسبه قیمت عمومی
- `GET /api/v1/transfers/routes/available_routes/`: مسیرهای موجود

### ۲.۲ مشکلات شناسایی شده در APIها

1. **عدم consistency در response format**
2. **عدم validation کامل برای input parameters**
3. **عدم error handling مناسب**
4. **عدم caching برای performance**

## ۳. ساختار فرانت‌اند (Frontend Components)

### ۳.۱ صفحات اصلی

#### `/transfers/page.tsx`
- **وظیفه**: نمایش مسیرهای محبوب و شروع رزرو
- **مشکلات شناسایی شده**:
  - عدم error handling مناسب
  - عدم loading states مناسب

#### `/transfers/custom/page.tsx`
- **وظیفه**: فرم رزرو سفارشی ترانسفر
- **مشکلات شناسایی شده**:
  - پیچیدگی بالا (1363 خط)
  - عدم separation of concerns
  - عدم validation سمت کلاینت
  - عدم error handling مناسب

### ۳.۲ سیستم Cart

#### useCart Hook
- **وظیفه**: مدیریت سبد خرید
- **مشکلات شناسایی شده**:
  - عدم sync کامل با backend
  - عدم validation برای transfer items
  - عدم error handling مناسب

## ۴. مشکلات کلیدی شناسایی شده

### ۴.۱ مشکلات ساختاری

1. **عدم consistency در naming conventions**
2. **عدم separation of concerns در frontend**
3. **عدم validation کامل در هر دو طرف**
4. **عدم error handling مناسب**

### ۴.۲ مشکلات عملکردی

1. **عدم caching مناسب**
2. **عدم optimization برای performance**
3. **عدم real-time updates**

### ۴.۳ مشکلات امنیتی

1. **عدم validation کامل برای input**
2. **عدم rate limiting**
3. **عدم proper authentication checks**

## ۵. پیشنهادات بهبود

### ۵.۱ بهبود مدل‌های داده‌ای

1. **اضافه کردن slug field به TransferRoute**
2. **بهبود validation rules**
3. **اضافه کردن indexes مناسب**
4. **بهبود relationship بین مدل‌ها**

### ۵.۲ بهبود APIها

1. **Standardization response format**
2. **بهبود error handling**
3. **اضافه کردن caching**
4. **بهبود validation**

### ۵.۳ بهبود فرانت‌اند

1. **Refactoring custom page به components کوچکتر**
2. **بهبود state management**
3. **اضافه کردن proper error handling**
4. **بهبود UX/UI**

### ۵.۴ بهبود سیستم قیمت‌گذاری

1. **Standardization فرمول محاسبه قیمت**
2. **بهبود validation برای pricing**
3. **اضافه کردن audit trail**
4. **بهبود performance**

## ۶. برنامه اجرایی

### فاز ۱: بهبود Backend (هفته ۱-۲)
1. بهبود مدل‌های داده‌ای
2. Standardization APIها
3. بهبود validation و error handling

### فاز ۲: بهبود Frontend (هفته ۳-۴)
1. Refactoring components
2. بهبود state management
3. بهبود UX/UI

### فاز ۳: تست و بهینه‌سازی (هفته ۵-۶)
1. Comprehensive testing
2. Performance optimization
3. Security audit

## ۷. نتیجه‌گیری

سیستم ترانسفر فعلی دارای ساختار نسبتاً کامل اما نیازمند بهبود در زمینه‌های مختلف است. تمرکز اصلی باید بر روی standardization، بهبود performance و امنیت باشد. 