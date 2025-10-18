# 🚀 دستورات سریع - Cheatsheet

## 📦 نصب و راه‌اندازی

### نصب وابستگی‌ها
```bash
cd backend
pip install -r requirements.txt
```

### راه‌اندازی پایگاه داده
```bash
python manage.py makemigrations
python manage.py migrate
```

### ایجاد سوپریوزر
```bash
python manage.py createsuperuser
```

---

## 🎪 ایجاد ایونت نمونه

### روش ۱: اسکریپت (توصیه می‌شود)

**ویندوز:**
```bash
create-sample-event.bat
```

**لینوکس/مک:**
```bash
chmod +x create-sample-event.sh
./create-sample-event.sh
```

### روش ۲: دستی
```bash
cd backend
python manage.py create_sample_event
```

---

## 🖥️ اجرای سرور

### محیط توسعه
```bash
cd backend
python manage.py runserver
```

### با پورت خاص
```bash
python manage.py runserver 8080
```

### دسترسی از شبکه
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🧪 تست API

### اسکریپت تست

**ویندوز:**
```bash
test-event-api.bat
```

**لینوکس/مک:**
```bash
chmod +x test-event-api.sh
./test-event-api.sh
```

### تست دستی با cURL

#### لیست ایونت‌ها
```bash
curl http://localhost:8000/api/events/
```

#### جزئیات ایونت (فارسی)
```bash
curl -H "Accept-Language: fa" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

#### جزئیات ایونت (انگلیسی)
```bash
curl -H "Accept-Language: en" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

#### جزئیات ایونت (عربی)
```bash
curl -H "Accept-Language: ar" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

#### جستجو
```bash
curl "http://localhost:8000/api/events/search/?q=music"
```

#### فیلتر بر اساس دسته‌بندی
```bash
curl "http://localhost:8000/api/events/?category=music-concert"
```

#### فیلتر بر اساس تاریخ
```bash
curl "http://localhost:8000/api/events/?date_from=2025-10-19&date_to=2025-10-25"
```

---

## 🌐 API Endpoints

### Events
```
GET    /api/events/                          # لیست ایونت‌ها
GET    /api/events/{slug}/                   # جزئیات ایونت
GET    /api/events/search/?q={query}         # جستجو
GET    /api/events/?category={slug}          # فیلتر دسته‌بندی
GET    /api/events/?venue={slug}             # فیلتر مکان
GET    /api/events/?date_from={date}         # فیلتر تاریخ
```

### Categories
```
GET    /api/categories/                      # لیست دسته‌بندی‌ها
GET    /api/categories/{slug}/               # جزئیات دسته‌بندی
```

### Venues
```
GET    /api/venues/                          # لیست مکان‌ها
GET    /api/venues/{slug}/                   # جزئیات مکان
```

### Artists
```
GET    /api/artists/                         # لیست هنرمندان
GET    /api/artists/{slug}/                  # جزئیات هنرمند
```

### Performances
```
GET    /api/events/{id}/performances/        # اجراهای ایونت
GET    /api/events/{id}/performances/{id}/seats/  # صندلی‌های اجرا
```

### Capacity
```
GET    /api/events/{id}/capacity_info/       # اطلاعات ظرفیت
```

---

## 🔧 دستورات Django

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py sqlmigrate events 0001
```

### Shell
```bash
python manage.py shell
python manage.py shell_plus  # اگر django-extensions نصب باشد
```

### Static Files
```bash
python manage.py collectstatic
python manage.py collectstatic --noinput
```

### Database
```bash
python manage.py dbshell
python manage.py dumpdata events > events.json
python manage.py loaddata events.json
```

### Testing
```bash
python manage.py test
python manage.py test events
python manage.py test events.tests.test_models
```

---

## 🐍 Python Shell Commands

### دسترسی به ایونت
```python
from events.models import Event

# دریافت ایونت
event = Event.objects.get(slug='istanbul-music-festival-2025')

# تغییر زبان
from parler.utils.context import switch_language

with switch_language(event, 'fa'):
    print(event.title)  # جشنواره موسیقی استانبول ۲۰۲۵

with switch_language(event, 'en'):
    print(event.title)  # Istanbul Music Festival 2025

with switch_language(event, 'ar'):
    print(event.title)  # مهرجان اسطنبول الموسيقي ٢٠٢٥
```

