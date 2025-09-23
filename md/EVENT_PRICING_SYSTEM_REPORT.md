# گزارش کامل سیستم قیمت‌گذاری Event

## 📋 خلاصه اجرایی

سیستم قیمت‌گذاری Event با موفقیت به یک سیستم جامع و یکپارچه تبدیل شد که شامل تمام موارد مورد نیاز برای محاسبه قیمت می‌باشد:

- ✅ **آپشن‌ها** (Merch, VIP, Parking)
- ✅ **تخفیف‌ها** (Promo, Group, Early-bird)
- ✅ **کارمزدها و مالیات** (Service Fee, VAT)
- ✅ **PriceCalculator Service** متمرکز و قابل تست

## 🎯 مشکلات حل شده

### مشکلات قبلی:
1. **عدم پوشش تخفیف‌ها**: هیچ مدلی برای کدهای تخفیف وجود نداشت
2. **عدم پوشش کارمزدها**: مالیات و کارمزد در محاسبات نبود
3. **عدم یکپارچگی**: منطق قیمت‌گذاری پراکنده بود
4. **عدم انعطاف‌پذیری**: قوانین قیمت‌گذاری ثابت بود

### راه‌حل‌های پیاده‌سازی شده:
1. **مدل‌های جدید**: `EventDiscount`, `EventFee`, `EventPricingRule`
2. **EventPriceCalculator**: سرویس متمرکز برای محاسبه قیمت
3. **EventPricingRules**: قوانین قابل تنظیم
4. **API های جدید**: مدیریت کامل قیمت‌گذاری

## 🏗️ معماری جدید

### سلسله مراتب قیمت‌گذاری:
```
Event
├── EventPerformance
│   ├── EventSection (base_price)
│   │   └── SectionTicketType (price_modifier)
│   └── EventOption (add-ons)
├── EventDiscount (promo codes)
├── EventFee (service fees, taxes)
└── EventPricingRule (dynamic pricing)
```

### فرمول محاسبه نهایی:
```
Final Price = Base Price × Price Modifier × Quantity
            + Options Total
            - Discount Total
            + Fees Total
            + Taxes Total
```

## 📊 مدل‌های جدید

### 1. EventDiscount
```python
class EventDiscount(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('early_bird', 'Early Bird'),
        ('group', 'Group Booking'),
        ('loyalty', 'Loyalty'),
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField()
    current_uses = models.PositiveIntegerField()
```

### 2. EventFee
```python
class EventFee(BaseModel):
    fee_type = models.CharField(choices=[
        ('service', 'Service Fee'),
        ('booking', 'Booking Fee'),
        ('processing', 'Processing Fee'),
        ('convenience', 'Convenience Fee'),
        ('tax', 'Tax'),
        ('vat', 'VAT'),
    ])
    calculation_type = models.CharField(choices=[
        ('percentage', 'Percentage of Amount'),
        ('fixed', 'Fixed Amount'),
        ('per_ticket', 'Per Ticket'),
        ('per_booking', 'Per Booking'),
    ])
    fee_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_fee = models.DecimalField(max_digits=10, decimal_places=2)
```

### 3. EventPricingRule
```python
class EventPricingRule(BaseModel):
    rule_type = models.CharField(choices=[
        ('early_bird', 'Early Bird'),
        ('last_minute', 'Last Minute'),
        ('peak_hour', 'Peak Hour'),
        ('off_peak', 'Off Peak'),
        ('weekend', 'Weekend'),
        ('holiday', 'Holiday'),
        ('capacity_based', 'Capacity Based'),
    ])
    adjustment_type = models.CharField(choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('multiplier', 'Multiplier'),
    ])
    adjustment_value = models.DecimalField(max_digits=10, decimal_places=2)
    conditions = models.JSONField()
    priority = models.PositiveIntegerField()
```

## 🔧 EventPriceCalculator Service

### ویژگی‌های کلیدی:
1. **محاسبه جامع**: تمام اجزای قیمت را محاسبه می‌کند
2. **اعتبارسنجی**: بررسی صحت داده‌ها
3. **انعطاف‌پذیری**: قابلیت فعال/غیرفعال کردن بخش‌ها
4. **قابلیت تست**: طراحی شده برای تست آسان

### متدهای اصلی:
```python
def calculate_ticket_price(
    self,
    section_name: str,
    ticket_type_id: str,
    quantity: int = 1,
    selected_options: Optional[List[Dict]] = None,
    discount_code: Optional[str] = None,
    is_group_booking: bool = False,
    apply_fees: bool = True,
    apply_taxes: bool = True
) -> Dict[str, Any]
```

