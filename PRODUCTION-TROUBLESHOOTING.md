# 🚨 Production Troubleshooting Guide - Peykan Tourism Platform

## 🔍 مشکل اصلی: فایل تنظیمات next-intl وجود ندارد

### خطای مشاهده شده:

```
at g (.next/server/chunks/3843.js:3:197830)
at p (.next/server/chunks/200.js:1:57126) {
  digest: '4199872379'
}
```

### علت مشکل:

فایل‌های تنظیمات `next-intl` و ترجمه‌ها به درستی در سرور کپی نشده‌اند یا پیکربندی نادرست است.

## ✅ راه‌حل‌های سریع:

### 1. اجرای اسکریپت جامع رفع مشکل

```bash
# اجرای اسکریپت جامع
./fix-production-issues.sh
```

### 2. اجرای مراحل دستی

```bash
# بررسی فایل‌های ترجمه
./copy-translations.sh

# رفع مشکل next-intl
./fix-nextintl.sh

# Build و Deploy
docker-compose -f docker-compose.production-secure.yml build --no-cache
docker-compose -f docker-compose.production-secure.yml up -d
```

## 🔧 عیب‌یابی تفصیلی:

### مرحله 1: بررسی فایل‌های مورد نیاز

اطمینان حاصل کنید که فایل‌های زیر موجود هستند:

```
frontend/
├── i18n/
│   ├── config.js          # ✅ موجود
│   └── request.js         # ✅ موجود
├── messages/
│   ├── fa.json           # ✅ موجود (36,607 tokens)
│   ├── en.json           # ✅ موجود (34,905 tokens)
│   └── tr.json           # ✅ موجود (2,343 tokens)
├── middleware.ts         # ✅ موجود
└── next.config.js        # ✅ موجود
```

### مرحله 2: بررسی پیکربندی next-intl

#### فایل `frontend/i18n/config.js`:

```javascript
export const locales = ["fa", "en", "tr"];
export const defaultLocale = "fa";
```

#### فایل `frontend/i18n/request.js`:

```javascript
import { getRequestConfig } from "next-intl/server";
import { locales, defaultLocale } from "./config.js";

export default getRequestConfig(async ({ locale }) => {
  if (!locale || !locales.includes(locale)) {
    locale = defaultLocale;
  }

  let messages;
  try {
    messages = (await import(`../messages/${locale}.json`)).default;
  } catch (error) {
    console.error(`Failed to load messages for locale ${locale}:`, error);
    messages = (await import(`../messages/${defaultLocale}.json`)).default;
  }

  return {
    locale,
    messages,
    timeZone: "Asia/Tehran",
  };
});
```

#### فایل `frontend/middleware.ts`:

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

#### فایل `frontend/next.config.js`:

```javascript
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.js");

// ... other config

export default withNextIntl(nextConfig);
```

### مرحله 3: بررسی Docker Build

#### بررسی .dockerignore:

اطمینان حاصل کنید که فایل‌های ترجمه در `.dockerignore` شامل نشده‌اند:

```bash
# فایل‌های زیر نباید در .dockerignore باشند:
# messages/
# i18n/
# middleware.ts
# next.config.js
```

#### Build مجدد:

```bash
# Clean build
docker-compose -f docker-compose.production-secure.yml down
docker system prune -f

# Build with no cache
docker-compose -f docker-compose.production-secure.yml build --no-cache frontend

# Start services
docker-compose -f docker-compose.production-secure.yml up -d
```

### مرحله 4: بررسی Container

```bash
# ورود به container
docker-compose -f docker-compose.production-secure.yml exec frontend sh

# بررسی فایل‌ها
ls -la /app/i18n/
ls -la /app/messages/
ls -la /app/.next/

# بررسی build logs
cat /app/.next/build-manifest.json
```

### مرحله 5: بررسی Logs

```bash
# بررسی logs کامل
docker-compose -f docker-compose.production-secure.yml logs --tail=100 frontend

# بررسی build logs
docker-compose -f docker-compose.production-secure.yml logs frontend | grep -i "error\|warn\|fail"

# بررسی runtime logs
docker-compose -f docker-compose.production-secure.yml logs frontend | grep -i "next-intl\|i18n\|locale"
```

## 🚀 راه‌حل‌های جایگزین:

### 1. Rebuild کامل سیستم

