# Quick Start Guide - Peykan Travel Platform

## 🚀 Development Setup

### Prerequisites
```bash
# Check versions
python --version  # Should be 3.10+
node --version    # Should be 18+
npm --version
```

### Backend Setup (5 minutes)

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment file
copy env.example .env
# Edit .env with your settings

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### Frontend Setup (3 minutes)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Copy environment file
copy .env.example .env.local
# Edit .env.local with API URL

# 4. Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🏭 Production Deployment

### Step 1: Prepare Environment

```bash
# Generate SECRET_KEY
cd backend
python generate_secret_key.py

# Copy and edit production environment
copy env.production.example .env
# Fill in all required values
```

### Step 2: Backend Deployment

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn peykan.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Step 3: Frontend Deployment

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

## 🔍 Verification

### Check Backend
```bash
# Health check
curl http://localhost:8000/api/v1/

# Admin panel
# Open: http://localhost:8000/admin/
```

### Check Frontend
```bash
# Open browser
# Navigate to: http://localhost:3000
```

## 📝 Common Commands

### Backend
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Create app
python manage.py startapp app_name
```

### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Start production
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

## 🐛 Troubleshooting

### Backend Issues

**Database connection error:**
```bash
# Check DATABASE_URL in .env
# Make sure PostgreSQL is running
```

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

**Migration errors:**
```bash
python manage.py migrate --fake-initial
```

### Frontend Issues

**Build errors:**
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

**Type errors:**
```bash
npm run type-check
```

**Port already in use:**
```bash
# Change port
npm run dev -- -p 3001
```

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Use strong database password
- [ ] Enable Redis authentication
- [ ] Set up firewall rules
- [ ] Configure rate limiting

## 📚 Documentation

- [Full README](README.md)
- [Production Deployment Checklist](PRODUCTION_DEPLOYMENT_CHECKLIST.md)
- [Production Preparation Summary](PRODUCTION_PREPARATION_SUMMARY.md)
- [راهنمای فارسی](راهنمای_راه_اندازی_لوکال.md)

## 🆘 Support

For issues and questions:
1. Check documentation in `docs/` folder
2. Review error logs
3. Contact development team

---

✨ Happy Coding!
