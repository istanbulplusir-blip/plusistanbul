# راهنمای سیستم محدودیت‌ها (Limit Validation System)

## 📋 **خلاصه**

این سیستم محدودیت‌های جامع و یکپارچه برای پلتفرم گردشگری پیکان فراهم می‌کند که شامل محدودیت‌های کارت، سفارش، و کاربران است.

## 🔧 **Backend Services**

### **LimitValidationService**

کلاس مرکزی برای بررسی همه محدودیت‌ها در بک‌اند.

#### **متدهای اصلی:**

```python
# بررسی محدودیت‌های کارت
validate_cart_limits(user, cart_items_count, cart_total, new_item_total)

# بررسی محدودیت‌های مرج کارت
validate_merge_limits(user, user_cart_items, user_cart_total, guest_cart_items, guest_cart_total)

# بررسی محدودیت‌های سفارش
validate_order_limits(user, cart_items_count, cart_total)

# بررسی Rate Limiting
validate_rate_limit(user, request_type)

# بررسی Duplicate Booking
validate_duplicate_booking(user, product_type, product_id, variant_id, booking_data)
```

### **LimitValidationMixin**

Mixin class برای اضافه کردن قابلیت validation به Views.

```python
class MyView(LimitValidationMixin, APIView):
    def post(self, request):
        # بررسی محدودیت‌های کارت
        is_valid, error = self.validate_cart_limits(request, cart, data)
        if not is_valid:
            return Response({'error': error}, status=400)
```

## 🎨 **Frontend Services**

### **LimitValidationService (TypeScript)**

کلاس مرکزی برای بررسی محدودیت‌ها در فرانت‌اند.

#### **متدهای اصلی:**

```typescript
// بررسی محدودیت‌های کارت
validateCartLimits(isAuthenticated, currentItems, currentTotal, newItemTotal);

// بررسی محدودیت‌های مرج کارت
validateMergeLimits(
  userCartItems,
  userCartTotal,
  guestCartItems,
  guestCartTotal
);

// بررسی محدودیت‌های شرکت‌کنندگان
validateParticipantLimits(participants, tourLimits);

// بررسی محدودیت‌های گزینه‌ها
validateOptionLimits(optionId, quantity, maxQuantity);
```

## ⚙️ **تنظیمات سیستم**

### **SystemSettings**

تنظیمات مرکزی در دیتابیس:

```python
# محدودیت‌های کارت مهمان
cart_max_items_guest = 3
cart_max_total_guest = 500.00

# محدودیت‌های کارت کاربر
cart_max_items_user = 10
cart_max_total_user = 5000.00

# محدودیت‌های Rate Limiting
cart_rate_limit_guest = 30  # requests/minute
cart_rate_limit_user = 20   # requests/minute

# محدودیت‌های سفارش
order_max_pending_per_user = 3
order_max_pending_per_product = 1
```

## 🚀 **استفاده در کد**

### **Backend Example:**

```python
from core.services import LimitValidationService

# بررسی محدودیت‌های کارت
is_valid, error = LimitValidationService.validate_cart_limits(
    user=request.user,
    cart_items_count=cart.items.count(),
    cart_total=cart.total,
    new_item_total=Decimal('100.00')
)

if not is_valid:
    return Response({'error': error}, status=400)
```

### **Frontend Example:**

```typescript
import { LimitValidationService } from "@/lib/services/limitValidation";

// بررسی محدودیت‌های کارت
const validation = LimitValidationService.validateCartLimits(
  isAuthenticated,
  currentItems,
  currentTotal,
  newItemTotal
);

if (!validation.isValid) {
  showError(validation.errorMessage);
  return;
}
```

## 🔍 **نحوه کار**

### **1. Cart Limits**

- **مهمان:** حداکثر 3 آیتم، مجموع $500
- **کاربر:** حداکثر 10 آیتم، مجموع $5000

### **2. Merge Limits**

- بررسی محدودیت‌های مهمان قبل از مرج
- بررسی محدودیت‌های کاربر بعد از مرج
- جلوگیری از دور زدن محدودیت‌ها

### **3. Order Limits**

- بررسی محدودیت‌های کارت قبل از ایجاد سفارش
- محدودیت حداکثر 3 سفارش pending برای هر کاربر

### **4. Rate Limiting**

- مهمان: 30 درخواست در دقیقه
- کاربر: 20 درخواست در دقیقه

### **5. Duplicate Booking**

- بررسی سفارشات pending موجود
- بررسی آیتم‌های موجود در کارت
- جلوگیری از رزرو تکراری

## 🛠️ **تنظیمات**

### **تغییر محدودیت‌ها:**

```python
# در Django Admin یا Shell
from core.models import SystemSettings

settings = SystemSettings.get_settings()
settings.cart_max_items_guest = 5  # تغییر محدودیت
settings.save()
```

### **به‌روزرسانی Frontend:**

```typescript
// در Frontend
LimitValidationService.updateSettings({
  cartMaxItemsGuest: 5,
  cartMaxTotalGuest: 1000,
});
```

## 🧪 **تست**

### **Backend Tests:**

```python
def test_cart_limits():
    # تست محدودیت‌های کارت
    is_valid, error = LimitValidationService.validate_cart_limits(
        user=None,  # مهمان
        cart_items_count=2,
        cart_total=Decimal('300.00'),
        new_item_total=Decimal('250.00')
    )
    assert not is_valid  # باید محدودیت را نقض کند
    assert 'exceed' in error
```

### **Frontend Tests:**

```typescript
describe("LimitValidationService", () => {
  it("should validate cart limits for guests", () => {
    const result = LimitValidationService.validateCartLimits(
      false, // مهمان
      2, // آیتم‌های فعلی
      300, // مجموع فعلی
      250 // مجموع آیتم جدید
    );

    expect(result.isValid).toBe(false);
    expect(result.errorMessage).toContain("exceed");
  });
});
```

## 📝 **نکات مهم**

1. **یکپارچگی:** همه محدودیت‌ها از یک مکان مدیریت می‌شوند
2. **امنیت:** محدودیت‌ها در همه سطوح (Frontend, Backend, Database) بررسی می‌شوند
3. **قابلیت نگهداری:** تغییرات در یک جا اعمال می‌شوند
4. **سازگاری:** Frontend و Backend هماهنگ هستند
5. **قابلیت توسعه:** آسان برای اضافه کردن محدودیت‌های جدید

## 🔄 **Migration**

برای اعمال تغییرات در دیتابیس:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🚨 **Troubleshooting**

### **مشکلات رایج:**

1. **تنظیمات ناسازگار:** بررسی SystemSettings در Admin
2. **خطاهای Frontend:** بررسی import های LimitValidationService
3. **مشکلات Migration:** اجرای مجدد makemigrations و migrate

### **لاگ‌ها:**

```python
# فعال‌سازی لاگ‌های debug
import logging
logging.getLogger('core.services').setLevel(logging.DEBUG)
```
