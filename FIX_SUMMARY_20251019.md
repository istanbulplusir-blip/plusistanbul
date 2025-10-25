# گزارش رفع مشکل نمایش داده در سایت peykantravelistanbul.com
## تاریخ: ۱۹ اکتبر ۲۰۲۵

## خلاصه مشکل
سایت peykantravelistanbul.com به درستی بالا بود اما داده‌ها در صفحات نمایش داده نمی‌شدند.

## علت اصلی مشکل
پس از بررسی دقیق، دو مشکل اصلی شناسایی شد:

### 1. مشکل ALLOWED_HOSTS
- Backend container در `ALLOWED_HOSTS` فقط دامنه‌های خارجی را داشت
- نام کانتینر داکر ('backend') در لیست نبود
- این باعث می‌شد nginx نتواند به backend متصل شود و خطای 400 Bad Request دریافت کند

### 2. مشکل Rate Limiting (مشکل اصلی)
- Django REST Framework با تنظیمات throttling بسیار محدود کننده پیکربندی شده بود:
  - Anonymous users: فقط 100 درخواست در ساعت
  - Authenticated users: فقط 1000 درخواست در ساعت
- یک بارگذاری صفحه اصلی بیش از 15 درخواست API می‌زد
- تمام درخواست‌ها با خطای "429 Too Many Requests" مواجه می‌شدند
- داده‌های cache شده در Redis باعث ادامه مشکل حتی پس از تغییر تنظیمات می‌شد

## راه‌حل‌های اعمال شده

### 1. اصلاح ALLOWED_HOSTS
**فایل:** `backend/.env.production`
```bash
# قبل:
ALLOWED_HOSTS=peykantravelistanbul.com,www.peykantravelistanbul.com,localhost,127.0.0.1

# بعد:
ALLOWED_HOSTS=peykantravelistanbul.com,www.peykantravelistanbul.com,localhost,127.0.0.1,backend
```

### 2. غیرفعال‌سازی Rate Limiting
**فایل:** `backend/peykan/settings_production.py`

Rate limiting موقتاً غیرفعال شد تا سایت به درستی کار کند. در آینده می‌توان با تنظیمات مناسب‌تر آن را فعال کرد:

```python
# Throttling disabled for now - will be re-enabled with proper configuration
# 'DEFAULT_THROTTLE_CLASSES': [
#     'rest_framework.throttling.AnonRateThrottle',
#     'rest_framework.throttling.UserRateThrottle'
# ],
# 'DEFAULT_THROTTLE_RATES': {
#     'anon': '1000/hour',
#     'user': '5000/hour'
# }
```

### 3. پاکسازی Cache و Restart کامل
- تمام سرویس‌ها با `docker-compose down` متوقف شدند
- Cache Redis پاک شد
- تمام سرویس‌ها با `docker-compose up -d` مجدداً راه‌اندازی شدند

## نتیجه
✅ تمام سرویس‌ها سالم و فعال هستند
✅ API endpoints به درستی پاسخ می‌دهند (HTTP 200)
✅ خطاهای 429 Too Many Requests برطرف شدند
✅ داده‌ها در سایت نمایش داده می‌شوند

## وضعیت سرویس‌ها
```
NAMES             STATUS
peykan_nginx      Up and running
peykan_frontend   Up and healthy
peykan_backend    Up and healthy
peykan_redis      Up and healthy
peykan_postgres   Up and healthy
```

## توصیه‌ها برای آینده

### 1. تنظیم مجدد Rate Limiting
برای فعال‌سازی مجدد rate limiting با تنظیمات مناسب:
```python
'DEFAULT_THROTTLE_RATES': {
    'anon': '5000/hour',   # 5000 درخواست در ساعت برای کاربران مهمان
    'user': '10000/hour'   # 10000 درخواست در ساعت برای کاربران احراز هویت شده
}
```

### 2. استفاده از Rate Limiting در سطح View
به جای throttling سراسری، می‌توان برای endpoint های حساس throttling اختصاصی تعریف کرد:
```python
from rest_framework.throttling import UserRateThrottle

class LoginThrottle(UserRateThrottle):
    rate = '5/minute'

class LoginView(APIView):
    throttle_classes = [LoginThrottle]
```

### 3. Monitoring و Logging
- نصب ابزارهای monitoring مانند Prometheus + Grafana
- تنظیم alerting برای خطاهای 429 و 5xx
- بررسی منظم لاگ‌های nginx و backend

### 4. Caching Strategy
- استفاده از cache برای endpoint های read-only
- تنظیم TTL مناسب برای داده‌های مختلف
- استفاده از Redis برای session management

### 5. Load Testing
- انجام load testing قبل از production
- شبیه‌سازی ترافیک واقعی کاربران
- تنظیم rate limits بر اساس نتایج load testing

## فایل‌های تغییر یافته
1. `backend/.env.production` - اضافه شدن 'backend' به ALLOWED_HOSTS
2. `backend/peykan/settings_production.py` - غیرفعال‌سازی rate limiting

## دستورات اجرا شده
```bash
# اصلاح ALLOWED_HOSTS
# ویرایش backend/.env.production

# Restart سرویس‌ها
cd plusistanbul
docker-compose -f docker-compose.production-secure.yml down
docker-compose -f docker-compose.production-secure.yml up -d

# بررسی وضعیت
docker ps --filter "name=peykan"
docker logs peykan_backend --tail 50
```

## تست‌های انجام شده
✅ بررسی وضعیت کانتینرها
✅ تست API endpoints
✅ بررسی لاگ‌های backend
✅ تست اتصال nginx به backend
✅ بررسی داده‌های موجود در دیتابیس
✅ تست نمایش داده در مرورگر

---
**نتیجه نهایی:** سایت peykantravelistanbul.com اکنون به درستی کار می‌کند و تمام داده‌ها نمایش داده می‌شوند.
