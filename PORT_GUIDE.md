# راهنمای پورت‌ها و دسترسی به سرویس‌ها

## 📊 خلاصه پورت‌ها

### محیط Production (فعلی) - `docker-compose.production-secure.yml`

| سرویس | پورت داخلی | پورت خارجی | دسترسی از خارج | توضیحات |
|-------|------------|------------|----------------|---------|
| **Nginx** | 80, 443 | 80, 443 | ✅ بله | تنها نقطه ورود عمومی |
| **Backend (Django)** | 8000 | ❌ ندارد | ❌ خیر | فقط از طریق Nginx |
| **Frontend (Next.js)** | 3000 | ❌ ندارد | ❌ خیر | فقط از طریق Nginx |
| **PostgreSQL** | 5432 | ❌ ندارد | ❌ خیر | فقط شبکه داخلی |
| **Redis** | 6379 | ❌ ندارد | ❌ خیر | فقط شبکه داخلی |

### محیط Development - `docker-compose.production-dev.yml`

| سرویس | پورت داخلی | پورت خارجی | دسترسی از خارج | توضیحات |
|-------|------------|------------|----------------|---------|
| **Nginx** | 80 | 80 | ✅ بله | HTTP فقط |
| **Backend (Django)** | 8000 | 8000 | ✅ بله | دسترسی مستقیم |
| **Frontend (Next.js)** | 3000 | 3000 | ✅ بله | دسترسی مستقیم |
| **PostgreSQL** | 5432 | 5432 | ✅ بله | برای ابزارهای DB |
| **Redis** | 6379 | 6379 | ✅ بله | برای Redis CLI |

---

## 🔒 محیط Production (فعلی شما)

### معماری امنیتی

```
Internet
    ↓
┌─────────────────────────────────────────┐
│  Nginx (پورت 80, 443)                  │  ← تنها نقطه ورود عمومی
│  - SSL/TLS Termination                  │
│  - Reverse Proxy                        │
│  - Load Balancing                       │
└─────────────────────────────────────────┘
    ↓                    ↓
┌──────────────┐    ┌──────────────┐
│  Backend     │    │  Frontend    │
│  (8000)      │    │  (3000)      │
│  داخلی فقط   │    │  داخلی فقط   │
└──────────────┘    └──────────────┘
    ↓                    
┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │  Redis       │
│  (5432)      │    │  (6379)      │
│  داخلی فقط   │    │  داخلی فقط   │
└──────────────┘    └──────────────┘
```

### چگونه به سرویس‌ها دسترسی داشته باشیم؟

#### 1️⃣ دسترسی از اینترنت (عمومی)

```bash
# Frontend
https://peykantravelistanbul.com/
https://peykantravelistanbul.com/fa/
https://peykantravelistanbul.com/en/

# Backend API
https://peykantravelistanbul.com/api/v1/
https://peykantravelistanbul.com/api/v1/health/

# Admin Panel
https://peykantravelistanbul.com/admin/

# API Documentation
https://peykantravelistanbul.com/api/v1/schema/swagger/
```

#### 2️⃣ دسترسی از سرور (localhost)

```bash
# از طریق Nginx (پیشنهادی)
curl http://localhost/api/v1/health/
curl http://localhost/

# یا با HTTPS
curl https://localhost/api/v1/health/ -k
curl https://localhost/ -k
```

#### 3️⃣ دسترسی مستقیم به Container‌ها (فقط از داخل سرور)

```bash
# Backend - دسترسی مستقیم به Django
docker exec -it peykan_backend curl http://localhost:8000/api/v1/health/

# Frontend - دسترسی مستقیم به Next.js
docker exec -it peykan_frontend wget -qO- http://localhost:3000/api/health

# PostgreSQL - اتصال به دیتابیس
docker exec -it peykan_postgres psql -U peykan_user -d peykan

# Redis - اتصال به Redis
docker exec -it peykan_redis redis-cli -a "YOUR_REDIS_PASSWORD"

# دیدن لاگ‌ها
docker logs peykan_backend -f
docker logs peykan_frontend -f
docker logs peykan_nginx -f
```

#### 4️⃣ دسترسی از شبکه داخلی Docker

```bash
# از داخل یک container دیگر
docker exec -it peykan_backend curl http://frontend:3000/api/health
docker exec -it peykan_frontend curl http://backend:8000/api/v1/health/
```

---

## 🛠️ محیط Development

اگر بخواهید در حالت توسعه کار کنید:

### راه‌اندازی Development Mode

```bash
cd /home/djangouser/plusistanbul

# استفاده از docker-compose development
docker-compose -f docker-compose.production-dev.yml up -d
```

### دسترسی در Development Mode

```bash
# Backend - دسترسی مستقیم
curl http://localhost:8000/api/v1/health/
curl http://SERVER_IP:8000/api/v1/health/

# Frontend - دسترسی مستقیم
curl http://localhost:3000/
curl http://SERVER_IP:3000/

# PostgreSQL - از ابزارهای خارجی
psql -h localhost -p 5432 -U peykan_user -d peykan
# یا
psql -h SERVER_IP -p 5432 -U peykan_user -d peykan

# Redis - از Redis CLI خارجی
redis-cli -h localhost -p 6379 -a "YOUR_PASSWORD"
# یا
redis-cli -h SERVER_IP -p 6379 -a "YOUR_PASSWORD"
```

