# تست دانلود فاکتور - مشکلات برطرف شده

## مشکلات شناسایی شده:

### 1. استفاده از `order.id` به جای `order.order_number`
**مشکل:** در صفحه لیست سفارشات از `order.id` (UUID) استفاده می‌شد
**راه حل:** تغییر به `order.order_number` (مثل ORDA3699B6E)

### 2. عدم ارسال Authorization Header
**مشکل:** خطای 401 Unauthorized به دلیل نبود توکن در header
**راه حل:** اضافه کردن Authorization header با Bearer token

### 3. عدم وجود endpoint برای invoice
**مشکل:** endpoint `/orders/{order_number}/invoice/` در backend وجود نداشت
**راه حل:** اضافه کردن `_get_invoice` method به `OrderActionView`

## تغییرات انجام شده:

### Backend (backend/orders/views.py):
1. اضافه کردن شرط `elif action == 'invoice'` در متد `get` کلاس `OrderActionView`
2. پیاده‌سازی متد `_get_invoice` برای تولید و ارسال PDF فاکتور

### Frontend (frontend/app/[locale]/orders/page.tsx):
1. تغییر `handleDownloadInvoice(order.id)` به `handleDownloadInvoice(order.order_number)`
2. اضافه کردن Authorization header با Bearer token
3. استفاده از `NEXT_PUBLIC_API_URL` برای URL کامل
4. بهبود error handling

## نحوه تست:

1. لاگین کنید: http://localhost:3000/en/login
2. به صفحه سفارشات بروید: http://localhost:3000/en/orders/
3. روی دکمه دانلود (Download) کلیک کنید
4. فاکتور باید به صورت PDF دانلود شود

## URL Endpoints:

- لیست سفارشات: `GET /api/v1/orders/`
- جزئیات سفارش: `GET /api/v1/orders/{order_number}/`
- دانلود فاکتور: `GET /api/v1/orders/{order_number}/invoice/`
- دانلود رسید: `GET /api/v1/orders/{order_number}/receipt/`

## نکات مهم:

- هر دو endpoint (invoice و receipt) حالا کار می‌کنند
- Authorization header الزامی است
- order_number باید به فرمت `ORD` + UUID باشد (مثل: ORDA3699B6E)
