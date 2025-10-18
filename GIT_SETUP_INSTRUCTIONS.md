# 📝 دستورالعمل Git Setup

## ✅ وضعیت فعلی

- ✅ Git repository initialize شده
- ✅ Branch `new-develop` ایجاد شده
- ✅ تغییرات Hero Slider commit شده (commit: 3043166)
- ⚠️ Remote repository تنظیم نشده

---

## 🚀 مراحل Push به Repository

### گام 1: اضافه کردن Remote Repository

اگر repository در GitHub/GitLab/Bitbucket دارید:

```bash
# برای GitHub:
git remote add origin https://github.com/YOUR_USERNAME/plusistanbul.git

# یا برای GitLab:
git remote add origin https://gitlab.com/YOUR_USERNAME/plusistanbul.git

# یا برای Bitbucket:
git remote add origin https://bitbucket.org/YOUR_USERNAME/plusistanbul.git
```

### گام 2: بررسی Remote

```bash
git remote -v
```

باید خروجی مشابه این را ببینید:
```
origin  https://github.com/YOUR_USERNAME/plusistanbul.git (fetch)
origin  https://github.com/YOUR_USERNAME/plusistanbul.git (push)
```

### گام 3: Push به Remote

```bash
# Push branch new-develop
git push -u origin new-develop
```

### گام 4: بررسی

```bash
git branch -a
```

باید branch `remotes/origin/new-develop` را ببینید.

---

## 📊 وضعیت Commit

### Commit فعلی:
```
Commit: 3043166
Branch: new-develop
Message: feat: Improve Hero Slider with default settings and bug fixes
Files: 15 files changed, 8352 insertions(+)
```

### فایل‌های Commit شده:
```
✅ 7 فایل مستندات:
   - HERO_SLIDER_ANALYSIS.md
   - HERO_SLIDER_COMPLETE_SUMMARY.md
   - HERO_SLIDER_DEFAULT_SETTINGS_GUIDE.md
   - HERO_SLIDER_FINAL_REPORT.md
   - HERO_SLIDER_FIXES.md
   - HERO_SLIDER_GUIDE_FA.md
   - HERO_SLIDER_IMPLEMENTATION_SUMMARY.md

✅ 4 فایل بک‌اند:
   - backend/shared/models.py
   - backend/shared/serializers.py
   - backend/shared/admin.py
   - backend/shared/migrations/0004_*.py

✅ 3 فایل فرانت‌اند:
   - frontend/lib/api/shared.ts
   - frontend/components/home/HeroSection.tsx
   - frontend/components/home/HeroSection.improved.tsx

✅ 1 اسکریپت:
   - backend/create_test_hero_slides.py
```

---

## 🔄 اگر Remote Repository ندارید

### ایجاد Repository جدید در GitHub:

1. به GitHub بروید: https://github.com
2. روی "New repository" کلیک کنید
3. نام: `plusistanbul` (یا هر نام دیگری)
4. توضیحات: "Peykan Tourism Platform"
5. Private/Public را انتخاب کنید
6. **بدون** README, .gitignore, license ایجاد کنید
7. روی "Create repository" کلیک کنید

### سپس:

```bash
# اضافه کردن remote
git remote add origin https://github.com/YOUR_USERNAME/plusistanbul.git

# Push
git push -u origin new-develop
```

---

## 🌿 مدیریت Branch ها

### Branch های فعلی:
```
* new-develop (فعلی)
  master
```

### توصیه:
- `master` یا `main`: برای production
- `new-develop`: برای development و تست
- `feature/*`: برای feature های جدید

### تغییر به branch دیگر:
```bash
# به master برگردید
git checkout master

# به new-develop برگردید
git checkout new-develop
```

---

## 📝 دستورات مفید Git

### بررسی وضعیت:
```bash
git status
git log --oneline
git branch -a
```

### Commit جدید:
```bash
git add .
git commit -m "your message"
```

### Push:
```bash
git push origin new-develop
```

### Pull:
```bash
git pull origin new-develop
```

---

## ✅ خلاصه

شما الان در branch `new-develop` هستید و تغییرات Hero Slider commit شده است.

**مراحل بعدی**:
1. Remote repository را اضافه کنید (اگر ندارید)
2. Push کنید: `git push -u origin new-develop`
3. در GitHub/GitLab Pull Request ایجاد کنید (اختیاری)

**همه چیز آماده است!** 🚀
