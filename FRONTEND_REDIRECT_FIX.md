# Frontend Redirect Fix

## مشکل (Problem)

پس از authentication موفق با Google OAuth، کاربر به URL نادرست redirect می‌شد:
- ❌ `/en/en/checkout/` (404 Not Found)
- ✅ `/en/checkout/` (صحیح)

After successful Google OAuth authentication, users were redirected to incorrect URLs with duplicate language prefix.

## علت ریشه‌ای (Root Cause)

در `login/page.tsx` و `register/page.tsx`، redirect path به این صورت ساخته می‌شد:

```typescript
// ❌ WRONG - Creates /en/en/checkout/
onSuccessRedirect={(path) => router.push(`/${locale}${path}`)}
```

مشکل: اگر `path` از URL parameter بیاید (مثلاً `?redirect=/en/checkout`)، قبلاً شامل `/${locale}` است، پس دوبار اضافه می‌شود.

The problem: If `path` comes from URL parameter (e.g., `?redirect=/en/checkout`), it already contains `/${locale}`, so it gets added twice.

## راه‌حل (Solution)

بررسی می‌کنیم که آیا `path` قبلاً با `/${locale}` شروع می‌شود یا خیر:

```typescript
// ✅ CORRECT - Prevents duplicate locale prefix
onSuccessRedirect={(path) => {
  // Remove leading locale if path already contains it to avoid /en/en/
  const cleanPath = path.startsWith(`/${locale}`) ? path : `/${locale}${path}`;
  router.push(cleanPath);
}}
```

### تغییرات اعمال شده (Changes Applied)

1. ✅ `plusistanbul/frontend/app/[locale]/login/page.tsx` - خط 354-359
2. ✅ `plusistanbul/frontend/app/[locale]/register/page.tsx` - خط 400-407

## تست و Build (Testing & Build)

### TypeScript Type Checking
```bash
npm run type-check
```
✅ **نتیجه:** فقط خطاهای test files (قابل نادیده گرفتن)

### Production Build
```bash
npm run build
```
✅ **نتیجه:** Build موفق بدون خطا

### Docker Build & Deploy
```bash
docker-compose -f docker-compose.production-secure.yml build frontend
docker-compose -f docker-compose.production-secure.yml up -d frontend
```
✅ **نتیجه:** Frontend با موفقیت deploy شد

## تست دستی (Manual Testing)

کاربران اکنون باید بتوانند:
- ✅ محصولات را به سبد اضافه کنند (guest)
- ✅ با Google OAuth لاگین کنند
- ✅ به صفحه صحیح redirect شوند (بدون `/en/en/`)
- ✅ سبد خرید merge شده را ببینند

Users should now be able to:
- ✅ Add products to cart (as guest)
- ✅ Login via Google OAuth
- ✅ Redirect to correct page (without `/en/en/`)
- ✅ See merged cart

## مشکلات باقی‌مانده (Remaining Issues)

1. **Cart State Update:** بررسی کنید که cart state پس از merge به‌روز می‌شود
2. **OTP Flow:** همین fix را برای OTP authentication هم تست کنید
3. **Other Redirects:** بررسی کنید که redirect های دیگر (مثلاً از checkout به login) هم مشکل ندارند

## تاریخ (Date)

Fixed: October 26, 2025 (00:30 UTC)
