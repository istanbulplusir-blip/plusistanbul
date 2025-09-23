# چک‌لیست استقرار پروژه Peykan Tourism

## 📋 فهرست مطالب
- [قبل از استقرار](#قبل-از-استقرار)
- [تنظیمات سرور](#تنظیمات-سرور)
- [تنظیمات پایگاه داده](#تنظیمات-پایگاه-داده)
- [تنظیمات امنیتی](#تنظیمات-امنیتی)
- [تنظیمات مانیتورینگ](#تنظیمات-مانیتورینگ)
- [مراحل استقرار](#مراحل-استقرار)
- [بعد از استقرار](#بعد-از-استقرار)
- [روال‌های اضطراری](#روال‌های-اضطراری)
- [قالب‌های دستورات](#قالب‌های-دستورات)

## 🔍 قبل از استقرار

### ✅ بررسی کد
- [ ] تمام تست‌ها موفق اجرا می‌شوند
- [ ] کد linting بدون خطا است
- [ ] تمام merge conflicts حل شده‌اند
- [ ] کد review انجام شده است
- [ ] مستندات API بروزرسانی شده است

### ✅ بررسی متغیرهای محیطی
- [ ] فایل `backend/.env` با مقادیر تولید تنظیم شده
- [ ] فایل `frontend/.env.local` با مقادیر تولید تنظیم شده
- [ ] کلیدهای API معتبر هستند
- [ ] تنظیمات پایگاه داده صحیح است
- [ ] تنظیمات Redis صحیح است

### ✅ بررسی امنیت
- [ ] `DEBUG=False` تنظیم شده
- [ ] `SECRET_KEY` تغییر کرده
- [ ] `ALLOWED_HOSTS` تنظیم شده
- [ ] CORS تنظیمات صحیح دارد
- [ ] فایل‌های حساس در `.gitignore` هستند

### ✅ بررسی عملکرد
- [ ] تصاویر بهینه‌سازی شده‌اند
- [ ] فایل‌های استاتیک فشرده شده‌اند
- [ ] کش‌ها فعال شده‌اند
- [ ] CDN تنظیم شده (در صورت نیاز)

## 🖥️ تنظیمات سرور

### ✅ پیش‌نیازهای سرور
- [ ] Ubuntu 20.04+ یا CentOS 8+ نصب شده
- [ ] Docker و Docker Compose نصب شده
- [ ] Nginx نصب شده (اختیاری)
- [ ] SSL certificate نصب شده
- [ ] Firewall تنظیم شده

### ✅ دسترسی‌ها
- [ ] SSH key authentication فعال است
- [ ] User با sudo privileges ایجاد شده
- [ ] Docker user در docker group است
- [ ] پورت‌های ضروری باز هستند (80, 443, 22)

### ✅ فضای دیسک
- [ ] حداقل 10GB فضای آزاد
- [ ] Volume برای PostgreSQL تنظیم شده
- [ ] Volume برای Redis تنظیم شده
- [ ] Volume برای media files تنظیم شده

## 🗄️ تنظیمات پایگاه داده

### ✅ PostgreSQL
- [ ] PostgreSQL 15+ نصب شده
- [ ] Database `peykan` ایجاد شده
- [ ] User `peykan_user` ایجاد شده
- [ ] Password قوی تنظیم شده
- [ ] Backup strategy تعریف شده

### ✅ Redis
- [ ] Redis 7+ نصب شده
- [ ] Password تنظیم شده (اختیاری)
- [ ] Persistence فعال شده
- [ ] Memory limits تنظیم شده

### ✅ Backup
- [ ] Automated backup script تنظیم شده
- [ ] Backup retention policy تعریف شده
- [ ] Backup testing انجام شده
- [ ] Restore procedure تست شده

## 🔒 تنظیمات امنیتی

### ✅ SSL/TLS
- [ ] SSL certificate معتبر نصب شده
- [ ] HTTPS redirect فعال شده
- [ ] HSTS header تنظیم شده
- [ ] SSL configuration بهینه شده

### ✅ Firewall
- [ ] UFW یا iptables فعال شده
- [ ] فقط پورت‌های ضروری باز هستند
- [ ] SSH access محدود شده
- [ ] Fail2ban نصب شده

### ✅ Docker Security
- [ ] Docker daemon با TLS تنظیم شده
- [ ] Non-root user برای containers
- [ ] Resource limits تنظیم شده
- [ ] Security scanning انجام شده

### ✅ Application Security
- [ ] Rate limiting فعال شده
- [ ] CORS policy تنظیم شده
- [ ] CSRF protection فعال شده
- [ ] XSS protection فعال شده

## 📊 تنظیمات مانیتورینگ

### ✅ Logging
- [ ] Centralized logging تنظیم شده
- [ ] Log rotation فعال شده
- [ ] Log retention policy تعریف شده
- [ ] Error alerting تنظیم شده

### ✅ Monitoring
- [ ] Health checks فعال شده
- [ ] Resource monitoring تنظیم شده
- [ ] Performance metrics جمع‌آوری می‌شود
- [ ] Alerting rules تعریف شده

### ✅ Backup Monitoring
- [ ] Backup success monitoring
- [ ] Backup size monitoring
- [ ] Restore testing automation
- [ ] Backup failure alerting

## 🚀 مراحل استقرار

### مرحله 1: آماده‌سازی
```bash
# بروزرسانی سرور
sudo apt update && sudo apt upgrade -y

# نصب Docker (اگر نصب نیست)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# نصب Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### مرحله 2: کلون کردن پروژه
```bash
# کلون کردن مخزن
git clone https://github.com/PeykanTravel/peykan-tourism.git
cd peykan-tourism

# تنظیم فایل‌های محیطی
cp backend/env.example backend/.env
cp frontend/.env.example frontend/.env.local

# ویرایش فایل‌های محیطی
nano backend/.env
nano frontend/.env.local
```

### مرحله 3: استقرار
```bash
# راه‌اندازی سرویس‌ها
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# انتظار برای آماده شدن سرویس‌ها
sleep 30

# اجرای migration ها
docker-compose exec backend python manage.py migrate

# جمع‌آوری فایل‌های استاتیک
docker-compose exec backend python manage.py collectstatic --noinput

# ایجاد superuser
docker-compose exec backend python manage.py createsuperuser
```

### مرحله 4: تست
```bash
# بررسی وضعیت سرویس‌ها
docker-compose ps

# تست health checks
curl -f http://localhost:8000/api/v1/health/
curl -f http://localhost:3000/

# بررسی لاگ‌ها
docker-compose logs --tail=50
```

## ✅ بعد از استقرار

### بررسی عملکرد
- [ ] تمام سرویس‌ها در حال اجرا هستند
- [ ] Health checks موفق هستند
- [ ] API endpoints پاسخ می‌دهند
- [ ] Frontend قابل دسترسی است
- [ ] Database connections موفق هستند

### بررسی امنیت
- [ ] HTTPS فعال است
- [ ] SSL certificate معتبر است
- [ ] Admin panel محافظت شده است
- [ ] API rate limiting کار می‌کند
- [ ] CORS policy درست کار می‌کند

### بررسی عملکرد
- [ ] Page load times قابل قبول هستند
- [ ] Database queries بهینه هستند
- [ ] Cache hit rates بالا هستند
- [ ] Memory usage در حد نرمال است
- [ ] CPU usage در حد نرمال است

### تست کاربری
- [ ] ثبت‌نام و ورود کار می‌کند
- [ ] جستجوی تورها کار می‌کند
- [ ] رزرو تور کار می‌کند
- [ ] پرداخت کار می‌کند
- [ ] پروفایل کاربر کار می‌کند

## 🔄 به‌روزرسانی

### مراحل به‌روزرسانی
```bash
# کشیدن تغییرات جدید
git pull origin main

# بررسی تغییرات
git log --oneline -10

# Backup از پایگاه داده
docker-compose exec postgres pg_dump -U peykan_user peykan > backup_$(date +%Y%m%d_%H%M%S).sql

# Rebuild و restart سرویس‌ها
docker-compose -f docker-compose.yml -f docker-compose.production.yml build
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# اجرای migration ها
docker-compose exec backend python manage.py migrate

# جمع‌آوری فایل‌های استاتیک
docker-compose exec backend python manage.py collectstatic --noinput

# بررسی وضعیت
docker-compose ps
curl -f http://localhost:8000/api/v1/health/
```

## 🚨 روال‌های اضطراری

### Rollback
```bash
# توقف سرویس‌ها
docker-compose down

# بازگشت به نسخه قبلی
git checkout HEAD~1

# راه‌اندازی مجدد
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# Restore database (در صورت نیاز)
docker-compose exec -T postgres psql -U peykan_user peykan < backup_file.sql
```

### Emergency Maintenance
```bash
# فعال کردن maintenance mode
docker-compose exec backend python manage.py maintenance_mode on

# انجام کارهای نگهداری
# ...

# غیرفعال کردن maintenance mode
docker-compose exec backend python manage.py maintenance_mode off
```

### Database Recovery
```bash
# توقف سرویس‌ها
docker-compose stop backend frontend

# Restore database
docker-compose exec -T postgres psql -U peykan_user peykan < backup_file.sql

# راه‌اندازی مجدد سرویس‌ها
docker-compose start backend frontend
```

## 📝 قالب‌های دستورات

### بررسی وضعیت
```bash
# وضعیت سرویس‌ها
docker-compose ps

# استفاده از منابع
docker stats

# لاگ‌های اخیر
docker-compose logs --tail=100

# لاگ سرویس خاص
docker-compose logs -f backend
```

### مدیریت پایگاه داده
```bash
# Backup
docker-compose exec postgres pg_dump -U peykan_user peykan > backup.sql

# Restore
docker-compose exec -T postgres psql -U peykan_user peykan < backup.sql

# Migration
docker-compose exec backend python manage.py migrate

# Shell
docker-compose exec backend python manage.py shell
```

### مدیریت فایل‌ها
```bash
# جمع‌آوری فایل‌های استاتیک
docker-compose exec backend python manage.py collectstatic --noinput

# پاک کردن cache
docker-compose exec redis redis-cli FLUSHALL

# بررسی فضای دیسک
docker system df
```

### مدیریت کاربران
```bash
# ایجاد superuser
docker-compose exec backend python manage.py createsuperuser

# تغییر رمز کاربر
docker-compose exec backend python manage.py changepassword username

# لیست کاربران
docker-compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print([u.email for u in User.objects.all()])"
```

---

## 📞 پشتیبانی اضطراری

### تماس‌های اضطراری
- **تیم توسعه**: @PeykanDev (تلگرام)
- **مدیر سیستم**: sysadmin@peykantravelistanbul.com
- **پشتیبانی فنی**: support@peykantravelistanbul.com

### مستندات اضافی
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)

**نکته**: این چک‌لیست باید قبل از هر استقرار بررسی شود و در صورت نیاز به‌روزرسانی شود. 