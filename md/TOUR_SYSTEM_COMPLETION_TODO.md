# 🏛️ TOUR SYSTEM COMPLETION TODO

## 📊 **وضعیت کلی پروژه**

- **تاریخ شروع:** [تاریخ امروز]
- **هدف:** حذف 100% ماک دیتا و تکمیل سیستم تورها
- **اولویت:** بالاترین (محصول ساده‌ترین)

## 🎯 **فاز 1: تکمیل API Endpoints (هفته 1)**

### ✅ **بخش‌های تکمیل شده:**

- [x] Models (Tour, TourVariant, TourSchedule, TourOption, TourReview, TourItinerary)
- [x] Basic Views (TourListView, TourDetailView, TourSearchView)
- [x] Basic Serializers (TourListSerializer, TourDetailSerializer)
- [x] Basic URLs (tour_list, tour_detail, tour_search)

### 🔧 **بخش‌های نیازمند تکمیل:**

#### 1.1 **Tour Schedules API**

- [x] بررسی وجود TourScheduleListView ✅
- [x] بررسی وجود TourAvailableSchedulesView ✅
- [x] تکمیل/ایجاد endpoints مورد نیاز ✅
- [x] تست API endpoints ✅

#### 1.2 **Tour Variants API**

- [x] بررسی وجود TourVariantListView ✅
- [x] بررسی وجود TourVariantDetailView ✅
- [x] تکمیل/ایجاد endpoints مورد نیاز ✅
- [x] تست API endpoints ✅

#### 1.3 **Tour Options API**

- [x] بررسی وجود TourOptionListView ✅
- [x] بررسی وجود TourOptionDetailView ✅
- [x] تکمیل/ایجاد endpoints مورد نیاز ✅
- [x] تست API endpoints ✅

#### 1.4 **Tour Reviews API**

- [x] بررسی وجود TourReviewListView ✅
- [x] بررسی وجود TourReviewCreateView ✅
- [x] تکمیل/ایجاد endpoints مورد نیاز ✅
- [x] تست API endpoints ✅

#### 1.5 **Tour Itinerary API**

- [x] بررسی وجود TourItineraryListView ✅
- [x] تکمیل/ایجاد endpoints مورد نیاز ✅
- [x] تست API endpoints ✅

#### 1.6 **Tour Booking Steps API**

- [x] بررسی وجود TourBookingStepsView ✅
- [x] ایجاد endpoint برای مراحل رزرو ✅
- [x] تست API endpoint ✅

## 🎯 **فاز 2: حذف ماک دیتا از فرانت‌اند (هفته 2)**

### 🔧 **بخش‌های نیازمند حذف:**

#### 2.1 **حذف مراحل رزرو ثابت**

- [x] بررسی کد موجود در tours/[slug]/page.tsx ✅
- [x] حذف آرایه bookingSteps ثابت ✅
- [x] جایگزینی با API call ✅
- [x] تست عملکرد ✅

#### 2.2 **حذف نمونه‌های variants ثابت**

- [x] بررسی کد موجود ✅
- [x] حذف نمونه‌های ثابت ✅
- [x] جایگزینی با API call ✅
- [x] تست عملکرد ✅

#### 2.3 **حذف نمونه‌های schedules ثابت**

- [x] بررسی کد موجود ✅
- [x] حذف نمونه‌های ثابت ✅
- [x] جایگزینی با API call ✅
- [x] تست عملکرد ✅

#### 2.4 **حذف نمونه‌های options ثابت**

- [x] بررسی کد موجود ✅
- [x] حذف نمونه‌های ثابت ✅
- [x] جایگزینی با API call ✅
- [x] تست عملکرد ✅

#### 2.5 **حذف نمونه‌های reviews ثابت**

- [x] بررسی کد موجود ✅
- [x] حذف نمونه‌های ثابت ✅
- [x] جایگزینی با API call ✅
- [x] تست عملکرد ✅

#### 2.6 **حذف نمونه‌های itinerary ثابت**

