# 🚀 راهنمای راه‌اندازی Production - Peykan Tourism Platform

## 📋 خلاصه تغییرات انجام شده

### ✅ به‌روزرسانی‌های انجام شده:

1. **حذف فایل‌های قدیمی:**

   - `security-fix-urgent.sh` (حذف شد)
   - `deploy-secure.sh` (حذف شد)
   - `backend/env.production` (حذف شد)

2. **به‌روزرسانی نسخه‌ها:**

   - Python: 3.11 → 3.12
   - Node.js: 18 → 20 LTS
   - PostgreSQL: 15 → 16
   - Django: 4.2.7 → 5.0.1
   - DRF: 3.14.0 → 3.15.2
   - Gunicorn: 21.2.0 → 22.0.0

3. **بهبود امنیت:**
   - SSL certificates با RSA 4096
   - تنظیمات امنیتی بهتر
   - Template جدید برای environment variables

## 🛠️ مراحل راه‌اندازی

### 1. آماده‌سازی Environment

```bash
# کپی کردن template
cp backend/env.production.template backend/.env.production

# ویرایش فایل environment
nano backend/.env.production
```

### 2. تنظیم مقادیر مهم

```bash
# تولید SECRET_KEY قوی
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# تولید پسوردهای قوی
openssl rand -base64 32
```

### 3. راه‌اندازی Production

```bash
# اجرای اسکریپت deploy
./deploy-production.sh
```

### 4. تنظیم SSL واقعی

```bash
# نصب Certbot
sudo apt install certbot python3-certbot-nginx

# دریافت SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تنظیم auto-renewal
sudo crontab -e
# اضافه کردن: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔐 تنظیمات امنیتی

### Firewall Configuration

```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# بلاک کردن پورت‌های داخلی
sudo iptables -I DOCKER-USER -p tcp --dport 5432 -j DROP
sudo iptables -I DOCKER-USER -p tcp --dport 6379 -j DROP
sudo iptables -I DOCKER-USER -p tcp --dport 8000 -j DROP
sudo iptables -I DOCKER-USER -p tcp --dport 3000 -j DROP
```

### Fail2ban Configuration

```bash
sudo apt install fail2ban

# تنظیم jail.local
sudo nano /etc/fail2ban/jail.local
```

## 📊 مانیتورینگ

### Health Checks

```bash
# بررسی وضعیت سرویس‌ها
docker-compose -f docker-compose.production-secure.yml ps

# بررسی logs
docker-compose -f docker-compose.production-secure.yml logs -f

# بررسی health endpoint
curl -f https://yourdomain.com/health
```

### Backup Strategy

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

## 🔄 به‌روزرسانی

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose -f docker-compose.production-secure.yml up -d --build

# Run migrations
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.production-secure.yml exec backend python manage.py collectstatic --noinput
```

### Cleanup

```bash
# حذف unused images
docker image prune -f

# حذف unused volumes
docker volume prune -f

# حذف unused networks
docker network prune -f
```

## 🚨 عیب‌یابی

### مشکلات رایج:

1. **Database Connection Failed**

   ```bash
   docker-compose -f docker-compose.production-secure.yml logs postgres
   ```

2. **Static Files Not Loading**

   ```bash
   docker-compose -f docker-compose.production-secure.yml exec backend python manage.py collectstatic --noinput --clear
   ```

3. **SSL Certificate Issues**
   ```bash
   openssl x509 -in nginx/ssl/cert.pem -text -noout
   ```

## 📞 پشتیبانی

در صورت بروز مشکل:

1. بررسی logs: `docker-compose -f docker-compose.production-secure.yml logs`
2. بررسی health checks
3. بررسی resource usage: `docker stats`
4. تماس با تیم پشتیبانی

---

**نکته مهم:** همیشه قبل از deploy در production، در محیط staging تست کنید.

## 🔗 لینک‌های مفید

- [Django 5.0 Release Notes](https://docs.djangoproject.com/en/5.0/releases/5.0/)
- [Node.js 20 LTS](https://nodejs.org/en/blog/release/v20.0.0)
- [PostgreSQL 16](https://www.postgresql.org/docs/16/release-16.html)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
