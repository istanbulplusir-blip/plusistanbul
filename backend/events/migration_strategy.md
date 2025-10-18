# استراتژی Migration برای سیستم ظرفیت Event

## 🎯 **هدف**
تبدیل سیستم ظرفیت فعلی (مشکل‌دار) به سیستم یکپارچه جدید با حفظ داده‌های موجود.

## 📋 **مراحل Migration**

### **مرحله ۱: آماده‌سازی**
```python
# 1. Backup داده‌های موجود
python manage.py dumpdata events > events_backup.json

# 2. ایجاد مدل‌های جدید
python manage.py makemigrations events --name add_capacity_models

# 3. بررسی migration بدون اجرا
python manage.py sqlmigrate events XXXX
```

### **مرحله ۲: Migration داده‌ها**
```python
# اسکریپت migration
def migrate_existing_capacity_data():
    """
    Migrate existing capacity data to new structure.
    """
    
    # 1. برای هر Event
    for event in Event.objects.all():
        print(f"Migrating event: {event.title}")
        
        # 2. برای هر Performance
        for performance in event.performances.all():
            print(f"  - Performance: {performance.date}")
            
            # 3. ایجاد Section ها بر اساس Seat های موجود
            sections_data = {}
            for seat in performance.seats.all():
                section_name = seat.section
                if section_name not in sections_data:
                    sections_data[section_name] = {
                        'seats': [],
                        'ticket_types': set()
                    }
                sections_data[section_name]['seats'].append(seat)
                if seat.ticket_type:
                    sections_data[section_name]['ticket_types'].add(seat.ticket_type)
            
            # 4. ایجاد EventSection ها
            for section_name, data in sections_data.items():
                # محاسبه ظرفیت section
                total_seats = len(data['seats'])
                
                # ایجاد section
                section = EventSection.objects.create(
                    performance=performance,
                    name=section_name,
                    total_capacity=total_seats,
                    available_capacity=total_seats,
                    base_price=100.00  # قیمت پیش‌فرض
                )
                
                # 5. ایجاد SectionTicketType ها
                if data['ticket_types']:
                    # تقسیم ظرفیت بین ticket types
                    capacity_per_ticket = total_seats // len(data['ticket_types'])
                    remaining_capacity = total_seats % len(data['ticket_types'])
                    
                    for i, ticket_type in enumerate(data['ticket_types']):
                        allocated_capacity = capacity_per_ticket
                        if i < remaining_capacity:
                            allocated_capacity += 1
                        
                        SectionTicketType.objects.create(
                            section=section,
                            ticket_type=ticket_type,
                            allocated_capacity=allocated_capacity,
                            available_capacity=allocated_capacity,
                            price_modifier=ticket_type.price_modifier
                        )
                else:
                    # اگر ticket type نداشت، یک default ایجاد کن
                    default_ticket = event.ticket_types.first()
                    if default_ticket:
                        SectionTicketType.objects.create(
                            section=section,
                            ticket_type=default_ticket,
                            allocated_capacity=total_seats,
                            available_capacity=total_seats,
                            price_modifier=1.00
                        )
            
            # 6. به‌روزرسانی Performance capacity
            total_performance_capacity = sum(
                section.total_capacity for section in performance.sections.all()
            )
            performance.max_capacity = total_performance_capacity
            performance.current_capacity = 0
            performance.save()
```

### **مرحله ۳: Validation و Testing**
```python
def validate_migration():
    """
    Validate that migration was successful.
    """
    
    for event in Event.objects.all():
        print(f"Validating event: {event.title}")
        
        for performance in event.performances.all():
            # Check performance capacity
            total_section_capacity = sum(
                s.total_capacity for s in performance.sections.all()
            )
            
            if total_section_capacity != performance.max_capacity:
                print(f"  ❌ Performance {performance.date}: Capacity mismatch")
                print(f"     Expected: {performance.max_capacity}, Actual: {total_section_capacity}")
            
            # Check section capacity
            for section in performance.sections.all():
                total_ticket_capacity = sum(
                    stt.allocated_capacity for stt in section.ticket_types.all()
                )
                
                if total_ticket_capacity != section.total_capacity:
                    print(f"  ❌ Section {section.name}: Capacity mismatch")
                    print(f"     Expected: {section.total_capacity}, Actual: {total_ticket_capacity}")
                
                # Check capacity components
                total_components = (
                    section.available_capacity + 
                    section.reserved_capacity + 
                    section.sold_capacity
                )
                
                if total_components != section.total_capacity:
                    print(f"  ❌ Section {section.name}: Component mismatch")
                    print(f"     Expected: {section.total_capacity}, Actual: {total_components}")
```

