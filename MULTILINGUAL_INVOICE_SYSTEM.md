# سیستم فاکتور چندزبانه ✨

## تغییرات انجام شده

### ✅ پشتیبانی از 3 زبان
- 🇬🇧 **English** (en)
- 🇮🇷 **فارسی** (fa) 
- 🇸🇦 **العربية** (ar)

---

## فایل‌های جدید

### 1. `backend/orders/invoice_translations.py`
فایل ترجمه‌های چندزبانه شامل:
- عناوین فاکتور و رسید
- برچسب‌های جدول
- اطلاعات شرکت
- پیام‌های footer
- وضعیت‌های پرداخت

**توابع:**
```python
get_translation(lang: str, key: str, default: str = '') -> str
is_rtl_language(lang: str) -> bool
```

---

## تغییرات Backend

### 1. `pdf_service.py` - متدهای اصلی

#### `generate_invoice(order, language='en')`
```python
def generate_invoice(self, order, language='en'):
    """
    Generate PDF invoice with multi-language support.
    
    Args:
        order: Order instance
        language: 'en', 'fa', or 'ar'
    """
```

#### `generate_receipt(order, language='en')`
```python
def generate_receipt(self, order, language='en'):
    """
    Generate PDF receipt with multi-language support.
    
    Args:
        order: Order instance
        language: 'en', 'fa', or 'ar'
    """
```

### 2. متدهای کمکی جدید

#### `_create_invoice_header(order, language, is_rtl)`
- هدر فاکتور با پشتیبانی چندزبانه
- لوگو
- عنوان
- شماره سفارش و تاریخ

#### `_create_invoice_billing(order, language, is_rtl)`
- اطلاعات صورتحساب
- نام، ایمیل، تلفن، آدرس
- جدول با استایل مناسب

#### `_create_items_table_invoice(order, language, is_rtl)`
- جدول آیتم‌ها
- ستون‌ها: محصول، تعداد، قیمت واحد، جمع
- پشتیبانی RTL

#### `_create_invoice_totals(order, language, is_rtl)`
- جمع جزء، تخفیف، مالیات، کارمزد
- جمع کل
- فرمت اعداد

#### `_create_receipt_header(order, language, is_rtl)`
- هدر رسید (ساده‌تر از فاکتور)
- رنگ سبز برای تمایز

#### `_create_order_details(order, language, is_rtl)`
- اطلاعات مشتری
- وضعیت پرداخت

#### `_create_footer(order, language, is_rtl)`
- پیام تشکر
- اطلاعات تماس
- کپی‌رایت

---

## تغییرات Views

### `views.py` - دریافت زبان از request

```python
def _get_invoice(self, order, request):
    # Get language from query param or header
    language = request.GET.get('lang') or \
               request.headers.get('Accept-Language', 'en').split(',')[0]
    
    # Validate language
    if language not in ['en', 'fa', 'ar']:
        language = 'en'
    
    # Generate with language
    pdf_data = pdf_generator.generate_invoice(order, language=language)
```

همین منطق برای `_get_receipt` هم اعمال شد.

---

## تغییرات Frontend

### `orders/page.tsx`

#### دریافت locale
```typescript
const locale = typeof window !== 'undefined' 
  ? window.location.pathname.split('/')[1] 
  : 'en';
```

#### ارسال زبان به API
```typescript
const handleDownloadDocument = async (orderNumber: string, type: 'invoice' | 'receipt') => {
  const url = new URL(`${apiUrl}/orders/${orderNumber}/${type}/`);
  url.searchParams.append('lang', locale);  // ✅ ارسال زبان
  
  const response = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    headers
  });
  // ...
};
```

---

## نحوه استفاده

### 1. دانلود با زبان خاص

#### از URL:
```
GET /api/v1/orders/ORDA3699B6E/invoice/?lang=fa
GET /api/v1/orders/ORDA3699B6E/receipt/?lang=ar
GET /api/v1/orders/ORDA3699B6E/invoice/?lang=en
```

#### از Header:
```
Accept-Language: fa-IR
Accept-Language: ar-SA
Accept-Language: en-US
```

### 2. در فرانت‌اند

