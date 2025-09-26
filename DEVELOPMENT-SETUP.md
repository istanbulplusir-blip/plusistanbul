# 🛠️ Development Environment Setup - Peykan Tourism Platform

## 🎯 هدف: راه‌اندازی محیط Development

### تفاوت بین Development و Production:

| Development     | Production          |
| --------------- | ------------------- |
| SQLite Database | PostgreSQL Database |
| Local Files     | Docker Containers   |
| Debug Mode      | Production Mode     |
| Local Server    | Nginx + Gunicorn    |

## ✅ مراحل راه‌اندازی Development:

### 1. بررسی محیط Development

```cmd
# اجرای اسکریپت بررسی
check-dev-environment.bat
```

### 2. Reset Database در Development

```cmd
# اجرای اسکریپت reset
reset-database-dev.bat
```

### 3. راه‌اندازی سرور Development

```cmd
cd backend
python manage.py runserver
```

## 🔧 مراحل دستی:

### مرحله 1: بررسی Python و Django

```cmd
# بررسی Python
python --version

# بررسی Django
cd backend
python -c "import django; print('Django version:', django.get_version())"
```

### مرحله 2: راه‌اندازی Virtual Environment

```cmd
# ایجاد virtual environment
python -m venv venv

# فعال‌سازی virtual environment
venv\Scripts\activate

# نصب requirements
pip install -r requirements.txt
```

### مرحله 3: تنظیم Database

```cmd
# حذف database قدیمی
del db.sqlite3

# حذف migration files
for /r %%i in (*.py) do (
    if not "%%~ni"=="__init__" (
        if "%%~pi"=="migrations\" (
            del "%%i" 2>nul
        )
    )
)

# ایجاد migration های جدید
python manage.py makemigrations

# اجرای migration ها
python manage.py migrate
```

### مرحله 4: ایجاد Superuser

```cmd
# ایجاد superuser
python manage.py createsuperuser
```

### مرحله 5: جمع‌آوری Static Files

```cmd
# جمع‌آوری static files
python manage.py collectstatic --noinput
```

### مرحله 6: راه‌اندازی سرور

```cmd
# راه‌اندازی development server
python manage.py runserver
```

## 🌐 دسترسی به Application:

### URLs مهم:

- **Frontend**: http://localhost:3000 (Next.js)
- **Backend**: http://localhost:8000 (Django)
- **Admin Panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/v1

## 🔍 بررسی مشکلات:

### 1. مشکلات Python

```cmd
# بررسی Python version
python --version

# بررسی pip
pip --version

# بررسی virtual environment
where python
```

### 2. مشکلات Django

```cmd
# بررسی Django installation
python -c "import django; print(django.get_version())"

# بررسی Django configuration
python manage.py check

# بررسی models
python manage.py check --deploy
```

### 3. مشکلات Database

```cmd
# بررسی database
python manage.py dbshell

# بررسی migrations
python manage.py showmigrations

# بررسی migration issues
python manage.py makemigrations --dry-run
```

### 4. مشکلات Static Files

```cmd
# بررسی static files
python manage.py collectstatic --dry-run

# بررسی static files directory
dir static
```

## 🚀 دستورات مفید:

### Django Commands:

```cmd
# راه‌اندازی سرور
python manage.py runserver

# راه‌اندازی سرور روی port خاص
python manage.py runserver 8080

# بررسی configuration
python manage.py check

# بررسی models
python manage.py validate

# ایجاد migration
python manage.py makemigrations

# اجرای migration
python manage.py migrate

# ایجاد superuser
python manage.py createsuperuser

# جمع‌آوری static files
python manage.py collectstatic

# بررسی migration status
python manage.py showmigrations
```

### Database Commands:

```cmd
# ورود به database shell
python manage.py dbshell

# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json
```

## 🔧 تنظیمات Development:

### فایل `backend/peykan/settings.py`:

```python
# Development settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### فایل `backend/.env.development`:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📋 Checklist Development:

- [ ] Python نصب شده است
- [ ] Virtual environment ایجاد شده است
- [ ] Requirements نصب شده‌اند
- [ ] Django configuration درست است
- [ ] Database reset شده است
- [ ] Migration ها اجرا شده‌اند
- [ ] Superuser ایجاد شده است
- [ ] Static files جمع‌آوری شده‌اند
- [ ] Development server راه‌اندازی شده است
- [ ] Application در browser قابل دسترسی است

## 🆘 عیب‌یابی:

### مشکل 1: Python not found

```cmd
# نصب Python از python.org
# یا استفاده از Chocolatey
choco install python
```

### مشکل 2: Django not found

```cmd
# نصب Django
pip install django

# یا نصب requirements
pip install -r requirements.txt
```

### مشکل 3: Database errors

```cmd
# Reset database
reset-database-dev.bat

# یا دستی
del db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### مشکل 4: Port already in use

```cmd
# استفاده از port دیگر
python manage.py runserver 8080

# یا توقف process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## 🎯 مزایای Development Environment:

1. **سرعت بالا** - بدون Docker overhead
2. **Debug آسان** - Django debug toolbar
3. **Hot reload** - تغییرات فوری
4. **SQLite** - ساده و سریع
5. **Local files** - دسترسی مستقیم

## 📞 پشتیبانی:

در صورت مشکل:

1. **بررسی logs** در terminal
2. **بررسی browser console** (F12)
3. **بررسی Django logs** در terminal
4. **اجرای اسکریپت بررسی** `check-dev-environment.bat`

---

**نکته مهم:** محیط Development برای تست و توسعه استفاده می‌شود. برای production از Docker استفاده کنید.
