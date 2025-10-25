# رفع مشکل Date Picker و نقشه در iOS Safari

## خلاصه مشکلات
در گوشی‌های آیفون و مرورگر Safari iOS، دو مشکل اصلی وجود داشت:

1. **نقشه:** باز می‌شود ولی اینتراکت ندارد
2. **Date Picker:** جدول پیکر تاریخ با کلیک باز نمیشود

## راه‌حل‌های اعمال شده

### 1. رفع مشکل نقشه
- بهبود تنظیمات `touch-action` برای iOS Safari
- اضافه کردن پشتیبانی از `tap` events در Leaflet
- بهبود event handling برای touch events
- اضافه کردن CSS های خاص iOS Safari

### 2. رفع مشکل Date Picker
- استفاده از `-webkit-appearance: menulist-button` برای iOS Safari
- اضافه کردن fallback methods برای `showPicker()` API
- بهبود trigger کردن native date picker
- اضافه کردن touch event handlers

## فایل‌های تغییر یافته
1. `frontend/components/transfers/MapLocationPicker.tsx`
2. `frontend/app/[locale]/transfers/booking/components/DateTimeSelection.tsx`
3. `frontend/app/globals.css`
4. `frontend/lib/utils/leafletConfig.ts`

## Deploy
```bash
cd plusistanbul
./deploy_ios_safari_fix.sh
```

## نتیجه
✅ نقشه و date picker در iOS Safari کار می‌کنند
✅ تجربه کاربری بهبود یافته است
✅ سازگاری با سایر مرورگرها حفظ شده است

تاریخ: 2025-01-21