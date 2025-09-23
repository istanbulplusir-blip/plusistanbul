# Cart Options Pricing Fix Report

## 🎯 مشکل اصلی

کاربر گزارش کرد که `selected_options` و `options_total` در محاسبه `total_price` و `subtotal` اعمال نمی‌شوند.

## 🔍 تحلیل مشکل

### وضعیت قبل از اصلاح:
- `selected_options` ذخیره می‌شد اما `options_total` محاسبه نمی‌شد
- `total_price` فقط شامل tour pricing بود، بدون options
- `CartSerializer.get_subtotal()` محاسبه اشتباه داشت

### مثال مشکل:
```json
{
  "selected_options": [
    {"price": 25.00, "quantity": 2},
    {"price": 15.00, "quantity": 1}
  ],
  "options_total": 0.00,  // ❌ اشتباه
  "total_price": 360.00   // ❌ فقط tour price
}
```

### وضعیت درست:
```json
{
  "selected_options": [
    {"price": 25.00, "quantity": 2},
    {"price": 15.00, "quantity": 1}
  ],
  "options_total": 65.00,  // ✅ درست
  "total_price": 425.00    // ✅ tour price + options
}
```

## 🛠️ اصلاحات انجام شده

### 1. اصلاح `CartItem.save()` در `backend/cart/models.py`

**مشکل**: `options_total` از `selected_options` محاسبه نمی‌شد

**اصلاح**: 
- اضافه کردن محاسبه خودکار `options_total` در هر بار `save()`
- فرمول: `Σ(option.price × option.quantity)`

```python
# Always recalculate options_total from selected_options
options_total = Decimal('0.00')
if self.selected_options:
    for option in self.selected_options:
        option_price = Decimal(str(option.get('price', 0)))
        option_quantity = int(option.get('quantity', 1))
        options_total += option_price * option_quantity
self.options_total = options_total
```

### 2. اصلاح `CartSerializer.get_subtotal()` در `backend/cart/serializers.py`

**مشکل**: محاسبه اشتباه subtotal برای تورها

**اصلاح**: 
- استفاده از `total_price` کامل (شامل tour + options)
- محاسبه صحیح برای events و transfers

```python
def get_subtotal(self, obj):
    total = 0
    for item in obj.items.all():
        if item.product_type == 'tour':
            # Use stored total_price which includes tour pricing + options
            total += item.total_price
        else:
            # For events and transfers, calculate normally
            item_total = item.unit_price * item.quantity
            # Add options if any
            if item.selected_options:
                for option_data in item.selected_options:
                    option_price = option_data.get('price', 0)
                    option_quantity = option_data.get('quantity', 1)
                    item_total += Decimal(str(option_price)) * int(option_quantity)
            total += item_total
    return total
```

## ✅ تست‌های انجام شده

### Test 1: محاسبه options_total
- **سناریو**: اضافه کردن 2 option با قیمت‌های مختلف
- **انتظار**: 65 دلار (25×2 + 15×1)
- **نتیجه**: 65 دلار ✅

### Test 2: محاسبه total_price با options
- **سناریو**: Tour (360) + Options (65)
- **انتظار**: 425 دلار
- **نتیجه**: 425 دلار ✅

### Test 3: آپدیت participants با options
- **سناریو**: تغییر participants + حفظ options
- **انتظار**: Tour price جدید + options
- **نتیجه**: درست ✅

### Test 4: حذف options
- **سناریو**: حذف همه options
- **انتظار**: فقط tour price
- **نتیجه**: درست ✅

### Test 5: CartSerializer
- **سناریو**: تست API response
- **انتظار**: subtotal و total_price درست
- **نتیجه**: درست ✅

## 🎉 نتیجه نهایی

### ✅ مشکلات حل شده:
1. **محاسبه options_total**: حالا خودکار از selected_options محاسبه می‌شود
2. **محاسبه total_price**: شامل tour pricing + options
3. **CartSerializer**: subtotal و total_price درست محاسبه می‌شوند
4. **سازگاری**: با آپدیت participants کار می‌کند

### ✅ فرمول نهایی:
```
options_total = Σ(option.price × option.quantity)
total_price = tour_price + options_total
subtotal = Σ(item.total_price)
```

### ✅ تأیید عملکرد:
- **Backend**: محاسبه درست
- **API**: پاسخ درست
- **Database**: ذخیره درست
- **Serializer**: نمایش درست

## 📋 فایل‌های تغییر یافته

1. **backend/cart/models.py** - اصلاح CartItem.save()
2. **backend/cart/serializers.py** - اصلاح CartSerializer.get_subtotal()

## 🔧 راهنمای استفاده

### برای Frontend:
```javascript
// هنگام آپدیت کارت، options را بفرستید
const updateData = {
  selected_options: [
    {
      option_id: "meal-option",
      name: "Extra Meal",
      price: 25.00,
      quantity: 2
    }
  ]
};
```

### برای Backend:
```python
# سیستم خودکار محاسبه می‌کند:
# - options_total = Σ(price × quantity)
# - total_price = tour_price + options_total
```

## 🎯 نتیجه‌گیری

مشکل محاسبه options در کارت کاملاً حل شد. سیستم حالا:
- **دقیق**: محاسبه خودکار options_total
- **کامل**: total_price شامل همه چیز
- **قابل اعتماد**: تست شده در تمام scenarios
- **سازگار**: با سیستم participants کار می‌کند

---

**تاریخ**: 2025-07-06  
**وضعیت**: ✅ کامل و تست شده  
**اولویت**: 🔴 Critical Fix - اعمال شد 