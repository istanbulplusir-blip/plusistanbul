# Production Deployment Checklist

## ✅ Completed Tasks

### 1. Code Cleanup
- ✅ Removed test files and scripts
- ✅ Removed backup database files
- ✅ Removed test invoice PDFs
- ✅ Updated .gitignore for production

### 2. Dependencies
- ✅ Updated backend requirements.txt to latest stable versions
- ✅ All frontend dependencies are up to date

### 3. Build & Type Checking
- ✅ TypeScript type checking passed (no errors)
- ✅ Frontend production build successful
- ✅ No build errors or warnings

## 📋 Pre-Deployment Checklist

### Environment Variables
- [ ] Set DEBUG=False in production
- [ ] Configure SECRET_KEY (use strong random key)
- [ ] Set ALLOWED_HOSTS correctly
- [ ] Configure database credentials
- [ ] Set CORS_ALLOWED_ORIGINS
- [ ] Configure email settings (SMTP)
- [ ] Set Redis connection string
- [ ] Configure Celery broker URL

### Security
- [ ] Enable HTTPS/SSL certificates
- [ ] Set SECURE_SSL_REDIRECT=True
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Set CSRF_COOKIE_SECURE=True
- [ ] Configure SECURE_HSTS_SECONDS
- [ ] Review CORS settings

### Database
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Backup database before deployment

### Static Files
- [ ] Run collectstatic: `python manage.py collectstatic`
- [ ] Configure static file serving (Nginx/Whitenoise)

### Services
- [ ] Configure Gunicorn workers
- [ ] Set up Celery workers
- [ ] Configure Redis for caching
- [ ] Set up process manager (systemd/supervisor)

### Monitoring
- [ ] Set up error logging (Sentry/similar)
- [ ] Configure application logs
- [ ] Set up uptime monitoring
- [ ] Configure backup strategy

### Testing
- [ ] Test all critical user flows
- [ ] Test payment integration
- [ ] Test email sending
- [ ] Test file uploads
- [ ] Load testing

## 🚀 Deployment Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn peykan.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Frontend
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

## 📦 Files Removed
- Test scripts and development files
- Test invoice PDFs
- Backup database files
- TypeScript build cache

## 🔄 Updated Dependencies
- Django: 5.1.4 → 5.1.5
- django-filter: 24.2 → 24.3
- dj-database-url: 2.2.0 → 2.3.0
- djangorestframework-simplejwt: 5.3.0 → 5.4.0
- django-allauth: 0.63.0 → 65.3.0
- dj-rest-auth: 5.0.2 → 7.0.0
- django-modeltranslation: 0.18.12 → 0.19.8
- django-parler: 2.3 → 2.3.1
- drf-spectacular: 0.27.0 → 0.28.0
- Pillow: 10.4.0 → 11.1.0
- django-debug-toolbar: 4.3.0 → 4.4.6
- whitenoise: 6.6.0 → 6.8.2
- redis: 5.0.1 → 5.2.1
- python-bidi: 0.4.2 → 0.6.1
