# راهنمای Push به Git Repository 🚀

## ✅ Commit موفق بود!

تغییرات با موفقیت commit شدند:
```
commit 0df4a1b
feat: Implement multilingual invoice system with smart RTL detection

63 files changed, 18343 insertions(+), 42 deletions(-)
```

---

## 📋 فایل‌های اضافه شده

### Backend:
- ✅ `backend/orders/` - سیستم کامل سفارشات
- ✅ `backend/orders/pdf_service.py` - سرویس تولید PDF چندزبانه
- ✅ `backend/orders/invoice_translations.py` - سیستم ترجمه فاکتور
- ✅ `backend/orders/views.py` - API endpoints با پشتیبانی زبان
- ✅ `backend/test_invoice.py` - تست تولید فاکتور
- ✅ `backend/test_mixed_language.py` - تست محتوای ترکیبی

### Frontend:
- ✅ `frontend/app/[locale]/orders/page.tsx` - صفحه لیست سفارشات
- ✅ `frontend/app/[locale]/orders/[orderNumber]/page.tsx` - صفحه جزئیات سفارش

### Documentation:
- ✅ 16 فایل مستندات (MD files)

---

## 🔧 مراحل Push به Repository

### گزینه 1: اگر Repository در GitHub/GitLab دارید

```bash
# اضافه کردن remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# یا برای GitLab:
git remote add origin https://gitlab.com/YOUR_USERNAME/YOUR_REPO.git

# Push کردن
git push -u origin new-develop
```

### گزینه 2: اگر Repository جدید می‌خواهید بسازید

#### در GitHub:
1. برو به https://github.com/new
2. نام repository رو وارد کن (مثلاً `peykan-tourism`)
3. روی "Create repository" کلیک کن
4. دستورات زیر رو اجرا کن:

```bash
git remote add origin https://github.com/YOUR_USERNAME/peykan-tourism.git
git push -u origin new-develop
```

#### در GitLab:
1. برو به https://gitlab.com/projects/new
2. نام project رو وارد کن
3. روی "Create project" کلیک کن
4. دستورات زیر رو اجرا کن:

```bash
git remote add origin https://gitlab.com/YOUR_USERNAME/peykan-tourism.git
git push -u origin new-develop
```

### گزینه 3: اگر Repository قبلاً وجود داشته

```bash
# بررسی remote قبلی
git remote -v

# اگر remote وجود نداشت، اضافه کن
git remote add origin YOUR_REPO_URL

# اگر remote وجود داشت ولی URL اشتباه بود
git remote set-url origin YOUR_REPO_URL

# Push کردن
git push -u origin new-develop
```

---

## 🌿 وضعیت Branch‌ها

```
* new-develop (HEAD) - آخرین تغییرات شما
  master - نسخه قبلی
  backup-20251018-001522 - نسخه backup
```

---

## 📊 خلاصه تغییرات

### تعداد فایل‌ها:
- 63 فایل تغییر کرده
- 18,343 خط اضافه شده
- 42 خط حذف شده

### ویژگی‌های اصلی:
1. ✅ سیستم فاکتور چندزبانه (انگلیسی، فارسی، عربی)
2. ✅ تشخیص هوشمند RTL
3. ✅ نمایش جزئیات کامل محصولات
4. ✅ پشتیبانی از محتوای ترکیبی
5. ✅ طراحی حرفه‌ای PDF
6. ✅ فونت‌های فارسی (Sahel)

---

## 🔍 بررسی تغییرات

### مشاهده فایل‌های تغییر یافته:
```bash
git show --name-only
```

### مشاهده diff:
```bash
git show
```

### مشاهده لیست commit‌ها:
```bash
git log --oneline
```

---

## ⚠️ نکات مهم

### 1. قبل از Push:
```bash
# بررسی وضعیت
git status

# بررسی branch فعلی
git branch

# بررسی remote
git remote -v
```

### 2. اگر خطا گرفتید:
```bash
# خطای authentication
# راه حل: استفاده از Personal Access Token

# خطای rejected
# راه حل: pull کردن تغییرات
git pull origin new-develop --rebase
git push origin new-develop
```

### 3. برای امنیت بیشتر:
```bash
# استفاده از SSH به جای HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

---

## 📝 دستورات کامل (مثال)

```bash
# 1. اضافه کردن remote (فقط یک بار)
git remote add origin https://github.com/YOUR_USERNAME/peykan-tourism.git

# 2. بررسی remote
git remote -v

# 3. Push کردن branch
git push -u origin new-develop

# 4. (اختیاری) Push کردن همه branch‌ها
git push --all origin

# 5. (اختیاری) Push کردن tags
git push --tags origin
```

---

## ✅ بعد از Push موفق

بعد از push موفق، می‌تونید:

1. **مشاهده در GitHub/GitLab:**
   - برو به repository
   - branch `new-develop` رو انتخاب کن
   - تغییرات رو ببین

2. **ایجاد Pull Request:**
   - برای merge کردن به `master`
   - Review تغییرات
   - Merge کردن

3. **Clone در سیستم دیگه:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   git checkout new-develop
   ```

---

## 🆘 کمک بیشتر

اگر مشکلی داشتید:

1. **بررسی لاگ:**
   ```bash
   git log --all --graph --oneline
   ```

2. **بررسی تفاوت branch‌ها:**
   ```bash
   git diff master new-develop
   ```

3. **بازگشت به commit قبلی (اگر لازم شد):**
   ```bash
   git reset --soft HEAD~1
   ```

---

## 📞 اطلاعات تماس Repository

بعد از اضافه کردن remote، اطلاعات رو اینجا یادداشت کنید:

```
Repository URL: _________________________________
Branch: new-develop
Last Commit: 0df4a1b
Date: 2025-01-18
```

---

## 🎉 موفق باشید!

تغییرات شما آماده push هستند. فقط کافیه remote رو اضافه کنید و push کنید! 🚀
