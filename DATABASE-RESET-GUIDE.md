# 🗑️ Database Reset Guide - Peykan Tourism Platform

## 🚨 مشکل: نیاز به پاک کردن کامل دیتابیس و migration ها

### علت مشکل:

- مشکلات migration و مدل‌ها
- تداخل در ساختار دیتابیس
- نیاز به شروع مجدد از ابتدا

## ✅ راه‌حل‌های پیشنهادی:

### 1. اجرای اسکریپت جامع (Linux/Mac)

```bash
# اجرای اسکریپت reset
./reset-database.sh
```

### 2. اجرای اسکریپت Windows

```cmd
# اجرای اسکریپت reset
reset-database.bat
```

### 3. اجرای مراحل دستی

```bash
# ورود به دایرکتوری backend
cd backend

# توقف سرویس‌ها
docker-compose -f ../docker-compose.production-secure.yml down

# حذف volumes دیتابیس
docker volume rm $(docker volume ls -q | grep -E "(postgres|redis)")

# حذف فایل‌های migration
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# حذف دیتابیس SQLite
rm -f db.sqlite3

# حذف cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# ایجاد migration های جدید
python manage.py makemigrations

# اجرای migration ها
python manage.py migrate

# جمع‌آوری static files
python manage.py collectstatic --noinput
```

## 🔧 بررسی مدل‌ها:

### 1. اجرای اسکریپت بررسی

```bash
# بررسی مدل‌ها
./check-models.sh
```

### 2. بررسی دستی

```bash
cd backend

# بررسی Django configuration
python manage.py check --deploy

# بررسی مدل‌ها
python manage.py check

# اعتبارسنجی مدل‌ها
python manage.py validate

# بررسی وضعیت migration ها
python manage.py showmigrations

# تست makemigrations
python manage.py makemigrations --dry-run
```

## 📋 مراحل کامل Reset:

### مرحله 1: توقف سرویس‌ها

```bash
docker-compose -f docker-compose.production-secure.yml down
```

### مرحله 2: حذف Database Volumes

```bash
# حذف PostgreSQL volume
docker volume rm $(docker volume ls -q | grep postgres)

# حذف Redis volume
docker volume rm $(docker volume ls -q | grep redis)

# یا حذف همه volumes
docker volume prune -f
```

### مرحله 3: حذف Migration Files

```bash
cd backend

# حذف همه migration files به جز __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# حذف migration files از هر app
apps=("agents" "car_rentals" "cart" "core" "events" "orders" "payments" "tours" "transfers" "users")

for app in "${apps[@]}"; do
    if [ -d "$app/migrations" ]; then
        find "$app/migrations" -name "*.py" -not -name "__init__.py" -delete
        find "$app/migrations" -name "*.pyc" -delete
    fi
done
```

### مرحله 4: حذف Database Files

```bash
# حذف SQLite database
rm -f db.sqlite3

# حذف سایر فایل‌های دیتابیس
rm -f *.db
rm -f *.sqlite
```

### مرحله 5: حذف Cache Files

```bash
# حذف Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### مرحله 6: ایجاد Migration های جدید

```bash
# ایجاد migration برای همه apps
python manage.py makemigrations

# یا ایجاد migration برای app خاص
python manage.py makemigrations agents
python manage.py makemigrations car_rentals
python manage.py makemigrations cart
python manage.py makemigrations core
python manage.py makemigrations events
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations tours
python manage.py makemigrations transfers
python manage.py makemigrations users
```

### مرحله 7: اجرای Migration ها

```bash
# اجرای همه migration ها
python manage.py migrate