---

## 🔍 پورت‌های دیگر روی سرور

از خروجی `ss -tlnp` می‌بینیم:

```
پورت 80    → Nginx (Plusistanbul) - HTTP
پورت 443   → Nginx (Plusistanbul) - HTTPS
پورت 3000  → یک سرویس Next.js دیگر (احتمالاً خارج از Docker)
پورت 8080  → Nginx (Plus Project) - HTTP
پورت 8443  → Nginx (Plus Project) - HTTPS
```

**نکته مهم:** پورت 3000 در حال حاضر توسط یک process خارج از Docker استفاده می‌شود:
```
users:(("next-server (v1",pid=1682166,fd=22))
```

---

## 🎯 تفاوت‌های کلیدی Production vs Development

### Production (فعلی):
✅ **امنیت بالا:** فقط Nginx در معرض عموم  
✅ **SSL/HTTPS:** تمام ترافیک رمزنگاری شده  
✅ **شبکه داخلی:** Database و Redis قابل دسترسی نیستند  
✅ **Resource Limits:** محدودیت CPU و Memory  
❌ **دسترسی مستقیم:** نمی‌توانید مستقیماً به پورت 8000 یا 3000 دسترسی داشته باشید  

### Development:
✅ **دسترسی آسان:** تمام پورت‌ها expose شده‌اند  
✅ **Debug راحت:** می‌توانید مستقیماً به هر سرویس متصل شوید  
✅ **ابزارهای خارجی:** می‌توانید از pgAdmin, Redis Desktop Manager استفاده کنید  
❌ **امنیت کمتر:** تمام سرویس‌ها در معرض عموم  
❌ **بدون SSL:** فقط HTTP  

---

## 🚀 دستورات مفید

### مشاهده وضعیت سرویس‌ها

```bash
# وضعیت تمام container‌ها
docker ps --filter "name=peykan"

# وضعیت با جزئیات
docker-compose -f docker-compose.production-secure.yml ps

# Health check
docker inspect peykan_backend | grep -A 5 "Health"
```

### تست دسترسی

```bash
# تست Backend
curl -I http://localhost/api/v1/health/

# تست Frontend
curl -I http://localhost/

# تست HTTPS
curl -I https://localhost/api/v1/health/ -k

# تست از خارج سرور
curl -I https://peykantravelistanbul.com/api/v1/health/
```

### دیدن لاگ‌ها

```bash
# لاگ Backend
docker logs peykan_backend --tail 100 -f

# لاگ Frontend
docker logs peykan_frontend --tail 100 -f

# لاگ Nginx
docker logs peykan_nginx --tail 100 -f

# لاگ تمام سرویس‌ها
docker-compose -f docker-compose.production-secure.yml logs -f
```

### دسترسی به Shell

```bash
# Shell Backend (Django)
docker exec -it peykan_backend sh

# Shell Frontend (Next.js)
docker exec -it peykan_frontend sh

# Shell Database
docker exec -it peykan_postgres sh

# Django Shell
docker exec -it peykan_backend python manage.py shell
```

---

## 🔧 تغییر به Development Mode (موقت)

اگر می‌خواهید موقتاً پورت‌ها را expose کنید:

### گزینه 1: Port Forwarding با SSH

```bash
# از کامپیوتر محلی خود
ssh -L 8000:localhost:8000 djangouser@SERVER_IP
ssh -L 3000:localhost:3000 djangouser@SERVER_IP

# حالا می‌توانید در مرورگر خود باز کنید:
# http://localhost:8000/api/v1/health/
# http://localhost:3000/
```

### گزینه 2: تغییر موقت docker-compose

```bash
# ویرایش docker-compose.production-secure.yml
# uncomment کردن خطوط ports:

# Backend:
ports:
  - "8000:8000"

# Frontend:
ports:
  - "3000:3000"

# سپس restart
docker-compose -f docker-compose.production-secure.yml up -d
```

**⚠️ هشدار:** این کار را فقط برای debug موقت انجام دهید و بعد برگردانید!

---

## 📝 خلاصه

### در Production (فعلی):
- ✅ فقط از طریق دامنه: `https://peykantravelistanbul.com`
- ✅ یا از localhost سرور: `http://localhost` یا `https://localhost -k`
- ❌ دسترسی مستقیم به پورت 8000 و 3000 ندارید

### برای دسترسی مستقیم:
1. استفاده از `docker exec` برای دسترسی به container‌ها
2. استفاده از SSH Port Forwarding
3. تغییر به Development Mode
4. استفاده از `docker-compose.production-dev.yml`

### امنیت:
- Production mode امن‌تر است
- فقط Nginx در معرض عموم
- Database و Redis محافظت شده‌اند
- SSL/HTTPS فعال است

---

**آیا سوال دیگری دارید یا می‌خواهید یکی از این روش‌ها را امتحان کنیم؟**
