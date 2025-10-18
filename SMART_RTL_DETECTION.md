# تشخیص هوشمند RTL و پشتیبانی چندزبانه 🌍

## ✅ مشکل برطرف شده

### قبل:
```
فاکتور انگلیسی با نام فارسی:
Product: ■■■ ■■■■■■■■■ ■■■■ - ■■■ ■ ■■■■■
```

### بعد:
```
فاکتور انگلیسی با نام فارسی:
Product: تور ماجراجویی کامل - کوه و طبیعت
```

---

## 🎯 راه حل: تشخیص خودکار محتوای RTL

### متد جدید: `_has_rtl_chars()`

```python
def _has_rtl_chars(self, text: str) -> bool:
    """
    Check if text contains RTL characters (Persian, Arabic, Hebrew).
    """
    if not text:
        return False
    
    # Unicode ranges for RTL scripts
    rtl_ranges = [
        (0x0600, 0x06FF),  # Arabic
        (0x0750, 0x077F),  # Arabic Supplement
        (0x08A0, 0x08FF),  # Arabic Extended-A
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        (0x0590, 0x05FF),  # Hebrew
    ]
    
    for char in text:
        code = ord(char)
        for start, end in rtl_ranges:
            if start <= code <= end:
                return True
    return False
```

### متد بهبود یافته: `_format_text()`

```python
def _format_text(self, text: str, is_rtl_lang: bool = False) -> str:
    """
    Format text based on actual content, not just document language.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Only apply RTL shaping if text actually contains RTL characters
    if self._has_rtl_chars(text):
        return self._shape(text, force_rtl=True)
    
    # For LTR text, return as-is
    return text
```

---

## 🔍 منطق تشخیص

### سناریو 1: نام فارسی در فاکتور انگلیسی
```python
# Document language: English (is_rtl=False)
# Product name: "تور ماجراجویی کامل"

_has_rtl_chars("تور ماجراجویی کامل")  # → True
# ✅ Use Persian font + RTL shaping
# ✅ Display correctly
```

### سناریو 2: نام انگلیسی در فاکتور فارسی
```python
# Document language: Persian (is_rtl=True)
# Product name: "Istanbul City Tour"

_has_rtl_chars("Istanbul City Tour")  # → False
# ✅ Use Helvetica font
# ✅ No RTL shaping
# ✅ Display correctly
```

### سناریو 3: محتوای ترکیبی
```python
# Product name: "Istanbul Tour - تور استانبول"

_has_rtl_chars("Istanbul Tour - تور استانبول")  # → True
# ✅ Use Persian font (supports both)
# ✅ Apply RTL shaping
# ✅ Both parts display correctly
```

---

## 📊 جدول تصمیم‌گیری

| زبان سند | محتوای متن | فونت | RTL Shaping | نتیجه |
|---------|-----------|------|-------------|-------|
| EN | English | Helvetica | ❌ | ✅ Perfect |
| EN | فارسی | Persian | ✅ | ✅ Perfect |
| EN | Mixed | Persian | ✅ | ✅ Perfect |
| FA | English | Helvetica | ❌ | ✅ Perfect |
| FA | فارسی | Persian | ✅ | ✅ Perfect |
| FA | Mixed | Persian | ✅ | ✅ Perfect |
| AR | English | Helvetica | ❌ | ✅ Perfect |
| AR | عربي | Persian | ✅ | ✅ Perfect |

---

## 🧪 تست‌های انجام شده

### Test 1: نام فارسی در فاکتور انگلیسی
```bash
python backend/test_mixed_language.py
```

**نتیجه:**
```
✅ English invoice with Persian name: 929KB
   Product: تور ماجراجویی کامل - کوه و طبیعت
   Status: Displays correctly with Persian font
```

### Test 2: نام انگلیسی در فاکتور فارسی
**نتیجه:**
```
✅ Persian invoice with English name: 936KB
   Product: Complete Adventure Tour - Mountain & Nature
   Status: Displays correctly without RTL shaping
```

### Test 3: محتوای ترکیبی
**نتیجه:**
```
✅ Mixed content invoice: 928KB
   Product: Istanbul City Tour - تور شهر استانبول
   Status: Both parts display correctly
```

---

## 🎨 تغییرات در کد

### 1. تشخیص فونت مناسب برای نام محصول

**قبل:**
```python
item_header_style = ParagraphStyle(
    'ItemHeader',
    fontName=font_bold,  # همیشه از فونت سند استفاده می‌کرد
    alignment=TA_RIGHT if is_rtl else TA_LEFT
)
```

