<｜ Assistant ｜>بر اساس بررسی دقیق هر سه صفحه، لیست کاملی از داده‌های ماک و مواردی که ارتباطی با بک‌اند ندارند تهیه کردم:
�� لیست داده‌های ماک و موارد بدون ارتباط با بک‌اند
🏷️ صفحه Tour Detail (/tours/[slug]/page.tsx)
۱. داده‌های ماک (Mock Data):
Booking Steps: آرایه bookingSteps با مقادیر ثابت فارسی
Tour Variants: نمونه‌های ثابت برای انواع تور
Tour Schedules: نمونه‌های ثابت برای برنامه‌های زمانی
Tour Options: نمونه‌های ثابت برای آپشن‌ها
Tour Reviews: نمونه‌های ثابت برای نظرات
Tour Itinerary: نمونه‌های ثابت برای برنامه سفر
۲. محاسبات فرانت‌اند:
calculatePricing(): محاسبه قیمت بر اساس تعداد شرکت‌کنندگان و آپشن‌ها
isTourBookable(): بررسی قابلیت رزرو تور
convertToPricingBreakdown(): تبدیل قیمت تور به فرمت EventPricingBreakdown
۳. UI State Management:
expandedSections: مدیریت بخش‌های قابل گسترش
activeTab: مدیریت تب‌های مختلف (overview, itinerary, reviews, pricing)
isFavorite: وضعیت مورد علاقه
🎭 صفحه Event Detail (/events/[slug]/page.tsx)
۱. داده‌های ماک:
Booking Steps: آرایه bookingSteps با ترجمه‌های ثابت
Seat Status: وضعیت صندلی‌ها (available, selected, reserved, sold, blocked)
۲. محاسبات فرانت‌اند:
formatDate(): فرمت‌دهی تاریخ
formatTime(): فرمت‌دهی زمان
getTimeInfo(): تشخیص نوع زمان (peak hours, midnight hours, normal hours)
۳. UI State Management:
currentStep: مرحله فعلی رزرو
isFavorite: وضعیت مورد علاقه
showPricingDetails: نمایش جزئیات قیمت
🚗 صفحه Transfer Booking (/transfers/booking/page.tsx)
۱. داده‌های ماک:
STEPS Array: آرایه ثابت مراحل رزرو با متن‌های فارسی
Hero Image: تصویر ثابت /images/transfer-hero.jpg
Badge Labels: برچسب‌های ثابت (محبوب، تخفیف، هزینه اضافی)
۲. محاسبات فرانت‌اند:
convertToPricingBreakdown(): تبدیل قیمت ترانسفر به فرمت EventPricingBreakdown
formatPrice(): فرمت‌دهی قیمت
formatDate(): فرمت‌دهی تاریخ
۳. UI State Management:
isFavorite: وضعیت مورد علاقه
showPricingDetails: نمایش جزئیات قیمت
discountCode: کد تخفیف
🔧 کامپوننت‌های Transfer Booking
۱. RouteSelection:
Badge Rendering: نمایش برچسب‌های محبوب، تخفیف، هزینه اضافی
Route Features: ویژگی‌های مسیر (محبوب، تخفیف رفت و برگشت، هزینه اضافی)
۲. VehicleSelection:
Feature Rendering: نمایش ویژگی‌های خودرو
Amenity Rendering: نمایش امکانات خودرو
Vehicle Icon Mapping: نگاشت آیکون‌ها بر اساس نوع خودرو
۳. DateTimeSelection:
Time Category Detection: تشخیص نوع زمان (ساعت شلوغ، نیمه شب، عادی)
Minimum Date/Time Calculation: محاسبه حداقل تاریخ و زمان
۴. PassengerSelection:
Capacity Validation: اعتبارسنجی ظرفیت مسافر و بار
Vehicle Capacity Mapping: نگاشت ظرفیت خودرو
۵. OptionsSelection:
Option Toggle Logic: منطق انتخاب/لغو آپشن‌ها
Quantity Management: مدیریت تعداد آپشن‌ها
۶. ContactForm:
Auto-fill Logic: منطق پر کردن خودکار اطلاعات کاربر
Form Validation: اعتبارسنجی فرم
۷. BookingSummary:
Price Calculation Display: نمایش محاسبات قیمت
Route Feature Rendering: نمایش ویژگی‌های مسیر
Vehicle Detail Rendering: نمایش جزئیات خودرو
Time Info Rendering: نمایش اطلاعات زمانی
PriceSummary Component: کامپوننت خلاصه قیمت با محاسبات فرانت‌اند
⚠️ مشکلات شناسایی شده:
۱. تکرار PricingBreakdown:
سایدبار: PricingBreakdown کامپوننت
مرحله آخر: PriceSummary کامپوننت
نتیجه: نمایش دوگانه اطلاعات قیمت
۲. محاسبات فرانت‌اند:
محاسبه قیمت: در BookingSummary با calculatePrice()
تبدیل داده: convertToPricingBreakdown() برای تبدیل به فرمت EventPricingBreakdown
محاسبه تخفیف: محاسبه دستی تخفیف رفت و برگشت
۳. داده‌های ثابت:
تصاویر: مسیرهای ثابت برای تصاویر
متن‌ها: متن‌های فارسی ثابت
مراحل: آرایه‌های ثابت مراحل رزرو
🎯 توصیه‌های بهبود:
۱. یکسان‌سازی PricingBreakdown:
حذف PriceSummary از مرحله آخر
استفاده فقط از PricingBreakdown در سایدبار
۲. انتقال محاسبات به بک‌اند:
انتقال محاسبات قیمت به API
انتقال منطق تخفیف به بک‌اند
۳. پویا کردن داده‌ها:
دریافت مراحل رزرو از API
دریافت تصاویر و متن‌ها از CMS
پویا کردن برچسب‌ها و ویژگی‌ها
۴. بهینه‌سازی State Management:
کاهش state‌های محلی
استفاده از store مرکزی برای مدیریت وضعیت
این لیست نشان می‌دهد که بخش قابل توجهی از منطق کسب‌وکار در فرانت‌اند پیاده‌سازی شده و نیاز به انتقال به بک‌اند دارد.