- [x] بررسی کد موجود ✅
- [x] حذف نمونه‌های ثابت ✅
- [x] جایگزینی با API call ✅
- [x] تست عملکرد ✅

## 🎯 **فاز 3: تکمیل تست‌ها (هفته 3)**

### 🔧 **بخش‌های نیازمند تکمیل:**

#### 3.1 **تست API Endpoints**

- [ ] ایجاد tests/test_tour_api.py
- [ ] تست Tour List API
- [ ] تست Tour Detail API
- [ ] تست Tour Schedules API
- [ ] تست Tour Variants API
- [ ] تست Tour Options API
- [ ] تست Tour Reviews API
- [ ] تست Tour Itinerary API

#### 3.2 **تست فرانت‌اند**

- [ ] ایجاد tests/tour.test.tsx
- [ ] تست Tour List Page
- [ ] تست Tour Detail Page
- [ ] تست Tour Booking Flow

#### 3.3 **تست Integration**

- [ ] تست کامل فرآیند رزرو
- [ ] تست مدیریت خطا
- [ ] تست responsive design

## 🎯 **فاز 4: بهینه‌سازی و تست نهایی (هفته 4)**

### 🔧 **بخش‌های نیازمند تکمیل:**

#### 4.1 **بهینه‌سازی Performance**

- [ ] اضافه کردن caching
- [ ] بهینه‌سازی queries
- [ ] lazy loading

#### 4.2 **تست نهایی**

- [ ] تست کامل فرآیند رزرو
- [ ] تست مدیریت خطا
- [ ] تست responsive design
- [ ] تست در local browser

## 📝 **یادداشت‌های مهم**

### ⚠️ **نکات احتیاطی:**

- قبل از ایجاد هر ساختار جدید، از عدم وجود آن اطمینان حاصل کن
- از ایجاد ساختارهای مشابه خودداری کن
- اگر ساختار مشابه وجود دارد، از همان استفاده کن یا اصلاح کن

### 🔍 **بررسی‌های ضروری:**

- [x] بررسی کامل models موجود ✅
- [x] بررسی کامل views موجود ✅
- [x] بررسی کامل serializers موجود ✅
- [x] بررسی کامل URLs موجود ✅
- [ ] بررسی کامل tests موجود

### 📚 **منابع مورد نیاز:**

- فایل‌های موجود در backend/tours/
- فایل‌های موجود در frontend/app/[locale]/tours/
- فایل‌های موجود در frontend/components/tours/

## 🚀 **دستورات اجرایی**

### **1. تکمیل API Endpoints**

```bash
cd peykan-tourism1/backend
python manage.py makemigrations tours
python manage.py migrate
python manage.py test tours.tests
```

### **2. حذف ماک دیتا از فرانت‌اند**

```bash
cd peykan-tourism1/frontend
npm run test
npm run build
npm run start
```

### **3. تست کامل سیستم**

```bash
cd peykan-tourism1/backend
python comprehensive_tour_test.py

cd peykan-tourism1/frontend
npm run test:e2e
```

## 📊 **پیشرفت کلی**

- **فاز 1:** 100% (6/6 بخش) ✅ **تکمیل شده!**
- **فاز 2:** 100% (6/6 بخش) ✅ **تکمیل شده!**
- **فاز 3:** 0% (0/3 بخش)
- **فاز 4:** 0% (0/2 بخش)
- **کل پیشرفت:** 71% (12/17 بخش)

## 🎯 **هدف نهایی**

- **100% ماک دیتا حذف شود**
- **تمام API endpoints تکمیل شوند** ✅
- **سیستم قابل تست در local browser شود**
- **Performance بهینه شود**
- **تست‌های جامع اضافه شوند**

---

**آخرین به‌روزرسانی:** [تاریخ امروز]
**وضعیت:** فاز 1 تکمیل شده - در حال شروع فاز 2
**تخمین زمان:** 3 هفته باقی‌مانده
**اولویت:** بالاترین
