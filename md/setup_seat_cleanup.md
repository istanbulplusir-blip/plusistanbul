# راه‌اندازی خودکار آزادسازی صندلی‌های منقضی شده

## **مشکل:**

صندلی‌های رزرو موقت بعد از نیم ساعت آزاد نمی‌شوند.

## **راه‌حل‌های موجود:**

### **1. Celery Beat (توصیه شده)**

Celery Beat هر 5 دقیقه task `cleanup_expired_reservations` را اجرا می‌کند.

**راه‌اندازی:**

```bash
# Terminal 1: Start Celery Worker
python manage.py start_celery_worker

# Terminal 2: Start Celery Beat
python manage.py start_celery_beat
```

**تنظیمات در `settings.py`:**

```python
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-reservations': {
        'task': 'events.tasks.cleanup_expired_reservations',
        'schedule': 300.0,  # Every 5 minutes
    },
}
```

### **2. Management Command**

اجرای دستی command برای آزادسازی صندلی‌ها:

```bash
python manage.py expire_event_holds
```

### **3. Cron Job (Linux/Unix)**

اضافه کردن به crontab:

```bash
# Edit crontab
crontab -e

# Add this line (runs every 5 minutes)
*/5 * * * * cd /path/to/peykan-tourism1/backend && python manage.py expire_event_holds
```

### **4. Windows Task Scheduler**

برای Windows:

1. Task Scheduler را باز کنید
2. Create Basic Task
3. Name: "Seat Cleanup"
4. Trigger: Every 5 minutes
5. Action: Start a program
6. Program: `python`
7. Arguments: `manage.py expire_event_holds`
8. Start in: `C:\path\to\peykan-tourism1\backend`

## **تست عملکرد:**

### **بررسی وضعیت صندلی‌ها:**

```bash
python check_seats.py
```

### **تست Celery Task:**

```bash
python test_celery_cleanup.py
```

## **نظارت و لاگ:**

### **Celery Logs:**

```bash
# Check Celery worker logs
tail -f celery.log

# Check Celery beat logs
tail -f celerybeat.log
```

### **Django Logs:**

```python
# In settings.py
LOGGING = {
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'events.tasks': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## **عیب‌یابی:**

### **مشکل: Celery Worker اجرا نمی‌شود**

```bash
# Check Redis connection
redis-cli ping

# Check Celery status
celery -A peykan status
```

### **مشکل: Tasks اجرا نمی‌شوند**

```bash
# Check periodic tasks
python manage.py shell -c "from django_celery_beat.models import PeriodicTask; print(PeriodicTask.objects.all())"
```

### **مشکل: صندلی‌ها آزاد نمی‌شوند**

```bash
# Check seat status
python manage.py shell -c "from events.models import Seat; print(Seat.objects.filter(status='reserved').count())"

# Manual cleanup
python manage.py expire_event_holds
```

## **بهینه‌سازی:**

### **1. کاهش فاصله زمانی:**

```python
# در settings.py - هر 2 دقیقه
'schedule': 120.0,
```

### **2. Batch Processing:**

```python
# در tasks.py - پردازش گروهی
@shared_task(bind=True, name='events.cleanup_expired_reservations')
def cleanup_expired_reservations(self):
    # Process in batches of 100
    batch_size = 100
    # ... rest of the code
```

### **3. Monitoring:**

```python
# اضافه کردن metrics
from django.core.cache import cache

def record_cleanup_metrics(seats_released):
    cache.set('cleanup_metrics', {
        'last_run': timezone.now(),
        'seats_released': seats_released,
        'total_runs': cache.get('cleanup_total_runs', 0) + 1
    })
```

## **نتیجه‌گیری:**

با راه‌اندازی Celery Beat، صندلی‌های منقضی شده هر 5 دقیقه به طور خودکار آزاد می‌شوند.
