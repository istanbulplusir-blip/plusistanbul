# 📚 Peykan Tourism Platform - Documentation

> مستندات کامل پروژه Peykan Tourism  
> **آخرین بروزرسانی:** 18 اکتبر 2025

---

## 🗂️ ساختار مستندات

### 📦 Features (قابلیت‌ها)

#### 🖼️ [Image Optimization](./features/image-optimization/)
سیستم مدیریت و بهینه‌سازی تصاویر
- [README - شروع از اینجا](./features/image-optimization/IMAGE_OPTIMIZATION_README.md)
- [تحلیل کامل](./features/image-optimization/IMAGE_OPTIMIZATION_ANALYSIS.md)
- [خلاصه فارسی](./features/image-optimization/خلاصه_تحلیل_تصاویر.md)
- [نمودارها](./features/image-optimization/IMAGE_SYSTEM_DIAGRAM.md)
- [راهنمای تصمیم‌گیری](./features/image-optimization/DECISION_GUIDE.md)

#### 🎨 [Hero Slider](./features/hero-slider/)
سیستم اسلایدر صفحه اصلی با پشتیبانی ویدیو
- [تحلیل کامل](./features/hero-slider/HERO_SLIDER_ANALYSIS.md)
- [راهنمای فارسی](./features/hero-slider/HERO_SLIDER_GUIDE_FA.md)
- [تنظیمات پیش‌فرض](./features/hero-slider/HERO_SLIDER_DEFAULT_SETTINGS_GUIDE.md)
- [گزارش نهایی](./features/hero-slider/HERO_SLIDER_FINAL_REPORT.md)

#### 🎭 [Events System](./features/events/)
سیستم مدیریت رویدادها و بلیط‌فروشی
- [راهنمای سیستم](./features/events/README_EVENT_SYSTEM.md)
- [راه‌اندازی سریع](./features/events/QUICK_EVENT_SETUP.md)
- [راهنمای ایجاد رویداد](./features/events/EVENT_CREATION_GUIDE.md)
- [خلاصه فایل‌ها](./features/events/EVENT_FILES_SUMMARY.md)

#### 🗺️ [Tours System](./features/tours/)
سیستم مدیریت تورها
- [خلاصه کامل](./features/tours/COMPLETE_TOUR_SUMMARY.md)

#### 🧾 [Invoice System](./features/invoices/)
سیستم فاکتور و پرداخت
- [تحلیل سیستم](./features/invoices/INVOICE_SYSTEM_ANALYSIS.md)
- [سیستم چندزبانه](./features/invoices/MULTILINGUAL_INVOICE_SYSTEM.md)
- [سیستم یکپارچه](./features/invoices/UNIFIED_INVOICE_SYSTEM.md)
- [راهنمای تست](./features/invoices/INVOICE_TESTING_GUIDE.md)

#### 🎯 [Other Features](./features/)
- [Banner Setup](./features/BANNER_SETUP_GUIDE.md)
- [Smart RTL Detection](./features/SMART_RTL_DETECTION.md)

---

### 🚀 [Setup & Installation](./setup/)
راهنمای نصب و راه‌اندازی
- [Quick Start](./setup/QUICK_START.md)
- [راهنمای راه‌اندازی لوکال](./setup/راهنمای_راه_اندازی_لوکال.md)
- [Git Setup](./setup/GIT_SETUP_INSTRUCTIONS.md)
- [Git Push Instructions](./setup/GIT_PUSH_INSTRUCTIONS.md)

---

### 🔧 [Development](./development/)
راهنمای توسعه
- [Commands Cheatsheet](./development/COMMANDS_CHEATSHEET.md)
- [دستورات مهم](./development/دستورات_مهم.md)
- [Backend Updates](./development/BACKEND_UPDATES.md)
- [Development Environment Variables](./development/DEVELOPMENT_ENVIRONMENT_VARIABLES.md)
- [Implementation Summary](./development/IMPLEMENTATION_SUMMARY.md)
- [Shared Test Data](./development/SHARED_TEST_DATA_SUMMARY.md)

---