```bash
# حذف کامل containers و images
docker-compose -f docker-compose.production-secure.yml down
docker system prune -a -f

# Build مجدد
docker-compose -f docker-compose.production-secure.yml build --no-cache
docker-compose -f docker-compose.production-secure.yml up -d
```

### 2. بررسی Environment Variables

```bash
# بررسی .env.production
cat backend/.env.production

# بررسی environment variables در container
docker-compose -f docker-compose.production-secure.yml exec frontend env | grep -i next
```

### 3. بررسی Network و Connectivity

```bash
# بررسی connectivity بین services
docker-compose -f docker-compose.production-secure.yml exec frontend ping backend
docker-compose -f docker-compose.production-secure.yml exec frontend curl -f http://backend:8000/api/health
```

### 4. بررسی File Permissions

```bash
# بررسی permissions
ls -la frontend/i18n/
ls -la frontend/messages/

# تنظیم permissions در صورت نیاز
chmod -R 644 frontend/messages/*.json
chmod -R 644 frontend/i18n/*.js
```

## 🔍 عیب‌یابی پیشرفته:

### 1. بررسی Next.js Build Process

```bash
cd frontend

# بررسی dependencies
npm list next-intl

# Test build locally
npm run build

# بررسی build output
ls -la .next/
ls -la .next/server/chunks/
```

### 2. بررسی Browser Console

1. باز کردن Developer Tools (F12)
2. بررسی Console tab برای خطاهای JavaScript
3. بررسی Network tab برای failed requests
4. بررسی Application tab برای localStorage/sessionStorage

### 3. بررسی Server-Side Rendering

```bash
# بررسی SSR logs
docker-compose -f docker-compose.production-secure.yml logs frontend | grep -i "ssr\|render\|hydrate"
```

## 📋 Checklist رفع مشکل:

- [ ] فایل‌های ترجمه موجود هستند (fa.json, en.json, tr.json)
- [ ] فایل‌های JSON معتبر هستند (jq validation)
- [ ] next-intl نصب شده است (npm list next-intl)
- [ ] تنظیمات i18n/config.js درست است
- [ ] تنظیمات i18n/request.js درست است
- [ ] middleware.ts درست پیکربندی شده است
- [ ] next.config.js شامل next-intl plugin است
- [ ] Docker build موفق است
- [ ] فایل‌ها در container کپی شده‌اند
- [ ] Environment variables درست هستند
- [ ] Network connectivity برقرار است
- [ ] Services در حال اجرا هستند
- [ ] Frontend در browser قابل دسترسی است

## 🆘 در صورت ادامه مشکل:

### 1. جمع‌آوری اطلاعات کامل

```bash
# جمع‌آوری logs
docker-compose -f docker-compose.production-secure.yml logs > production-logs.txt

# جمع‌آوری system info
docker system info > docker-info.txt
docker-compose -f docker-compose.production-secure.yml ps > services-status.txt

# جمع‌آوری file info
ls -la frontend/i18n/ > i18n-files.txt
ls -la frontend/messages/ > messages-files.txt
```

### 2. بررسی System Resources

```bash
# بررسی disk space
df -h

# بررسی memory usage
free -h

# بررسی Docker resources
docker system df
```

### 3. بررسی Network Issues

```bash
# بررسی ports
netstat -tulpn | grep -E ":(3000|8000|5432|6379)"

# بررسی firewall
sudo ufw status
```

## 📞 پشتیبانی:

در صورت ادامه مشکل، اطلاعات زیر را جمع‌آوری کنید:

1. **Logs کامل:**

   ```bash
   docker-compose -f docker-compose.production-secure.yml logs > full-logs.txt
   ```

2. **System Information:**

   ```bash
   uname -a > system-info.txt
   docker version >> system-info.txt
   docker-compose version >> system-info.txt
   ```

3. **File Structure:**

   ```bash
   find frontend -name "*.js" -o -name "*.json" -o -name "*.ts" | head -20 > file-structure.txt
   ```

4. **Build Output:**
   ```bash
   cd frontend && npm run build 2>&1 | tee build-output.txt
   ```

---

**نکته مهم:** این مشکل معمولاً به دلیل عدم کپی شدن فایل‌های ترجمه در Docker build یا پیکربندی نادرست next-intl رخ می‌دهد. با اجرای مراحل فوق باید مشکل حل شود.
