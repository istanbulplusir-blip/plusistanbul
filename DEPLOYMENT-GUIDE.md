# راهنمای Deploy Production - Peykan Tourism Platform

## 📋 پیش‌نیازها

### 1. نصب Docker و Docker Compose

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. تنظیم Environment Variables

فایل `backend/.env.production` را کپی کنید و مقادیر را تغییر دهید:

```bash
cp backend/env.production backend/.env.production
```

**مقادیر مهم که باید تغییر دهید:**

```bash
# Django Settings
SECRET_KEY=your-very-strong-secret-key-here-minimum-50-characters
DEBUG=False

# Database
POSTGRES_PASSWORD=your-strong-database-password

# Redis
REDIS_PASSWORD=your-strong-redis-password

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS
KAVENEGAR_API_KEY=your-kavenegar-api-key

# Payment
PAYMENT_SECRET_KEY=your-payment-secret-key
```

### 3. تولید SECRET_KEY قوی

```bash
# روش 1: استفاده از Django
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# روش 2: استفاده از OpenSSL
openssl rand -base64 50

# روش 3: استفاده از Python
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 🚀 مراحل Deploy

### 1. Deploy خودکار (پیشنهادی)

```bash
# اجرای اسکریپت Deploy
./deploy-production.sh
```

### 2. Deploy دستی

```bash
# 1. ایجاد دایرکتوری‌های مورد نیاز
mkdir -p postgres redis nginx/ssl backend/logs

# 2. تولید SSL certificates (موقت)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/CN=peykantravelistanbul.com"

# 3. اجرای سرویس‌ها
docker-compose -f docker-compose.production-secure.yml up -d --build

# 4. اجرای migrations
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py migrate

# 5. جمع‌آوری static files
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py collectstatic --noinput

# 6. ایجاد superuser
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py createsuperuser
```

## 🔐 تنظیمات امنیتی

### 1. SSL Certificates واقعی

```bash
# نصب Certbot
sudo apt install certbot python3-certbot-nginx

# دریافت SSL certificate
sudo certbot --nginx -d peykantravelistanbul.com -d www.peykantravelistanbul.com

# تنظیم auto-renewal
sudo crontab -e
# اضافه کردن این خط:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (CentOS)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 3. Database Backup

```bash
# ایجاد backup script
cat > backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose -f docker-compose.production-secure.yml exec -T postgres pg_dump -U peykan_user peykan > $BACKUP_DIR/backup_$DATE.sql

# حذف backup های قدیمی (بیش از 7 روز)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x backup-db.sh

# اضافه کردن به crontab
echo "0 2 * * * /path/to/backup-db.sh" | crontab -
```

## 📊 مانیتورینگ

### 1. بررسی وضعیت سرویس‌ها

```bash
# وضعیت containers
docker-compose -f docker-compose.production-secure.yml ps

# Logs
docker-compose -f docker-compose.production-secure.yml logs -f

# Resource usage
docker stats
```

### 2. Health Checks

```bash
# بررسی health endpoint
curl -f http://localhost/health

# بررسی database
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py check --database default

# بررسی Redis
docker-compose -f docker-compose.production-secure.yml exec redis redis-cli -a $REDIS_PASSWORD ping
```

## 🔧 عیب‌یابی

### مشکلات رایج:

#### 1. Database Connection Failed

```bash
# بررسی logs
docker-compose -f docker-compose.production-secure.yml logs postgres

# بررسی network
docker network ls
docker network inspect istanbulplus-v1-ir_peykan_internal
```

#### 2. Static Files Not Loading

```bash
# بررسی permissions
docker-compose -f docker-compose.production-secure.yml exec backend ls -la /app/staticfiles/

# جمع‌آوری مجدد static files
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py collectstatic --noinput --clear
```

#### 3. SSL Certificate Issues

```bash
# بررسی certificate
openssl x509 -in nginx/ssl/cert.pem -text -noout

# بررسی nginx config
docker-compose -f docker-compose.production-secure.yml exec nginx nginx -t
```

## 📈 بهینه‌سازی Performance

### 1. Database Optimization

```bash
# اجرای VACUUM
docker-compose -f docker-compose.production-secure.yml exec postgres psql -U peykan_user -d peykan -c "VACUUM ANALYZE;"

# بررسی slow queries
docker-compose -f docker-compose.production-secure.yml exec postgres psql -U peykan_user -d peykan -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### 2. Redis Optimization

```bash
# بررسی memory usage
docker-compose -f docker-compose.production-secure.yml exec redis redis-cli -a $REDIS_PASSWORD info memory

# پاک کردن cache
docker-compose -f docker-compose.production-secure.yml exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB
```

## 🔄 Update و Maintenance

### 1. Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose -f docker-compose.production-secure.yml up -d --build

# Run migrations
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py migrate
```

### 2. Cleanup

```bash
# حذف unused images
docker image prune -f

# حذف unused volumes
docker volume prune -f

# حذف unused networks
docker network prune -f
```

## 📞 پشتیبانی

در صورت بروز مشکل:

1. بررسی logs: `docker-compose -f docker-compose.production-secure.yml logs`
2. بررسی health checks
3. بررسی resource usage: `docker stats`
4. تماس با تیم پشتیبانی

---

**نکته مهم:** همیشه قبل از deploy در production، در محیط staging تست کنید.
