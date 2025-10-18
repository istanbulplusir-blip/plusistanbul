# سیستم فاکتور با جزئیات کامل محصولات 📋

## ✅ مشکل برطرف شده

### قبل:
```
Product: ■■■■■■■■■
Qty: 5
Price: 200.00
Total: 860.00
```

### بعد:
```
1. Istanbul City Tour - STANDARD

• Type: STANDARD
• Booking Date: 2025-10-18
• Booking Time: 09:00
• Adult: 3 x 200.00 USD
• Child: 1 x 140.00 USD
• Infant: 1 (Free)
• Professional Photography: 1 x 40.00 USD
• Lunch Upgrade: 1 x 20.00 USD

Quantity: 5
Unit Price: 200.00 USD
Total: 860.00 USD
```

---

## 🎯 جزئیات نمایش داده شده

### برای تورها (Tours):
1. ✅ **نام محصول** - عنوان کامل تور
2. ✅ **نوع/واریانت** - مثل STANDARD, PREMIUM, VIP
3. ✅ **تاریخ رزرو** - Booking Date
4. ✅ **زمان رزرو** - Booking Time
5. ✅ **شرکت‌کنندگان:**
   - Adult (بزرگسال) - تعداد × قیمت
   - Child (کودک) - تعداد × قیمت (70% قیمت بزرگسال)
   - Infant (نوزاد) - تعداد (رایگان)
6. ✅ **گزینه‌های انتخابی** - مثل عکاسی، ناهار، راهنما
7. ✅ **درخواست‌های ویژه** - Special Requests
8. ✅ **خلاصه قیمت:**
   - تعداد کل
   - قیمت واحد
   - جمع کل

### برای انتقال (Transfers):
- تاریخ و زمان رفت
- تاریخ و زمان برگشت (اگر دوطرفه)
- مبدا و مقصد
- نوع وسیله نقلیه
- تعداد مسافران

### برای رویدادها (Events):
- تاریخ و زمان رویداد
- نوع بلیط
- بخش/سکشن
- شماره صندلی‌ها

---

## 📊 ساختار داده

### OrderItem Model:
```python
class OrderItem:
    # Basic Info
    product_title: str          # نام محصول
    product_type: str           # tour, event, transfer, car_rental
    variant_name: str           # نوع واریانت
    
    # Booking Info
    booking_date: date          # تاریخ رزرو
    booking_time: time          # زمان رزرو
    quantity: int               # تعداد کل
    
    # Pricing
    unit_price: Decimal         # قیمت واحد
    total_price: Decimal        # قیمت کل
    currency: str               # واحد پول
    
    # Detailed Data
    booking_data: dict = {
        'participants': {
            'adult': int,       # تعداد بزرگسال
            'child': int,       # تعداد کودک
            'infant': int       # تعداد نوزاد
        },
        'special_requests': str,
        'schedule_id': str,
        # ... more fields
    }
    
    # Options
    selected_options: list = [
        {
            'name': str,        # نام گزینه
            'quantity': int,    # تعداد
            'price': Decimal    # قیمت
        }
    ]
```

---

## 🔧 تغییرات انجام شده

### 1. متد `_create_items_table_invoice()` بازنویسی شد

**قبل:**
- فقط یک جدول ساده با 4 ستون
- بدون جزئیات

**بعد:**
- برای هر آیتم:
  1. هدر با نام محصول
  2. لیست جزئیات (نوع، تاریخ، زمان، شرکت‌کنندگان، گزینه‌ها)
  3. جدول خلاصه قیمت

### 2. پشتیبانی از RTL

- جزئیات به صورت خط به خط نمایش داده می‌شود
- از HTML tags استفاده نمی‌شود (مشکل RTL)
- فونت و تراز صحیح

### 3. ترجمه‌های جدید

اضافه شده به `invoice_translations.py`:
- `variant_type` - نوع
- `participants` - شرکت‌کنندگان
- `adult` - بزرگسال
- `child` - کودک
- `infant` - نوزاد
- `free` - رایگان
- `options` - گزینه‌ها

---

## 📝 مثال خروجی

