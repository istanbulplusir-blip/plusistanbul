# 🛡️ راهنمای نصب امن Peykan Tourism Platform

## ⚠️ اقدامات فوری (قبل از هر چیز)

### 1. بلاک کردن دسترسی بیرونی به Redis

```bash
# اجرای فوری (بدون قطع سرویس)
sudo bash security-fix-urgent.sh
```

### 2. بررسی وضعیت فعلی

```bash
# بررسی پورت‌های باز
sudo netstat -tulpn | grep -E ':(6379|5432|8000|3000)'

# بررسی دسترسی Redis
redis-cli -h your-server-ip -p 6379 ping
```

## 🔧 نصب کامل امن

### مرحله 1: آماده‌سازی سرور

```bash
# کپی پروژه
sudo cp -r peykan-tourism1 /opt/
cd /opt/peykan-tourism1

# اجرای اسکریپت نصب امن
sudo bash deploy-secure.sh
```

### مرحله 2: تنظیم متغیرهای محیطی

```bash
# کپی فایل امن
sudo cp backend/env.production-secure backend/.env.production

# ویرایش متغیرها
sudo nano backend/.env.production
```

**متغیرهای مهم:**

```bash
# تغییر این مقادیر الزامی است:
SECRET_KEY=your-very-long-random-secret-key-here
JWT_SECRET_KEY=different-jwt-secret-key-here
REDIS_PASSWORD=strong-redis-password-here
POSTGRES_PASSWORD=strong-postgres-password-here
```

### مرحله 3: تنظیم Redis

```bash
# ویرایش فایل Redis
sudo nano redis/redis.conf

# تغییر پسورد در فایل
requirepass YOUR_STRONG_REDIS_PASSWORD_HERE
```

### مرحله 4: تنظیم Nginx

```bash
# کپی فایل امن
sudo cp nginx/nginx-secure.conf nginx/nginx.conf

# تنظیم SSL certificates
sudo mkdir -p nginx/ssl
# قرار دادن cert.pem و key.pem در این مسیر
```

### مرحله 5: راه‌اندازی سرویس‌ها

```bash
# شروع سرویس‌ها
sudo systemctl start peykan-tourism

# بررسی وضعیت
sudo systemctl status peykan-tourism

# بررسی لاگ‌ها
sudo docker compose -f docker-compose.production-secure.yml logs -f
```

## 🔍 بررسی امنیت

### 1. تست دسترسی Redis

```bash
# باید خطا بدهد (دسترسی بسته)
redis-cli -h your-server-ip -p 6379 ping

# دسترسی داخلی (باید کار کند)
docker exec peykan_redis redis-cli -a YOUR_REDIS_PASSWORD ping
```

### 2. تست دسترسی Database

```bash
# باید خطا بدهد (دسترسی بسته)
psql -h your-server-ip -p 5432 -U peykan_user peykan

# دسترسی داخلی (باید کار کند)
docker exec peykan_postgres psql -U peykan_user peykan
```

### 3. بررسی فایروال

```bash
# بررسی قوانین UFW
sudo ufw status

# بررسی قوانین iptables
sudo iptables -L DOCKER-USER -n
```

## 📊 مانیتورینگ و نگهداری

### 1. پشتیبان‌گیری خودکار

```bash
# اضافه کردن به crontab
sudo crontab -e

# اضافه کردن این خط (هر روز ساعت 2 صبح)
0 2 * * * /opt/peykan-tourism1/backup-secure.sh
```

### 2. مانیتورینگ لاگ‌ها

```bash
# مانیتورینگ لاگ‌های Django
sudo docker logs -f peykan_backend

# مانیتورینگ لاگ‌های Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# مانیتورینگ fail2ban
sudo fail2ban-client status
```

### 3. به‌روزرسانی امنیتی

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# به‌روزرسانی Docker images
sudo docker compose -f docker-compose.production-secure.yml pull
sudo docker compose -f docker-compose.production-secure.yml up -d
```

## 🚨 عیب‌یابی

### مشکلات رایج:

#### 1. Redis دسترسی ندارد

```bash
# بررسی پسورد
docker exec peykan_redis redis-cli -a YOUR_PASSWORD ping

# بررسی فایل config
docker exec peykan_redis cat /usr/local/etc/redis/redis.conf | grep requirepass
```

#### 2. Database اتصال ندارد

```bash
# بررسی اتصال
docker exec peykan_postgres pg_isready -U peykan_user

# بررسی متغیرهای محیطی
docker exec peykan_backend env | grep DATABASE
```

#### 3. Nginx خطا می‌دهد

```bash
# بررسی تنظیمات
sudo nginx -t

# بررسی SSL certificates
sudo openssl x509 -in nginx/ssl/cert.pem -text -noout
```

## 📋 چک‌لیست امنیت

- [ ] Redis بدون دسترسی بیرونی
- [ ] Database بدون دسترسی بیرونی
- [ ] پسوردهای قوی تنظیم شده
- [ ] SSL certificates نصب شده
- [ ] فایروال فعال است
- [ ] fail2ban فعال است
- [ ] لاگ‌ها مانیتور می‌شوند
- [ ] پشتیبان‌گیری خودکار فعال است
- [ ] به‌روزرسانی‌های امنیتی نصب شده
- [ ] تنظیمات Django امن است

## 📞 پشتیبانی

در صورت بروز مشکل:

1. بررسی لاگ‌ها
2. تست اتصالات داخلی
3. بررسی تنظیمات فایروال
4. تماس با تیم فنی