### **مرحله ۴: Rollback Plan**
```python
def rollback_migration():
    """
    Rollback migration if needed.
    """
    
    # 1. حذف مدل‌های جدید
    SectionTicketType.objects.all().delete()
    EventSection.objects.all().delete()
    
    # 2. بازگردانی داده‌های قدیمی
    # (از backup)
    
    # 3. حذف migration
    # python manage.py migrate events XXXX --reverse
```

## 🔧 **تغییرات در مدل‌های موجود**

### **EventPerformance Model**
```python
class EventPerformance(BaseScheduleModel):
    # حذف فیلدهای تکراری
    # ticket_capacities = models.JSONField()  # ❌ حذف شود
    
    # اضافه کردن validation
    def clean(self):
        super().clean()
        # Validate against venue capacity
        if self.max_capacity > self.event.venue.total_capacity:
            raise ValidationError('Performance capacity cannot exceed venue capacity')
    
    def save(self, *args, **kwargs):
        # Auto-calculate capacity from sections
        if not self.pk:  # New performance
            self.max_capacity = 0
            self.current_capacity = 0
        super().save(*args, **kwargs)
```

### **Seat Model**
```python
class Seat(BaseModel):
    # تغییر relationship
    section = models.ForeignKey(
        'EventSection',  # جدید
        on_delete=models.CASCADE,
        related_name='seats',
        verbose_name=_('Section')
    )
    
    # حذف ticket_type از Seat (به SectionTicketType منتقل می‌شود)
    # ticket_type = models.ForeignKey(...)  # ❌ حذف شود
    
    def save(self, *args, **kwargs):
        # Validate seat number uniqueness within section
        if Seat.objects.filter(
            section=self.section,
            seat_number=self.seat_number,
            row_number=self.row_number
        ).exclude(id=self.id).exists():
            raise ValidationError('Seat already exists in this section')
        super().save(*args, **kwargs)
```

## 📊 **مقایسه قبل و بعد**

### **قبل (مشکل‌دار)**
```
Venue (2000) 
├── Performance (1000) ❌ کمتر از venue
    ├── TicketType VIP (1000) ❌ بیشتر از performance
    ├── TicketType Normal (1000) ❌ بیشتر از performance  
    └── TicketType Economy (1000) ❌ بیشتر از performance
        └── Seat (150) ❌ بسیار کمتر از capacity
```

### **بعد (صحیح)**
```
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

## ⚠️ **نکات مهم**

### **۱. Backward Compatibility**
- حفظ API های موجود تا زمان migration کامل
- ایجاد wrapper functions برای compatibility

### **۲. Performance**
- استفاده از select_related و prefetch_related
- Indexing مناسب برای queries

### **۳. Testing**
- تست کامل قبل از deployment
- تست rollback scenario
- تست performance impact

## 📅 **Timeline**

### **هفته ۱: آماده‌سازی**
- [ ] ایجاد مدل‌های جدید
- [ ] نوشتن migration scripts
- [ ] تست روی محیط development

### **هفته ۲: Migration**
- [ ] Backup داده‌ها
- [ ] اجرای migration
- [ ] Validation و testing

### **هفته ۳: بهینه‌سازی**
- [ ] بهینه‌سازی queries
- [ ] اضافه کردن indexes
- [ ] تست performance

### **هفته ۴: Deployment**
- [ ] Deployment به staging
- [ ] تست نهایی
- [ ] Deployment به production 