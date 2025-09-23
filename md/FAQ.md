# Frequently Asked Questions (FAQ) - Peykan Tourism

## 🚀 Getting Started

### **Q: چطور پروژه را راه‌اندازی کنم؟**
**A**: ساده‌ترین راه استفاده از اسکریپت خودکار است:

```bash
# Windows
.\setup-dev.ps1

# Linux/Mac
./setup-dev.sh
```

یا به صورت دستی:
```bash
git clone https://github.com/PeykanTravel/peykan-tourism.git
cd peykan-tourism
docker-compose up -d
```

### **Q: چه پیش‌نیازهایی نیاز دارم؟**
**A**: 
- **Docker Desktop** (توصیه شده)
- **Git**
- **Node.js 18+** (اگر بدون Docker)
- **Python 3.11+** (اگر بدون Docker)
- **PostgreSQL** (اگر بدون Docker)

### **Q: چطور بفهمم همه چیز درست کار می‌کند؟**
**A**: بعد از راه‌اندازی، این آدرس‌ها را چک کنید:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

---

## 🔧 Development

### **Q: چطور کد جدید اضافه کنم؟**
**A**: 
1. Branch جدید بسازید: `git checkout -b feature/your-feature`
2. کد بنویسید و تست کنید
3. Commit کنید: `git commit -m "feat: add your feature"`
4. Push کنید: `git push origin feature/your-feature`
5. Pull Request بسازید

### **Q: چطور تست‌ها را اجرا کنم؟**
**A**: 
```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm test

# All tests
docker-compose exec backend python manage.py test && docker-compose exec frontend npm test
```

### **Q: چطور migration جدید بسازم؟**
**A**: 
```bash
# Create migration
docker-compose exec backend python manage.py makemigrations

# Apply migration
docker-compose exec backend python manage.py migrate

# Check migration status
docker-compose exec backend python manage.py showmigrations
```

### **Q: چطور superuser بسازم؟**
**A**: 
```bash
docker-compose exec backend python manage.py createsuperuser
```

---

## 🐛 Troubleshooting

### **Q: Docker نمی‌آید بالا، چه کار کنم؟**
**A**: 
1. بررسی کنید Docker Desktop اجرا است
2. کانتینرها را پاک کنید: `docker-compose down`
3. دوباره بسازید: `docker-compose up -d --build`
4. لاگ‌ها را ببینید: `docker-compose logs -f`

### **Q: خطای "Database connection failed" می‌گیرم**
**A**: 
1. بررسی کنید PostgreSQL اجرا است
2. Migration ها را اجرا کنید: `docker-compose exec backend python manage.py migrate`
3. دیتابیس را ریست کنید: `docker-compose down -v && docker-compose up -d`

### **Q: Frontend لود نمی‌شود**
**A**: 
1. بررسی کنید frontend container اجرا است: `docker-compose ps`
2. لاگ‌ها را ببینید: `docker-compose logs frontend`
3. ریستارت کنید: `docker-compose restart frontend`

### **Q: API endpoints کار نمی‌کنند**
**A**: 
1. بررسی کنید backend اجرا است
2. CORS settings را چک کنید
3. API URL را در frontend بررسی کنید
4. لاگ‌های backend را ببینید

---

## 🔒 Security

### **Q: چطور environment variables را تنظیم کنم؟**
**A**: 
1. فایل `backend/.env` بسازید
2. از `backend/env.example` کپی کنید
3. مقادیر را تغییر دهید
4. هرگز فایل `.env` را commit نکنید

### **Q: چطور SSL certificate اضافه کنم؟**
**A**: 
1. فایل‌های SSL را در `nginx/ssl/` قرار دهید
2. `nginx/nginx.conf` را تنظیم کنید
3. Nginx را ریستارت کنید: `docker-compose restart nginx`

### **Q: چطور امنیت را بهبود دهم؟**
**A**: 
- از HTTPS استفاده کنید
- Environment variables را محافظت کنید
- Regular updates انجام دهید
- Security tests اجرا کنید
- [Security Guide](./SECURITY.md) را مطالعه کنید

---

## 🚀 Deployment

### **Q: چطور روی سرور دیپلوی کنم؟**
**A**: 
```bash
# Automated deployment
./deploy.sh

# Manual deployment
ssh user@server
cd /path/to/project
git pull origin main
docker-compose -f docker-compose.production.yml up -d --build
```

### **Q: چطور backup بگیرم؟**
**A**: 
```bash
# Database backup
docker-compose exec postgres pg_dump -U peykan_user peykan > backup.sql

# Full backup
tar -czf backup-$(date +%Y%m%d).tar.gz . --exclude=node_modules --exclude=.git
```

### **Q: چطور rollback کنم؟**
**A**: 
```bash
# Stop services
docker-compose down

# Restore previous version
git checkout <previous-tag>

# Restore database (if needed)
docker-compose exec postgres psql -U peykan_user -d peykan < backup.sql

# Start services
docker-compose -f docker-compose.production.yml up -d
```

---

## 💰 Payment & Billing

### **Q: چطور payment gateway اضافه کنم؟**
**A**: 
1. در `backend/.env` تنظیمات payment را اضافه کنید
2. Payment provider API keys را تنظیم کنید
3. Payment views را پیاده‌سازی کنید
4. Webhook endpoints را اضافه کنید

### **Q: چطور multi-currency پشتیبانی کنم؟**
**A**: 
- از `CurrencyConverterService` استفاده کنید
- Currency rates را به‌روزرسانی کنید
- Frontend currency selector اضافه کنید
- Price calculations را update کنید

---

## 🌐 Internationalization

