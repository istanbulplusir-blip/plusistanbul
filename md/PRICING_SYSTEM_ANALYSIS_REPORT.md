# گزارش تحلیل کامل سیستم قیمت‌گذاری پلتفرم پیکان توریسم

## خلاصه مدیریتی 

بعد از بررسی دقیق سیستم، مشکلات حادی در قیمت‌گذاری شناسایی شد که عمدتاً به دلیل **عدم‌انطباق سیستم قیمت‌گذاری Backend و Frontend** است. در حالی که صفحه جزئیات تور درست عمل می‌کند، صفحه کارت مشکلات جدی در محاسبه قیمت دارد.

---

## 🔍 مشکلات شناسایی شده

### 1. ⚠️ **CRITICAL: عدم انطباق سیستم قیمت‌گذاری Backend و Frontend**

**مشکل اصلی**: سیستم Backend و Frontend قیمت‌گذاری متفاوتی دارند:

#### Backend Structure:
```
TourVariant:
  - base_price: 100.00, 150.00, 250.00 (قیمت مطلق)
  - price_modifier: 0.80, 1.00, 0.00 (ضریب قیمت)

Tour: 
  - price: 150.00 (قیمت پایه تور)
```

#### Frontend Logic:
- **صفحه جزئیات تور**: از `pricing_summary` API استفاده می‌کند (✅ درست)
- **صفحه کارت**: از `unit_price × quantity` استفاده می‌کند (❌ اشتباه)

### 2. ⚠️ **مشکل محاسبه قیمت در صفحه کارت**

**نحوه اشتباه فعلی در Cart Page:**
```typescript
// frontend/app/[locale]/cart/page.tsx - خط 194
const totalPrice = items.reduce((sum, item) => {
  if (item.type === 'tour') {
    return sum + item.subtotal;  // درست
  } else {
    return sum + (item.price * item.quantity);  // اشتباه برای تور
  }
}, 0);
```

**مشکل**: صفحه کارت از فرمول `price × quantity` استفاده می‌کند که برای تور اشتباه است زیرا:
- `quantity` در تور تعداد total participants است
- اما قیمت باید بر اساس سن‌گروه‌ها محاسبه شود نه quantity ساده

### 3. ⚠️ **Backend Cart Pricing Logic مبهم**

**مشکل در AddToCartView:**
```python
# backend/cart/views.py - خط 66-67
if data.get('variant_id'):
    variant = TourVariant.objects.get(id=variant_id, tour=product)
    unit_price = variant.base_price  # استفاده از base_price
```

**اما داده‌های موجود نشان می‌دهد:**
- Tour.price = 150.00
- Variant.base_price = 100.00, 150.00, 250.00
- Variant.price_modifier = 0.80, 1.00, 0.00

**مشکل**: منطق pricing واضح نیست که کدام فیلد اولویت دارد.

---

## 📊 داده‌های موجود در دیتابیس

### نمونه داده‌ها:
```
Tour: Persepolis Historical Tour
├── Tour.price: 150.00 USD
├── Variants:
│   ├── Eco: base_price=100.00, price_modifier=0.80
│   ├── Normal: base_price=150.00, price_modifier=1.00  
│   └── VIP: base_price=250.00, price_modifier=0.00
```

---

## 🔄 مقایسه سیستم‌های موجود

### ✅ **صفحه جزئیات تور (درست عمل می‌کند)**

**مکانیزم:**
```typescript
// frontend/app/[locale]/tours/[slug]/page.tsx - خط 229-276
const calculatePricing = () => {
  const variantPricing = tour.pricing_summary[selectedVariant.id];
  
  Object.entries(participants).forEach(([type, count]) => {
    const ageGroupPricing = variantPricing.age_groups[type];
    const price = ageGroupPricing.final_price;
    const cost = price * count;
    total += cost;
  });
}
```

**چرا درست است:**
- از `pricing_summary` API استفاده می‌کند
- قیمت بر اساس سن‌گروه محاسبه می‌شود
- Backend تمام محاسبات را انجام داده و final_price ارسال می‌کند

### ❌ **صفحه کارت (اشتباه عمل می‌کند)**

**مکانیزم فعلی:**
```typescript
// frontend/lib/hooks/useCart.ts - خط 192-198
const totalPrice = items.reduce((sum, item) => {
  if (item.type === 'tour') {
    return sum + item.subtotal;  // درست
  } else {
    return sum + (item.price * item.quantity);  // اشتباه
  }
}, 0);
```

**مشکل:**
- `item.price` همان `unit_price` از backend است که قیمت پایه variant است
- `item.quantity` تعداد total participants است
- فرمول `unit_price × quantity` برای تورها اشتباه است

---

## 🛠️ راه‌حل‌های پیشنهادی

### راه‌حل 1: **اصلاح Frontend Cart Logic** (پیشنهاد اول)

**فایل:** `frontend/app/[locale]/cart/page.tsx`

