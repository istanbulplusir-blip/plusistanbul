# گزارش جامع تحلیل سیستم ظرفیت Event - Peykan Tourism

## 📊 **خلاصه اجرایی**

### 🚨 **مشکلات بحرانی شناسایی شده**
1. **عدم ارتباط TicketType و Seat**: 600 صندلی بدون نوع بلیط
2. **عدم یکپارچگی ظرفیت**: Venue(2000) < Performance(1000) < ΣTicketType(3000) > Actual Seats(150)
3. **عدم وجود Invariant ها**: هیچ validation یا constraint برای ظرفیت
4. **مدیریت نادرست Section**: Section فقط در Seat ذخیره می‌شود

### ✅ **راه‌حل پیشنهادی**
سیستم یکپارچه ظرفیت با سلسله‌مراتب: `Venue → Performance → Section → TicketType → Seat`

---

## 🔍 **تحلیل وضعیت فعلی**

### **۱. ساختار مدل‌های موجود**

#### **Venue Model**
```python
class Venue(BaseTranslatableModel):
    total_capacity = models.PositiveIntegerField()  # ✅ 2000 نفر
```

#### **EventPerformance Model**
```python
class EventPerformance(BaseScheduleModel):
    # از BaseScheduleModel:
    max_capacity = models.PositiveIntegerField()      # ❌ 1000 نفر (کمتر از venue)
    current_capacity = models.PositiveIntegerField()  # ✅ 0 نفر
    
    # فیلد اضافی:
    ticket_capacities = models.JSONField()  # ❌ {'VIP': 1000, 'Normal': 1000, 'Economy': 1000}
```

#### **TicketType Model**
```python
class TicketType(BaseVariantModel):
    # از BaseVariantModel:
    capacity = models.PositiveIntegerField()  # ❌ هر کدام 1000 نفر (جمع = 3000!)
```

#### **Seat Model**
```python
class Seat(BaseModel):
    ticket_type = models.ForeignKey(TicketType, null=True, blank=True)  # ❌ اختیاری!
    section = models.CharField(max_length=50)  # ❌ فقط string
    status = models.CharField(choices=STATUS_CHOICES)  # ✅ available/reserved/sold
```

### **۲. مشکلات شناسایی شده**

#### **مشکل ۱: عدم ارتباط TicketType و Seat**
```
❌ وضعیت فعلی:
- 600 صندلی بدون ticket_type
- هیچ صندلی به ticket_type متصل نیست
- عدم امکان مدیریت ظرفیت صحیح
```

#### **مشکل ۲: عدم یکپارچگی ظرفیت**
```
❌ سلسله‌مراتب فعلی:
Venue (2000) 
├── Performance (1000) ❌ کمتر از venue
    ├── TicketType VIP (1000) ❌ بیشتر از performance
    ├── TicketType Normal (1000) ❌ بیشتر از performance  
    └── TicketType Economy (1000) ❌ بیشتر از performance
        └── Seat (150) ❌ بسیار کمتر از capacity
```

#### **مشکل ۳: عدم وجود Invariant ها**
```python
# ❌ هیچ validation وجود ندارد:
# - Venue.capacity ≥ Performance.max_capacity
# - Performance.max_capacity ≥ Σ(TicketType.capacity)
# - TicketType.capacity ≥ Actual Seats
```

#### **مشکل ۴: مدیریت نادرست Section**
```python
# ❌ Section فقط در Seat ذخیره می‌شود:
section = models.CharField(max_length=50)  # فقط string

# ❌ هیچ مدل جداگانه‌ای برای Section وجود ندارد
# ❌ ظرفیت Section محاسبه نمی‌شود
# ❌ قیمت‌گذاری Section وجود ندارد
```

---

## 💡 **راه‌حل پیشنهادی: سیستم یکپارچه ظرفیت**

### **۱. مدل‌های جدید**

#### **EventSection Model**
```python
class EventSection(BaseModel):
    performance = models.ForeignKey(EventPerformance)
    name = models.CharField(max_length=50)
    
    # Capacity management
    total_capacity = models.PositiveIntegerField()
    available_capacity = models.PositiveIntegerField()
    reserved_capacity = models.PositiveIntegerField(default=0)
    sold_capacity = models.PositiveIntegerField(default=0)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Validation
    def clean(self):
        if self.available_capacity + self.reserved_capacity + self.sold_capacity != self.total_capacity:
            raise ValidationError('Capacity components must sum to total capacity')
```