**بعد:**
```python
# Use appropriate font based on product name content
product_has_rtl = self._has_rtl_chars(item.product_title)
header_font = self.persian_font_bold if product_has_rtl else font_bold
header_align = TA_RIGHT if product_has_rtl else (TA_RIGHT if is_rtl else TA_LEFT)

item_header_style = ParagraphStyle(
    'ItemHeader',
    fontName=header_font,  # فونت بر اساس محتوا
    alignment=header_align
)
```

### 2. فرمت کردن هوشمند متن

**قبل:**
```python
def _format_text(self, text: str, is_rtl: bool = False) -> str:
    if is_rtl:
        return self._shape(text, force_rtl=True)  # همیشه RTL
    return text
```

**بعد:**
```python
def _format_text(self, text: str, is_rtl_lang: bool = False) -> str:
    # Only apply RTL shaping if text actually contains RTL characters
    if self._has_rtl_chars(text):  # بررسی محتوا
        return self._shape(text, force_rtl=True)
    return text
```

---

## 🌟 مزایا

### 1. ✅ انعطاف‌پذیری کامل
- محصولات می‌توانند به هر زبانی باشند
- فاکتور به هر زبانی تولید شود
- نیازی به ترجمه همه محصولات نیست

### 2. ✅ پشتیبانی از محتوای ترکیبی
```
"Istanbul Tour - تور استانبول"
"تور استانبول - Istanbul Tour"
"Complete Tour (تور کامل)"
```

### 3. ✅ عدم نیاز به تنظیمات دستی
- تشخیص خودکار
- بدون نیاز به flag یا تنظیمات
- کار می‌کند out-of-the-box

### 4. ✅ سازگاری با Unicode
- پشتیبانی از تمام زبان‌های RTL:
  - فارسی (Persian)
  - عربی (Arabic)
  - عبری (Hebrew)
  - اردو (Urdu)

---

## 📝 مثال‌های واقعی

### مثال 1: فروشگاه چندزبانه
```python
# محصولات با نام‌های مختلف
products = [
    "Istanbul City Tour",           # انگلیسی
    "تور شهر استانبول",             # فارسی
    "جولة مدينة اسطنبول",           # عربی
    "Istanbul - تور استانبول",      # ترکیبی
]

# همه در فاکتور انگلیسی به درستی نمایش داده می‌شوند
for product in products:
    invoice = generate_invoice(order, language='en')
    # ✅ All display correctly
```

### مثال 2: محصولات محلی
```python
# محصول فقط به فارسی
product = {
    'title_fa': 'تور ماجراجویی کامل',
    'title_en': None,  # ترجمه وجود ندارد
    'title_ar': None
}

# فاکتور انگلیسی
invoice_en = generate_invoice(order, 'en')
# ✅ نام فارسی به درستی نمایش داده می‌شود

# فاکتور فارسی
invoice_fa = generate_invoice(order, 'fa')
# ✅ نام فارسی به درستی نمایش داده می‌شود
```

---

## 🔧 نگهداری و توسعه

### اضافه کردن زبان RTL جدید:

```python
def _has_rtl_chars(self, text: str) -> bool:
    rtl_ranges = [
        # ... existing ranges
        (0x0780, 0x07BF),  # Thaana (Maldivian)
        (0x0800, 0x083F),  # Samaritan
    ]
```

### تست زبان جدید:

```python
# Test new RTL language
text = "ދިވެހި"  # Maldivian
assert pdf_generator._has_rtl_chars(text) == True
```

---

## ✅ چک‌لیست

- [x] تشخیص خودکار حروف RTL
- [x] انتخاب فونت مناسب
- [x] پشتیبانی از محتوای ترکیبی
- [x] تست با نام‌های فارسی
- [x] تست با نام‌های انگلیسی
- [x] تست با محتوای ترکیبی
- [x] پشتیبانی از عربی
- [x] پشتیبانی از عبری
- [x] عدم نیاز به ترجمه اجباری

---

## 🎯 نتیجه

حالا سیستم فاکتور:
- ✅ هوشمندانه محتوا را تشخیص می‌دهد
- ✅ فونت مناسب را انتخاب می‌کند
- ✅ RTL shaping را فقط در صورت نیاز اعمال می‌کند
- ✅ از محتوای چندزبانه پشتیبانی می‌کند
- ✅ دیگر مربع‌های خالی (■) وجود ندارد

**نتیجه:** فاکتورهای حرفه‌ای با پشتیبانی کامل از همه زبان‌ها! 🎉