### 🌐 [Deployment](./deployment/)
راهنمای استقرار و Production
- [Deployment Checklist](./deployment/DEPLOYMENT_CHECKLIST.md)
- [Production Deployment Checklist](./deployment/PRODUCTION_DEPLOYMENT_CHECKLIST.md)
- [Production Ready Checklist](./deployment/PRODUCTION_READY_CHECKLIST.md)
- [Production Dev Setup](./deployment/PRODUCTION_DEV_SETUP.md)
- [Production Preparation Summary](./deployment/PRODUCTION_PREPARATION_SUMMARY.md)

---

## 🎯 شروع سریع

### برای توسعه‌دهندگان جدید:
1. 📖 [Quick Start Guide](./setup/QUICK_START.md)
2. 🔧 [Commands Cheatsheet](./development/COMMANDS_CHEATSHEET.md)
3. 🎨 [Hero Slider Guide](./features/hero-slider/HERO_SLIDER_GUIDE_FA.md)

### برای کار با قابلیت‌های خاص:
- **تصاویر:** [Image Optimization](./features/image-optimization/IMAGE_OPTIMIZATION_README.md)
- **رویدادها:** [Events System](./features/events/README_EVENT_SYSTEM.md)
- **فاکتور:** [Invoice System](./features/invoices/INVOICE_SYSTEM_ANALYSIS.md)

### برای استقرار:
1. 📋 [Production Checklist](./deployment/PRODUCTION_READY_CHECKLIST.md)
2. 🚀 [Deployment Guide](./deployment/DEPLOYMENT_CHECKLIST.md)

---

## 📊 ساختار پروژه

```
peykan-tourism/
├── backend/           # Django Backend
│   ├── agents/       # سیستم نمایندگی
│   ├── cart/         # سبد خرید
│   ├── car_rentals/  # اجاره خودرو
│   ├── core/         # هسته اصلی
│   ├── events/       # رویدادها
│   ├── orders/       # سفارشات
│   ├── payments/     # پرداخت
│   ├── shared/       # مشترک (Hero, Banner, etc.)
│   ├── tours/        # تورها
│   ├── transfers/    # ترانسفر
│   └── users/        # کاربران
│
├── frontend/         # Next.js 15 Frontend
│   ├── app/         # App Router
│   ├── components/  # کامپوننت‌ها
│   ├── lib/         # Utilities
│   └── public/      # Static files
│
├── docs/            # 📚 این پوشه!
│   ├── features/    # مستندات قابلیت‌ها
│   ├── setup/       # راهنمای نصب
│   ├── development/ # راهنمای توسعه
│   └── deployment/  # راهنمای استقرار
│
└── scripts/         # اسکریپت‌های کمکی
```

---

## 🔍 جستجوی سریع

### مشکلات رایج:
- **تصاویر لود نمیشوند:** [Image Optimization Guide](./features/image-optimization/IMAGE_OPTIMIZATION_README.md)
- **Hero Slider کار نمیکند:** [Hero Slider Fixes](./features/hero-slider/HERO_SLIDER_FIXES.md)
- **خطای CSRF:** استفاده از `fix-csrf-issue.sh`
- **مشکل Git:** [Git Setup Instructions](./setup/GIT_SETUP_INSTRUCTIONS.md)

### دستورات پرکاربرد:
```bash
# Development
npm run dev          # Frontend
python manage.py runserver  # Backend

# Testing
npm test            # Frontend tests
python manage.py test  # Backend tests

# Deployment
./deploy.sh         # Deploy to production
```

---

## 🤝 مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. Branch جدید بسازید
3. تغییرات را commit کنید
4. Pull Request ایجاد کنید

---

## 📞 پشتیبانی

- **Issues:** GitHub Issues
- **Email:** support@peykan-tourism.com
- **Docs:** این پوشه!

---

## 📝 یادداشت‌ها

- همه مستندات به صورت Markdown هستند
- فایل‌های فارسی با پسوند `_FA` یا نام فارسی مشخص شده‌اند
- برای بروزرسانی مستندات، PR ایجاد کنید

---

**آخرین بروزرسانی:** 18 اکتبر 2025  
**نسخه:** 1.0  
**وضعیت:** ✅ Active Development

