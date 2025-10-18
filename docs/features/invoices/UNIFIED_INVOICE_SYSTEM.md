# سیستم یکپارچه فاکتور و رسید ✅

## تغییرات انجام شده

### ✅ مشکل: دو سیستم جداگانه برای تولید PDF
**قبل:**
- `pdf_service.py` → فاکتور با فارسی و طراحی حرفه‌ای
- `receipt_service.py` → رسید ساده بدون فارسی

**بعد:**
- فقط `pdf_service.py` → هم فاکتور و هم رسید با فارسی و طراحی یکسان

---

## تغییرات Backend

### 1. آپدیت `views.py` - متد `_get_receipt`
```python
def _get_receipt(self, order, request):
    """Generate and return order receipt PDF using unified pdf_service."""
    try:
        from .pdf_service import pdf_generator
        # حالا از همان سرویس استفاده می‌کنیم
        pdf_data = pdf_generator.generate_receipt(order)
        
        from django.http import HttpResponse
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{order.order_number}.pdf"'
        return response
    except Exception as e:
        return Response(
            {'error': f'Failed to generate receipt: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### 2. متد `_get_invoice` قبلاً اضافه شده بود
```python
def _get_invoice(self, order, request):
    """Generate and return order invoice PDF."""
    try:
        from .pdf_service import pdf_generator
        pdf_data = pdf_generator.generate_invoice(order)
        
        from django.http import HttpResponse
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
        return response
    except Exception as e:
        return Response(
            {'error': f'Failed to generate invoice: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

---

## تغییرات Frontend

### 1. تابع یکپارچه `handleDownloadDocument`
```typescript
const handleDownloadDocument = async (orderNumber: string, type: 'invoice' | 'receipt') => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error(t('errorGettingInvoice'));
    }

    const headers: Record<string, string> = {
      'Authorization': `Bearer ${token}`,
    };

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const response = await fetch(`${apiUrl}/orders/${orderNumber}/${type}/`, {
      method: 'GET',
      credentials: 'include',
      headers
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || t('errorGettingInvoice'));
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `${type}-${orderNumber}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : t('errorDownloadInvoice');
    console.error(`Download ${type} error:`, err);
    alert(errorMessage);
  }
};
```

### 2. دو تابع کمکی
```typescript
const handleDownloadInvoice = (orderNumber: string) => handleDownloadDocument(orderNumber, 'invoice');
const handleDownloadReceipt = (orderNumber: string) => handleDownloadDocument(orderNumber, 'receipt');
```

---

## API Endpoints

### دو endpoint فعال:

1. **دانلود فاکتور (Invoice)**
   ```
   GET /api/v1/orders/{order_number}/invoice/
   ```
   - فاکتور کامل با اطلاعات صورتحساب
   - شامل: نام، ایمیل، تلفن، آدرس
   - مناسب برای امور مالیاتی

2. **دانلود رسید (Receipt)**
   ```
   GET /api/v1/orders/{order_number}/receipt/
   ```
   - رسید ساده‌تر
   - تأیید پرداخت
   - مناسب برای مشتری

---

## مزایای سیستم یکپارچه

### ✅ یکپارچگی
- یک سرویس واحد برای همه PDFها
- نگهداری آسان‌تر
- کد تمیزتر

### ✅ پشتیبانی فارسی
- هر دو نوع سند با فارسی
- RTL صحیح
- فونت‌های زیبا (Vazirmatn, Sahel)

### ✅ طراحی یکسان
- ظاهر حرفه‌ای
- رنگ‌بندی یکسان
- لوگو در همه اسناد

### ✅ انعطاف‌پذیری
- کاربر می‌تواند انتخاب کند
- فاکتور برای حسابداری
- رسید برای مشتری

---

## تفاوت Receipt و Invoice

| ویژگی | Receipt (رسید) | Invoice (فاکتور) |
|-------|----------------|------------------|
| هدف | تأیید پرداخت | سند مالیاتی |
| زمان صدور | بعد از پرداخت | قبل/بعد از پرداخت |
| جزئیات | ساده‌تر | کامل‌تر |
| اطلاعات صورتحساب | خیر | بله |
| آدرس | خیر | بله |
| مالیات | ساده | جزئیات کامل |

---

## نحوه استفاده

### در صفحه لیست سفارشات (`/orders/`)
```typescript
// دانلود فاکتور
<button onClick={() => handleDownloadInvoice(order.order_number)}>
  Download Invoice
</button>

// یا دانلود رسید
<button onClick={() => handleDownloadReceipt(order.order_number)}>
  Download Receipt
</button>
```

### در صفحه جزئیات سفارش (`/orders/ORDA3699B6E/`)
```typescript
// از orderService استفاده می‌کند
await orderService.downloadReceipt(order.order_number);
```

---

## فایل‌های قابل حذف (اختیاری)

اگر می‌خواهید کد را تمیزتر کنید:
- ❌ `backend/orders/receipt_service.py` - دیگر استفاده نمی‌شود

---

## تست

1. لاگین کنید
2. به `/orders/` بروید
3. روی دکمه Download کلیک کنید
4. فاکتور با فارسی و طراحی حرفه‌ای دانلود می‌شود
5. به `/orders/ORDA3699B6E/` بروید
6. روی دکمه Download Receipt کلیک کنید
7. رسید با همان کیفیت دانلود می‌شود

---

## نتیجه

✅ سیستم یکپارچه شد
✅ هر دو صفحه از یک سرویس استفاده می‌کنند
✅ پشتیبانی کامل از فارسی
✅ طراحی حرفه‌ای و یکسان
✅ دو گزینه: Invoice و Receipt