#### **SectionTicketType Model**
```python
class SectionTicketType(BaseModel):
    section = models.ForeignKey(EventSection)
    ticket_type = models.ForeignKey(TicketType)
    
    # Capacity allocation
    allocated_capacity = models.PositiveIntegerField()
    available_capacity = models.PositiveIntegerField()
    reserved_capacity = models.PositiveIntegerField(default=0)
    sold_capacity = models.PositiveIntegerField(default=0)
    
    # Pricing
    price_modifier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    
    @property
    def final_price(self):
        return self.section.base_price * self.price_modifier
```

#### **CapacityManager Service**
```python
class CapacityManager:
    @staticmethod
    def validate_venue_capacity(venue, performances):
        total_capacity = sum(p.max_capacity for p in performances)
        if total_capacity > venue.total_capacity:
            raise ValidationError('Total performance capacity exceeds venue capacity')
    
    @staticmethod
    def create_performance_capacity(performance, capacity_config):
        # Create complete capacity structure
        pass
    
    @staticmethod
    def reserve_seats(performance, ticket_type_id, section_name, count):
        # Reserve seats with validation
        pass
```

### **۲. سلسله‌مراتب جدید**

#### **ساختار صحیح**
```
✅ سلسله‌مراتب جدید:
Venue (2000)
├── Performance (1500) ✅ کمتر از venue
    ├── Section VIP (300)
    │   └── SectionTicketType VIP (300) ✅ برابر با section
    ├── Section Normal (800)
    │   └── SectionTicketType Normal (800) ✅ برابر با section
    └── Section Economy (400)
        └── SectionTicketType Economy (400) ✅ برابر با section
            └── Seat (150) ✅ منطقی
```

#### **Invariant های جدید**
```python
# ✅ Validation rules:
# 1. Venue.capacity ≥ Performance.max_capacity
# 2. Performance.max_capacity = Σ(Section.total_capacity)
# 3. Section.total_capacity = Σ(SectionTicketType.allocated_capacity)
# 4. SectionTicketType.allocated_capacity = available + reserved + sold
```

---

## 🔧 **استراتژی Migration**

### **مرحله ۱: آماده‌سازی**
```bash
# 1. Backup داده‌های موجود
python manage.py dumpdata events > events_backup.json

# 2. ایجاد مدل‌های جدید
python manage.py makemigrations events --name add_capacity_models

# 3. بررسی migration
python manage.py sqlmigrate events XXXX
```

### **مرحله ۲: Migration داده‌ها**
```python
def migrate_existing_capacity_data():
    # 1. برای هر Event
    for event in Event.objects.all():
        # 2. برای هر Performance
        for performance in event.performances.all():
            # 3. ایجاد Section ها بر اساس Seat های موجود
            sections_data = {}
            for seat in performance.seats.all():
                section_name = seat.section
                if section_name not in sections_data:
                    sections_data[section_name] = {'seats': [], 'ticket_types': set()}
                sections_data[section_name]['seats'].append(seat)
                if seat.ticket_type:
                    sections_data[section_name]['ticket_types'].add(seat.ticket_type)
            
            # 4. ایجاد EventSection ها
            for section_name, data in sections_data.items():
                total_seats = len(data['seats'])
                section = EventSection.objects.create(
                    performance=performance,
                    name=section_name,
                    total_capacity=total_seats,
                    available_capacity=total_seats,
                    base_price=100.00
                )
                
                # 5. ایجاد SectionTicketType ها
                if data['ticket_types']:
                    capacity_per_ticket = total_seats // len(data['ticket_types'])
                    for ticket_type in data['ticket_types']:
                        SectionTicketType.objects.create(
                            section=section,
                            ticket_type=ticket_type,
                            allocated_capacity=capacity_per_ticket,
                            available_capacity=capacity_per_ticket,
                            price_modifier=ticket_type.price_modifier
                        )
```

### **مرحله ۳: Validation و Testing**
```python
def validate_migration():
    for event in Event.objects.all():
        for performance in event.performances.all():
            # Check performance capacity
            total_section_capacity = sum(s.total_capacity for s in performance.sections.all())
            if total_section_capacity != performance.max_capacity:
                print(f"❌ Performance {performance.date}: Capacity mismatch")
            
            # Check section capacity
            for section in performance.sections.all():
                total_ticket_capacity = sum(stt.allocated_capacity for stt in section.ticket_types.all())
                if total_ticket_capacity != section.total_capacity:
                    print(f"❌ Section {section.name}: Capacity mismatch")
```

