# دستورالعمل اعمال تغییرات در Production

## روش سریع (توصیه می‌شود) ⚡

فقط یک دستور:

```bash
cd /home/djangouser/plusistanbul
./quick_fix.sh
```

این اسکریپت تمام کارها را به صورت خودکار انجام می‌دهد.

---

## روش دستی (گام به گام) 📝

### 1. رفتن به پوشه پروژه
```bash
cd /home/djangouser/plusistanbul
```

### 2. ایجاد تصاویر پیش‌فرض
```bash
cd backend
python3 create_placeholders.py
cd ..
```

### 3. Rebuild کانتینر backend
```bash
docker-compose up -d --build backend
```

### 4. اجرای migration ها
```bash
docker-compose exec backend python manage.py migrate shared
```

### 5. ایجاد Hero Slider نمونه (اختیاری)
```bash
docker-compose exec backend python manage.py shell
```

سپس در shell پایتون:
```python
from shared.models import HeroSlider

# بررسی وجود hero slider
if not HeroSlider.objects.filter(is_active=True).exists():
    hero = HeroSlider.objects.create(
        order=1,
        is_active=True,
        display_duration=5000,
        button_url='/tours',
        button_type='primary',
        show_for_authenticated=True,
        show_for_anonymous=True,
        video_type='none'
    )
    
    hero.set_current_language('fa')
    hero.title = 'به پیکان توریسم خوش آمدید'
    hero.subtitle = 'بهترین تورهای استانبول'
    hero.button_text = 'مشاهده تورها'
    hero.save()
    
    print("Hero slider created!")
else:
    print("Hero slider already exists!")

exit()
```

### 6. Restart کردن frontend
```bash
docker-compose restart frontend
```

---

## بررسی نتیجه 🔍

### 1. بررسی لاگ‌ها
```bash
# لاگ backend
docker-compose logs -f backend

# لاگ frontend
docker-compose logs -f frontend

# لاگ nginx
docker-compose logs -f nginx
```

### 2. بررسی API
```bash
curl https://peykantravelistanbul.com/api/shared/hero-sliders/active/
```

باید JSON با URL های صحیح برگردد.

### 3. بررسی سایت
باز کردن در مرورگر:
- https://peykantravelistanbul.com

### 4. بررسی Admin Panel
- https://peykantravelistanbul.com/admin/
- وارد شوید با اکانت admin
- به بخش `Shared > Hero Sliders` بروید
- یک Hero Slider جدید ایجاد کنید و تصاویر آپلود کنید

---

## آپلود تصاویر و ویدیو در Admin 📤

### مراحل آپلود تصویر:

1. وارد Admin Panel شوید
2. به `Shared > Hero Sliders` بروید
3. روی "Add Hero Slide" کلیک کنید
4. فیلدها را پر کنید:
   - **Title**: عنوان اسلاید (فارسی/انگلیسی)
   - **Subtitle**: زیرعنوان
   - **Description**: توضیحات
   - **Button Text**: متن دکمه
   - **Button URL**: لینک دکمه (مثلاً `/tours`)
   - **Order**: ترتیب نمایش (عدد کوچکتر = اولویت بالاتر)

5. در بخش **Images**:
   - **Desktop Image**: تصویر دسکتاپ (1920x1080 پیکسل)
   - **Tablet Image**: تصویر تبلت (1024x768 پیکسل)
   - **Mobile Image**: تصویر موبایل (768x1024 پیکسل)

6. در بخش **Video Settings** (اختیاری):
   - **Video Type**: نوع ویدیو را انتخاب کنید
     - `No Video`: بدون ویدیو
     - `Upload Video File`: آپلود فایل ویدیو
     - `External Video URL`: لینک ویدیو خارجی
   - **Video File**: فایل ویدیو (MP4, WebM, OGV - حداکثر 50MB)
   - **Video URL**: یا لینک ویدیو (YouTube, Vimeo, etc.)
   - **Video Thumbnail**: تصویر پیش‌نمایش ویدیو

7. در بخش **Video Controls**:
   - **Autoplay Video**: پخش خودکار (✓ توصیه می‌شود)
   - **Video Muted**: بی‌صدا (✓ برای autoplay لازم است)
   - **Show Video Controls**: نمایش کنترل‌های ویدیو
   - **Loop Video**: تکرار ویدیو

8. **Save** کنید

---

## نکات مهم ⚠️

### تصاویر:
- ✅ فرمت‌های پشتیبانی شده: JPG, PNG, WebP
- ✅ حداکثر حجم: 10MB
- ✅ سایز توصیه شده:
  - Desktop: 1920x1080
  - Tablet: 1024x768
  - Mobile: 768x1024

### ویدیوها:
- ✅ فرمت‌های پشتیبانی شده: MP4, WebM, OGV
- ✅ حداکثر حجم: 50MB
- ⚠️ برای autoplay، ویدیو باید muted باشد
- ⚠️ ویدیوهای بزرگ ممکن است سرعت سایت را کاهش دهند

---

## مشکلات احتمالی و راه‌حل 🔧

### مشکل 1: تصاویر نمایش داده نمی‌شوند
**راه‌حل**:
```bash
# بررسی permissions
chmod -R 755 /home/djangouser/plusistanbul/backend/media

# بررسی ownership
chown -R djangouser:djangouser /home/djangouser/plusistanbul/backend/media

# Restart containers
docker-compose restart
```

### مشکل 2: ویدیوها play نمی‌شوند
**راه‌حل**:
- فرمت ویدیو را بررسی کنید (باید MP4 باشد)
- حجم فایل را بررسی کنید (نباید بیشتر از 50MB باشد)
- مطمئن شوید که `video_muted=True` است برای autoplay

### مشکل 3: خطای 404 برای media files
**راه‌حل**:
```bash
# بررسی nginx config
docker-compose exec nginx nginx -t

# Restart nginx
docker-compose restart nginx
```

### مشکل 4: تغییرات اعمال نمی‌شوند
**راه‌حل**:
```bash
# پاک کردن cache مرورگر
# یا باز کردن سایت در حالت Incognito

# Rebuild کامل
docker-compose down
docker-compose up -d --build
```

---

## تست نهایی ✅

بعد از اعمال تغییرات، این موارد را بررسی کنید:

1. ✅ سایت باز می‌شود: https://peykantravelistanbul.com
2. ✅ تصاویر Hero نمایش داده می‌شوند
3. ✅ ویدیوها (در صورت وجود) play می‌شوند
4. ✅ دکمه‌ها کار می‌کنند
5. ✅ در Console مرورگر خطایی نیست
6. ✅ Admin Panel کار می‌کند

---

## پشتیبانی 💬

اگر مشکلی پیش آمد:

1. لاگ‌ها را بررسی کنید:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   docker-compose logs -f nginx
   ```

2. وضعیت کانتینرها را بررسی کنید:
   ```bash
   docker-compose ps
   ```

3. اگر مشکل حل نشد، تمام کانتینرها را restart کنید:
   ```bash
   docker-compose restart
   ```

---

**موفق باشید! 🎉**
