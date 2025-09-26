# 🔧 Next.js Internationalization (next-intl) Troubleshooting Guide

## 🚨 مشکل: فایل تنظیمات next-intl وجود ندارد

### علت مشکل:

خطای `digest: '4199872379'` در frontend نشان می‌دهد که فایل‌های تنظیمات next-intl به درستی در سرور کپی نشده‌اند یا پیکربندی نادرست است.

## ✅ راه‌حل‌های پیشنهادی:

### 1. بررسی فایل‌های مورد نیاز

اطمینان حاصل کنید که فایل‌های زیر موجود هستند:

```
frontend/
├── i18n/
│   ├── config.js          # تنظیمات زبان‌ها
│   └── request.js         # تنظیمات درخواست
├── messages/
│   ├── fa.json           # ترجمه‌های فارسی
│   ├── en.json           # ترجمه‌های انگلیسی
│   └── tr.json           # ترجمه‌های ترکی
├── middleware.ts         # میدل‌ویر next-intl
└── next.config.js        # تنظیمات Next.js
```

### 2. اجرای اسکریپت بررسی

```bash
# بررسی فایل‌های ترجمه
./copy-translations.sh

# رفع مشکل next-intl
./fix-nextintl.sh
```

### 3. بررسی Docker Build

```bash
# Build مجدد frontend
docker-compose -f docker-compose.production-secure.yml build frontend

# بررسی logs
docker-compose -f docker-compose.production-secure.yml logs frontend
```

### 4. بررسی فایل‌های ترجمه

اطمینان حاصل کنید که فایل‌های JSON معتبر هستند:

```bash
# بررسی JSON files
jq empty frontend/messages/fa.json
jq empty frontend/messages/en.json
jq empty frontend/messages/tr.json
```

### 5. بررسی تنظیمات next.config.js

فایل `frontend/next.config.js` باید شامل تنظیمات زیر باشد:

```javascript
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.js");

// ... other config

export default withNextIntl(nextConfig);
```

### 6. بررسی middleware.ts

فایل `frontend/middleware.ts` باید شامل تنظیمات زیر باشد:

```typescript
import createMiddleware from "next-intl/middleware";
import { locales, defaultLocale } from "./i18n/config";

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: "always",
});

export const config = {
  matcher: ["/((?!api|_next|_vercel|static|.*\\..*).*)"],
};
```

## 🔍 عیب‌یابی پیشرفته:

### 1. بررسی Docker Container

```bash
# ورود به container
docker-compose -f docker-compose.production-secure.yml exec frontend sh

# بررسی فایل‌ها در container
ls -la /app/i18n/
ls -la /app/messages/
ls -la /app/.next/
```

### 2. بررسی Build Logs

```bash
# بررسی logs کامل
docker-compose -f docker-compose.production-secure.yml logs --tail=100 frontend

# بررسی build process
docker-compose -f docker-compose.production-secure.yml build --no-cache frontend
```

### 3. بررسی Network Issues

```bash
# بررسی connectivity
docker-compose -f docker-compose.production-secure.yml exec frontend ping backend

# بررسی API endpoints
curl -f http://localhost:3000/api/health
```

## 🚀 راه‌حل‌های جایگزین:

### 1. Rebuild کامل

```bash
# حذف containers و images
docker-compose -f docker-compose.production-secure.yml down
docker system prune -f

# Build مجدد
docker-compose -f docker-compose.production-secure.yml build --no-cache
docker-compose -f docker-compose.production-secure.yml up -d
```

### 2. بررسی Environment Variables

اطمینان حاصل کنید که متغیرهای محیطی درست تنظیم شده‌اند:

```bash
# بررسی .env.production
cat backend/.env.production

# بررسی environment variables در container
docker-compose -f docker-compose.production-secure.yml exec frontend env
```

### 3. بررسی File Permissions

```bash
# بررسی permissions
ls -la frontend/i18n/
ls -la frontend/messages/

# تنظیم permissions در صورت نیاز
chmod -R 644 frontend/messages/*.json
chmod -R 644 frontend/i18n/*.js
```

## 📋 Checklist برای رفع مشکل:

- [ ] فایل‌های ترجمه موجود هستند
- [ ] فایل‌های JSON معتبر هستند
- [ ] next-intl نصب شده است
- [ ] تنظیمات next.config.js درست است
- [ ] middleware.ts درست پیکربندی شده است
- [ ] Docker build موفق است
- [ ] فایل‌ها در container کپی شده‌اند
- [ ] Environment variables درست هستند
- [ ] Network connectivity برقرار است

## 🆘 در صورت ادامه مشکل:

1. **بررسی کامل logs:**

   ```bash
   docker-compose -f docker-compose.production-secure.yml logs --tail=200
   ```

2. **بررسی system resources:**

   ```bash
   docker system df
   docker system events
   ```

3. **بررسی Next.js build locally:**

   ```bash
   cd frontend
   npm run build
   npm start
   ```

4. **بررسی browser console** برای خطاهای JavaScript

5. **بررسی network tab** در browser developer tools

---

**نکته مهم:** این مشکل معمولاً به دلیل عدم کپی شدن فایل‌های ترجمه در Docker build یا پیکربندی نادرست next-intl رخ می‌دهد. با اجرای مراحل فوق باید مشکل حل شود.