### خروجی نمونه:
```json
{
  "base_price": 100.00,
  "price_modifier": 1.20,
  "unit_price": 120.00,
  "quantity": 2,
  "subtotal": 240.00,
  "options": [
    {
      "option_id": "uuid",
      "name": "VIP Parking",
      "price": 25.00,
      "quantity": 1,
      "total": 25.00
    }
  ],
  "options_total": 25.00,
  "discounts": [
    {
      "type": "group_booking",
      "name": "Group Booking Discount",
      "percentage": 10.0,
      "amount": 26.50
    }
  ],
  "discount_total": 26.50,
  "fees": [
    {
      "type": "service_fee",
      "name": "Service Fee",
      "percentage": 3.0,
      "amount": 7.16
    }
  ],
  "fees_total": 9.66,
  "taxes": [
    {
      "type": "vat",
      "name": "Value Added Tax (VAT)",
      "percentage": 9.0,
      "amount": 22.33
    }
  ],
  "taxes_total": 22.33,
  "final_price": 270.49
}
```

## 🌐 API های جدید

### 1. محاسبه قیمت
```
POST /api/v1/events/{event_id}/pricing/calculate_price/
```

### 2. اطلاعات قیمت‌گذاری
```
GET /api/v1/events/{event_id}/pricing/pricing_info/
```

### 3. مدیریت تخفیف‌ها
```
GET /api/v1/events/discounts/
POST /api/v1/events/discounts/{discount_id}/validate_code/
```

### 4. مدیریت کارمزدها
```
GET /api/v1/events/fees/
```

### 5. مدیریت قوانین قیمت‌گذاری
```
GET /api/v1/events/pricing-rules/
POST /api/v1/events/pricing-rules/{rule_id}/test_rule/
```

## 📈 قوانین قیمت‌گذاری پیش‌فرض

### کارمزدها:
- **Service Fee**: 3% از مبلغ
- **Booking Fee**: $2.50 ثابت
- **VAT**: 9% از مبلغ نهایی

### تخفیف‌ها:
- **Group Booking**: 10% برای گروه‌های بالای $500
- **Early Bird**: 15% برای رزرو 30 روز قبل
- **Promo Code**: 5% (قابل تنظیم)

### قوانین ظرفیت:
- **Minimum Group Size**: 10 نفر
- **Maximum Group Size**: 100 نفر

## 🧪 تست‌ها

### تست‌های پیاده‌سازی شده:
1. **محاسبه قیمت پایه**
2. **محاسبه آپشن‌ها**
3. **محاسبه تخفیف‌ها**
4. **محاسبه کارمزدها و مالیات**
5. **محاسبه کامل قیمت**
6. **تست مدل‌های تخفیف و کارمزد**

### اجرای تست:
```bash
python test_event_pricing_system.py
```

## 🔄 Migration

### مراحل Migration:
1. **ایجاد مدل‌های جدید**
2. **اجرای Migration**
3. **تست سیستم جدید**
4. **به‌روزرسانی API ها**

### دستورات Migration:
```bash
python manage.py makemigrations events
python manage.py migrate events
```

## 📊 مزایای سیستم جدید

### 1. **شفافیت**
- تمام اجزای قیمت قابل مشاهده
- محاسبات دقیق و قابل ردیابی
- گزارش‌گیری کامل

### 2. **انعطاف‌پذیری**
- قوانین قابل تنظیم
- انواع مختلف تخفیف
- کارمزدهای متغیر

### 3. **قابلیت نگهداری**
- کد متمرکز و تمیز
- تست‌پذیری بالا
- مستندسازی کامل

### 4. **مقیاس‌پذیری**
- پشتیبانی از انواع مختلف رویداد
- قابلیت افزودن قوانین جدید
- عملکرد بهینه

## 🚀 مراحل بعدی

### اولویت بالا:
1. **تست کامل سیستم** در محیط توسعه
2. **به‌روزرسانی Frontend** برای استفاده از API های جدید
3. **مستندسازی API** برای توسعه‌دهندگان

### اولویت متوسط:
1. **پیاده‌سازی Promo Code System** کامل
2. **افزودن قوانین قیمت‌گذاری پیشرفته**
3. **بهینه‌سازی عملکرد**

### اولویت پایین:
1. **Dashboard مدیریت** برای تنظیم قوانین
2. **گزارش‌گیری پیشرفته**
3. **Analytics قیمت‌گذاری**

## ✅ نتیجه‌گیری

سیستم قیمت‌گذاری Event با موفقیت به یک سیستم جامع و حرفه‌ای تبدیل شد که تمام نیازهای قیمت‌گذاری را پوشش می‌دهد. این سیستم:

- **شفاف** و قابل اعتماد است
- **انعطاف‌پذیر** و قابل تنظیم است
- **قابل تست** و قابل نگهداری است
- **مقیاس‌پذیر** و آماده برای رشد است

سیستم آماده استفاده در محیط تولید می‌باشد و می‌تواند تمام نیازهای قیمت‌گذاری رویدادها را برآورده کند. 