```typescript
// زبان به صورت خودکار از URL گرفته می‌شود
// /fa/orders/ → lang=fa
// /en/orders/ → lang=en
// /ar/orders/ → lang=ar

handleDownloadInvoice(orderNumber);  // ✅ زبان خودکار
```

---

## ویژگی‌های استاندارد

### ✅ RTL Support
- فارسی و عربی: راست به چپ
- انگلیسی: چپ به راست
- تراز متن صحیح
- ترتیب ستون‌های جدول

### ✅ Font Support
- RTL: Vazirmatn, Sahel (فونت‌های فارسی)
- LTR: Helvetica (فونت استاندارد)

### ✅ Layout
- A4 page size
- 2cm margins
- Professional spacing
- Color coding:
  - Invoice: Blue theme (#3498db)
  - Receipt: Green theme (#27ae60)

### ✅ Content
- Company logo
- Order information
- Customer details
- Items table with alternating rows
- Totals with highlighting
- Footer with contact info

---

## مثال‌های خروجی

### فاکتور انگلیسی
```
📄 Sales Invoice
Order Number: ORDA3699B6E
Date: 2025/01/15 - 14:30

👤 Billing Information
Customer Name: John Doe
Email: john@example.com
Phone: +1234567890

📦 Items
Product          | Qty | Unit Price | Total
Tour Package     | 2   | 100.00     | 200.00

Subtotal:        200.00 USD
Service Fee:     10.00 USD
Tax:             15.00 USD
Discount:        -5.00 USD
Total Amount:    220.00 USD

✨ Thank you for your business!
```

### فاکتور فارسی
```
📄 فاکتور فروش
شماره سفارش: ORDA3699B6E
تاریخ: 1403/10/25 - 14:30

👤 اطلاعات صورتحساب
نام مشتری: علی احمدی
ایمیل: ali@example.com
تلفن: 09123456789

📦 آیتم
محصول          | تعداد | قیمت واحد | جمع
پکیج تور       | 2     | 100.00    | 200.00

جمع جزء:         200.00 USD
کارمزد خدمات:    10.00 USD
مالیات:          15.00 USD
تخفیف:           -5.00 USD
مبلغ قابل پرداخت: 220.00 USD

✨ از خرید شما متشکریم!
```

---

## تست

### 1. تست زبان‌های مختلف
```bash
# فارسی
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=fa"

# انگلیسی
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=en"

# عربی
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=ar"
```

### 2. تست از مرورگر
1. برو به: `http://localhost:3000/fa/orders/`
2. روی دکمه Download کلیک کن
3. فاکتور فارسی دانلود می‌شود

4. برو به: `http://localhost:3000/en/orders/`
5. روی دکمه Download کلیک کن
6. فاکتور انگلیسی دانلود می‌شود

---

## مزایا

### ✅ چندزبانه
- پشتیبانی کامل از 3 زبان
- قابل توسعه برای زبان‌های بیشتر

### ✅ استاندارد
- طراحی حرفه‌ای
- فرمت A4
- رنگ‌بندی مناسب

### ✅ RTL Support
- راست به چپ برای فارسی و عربی
- چپ به راست برای انگلیسی

### ✅ یکپارچه
- یک سرویس برای همه
- کد تمیز و قابل نگهداری

### ✅ انعطاف‌پذیر
- زبان از URL یا Header
- Fallback به انگلیسی

---

## توسعه آینده

### اضافه کردن زبان جدید:

1. به `invoice_translations.py` اضافه کنید:
```python
INVOICE_TRANSLATIONS = {
    'de': {  # آلمانی
        'invoice_title': 'Rechnung',
        'customer_name': 'Kundenname',
        # ...
    }
}
```

2. در `views.py` به لیست زبان‌ها اضافه کنید:
```python
if language not in ['en', 'fa', 'ar', 'de']:
    language = 'en'
```

3. تمام! 🎉

---

## نتیجه

✅ سیستم فاکتور چندزبانه و استاندارد
✅ پشتیبانی از 3 زبان (en, fa, ar)
✅ RTL Support کامل
✅ طراحی حرفه‌ای
✅ یک صفحه‌ای و بهینه
✅ قابل توسعه
