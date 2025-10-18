# 🧾 Invoice System

> سیستم جامع فاکتور و پرداخت با پشتیبانی چندزبانه

---

## 📚 مستندات موجود

### تحلیل‌ها
- **[INVOICE_SYSTEM_ANALYSIS.md](./INVOICE_SYSTEM_ANALYSIS.md)** - تحلیل کامل سیستم
- **[MULTILINGUAL_INVOICE_SYSTEM.md](./MULTILINGUAL_INVOICE_SYSTEM.md)** - سیستم چندزبانه
- **[UNIFIED_INVOICE_SYSTEM.md](./UNIFIED_INVOICE_SYSTEM.md)** - سیستم یکپارچه
- **[DETAILED_INVOICE_SYSTEM.md](./DETAILED_INVOICE_SYSTEM.md)** - جزئیات کامل

### راهنماها
- **[INVOICE_TESTING_GUIDE.md](./INVOICE_TESTING_GUIDE.md)** - راهنمای تست
- **[TEST_INVOICE_DOWNLOAD.md](./TEST_INVOICE_DOWNLOAD.md)** - تست دانلود فاکتور

---

## 🎯 قابلیت‌ها

### فاکتور
- ✅ ایجاد خودکار فاکتور
- ✅ شماره فاکتور یکتا
- ✅ اطلاعات کامل سفارش
- ✅ جزئیات محصولات

### چندزبانه
- ✅ فارسی (RTL)
- ✅ انگلیسی (LTR)
- ✅ ترکی (LTR)
- ✅ تشخیص خودکار زبان

### PDF Generation
- ✅ تولید PDF با کیفیت بالا
- ✅ فونت‌های فارسی
- ✅ لوگو و برندینگ
- ✅ QR Code

### ارسال
- ✅ ایمیل خودکار
- ✅ WhatsApp
- ✅ دانلود مستقیم

---

## 🚀 شروع سریع

### دریافت فاکتور

```bash
# دانلود PDF
GET /api/v1/orders/{order_number}/invoice/download/

# دریافت اطلاعات
GET /api/v1/orders/{order_number}/invoice/

# ارسال ایمیل
POST /api/v1/orders/{order_number}/invoice/send-email/
```

### تست

```bash
# استفاده از اسکریپت تست
python backend/orders/examples.py

# یا دستی
curl http://localhost:8000/api/v1/orders/ORD-123/invoice/download/
```

---

## 📊 ساختار فاکتور

### اطلاعات اصلی
- شماره فاکتور
- تاریخ صدور
- اطلاعات مشتری
- اطلاعات شرکت

### جزئیات سفارش
- لیست محصولات
- قیمت واحد
- تعداد
- جمع کل

### مالیات و تخفیف
- مالیات (اگر وجود داشته باشد)
- تخفیف
- مبلغ نهایی

### اطلاعات پرداخت
- روش پرداخت
- وضعیت پرداخت
- شماره تراکنش

---

## 🔧 تنظیمات

### Backend Configuration

```python
# backend/orders/pdf_service.py
class InvoicePDFService:
    - generate_invoice_pdf()
    - _add_header()
    - _add_customer_info()
    - _add_items_table()
    - _add_footer()
```

### Email Templates

```python
# backend/orders/email_templates.py
- get_invoice_email_template()
- Multilingual support
- HTML formatting
```

---

## 🌐 پشتیبانی چندزبانه

### فارسی (RTL)
```python
invoice_data = {
    'language': 'fa',
    'direction': 'rtl',
    'translations': {...}
}
```

### انگلیسی (LTR)
```python
invoice_data = {
    'language': 'en',
    'direction': 'ltr',
    'translations': {...}
}
```

### تشخیص خودکار
سیستم بر اساس زبان سفارش، خودکار زبان فاکتور را تشخیص میدهد.

---

## 📝 فرمت فاکتور

### PDF
- فرمت: A4
- فونت فارسی: Vazir
- فونت انگلیسی: Helvetica
- کیفیت: بالا

### محتوا
```
┌─────────────────────────────────┐
│ Logo + Company Info             │
├─────────────────────────────────┤
│ Invoice Number: INV-2024-001    │
│ Date: 2024-10-18                │
├─────────────────────────────────┤
│ Customer Information            │
├─────────────────────────────────┤
│ Items Table                     │
│ - Product 1                     │
│ - Product 2                     │
├─────────────────────────────────┤
│ Subtotal:    $100               │
│ Tax:         $10                │
│ Discount:    -$5                │
│ Total:       $105               │
├─────────────────────────────────┤
│ Payment Info                    │
│ QR Code                         │
└─────────────────────────────────┘
```

---

## 🔗 لینک‌های مرتبط

- [بازگشت به Features](../)
- [Orders System](../../development/)
- [Payment System](../../development/)
- [Email System](../../development/)

---

## 🐛 مشکلات رایج

### فاکتور تولید نمیشود
- بررسی وجود سفارش
- بررسی وضعیت سفارش
- بررسی نصب ReportLab

### فونت فارسی نمایش داده نمیشود
- بررسی نصب فونت Vazir
- بررسی مسیر فونت در settings

### ایمیل ارسال نمیشود
- بررسی تنظیمات SMTP
- بررسی ایمیل مشتری
- بررسی لاگ‌ها

---

## 📦 Dependencies

```bash
# Python packages
reportlab>=3.6.0
pillow>=9.0.0
qrcode>=7.3.1

# Fonts
vazir-font
```

---

**آخرین بروزرسانی:** 18 اکتبر 2025