### دریافت اجراها
```python
performances = event.performances.all()
for perf in performances:
    print(f"{perf.date} - {perf.start_time}")
```

### دریافت صندلی‌ها
```python
from events.models import Seat

# صندلی‌های موجود
available_seats = Seat.objects.filter(
    performance=performances[0],
    status='available'
)
print(f"Available seats: {available_seats.count()}")
```

---

## 📊 دستورات مفید

### بررسی وضعیت
```bash
python manage.py check
python manage.py check --deploy
```

### پاک‌سازی
```bash
python manage.py clearsessions
python manage.py flush  # حذف تمام داده‌ها (خطرناک!)
```

### کاربران
```bash
python manage.py createsuperuser
python manage.py changepassword username
```

---

## 🔍 دستورات جستجو

### grep در فایل‌ها
```bash
# ویندوز
findstr /s /i "Event" *.py

# لینوکس/مک
grep -r "Event" *.py
```

### پیدا کردن فایل
```bash
# ویندوز
dir /s /b *event*.py

# لینوکس/مک
find . -name "*event*.py"
```

---

## 📝 دستورات Git

### وضعیت
```bash
git status
git log --oneline
```

### Commit
```bash
git add .
git commit -m "Add event system with 3 languages"
git push origin main
```

### Branch
```bash
git branch
git checkout -b feature/events
git merge feature/events
```

---

## 🐳 Docker (اختیاری)

### Build
```bash
docker-compose build
```

### Run
```bash
docker-compose up
docker-compose up -d  # در پس‌زمینه
```

### Stop
```bash
docker-compose down
```

### Logs
```bash
docker-compose logs -f
```

---

## 📦 pip Commands

### نصب
```bash
pip install django
pip install -r requirements.txt
```

### لیست
```bash
pip list
pip freeze > requirements.txt
```

### به‌روزرسانی
```bash
pip install --upgrade django
pip install --upgrade -r requirements.txt
```

---

## 🔐 Environment Variables

### تنظیم متغیرها

**ویندوز:**
```bash
set DEBUG=True
set SECRET_KEY=your-secret-key
```

**لینوکس/مک:**
```bash
export DEBUG=True
export SECRET_KEY=your-secret-key
```

### استفاده از .env
```bash
# ایجاد فایل .env
echo "DEBUG=True" > .env
echo "SECRET_KEY=your-secret-key" >> .env

# نصب python-dotenv
pip install python-dotenv
```

---

## 🧹 پاک‌سازی

### حذف فایل‌های پایتون
```bash
# ویندوز
del /s /q *.pyc
rmdir /s /q __pycache__

# لینوکس/مک
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### حذف migrations
```bash
# ویندوز
del /s /q migrations\*.py
# نگه داشتن __init__.py

# لینوکس/مک
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
```

---

## 📱 دستورات مفید دیگر

### بررسی نسخه
```bash
python --version
django-admin --version
pip --version
```

### نصب ابزارهای توسعه
```bash
pip install django-debug-toolbar
pip install django-extensions
pip install ipython
```

### اجرای تست‌ها با coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## 🎯 دستورات سریع پروژه

### راه‌اندازی کامل از صفر
```bash
# 1. نصب وابستگی‌ها
cd backend
pip install -r requirements.txt

# 2. راه‌اندازی دیتابیس
python manage.py migrate

# 3. ایجاد سوپریوزر
python manage.py createsuperuser

# 4. ایجاد ایونت نمونه
python manage.py create_sample_event

# 5. اجرای سرور
python manage.py runserver
```

### تست سریع
```bash
# تست API
curl http://localhost:8000/api/events/

# تست با زبان فارسی
curl -H "Accept-Language: fa" \
     http://localhost:8000/api/events/istanbul-music-festival-2025/
```

---

## 📚 لینک‌های مفید

- **پنل ادمین**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/
- **Events API**: http://localhost:8000/api/events/
- **Swagger Docs**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

---

## 💡 نکات

1. همیشه محیط مجازی را فعال کنید
2. قبل از commit، تست‌ها را اجرا کنید
3. از .gitignore برای فایل‌های حساس استفاده کنید
4. مستندات را به‌روز نگه دارید
5. از environment variables برای تنظیمات استفاده کنید

---

**این فایل را bookmark کنید! 🔖**