### **Q: چطور زبان جدید اضافه کنم؟**
**A**: 
1. فایل ترجمه جدید در `frontend/i18n/` بسازید
2. در `frontend/i18n/config.ts` اضافه کنید
3. Backend translations را اضافه کنید
4. RTL support را در نظر بگیرید

### **Q: چطور RTL support اضافه کنم؟**
**A**: 
- از CSS `direction: rtl` استفاده کنید
- TailwindCSS RTL classes استفاده کنید
- Text alignment را تنظیم کنید
- Layout components را adapt کنید

---

## 📊 Performance

### **Q: چطور performance را بهبود دهم؟**
**A**: 
- از Redis caching استفاده کنید
- Database indexes اضافه کنید
- Image optimization انجام دهید
- Code splitting استفاده کنید
- CDN برای static files

### **Q: چطور monitoring اضافه کنم？**
**A**: 
- Health checks اضافه کنید
- Logging configuration تنظیم کنید
- Performance metrics جمع‌آوری کنید
- Alerting system راه‌اندازی کنید

---

## 🤝 Contributing

### **Q: چطور مشارکت کنم؟**
**A**: 
1. [Contributing Guide](./CONTRIBUTING.md) را مطالعه کنید
2. Fork کنید و clone کنید
3. Branch جدید بسازید
4. کد بنویسید و تست کنید
5. Pull Request بسازید

### **Q: چطور bug report کنم؟**
**A**: 
1. [GitHub Issues](https://github.com/PeykanTravel/peykan-tourism/issues) بروید
2. Issue جدید بسازید
3. Template را پر کنید
4. Screenshots اضافه کنید

### **Q: چطور feature request کنم؟**
**A**: 
1. [GitHub Discussions](https://github.com/PeykanTravel/peykan-tourism/discussions) بروید
2. Discussion جدید بسازید
3. Use case را توضیح دهید
4. Community feedback جمع‌آوری کنید

---

## 📚 Documentation

### **Q: کجا مستندات کامل را پیدا کنم؟**
**A**: 
- [Development Guide](./DEVELOPMENT_GUIDE.md)
- [API Documentation](./backend/README.md)
- [Deployment Guide](./DEPLOYMENT_CHECKLIST.md)
- [Contributing Guide](./CONTRIBUTING.md)

### **Q: چطور API documentation آپدیت کنم؟**
**A**: 
- از Django REST Framework documentation استفاده کنید
- Swagger/OpenAPI اضافه کنید
- Code comments را به‌روزرسانی کنید
- Examples اضافه کنید

---

## 🆘 Support

### **Q: کجا کمک بگیرم؟**
**A**: 
- [Support Guide](./SUPPORT.md) را مطالعه کنید
- [GitHub Issues](https://github.com/PeykanTravel/peykan-tourism/issues) جستجو کنید
- [GitHub Discussions](https://github.com/PeykanTravel/peykan-tourism/discussions) بپرسید
- Email: support@peykantravelistanbul.com

### **Q: چطور با تیم تماس بگیرم؟**
**A**: 
- **Technical Issues**: tech-support@peykantravelistanbul.com
- **Security Issues**: security@peykantravelistanbul.com
- **Business Inquiries**: business@peykantravelistanbul.com
- **General Support**: support@peykantravelistanbul.com

---

## 🔄 Updates & Maintenance

### **Q: چطور پروژه را آپدیت کنم؟**
**A**: 
```bash
# Pull latest changes
git pull origin main

# Update dependencies
docker-compose exec backend pip install -r requirements.txt
docker-compose exec frontend npm install

# Rebuild containers
docker-compose up -d --build
```

### **Q: چطور dependencies را آپدیت کنم؟**
**A**: 
```bash
# Backend dependencies
docker-compose exec backend pip install --upgrade -r requirements.txt

# Frontend dependencies
docker-compose exec frontend npm update

# Security updates
docker-compose exec backend safety check
docker-compose exec frontend npm audit fix
```

---

## 📈 Scaling

### **Q: چطور پروژه را scale کنم؟**
**A**: 
- Load balancer اضافه کنید
- Database replication راه‌اندازی کنید
- CDN برای static files
- Microservices architecture
- Container orchestration (Kubernetes)

### **Q: چطور database را optimize کنم؟**
**A**: 
- Database indexes اضافه کنید
- Query optimization انجام دهید
- Connection pooling تنظیم کنید
- Regular maintenance انجام دهید
- Monitoring اضافه کنید

---

**نکته**: اگر سوال شما در اینجا پاسخ داده نشده، لطفاً [Support Guide](./SUPPORT.md) را مطالعه کنید یا با تیم تماس بگیرید. 

### **Q: خطاهای رایج راه‌اندازی لوکال (PostgreSQL/ویندوز) و راه‌حل آن‌ها؟**
**A**:
- اگر با خطای psycopg2 یا psycopg2-binary مواجه شدید:
  1. مطمئن شوید محیط مجازی فعال است.
  2. دستور زیر را اجرا کنید:
     ```sh
     pip install psycopg2-binary
     ```
- اگر با خطای UnicodeDecodeError یا embedded null character در فایل .env مواجه شدید:
  1. فایل .env را با ویرایشگر متن (مثل VSCode یا Notepad++) باز کنید.
  2. از منوی Save with Encoding، گزینه UTF-8 (بدون BOM) را انتخاب و ذخیره کنید.
- اگر پروژه به دیتابیس متصل نمی‌شود:
  1. مطمئن شوید PostgreSQL نصب است و دیتابیس peykan_tourism ساخته شده.
  2. مقادیر یوزر و پسورد را در .env درست وارد کنید.
- اگر با خطای فعال‌سازی venv مواجه شدید:
  - در ویندوز: `venv\Scripts\activate`
  - در لینوکس/مک: `source venv/bin/activate` 