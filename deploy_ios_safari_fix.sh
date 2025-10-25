#!/bin/bash

# رفع مشکلات iOS Safari برای نقشه و Date Picker
# iOS Safari Fix Deployment Script

echo "🚀 شروع deploy رفع مشکلات iOS Safari..."
echo "🚀 Starting iOS Safari fixes deployment..."

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع لاگ
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# بررسی وجود docker-compose
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose یافت نشد. لطفاً آن را نصب کنید."
    error "docker-compose not found. Please install it."
    exit 1
fi

# بررسی وجود فایل docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    error "فایل docker-compose.yml یافت نشد."
    error "docker-compose.yml file not found."
    exit 1
fi

log "📋 خلاصه تغییرات iOS Safari:"
log "📋 iOS Safari Changes Summary:"
echo "  ✅ رفع مشکل تاچ نقشه در iOS Safari"
echo "  ✅ Fixed map touch interaction in iOS Safari"
echo "  ✅ رفع مشکل Date Picker در iOS Safari"
echo "  ✅ Fixed Date Picker in iOS Safari"
echo "  ✅ بهبود تنظیمات Leaflet برای iOS"
echo "  ✅ Improved Leaflet configuration for iOS"
echo "  ✅ اضافه کردن CSS های خاص iOS Safari"
echo "  ✅ Added iOS Safari specific CSS"

# تأیید ادامه
read -p "آیا می‌خواهید ادامه دهید؟ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    warning "عملیات لغو شد."
    warning "Operation cancelled."
    exit 0
fi

# مرحله 1: متوقف کردن سرویس‌ها
log "🛑 متوقف کردن سرویس‌های فعلی..."
log "🛑 Stopping current services..."
docker-compose down

if [ $? -eq 0 ]; then
    success "سرویس‌ها با موفقیت متوقف شدند."
    success "Services stopped successfully."
else
    error "خطا در متوقف کردن سرویس‌ها."
    error "Error stopping services."
    exit 1
fi

# مرحله 2: پاک کردن cache و build مجدد
log "🧹 پاک کردن cache و build مجدد frontend..."
log "🧹 Cleaning cache and rebuilding frontend..."

# پاک کردن .next cache
if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    log "پاک کردن .next cache انجام شد."
    log ".next cache cleared."
fi

# پاک کردن node_modules cache (اختیاری)
if [ -d "frontend/node_modules/.cache" ]; then
    rm -rf frontend/node_modules/.cache
    log "پاک کردن node_modules cache انجام شد."
    log "node_modules cache cleared."
fi

# Build مجدد frontend
docker-compose build --no-cache frontend

if [ $? -eq 0 ]; then
    success "Frontend با موفقیت build شد."
    success "Frontend built successfully."
else
    error "خطا در build کردن frontend."
    error "Error building frontend."
    exit 1
fi

# مرحله 3: راه‌اندازی مجدد سرویس‌ها
log "🚀 راه‌اندازی مجدد سرویس‌ها..."
log "🚀 Starting services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    success "سرویس‌ها با موفقیت راه‌اندازی شدند."
    success "Services started successfully."
else
    error "خطا در راه‌اندازی سرویس‌ها."
    error "Error starting services."
    exit 1
fi

# مرحله 4: بررسی وضعیت سرویس‌ها
log "🔍 بررسی وضعیت سرویس‌ها..."
log "🔍 Checking services status..."
sleep 10

docker-compose ps

# مرحله 5: تست سلامت
log "🏥 تست سلامت سرویس‌ها..."
log "🏥 Health check..."

# تست frontend
log "تست frontend..."
log "Testing frontend..."
if curl -f -s http://localhost:3000 > /dev/null; then
    success "Frontend در دسترس است."
    success "Frontend is accessible."
else
    warning "Frontend ممکن است هنوز در حال راه‌اندازی باشد."
    warning "Frontend might still be starting up."
fi

# تست backend
log "تست backend..."
log "Testing backend..."
if curl -f -s http://localhost:8000/api/health/ > /dev/null; then
    success "Backend در دسترس است."
    success "Backend is accessible."
else
    warning "Backend ممکن است هنوز در حال راه‌اندازی باشد."
    warning "Backend might still be starting up."
fi

# نمایش لاگ‌های اخیر
log "📋 نمایش لاگ‌های اخیر frontend..."
log "📋 Showing recent frontend logs..."
docker-compose logs --tail=20 frontend

echo
success "🎉 Deploy رفع مشکلات iOS Safari با موفقیت انجام شد!"
success "🎉 iOS Safari fixes deployment completed successfully!"

echo
log "📱 برای تست تغییرات:"
log "📱 To test the changes:"
echo "  1. روی یک دستگاه iOS یا شبیه‌ساز iOS بروید"
echo "  1. Go to an iOS device or iOS simulator"
echo "  2. به آدرس http://your-server:3000 بروید"
echo "  2. Navigate to http://your-server:3000"
echo "  3. به صفحه transfers/booking بروید"
echo "  3. Go to transfers/booking page"
echo "  4. نقشه و date picker را تست کنید"
echo "  4. Test the map and date picker"

echo
log "🔧 فایل‌های تغییر یافته:"
log "🔧 Modified files:"
echo "  - frontend/components/transfers/MapLocationPicker.tsx"
echo "  - frontend/app/[locale]/transfers/booking/components/DateTimeSelection.tsx"
echo "  - frontend/app/globals.css"
echo "  - frontend/lib/utils/leafletConfig.ts"

echo
log "📚 مستندات بیشتر:"
log "📚 Additional documentation:"
echo "  - IOS_MAP_FIX_SUMMARY.md"
echo "  - README.md"

echo
warning "⚠️  اگر مشکلی وجود دارد، لاگ‌ها را بررسی کنید:"
warning "⚠️  If there are issues, check the logs:"
echo "  docker-compose logs frontend"
echo "  docker-compose logs backend"