### فاکتور انگلیسی:
```
📦 Items

1. Istanbul City Tour - STANDARD

• Type: STANDARD
• Booking Date: 2025-10-18
• Booking Time: 09:00
• Adult: 3 x 200.00 USD
• Child: 1 x 140.00 USD
• Infant: 1 (Free)
• Professional Photography: 1 x 40.00 USD
• Lunch Upgrade: 1 x 20.00 USD

┌─────────────┬──────────────┐
│ Quantity    │ 5            │
│ Unit Price  │ 200.00 USD   │
│ Total       │ 860.00 USD   │
└─────────────┴──────────────┘

2. Bosphorus Cruise - PREMIUM

• Type: PREMIUM
• Booking Date: 2025-10-19
• Booking Time: 14:00
• Adult: 2 x 150.00 USD

┌─────────────┬──────────────┐
│ Quantity    │ 2            │
│ Unit Price  │ 150.00 USD   │
│ Total       │ 300.00 USD   │
└─────────────┴──────────────┘
```

### فاکتور فارسی:
```
📦 آیتم

1. تور شهر استانبول - STANDARD

• نوع: STANDARD
• تاریخ رزرو: 2025-10-18
• زمان رزرو: 09:00
• بزرگسال: 3 x 200.00 USD
• کودک: 1 x 140.00 USD
• نوزاد: 1 (رایگان)
• عکاسی حرفه‌ای: 1 x 40.00 USD
• ارتقای ناهار: 1 x 20.00 USD

┌─────────────┬──────────────┐
│ تعداد       │ 5            │
│ قیمت واحد   │ 200.00 USD   │
│ جمع         │ 860.00 USD   │
└─────────────┴──────────────┘
```

---

## 🧪 تست

### 1. تست Backend:
```bash
python backend/test_invoice.py
```

فایل‌های تولید شده:
- `invoice_en.pdf` - با جزئیات کامل انگلیسی
- `invoice_fa.pdf` - با جزئیات کامل فارسی
- `invoice_ar.pdf` - با جزئیات کامل عربی

### 2. تست از مرورگر:
```
http://localhost:3000/fa/orders/
```
دکمه Download → فاکتور با جزئیات کامل

---

## 🎨 طراحی

### رنگ‌بندی:
- **هدر آیتم:** #2c3e50 (تیره)
- **جزئیات:** #7f8c8d (خاکستری)
- **جدول قیمت:** پس‌زمینه سبز روشن (#e8f6f3)

### فونت:
- **RTL:** Persian (Sahel/Vazirmatn)
- **LTR:** Helvetica
- **سایز:** 8-11pt

### فاصله‌گذاری:
- بین آیتم‌ها: 0.3cm
- بعد از جزئیات: 0.2cm
- بعد از جدول: 0.3cm

---

## 🔄 جریان داده

### 1. سبد خرید → سفارش:
```
Cart Item → Order Item
├─ product_title ✅
├─ variant_name ✅
├─ booking_date ✅
├─ booking_time ✅
├─ booking_data ✅
│  ├─ participants ✅
│  └─ special_requests ✅
└─ selected_options ✅
```

### 2. سفارش → فاکتور:
```
Order Item → Invoice Details
├─ Extract product info
├─ Extract booking info
├─ Extract participants
├─ Extract options
└─ Format for display
```

---

## 📈 بهبودهای آینده

### 1. تصاویر محصول:
```python
# اضافه کردن تصویر کوچک محصول
if item.product_image_url:
    img = Image(item.product_image_url, width=2*cm, height=2*cm)
    content.append(img)
```

### 2. QR Code:
```python
# QR code برای تأیید سفارش
from reportlab.graphics.barcode import qr
qr_code = qr.QrCodeWidget(order.order_number)
content.append(qr_code)
```

### 3. نقشه مسیر (برای انتقال):
```python
# نمایش نقشه مسیر
if item.product_type == 'transfer':
    # Add map image
    pass
```

---

## ✅ نتیجه

فاکتورها حالا شامل:
- ✅ جزئیات کامل محصولات
- ✅ اطلاعات شرکت‌کنندگان
- ✅ گزینه‌های انتخابی
- ✅ تاریخ و زمان دقیق
- ✅ قیمت‌گذاری شفاف
- ✅ پشتیبانی چندزبانه
- ✅ RTL Support
- ✅ طراحی حرفه‌ای

دیگر مربع‌های خالی (■) وجود ندارد! 🎉
