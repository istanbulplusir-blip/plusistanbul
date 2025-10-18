# راهنمای تست فاکتور چندزبانه

## ✅ تست انجام شده

### Backend Test
```bash
python backend/test_invoice.py
```

**نتیجه:**
- ✅ English invoice: 912KB
- ✅ Persian invoice: 936KB  
- ✅ Arabic invoice: 935KB
- ✅ Font loaded: Sahel-Bold

---

## 🧪 تست از مرورگر

### 1. تست فاکتور فارسی
```
URL: http://localhost:3000/fa/orders/
```
1. لاگین کنید
2. به صفحه سفارشات بروید
3. روی دکمه Download کلیک کنید
4. فایل `invoice-ORDA3699B6E.pdf` دانلود می‌شود
5. باز کنید و بررسی کنید:
   - ✅ متن فارسی خوانا باشد
   - ✅ راست به چپ باشد
   - ✅ فونت صحیح باشد

### 2. تست فاکتور انگلیسی
```
URL: http://localhost:3000/en/orders/
```
همان مراحل بالا را تکرار کنید.

### 3. تست فاکتور عربی
```
URL: http://localhost:3000/ar/orders/
```
همان مراحل بالا را تکرار کنید.

---

## 🔍 بررسی مشکلات احتمالی

### مشکل 1: متن نامفهوم (مربعی‌ها یا علامت سوال)
**علت:** فونت فارسی لود نشده
**راه حل:**
```bash
# بررسی وجود فونت
ls backend/static/fonts/sahel/
ls backend/static/fonts/vazir/

# اگر وجود ندارد، دانلود کنید
```

### مشکل 2: زبان تغییر نمی‌کند
**علت:** پارامتر `lang` ارسال نمی‌شود
**راه حل:** 
1. باز کردن Developer Tools (F12)
2. رفتن به Network tab
3. کلیک روی دکمه Download
4. بررسی URL:
   ```
   http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=fa
   ```
5. اگر `?lang=fa` وجود ندارد، مشکل از فرانت‌اند است

### مشکل 3: خطای 401 Unauthorized
**علت:** توکن ارسال نمی‌شود
**راه حل:**
```javascript
// بررسی localStorage
console.log(localStorage.getItem('access_token'));
```

---

## 📝 تست دستی API

### با curl:
```bash
# فارسی
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=fa" \
  --output invoice_fa.pdf

# انگلیسی
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=en" \
  --output invoice_en.pdf

# عربی
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/?lang=ar" \
  --output invoice_ar.pdf
```

### با Postman:
1. Method: GET
2. URL: `http://localhost:8000/api/v1/orders/ORDA3699B6E/invoice/`
3. Headers:
   - `Authorization: Bearer YOUR_TOKEN`
4. Query Params:
   - `lang: fa` (یا `en` یا `ar`)
5. Send
6. Save Response → Save to file

---

## ✅ چک‌لیست تست

### فاکتور فارسی (fa):
- [ ] متن فارسی خوانا است
- [ ] راست به چپ است
- [ ] فونت صحیح است
- [ ] اعداد فارسی نیست (انگلیسی باشد)
- [ ] ایموجی‌ها نمایش داده می‌شوند
- [ ] جداول صحیح هستند
- [ ] رنگ‌بندی درست است

### فاکتور انگلیسی (en):
- [ ] متن انگلیسی است
- [ ] چپ به راست است
- [ ] فونت Helvetica است
- [ ] اعداد انگلیسی هستند
- [ ] ایموجی‌ها نمایش داده می‌شوند
- [ ] جداول صحیح هستند
- [ ] رنگ‌بندی درست است

### فاکتور عربی (ar):
- [ ] متن عربی خوانا است
- [ ] راست به چپ است
- [ ] فونت صحیح است
- [ ] اعداد انگلیسی هستند
- [ ] ایموجی‌ها نمایش داده می‌شوند
- [ ] جداول صحیح هستند
- [ ] رنگ‌بندی درست است

---

## 🐛 Debug Mode

اگر مشکل دارید، این کد را در `views.py` اضافه کنید:

```python
def _get_invoice(self, order, request):
    try:
        from .pdf_service import pdf_generator

        # Debug: Print language detection
        lang_from_query = request.GET.get('lang')
        lang_from_header = request.headers.get('Accept-Language', 'en')
        print(f"🔍 Language from query: {lang_from_query}")
        print(f"🔍 Language from header: {lang_from_header}")
        
        language = lang_from_query or lang_from_header.split(',')[0].split('-')[0].lower()
        
        if language not in ['en', 'fa', 'ar']:
            language = 'en'
        
        print(f"✅ Final language: {language}")
        
        # ... rest of code
```

سپس در console سرور بررسی کنید که زبان درست تشخیص داده می‌شود.

---

## 📊 نتیجه انتظاری

### فاکتور فارسی باید شامل:
```
📄 فاکتور فروش
شماره سفارش: ORDA3699B6E
تاریخ: 2025/01/15 - 14:30

👤 اطلاعات صورتحساب
نام مشتری: علی احمدی
ایمیل: ali@example.com
...

✨ از خرید شما متشکریم!
```

### فاکتور انگلیسی باید شامل:
```
📄 Sales Invoice
Order Number: ORDA3699B6E
Date: 2025/01/15 - 14:30

👤 Billing Information
Customer Name: Ali Ahmadi
Email: ali@example.com
...

✨ Thank you for your business!
```

---

## 🎯 نکات مهم

1. **فونت فارسی:** اگر فونت لود نشد، از Helvetica استفاده می‌شود (متن نامفهوم می‌شود)
2. **RTL:** فقط برای `fa` و `ar` فعال است
3. **Fallback:** اگر زبان نامعتبر باشد، به `en` برمی‌گردد
4. **Cache:** اگر تغییری ندیدید، cache مرورگر را پاک کنید

---

## 🚀 مرحله بعد

اگر همه تست‌ها موفق بود:
1. ✅ فونت‌ها را در production هم قرار دهید
2. ✅ لوگوی شرکت را اضافه کنید
3. ✅ اطلاعات تماس را به‌روز کنید
4. ✅ ترجمه‌های بیشتر اضافه کنید