# یا اجرای migration برای app خاص
python manage.py migrate agents
python manage.py migrate car_rentals
python manage.py migrate cart
python manage.py migrate core
python manage.py migrate events
python manage.py migrate orders
python manage.py migrate payments
python manage.py migrate tours
python manage.py migrate transfers
python manage.py migrate users
```

### مرحله 8: ایجاد Superuser

```bash
# ایجاد superuser
python manage.py createsuperuser
```

### مرحله 9: جمع‌آوری Static Files

```bash
# جمع‌آوری static files
python manage.py collectstatic --noinput
```

### مرحله 10: راه‌اندازی سرویس‌ها

```bash
cd ..
docker-compose -f docker-compose.production-secure.yml up -d
```

## 🔍 بررسی مشکلات مدل‌ها:

### مشکلات رایج:

1. **Missing Imports:**

   ```python
   # در models.py
   from django.db import models
   from django.contrib.auth.models import User
   ```

2. **Circular Imports:**

   ```python
   # استفاده از string references
   user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
   ```

3. **Invalid Field Definitions:**

   ```python
   # مثال صحیح
   status = models.CharField(max_length=20, choices=STATUS_CHOICES)
   ```

4. **Missing related_name:**
   ```python
   # مثال صحیح
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
   ```

### بررسی مدل‌ها:

```bash
# بررسی Django configuration
python manage.py check --deploy

# بررسی مدل‌ها
python manage.py check

# اعتبارسنجی مدل‌ها
python manage.py validate

# بررسی migration status
python manage.py showmigrations

# تست makemigrations
python manage.py makemigrations --dry-run
```

## 🚀 راه‌حل‌های جایگزین:

### 1. Reset کامل سیستم

```bash
# حذف کامل containers و volumes
docker-compose -f docker-compose.production-secure.yml down
docker system prune -a -f
docker volume prune -f

# Build مجدد
docker-compose -f docker-compose.production-secure.yml build --no-cache
docker-compose -f docker-compose.production-secure.yml up -d
```

### 2. Reset فقط دیتابیس

```bash
# توقف فقط دیتابیس
docker-compose -f docker-compose.production-secure.yml stop postgres

# حذف volume دیتابیس
docker volume rm $(docker volume ls -q | grep postgres)

# راه‌اندازی مجدد دیتابیس
docker-compose -f docker-compose.production-secure.yml up -d postgres

# اجرای migration ها
cd backend
python manage.py migrate
```

### 3. Backup قبل از Reset

```bash
# Backup دیتابیس
docker-compose -f docker-compose.production-secure.yml exec postgres pg_dump -U peykan_user peykan > backup.sql

# Restore دیتابیس
docker-compose -f docker-compose.production-secure.yml exec -T postgres psql -U peykan_user peykan < backup.sql
```

## 📋 Checklist:

- [ ] سرویس‌ها متوقف شده‌اند
- [ ] Database volumes حذف شده‌اند
- [ ] Migration files حذف شده‌اند
- [ ] Database files حذف شده‌اند
- [ ] Cache files حذف شده‌اند
- [ ] Migration های جدید ایجاد شده‌اند
- [ ] Migration ها اجرا شده‌اند
- [ ] Superuser ایجاد شده است
- [ ] Static files جمع‌آوری شده‌اند
- [ ] سرویس‌ها راه‌اندازی شده‌اند

## 🆘 در صورت ادامه مشکل:

### 1. بررسی Logs

```bash
# بررسی logs کامل
docker-compose -f docker-compose.production-secure.yml logs

# بررسی logs دیتابیس
docker-compose -f docker-compose.production-secure.yml logs postgres

# بررسی logs backend
docker-compose -f docker-compose.production-secure.yml logs backend
```

### 2. بررسی Model Issues

```bash
cd backend

# بررسی مدل‌ها
python manage.py check

# بررسی migration issues
python manage.py showmigrations

# تست makemigrations
python manage.py makemigrations --dry-run
```

### 3. بررسی Database Connectivity

```bash
# بررسی اتصال دیتابیس
docker-compose -f docker-compose.production-secure.yml exec postgres psql -U peykan_user -d peykan -c "SELECT 1;"

# بررسی Django database
cd backend
python manage.py dbshell
```

---

**نکته مهم:** این عملیات تمام داده‌های موجود را حذف می‌کند. قبل از اجرا از داده‌های مهم backup تهیه کنید.