---

## 🚀 **مزایای سیستم جدید**

### **۱. یکپارچگی ظرفیت**
- ✅ `Venue.capacity ≥ Performance.max_capacity`
- ✅ `Performance.max_capacity = Σ(Section.total_capacity)`
- ✅ `Section.total_capacity = Σ(SectionTicketType.allocated_capacity)`

### **۲. مدیریت بهتر Section**
- ✅ مدل جداگانه برای Section
- ✅ ظرفیت مستقل برای هر Section
- ✅ قیمت‌گذاری مستقل برای هر Section

### **۳. انعطاف‌پذیری بیشتر**
- ✅ امکان داشتن چند TicketType در یک Section
- ✅ امکان تنظیم قیمت متفاوت برای هر Section
- ✅ امکان مدیریت ظرفیت دقیق‌تر

### **۴. Validation قوی‌تر**
- ✅ Database constraints
- ✅ Model-level validation
- ✅ Service-level validation

### **۵. Performance بهتر**
- ✅ کاهش تعداد queries
- ✅ استفاده از select_related و prefetch_related
- ✅ Indexing مناسب

---

## 📋 **توصیه‌های اجرایی**

### **اولویت ۱: فوری (1-2 هفته)**
1. **ایجاد مدل‌های جدید**: EventSection و SectionTicketType
2. **نوشتن migration scripts**: برای تبدیل داده‌های موجود
3. **تست روی محیط development**: قبل از deployment

### **اولویت ۲: میان‌مدت (2-4 هفته)**
1. **Migration داده‌ها**: اجرای migration scripts
2. **Validation و testing**: اطمینان از صحت migration
3. **بهینه‌سازی queries**: بهبود performance

### **اولویت ۳: بلندمدت (1-2 ماه)**
1. **Deployment به production**: بعد از تست کامل
2. **Monitoring و maintenance**: نظارت بر عملکرد
3. **بهبود مستمر**: بر اساس feedback

---

## ⚠️ **ریسک‌ها و راه‌حل‌ها**

### **ریسک ۱: از دست رفتن داده**
**راه‌حل**: Backup کامل قبل از migration

### **ریسک ۲: Downtime طولانی**
**راه‌حل**: Migration در ساعات کم‌ترافیک

### **ریسک ۳: عدم تطابق API**
**راه‌حل**: حفظ backward compatibility

### **ریسک ۴: Performance degradation**
**راه‌حل**: بهینه‌سازی queries و indexing

---

## 📊 **مقایسه قبل و بعد**

| جنبه | قبل | بعد |
|------|-----|-----|
| **یکپارچگی ظرفیت** | ❌ ناموجود | ✅ کامل |
| **مدیریت Section** | ❌ فقط string | ✅ مدل کامل |
| **Validation** | ❌ ناموجود | ✅ قوی |
| **Performance** | ❌ ضعیف | ✅ بهینه |
| **انعطاف‌پذیری** | ❌ محدود | ✅ بالا |
| **قابلیت نگهداری** | ❌ مشکل‌دار | ✅ آسان |

---

## 🎯 **نتیجه‌گیری**

سیستم ظرفیت فعلی Event در Peykan Tourism دارای مشکلات بحرانی است که نیاز به بازطراحی کامل دارد. راه‌حل پیشنهادی شامل:

1. **مدل‌های جدید**: EventSection و SectionTicketType
2. **Service جدید**: CapacityManager
3. **Validation قوی**: در تمام سطوح
4. **Migration strategy**: برای حفظ داده‌ها

این تغییرات منجر به:
- ✅ یکپارچگی کامل ظرفیت
- ✅ مدیریت بهتر Section
- ✅ انعطاف‌پذیری بیشتر
- ✅ Performance بهتر
- ✅ قابلیت نگهداری آسان‌تر

**توصیه**: اجرای این تغییرات در اسرع وقت برای جلوگیری از مشکلات بیشتر.

---

**تاریخ گزارش**: ۹ تیر ۱۴۰۴  
**وضعیت**: 🔴 نیاز به اقدام فوری  
**اولویت**: 🚨 بحرانی  
**زمان تخمینی**: ۴-۶ هفته 