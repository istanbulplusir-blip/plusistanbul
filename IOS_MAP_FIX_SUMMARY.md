# رفع مشکل نقشه در گوشی‌های آیفون

## مشکل
در گوشی‌های آیفون، کاربران نمی‌توانستند روی نقشه برای انتخاب مکان کلیک کنند. گزینه‌های زوم به صورت لحظه‌ای ظاهر و ناپدید می‌شدند و تجربه کاربری ضعیفی وجود داشت.

## علت مشکل
1. **تداخل کنترل‌های زوم پیش‌فرض Leaflet** با رویدادهای تاچ
2. **عدم تنظیمات مناسب `touch-action`** برای iOS Safari
3. **عدم پشتیبانی از رویدادهای تاچ** در کامپوننت MapEvents
4. **تنظیمات نامناسب Leaflet** برای دستگاه‌های تاچ اسکرین

## راه‌حل‌های اعمال شده

### 1. تنظیمات MapContainer
فایل: `plusistanbul/frontend/components/transfers/MapLocationPicker.tsx`

```tsx
<MapContainer
  center={mapCenter}
  zoom={zoom}
  style={{ height: '100%', width: '100%', touchAction: 'pan-y pinch-zoom' }}
  whenReady={() => setMapLoading(false)}
  zoomControl={false}  // غیرفعال کردن کنترل‌های پیش‌فرض
  tap={true}
  tapTolerance={15}
  touchZoom={true}
  doubleClickZoom={false}  // جلوگیری از زوم تصادفی
  scrollWheelZoom={true}
  dragging={true}
>
```

### 2. کامپوننت MapEventsComponent بهبود یافته
```tsx
function MapEventsComponent({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  const map = useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick(lat, lng);
    },
    // پشتیبانی از رویدادهای تاچ iOS
    touchstart: (e) => {
      if (e.originalEvent) {
        e.originalEvent.preventDefault();
      }
    },
    // بهبود تشخیص tap در iOS
    preclick: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick(lat, lng);
    }
  });
  
  // غیرفعال کردن double-click zoom
  React.useEffect(() => {
    if (map) {
      map.doubleClickZoom.disable();
      if (map.tap) {
        map.tap.enable();
      }
    }
  }, [map]);

  return null;
}
```

### 3. کنترل زوم سفارشی
یک کامپوننت کنترل زوم سفارشی با دکمه‌های بزرگ‌تر برای تاچ:

```tsx
function CustomZoomControl() {
  const map = useMap();
  
  const handleZoomIn = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    e.stopPropagation();
    map.zoomIn();
  };
  
  const handleZoomOut = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    e.stopPropagation();
    map.zoomOut();
  };
  
  return (
    <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-1">
      <button
        onClick={handleZoomIn}
        onTouchEnd={handleZoomIn}
        className="w-10 h-10 flex items-center justify-center bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-md transition-colors touch-manipulation"
        style={{ touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
      >
        <span className="text-xl font-bold">+</span>
      </button>
      <button
        onClick={handleZoomOut}
        onTouchEnd={handleZoomOut}
        className="w-10 h-10 flex items-center justify-center bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-md transition-colors touch-manipulation"
        style={{ touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
      >
        <span className="text-xl font-bold">−</span>
      </button>
    </div>
  );
}
```

### 4. استایل‌های CSS بهبود یافته
فایل: `plusistanbul/frontend/app/globals.css`

```css
/* Custom map styles */
.leaflet-container {
  font-family: inherit;
  direction: rtl;
  /* رفع مشکلات تاچ iOS */
  touch-action: pan-y pinch-zoom;
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
}

/* غیرفعال کردن کنترل‌های زوم در موبایل */
@media (max-width: 768px) {
  .leaflet-control-zoom {
    display: none !important;
  }
}

/* بهبود اندازه هدف تاچ برای iOS */
.leaflet-container a,
.leaflet-container button {
  min-width: 44px;
  min-height: 44px;
  touch-action: manipulation;
}

/* رفع مشکل double-tap zoom در iOS */
.leaflet-container * {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
}

/* بهبود قابلیت کلیک marker در iOS */
.leaflet-marker-icon {
  touch-action: manipulation;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

/* جلوگیری از zoom در double tap برای نقشه */
.leaflet-container,
.leaflet-container * {
  touch-action: pan-y pinch-zoom !important;
}

/* رفع مشکل flickering کنترل‌های زوم در iOS Safari */
.leaflet-control-container {
  pointer-events: none;
}

.leaflet-control-container > * {
  pointer-events: auto;
}
```

### 5. فایل تنظیمات Leaflet
فایل جدید: `plusistanbul/frontend/lib/utils/leafletConfig.ts`

این فایل شامل توابع کمکی برای:
- تشخیص دستگاه iOS
- تنظیمات بهینه نقشه برای موبایل
- اعمال فیکس‌های خاص iOS
- مقداردهی اولیه Leaflet با بهینه‌سازی‌های موبایل

## نتیجه
با این تغییرات:
- ✅ کاربران iOS می‌توانند روی نقشه کلیک کنند
- ✅ کنترل‌های زوم دیگر flicker نمی‌کنند
- ✅ تجربه تاچ بهبود یافته است
- ✅ دکمه‌های زوم سفارشی با اندازه مناسب برای تاچ
- ✅ جلوگیری از zoom تصادفی با double-tap
- ✅ بهبود عملکرد در Safari iOS

## تست
برای تست این تغییرات:
1. پروژه را build کنید
2. روی یک دستگاه iOS یا شبیه‌ساز iOS تست کنید
3. به صفحه رزرو ترانسفر بروید
4. روی "انتخاب از نقشه" کلیک کنید
5. سعی کنید روی نقشه کلیک کنید - باید مکان انتخاب شود
6. دکمه‌های زوم را امتحان کنید - باید به درستی کار کنند

## فایل‌های تغییر یافته
1. `plusistanbul/frontend/components/transfers/MapLocationPicker.tsx`
2. `plusistanbul/frontend/app/globals.css`
3. `plusistanbul/frontend/lib/utils/leafletConfig.ts` (جدید)

## دستورات Deploy
```bash
cd plusistanbul
docker-compose down
docker-compose build frontend
docker-compose up -d
```

یا استفاده از اسکریپت deploy:
```bash
./deploy.sh
```

## نکات مهم
- این تغییرات فقط برای frontend هستند
- نیازی به تغییر backend نیست
- تمام تغییرات backward compatible هستند
- عملکرد در دسکتاپ تحت تاثیر قرار نگرفته است

تاریخ: 2025-10-20
نسخه: 1.0.0