```typescript
// جایگزین کردن pricing calculation
const calculateItemTotal = (item: CartItem) => {
  if (item.type === 'tour') {
    // استفاده از subtotal از backend که قبلاً محاسبه شده
    return item.subtotal;
  } else {
    // برای event و transfer
    return item.price * item.quantity;
  }
};

const totalPrice = items.reduce((sum, item) => {
  return sum + calculateItemTotal(item);
}, 0);
```

### راه‌حل 2: **بهبود Backend Pricing API** (پیشنهاد دوم)

**فایل:** `backend/cart/serializers.py`

```python
class CartItemSerializer(serializers.ModelSerializer):
    def get_total_price(self, obj):
        """Calculate accurate total price based on age groups."""
        if obj.product_type == 'tour':
            # استفاده از TourPricing برای محاسبه دقیق
            tour = Tour.objects.get(id=obj.product_id)
            variant = TourVariant.objects.get(id=obj.variant_id)
            
            participants = obj.booking_data.get('participants', {})
            total = 0
            
            for age_group, count in participants.items():
                pricing = TourPricing.objects.get(
                    tour=tour, 
                    variant=variant, 
                    age_group=age_group
                )
                total += pricing.final_price * count
            
            return total + obj.options_total
        else:
            return obj.unit_price * obj.quantity + obj.options_total
```

### راه‌حل 3: **Unified Pricing Service** (پیشنهاد سوم)

**ایجاد سرویس واحد قیمت‌گذاری:**

```python
# backend/shared/services.py
class PricingService:
    @staticmethod
    def calculate_tour_price(tour, variant, participants, options=None):
        """Calculate accurate tour price based on participants and options."""
        total = 0
        
        # محاسبه بر اساس سن‌گروه‌ها
        for age_group, count in participants.items():
            pricing = TourPricing.objects.get(
                tour=tour, variant=variant, age_group=age_group
            )
            total += pricing.final_price * count
        
        # اضافه کردن options
        if options:
            for option in options:
                total += option['price'] * option['quantity']
        
        return total
```

---

## 🧪 تست‌های پیشنهادی

### تست 1: **Price Consistency Test**
```python
def test_pricing_consistency():
    """تست انطباق قیمت بین صفحه تور و کارت"""
    # انتخاب تور و variant
    # محاسبه قیمت در صفحه تور
    # اضافه کردن به کارت
    # بررسی انطباق قیمت‌ها
```

### تست 2: **Age Group Pricing Test**
```python
def test_age_group_pricing():
    """تست قیمت‌گذاری بر اساس سن‌گروه‌ها"""
    # تست pricing factors
    # تست free pricing برای infants
    # تست variant pricing differences
```

---

## 📋 اولویت‌بندی اقدامات

### فوری (اولویت 1):
1. **اصلاح محاسبه totalPrice در صفحه کارت**
2. **تست pricing consistency بین صفحات**
3. **رفع warning های console در cart page**

### کوتاه‌مدت (اولویت 2):
1. **ایجاد Unified Pricing Service**
2. **بهبود CartItem serializer**
3. **اضافه کردن pricing validation**

### بلندمدت (اولویت 3):
1. **مستندسازی سیستم قیمت‌گذاری**
2. **ایجاد automated pricing tests**
3. **بهینه‌سازی performance**

---

## 🔍 نکات فنی مهم

### Backend Pricing Fields:
- **Tour.price**: قیمت پایه تور (ممکن است deprecated باشد)
- **TourVariant.base_price**: قیمت مطلق variant (استفاده فعلی)
- **TourVariant.price_modifier**: ضریب قیمت (احتمالاً legacy)
- **TourPricing.factor**: ضریب سن‌گروه (0.00-2.00)

### Frontend Pricing Logic:
- **Tour Detail**: از `pricing_summary` API ✅
- **Cart Display**: از `item.subtotal` ✅  
- **Cart Total**: مشکل در محاسبه ❌

---

## 📈 Impact Assessment

### تأثیر فعلی مشکل:
- ❌ **قیمت اشتباه در سبد خرید**
- ❌ **عدم اعتماد کاربران**
- ❌ **احتمال خطا در پرداخت**

### تأثیر پس از رفع:
- ✅ **قیمت‌گذاری دقیق و یکپارچه**
- ✅ **تجربه کاربری بهتر**
- ✅ **آماده شدن برای scale کردن**

---

## 🚀 نتیجه‌گیری

سیستم قیمت‌گذاری Backend قوی و مناسب است، اما Frontend در قسمت Cart صفحه نیاز به اصلاح دارد. با اصلاحات پیشنهادی، سیستم یکپارچه و قابل اعتماد خواهد شد.

**وضعیت فعلی**: 🟡 قابل استفاده با محدودیت  
**وضعیت پس از اصلاح**: 🟢 کاملاً آماده تولید

---

*گزارش تهیه شده در: ۲۰۲۵*  
*تحلیل‌گر: AI Assistant*  
*وضعیت: آماده پیاده‌سازی* 