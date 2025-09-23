# راهنمای Authentication - Peykan Tourism

## صفحات ایجاد شده

### 1. صفحه ورود (Login)
- **مسیر**: `/login` یا `/fa/login` یا `/tr/login`
- **ویژگی‌ها**:
  - فرم زیبا با طراحی مدرن
  - نمایش/مخفی کردن رمز عبور
  - اعتبارسنجی فرم
  - پیام‌های خطا و موفقیت
  - پشتیبانی از redirect بعد از ورود
  - ترجمه کامل (فارسی، انگلیسی، ترکی)

### 2. صفحه ثبت‌نام (Register)
- **مسیر**: `/register` یا `/fa/register` یا `/tr/register`
- **ویژگی‌ها**:
  - فرم کامل ثبت‌نام
  - فیلدهای: نام، نام خانوادگی، ایمیل، تلفن، رمز عبور، تکرار رمز عبور
  - اعتبارسنجی رمز عبور (حداقل 8 کاراکتر)
  - نمایش/مخفی کردن رمز عبور
  - ترجمه کامل

### 3. Navbar به‌روزرسانی شده
- **ویژگی‌ها**:
  - نمایش لینک‌های ورود و ثبت‌نام برای کاربران غیرعضو
  - نمایش لینک‌های پروفایل و خروج برای کاربران عضو
  - پشتیبانی از زبان‌های مختلف

## API Endpoints

### Backend (Django)
- **ثبت‌نام**: `POST /api/v1/auth/register/`
- **ورود**: `POST /api/v1/auth/login/`
- **خروج**: `POST /api/v1/auth/logout/`
- **تازه‌سازی توکن**: `POST /api/v1/auth/token/refresh/`
- **پروفایل**: `GET /api/v1/auth/profile/`
- **به‌روزرسانی پروفایل**: `PATCH /api/v1/auth/profile/`
- **تغییر رمز عبور**: `POST /api/v1/auth/change-password/`

### Frontend (Next.js)
- **فایل API**: `frontend/lib/api/auth.ts`
- **Types**: `frontend/lib/types/api.ts`

## نحوه استفاده

### 1. مشاهده رویدادها بدون ورود
- کاربران می‌توانند رویدادها را مشاهده کنند
- می‌توانند صندلی‌ها را انتخاب کنند
- **اما برای افزودن به سبد خرید نیاز به ورود دارند**

### 2. ورود و ثبت‌نام
- از طریق Navbar یا مستقیماً از URL
- بعد از ورود موفق، کاربر به صفحه اصلی هدایت می‌شود
- توکن‌ها در localStorage ذخیره می‌شوند

### 3. افزودن به سبد خرید
- بعد از ورود، کاربران می‌توانند صندلی‌ها را به سبد خرید اضافه کنند
- می‌توانند checkout کنند

## ساختار فایل‌ها

```
frontend/
├── app/[locale]/
│   ├── login/
│   │   └── page.tsx          # صفحه ورود
│   └── register/
│       └── page.tsx          # صفحه ثبت‌نام
├── lib/
│   ├── api/
│   │   └── auth.ts           # API functions
│   └── types/
│       └── api.ts            # TypeScript types
└── components/
    └── Navbar.tsx            # Navbar به‌روزرسانی شده
```

## ترجمه‌ها

### فارسی (fa)
- ورود، ثبت‌نام، خروج، پروفایل
- پیام‌های خطا و موفقیت
- Placeholder ها

### انگلیسی (en)
- Login, Register, Logout, Profile
- Error and success messages
- Placeholders

### ترکی (tr)
- Giriş, Kayıt Ol, Çıkış, Profil
- Error and success messages
- Placeholders

## نکات مهم

1. **امنیت**: توکن‌ها در localStorage ذخیره می‌شوند
2. **UX**: پیام‌های loading و error نمایش داده می‌شوند
3. **Responsive**: صفحات در تمام دستگاه‌ها به خوبی نمایش داده می‌شوند
4. **Accessibility**: فرم‌ها برای screen reader ها بهینه شده‌اند
5. **Validation**: اعتبارسنجی سمت client و server

## تست

1. Backend را اجرا کنید: `cd backend && python manage.py runserver`
2. Frontend را اجرا کنید: `cd frontend && npm run dev`
3. به `http://localhost:3000` بروید
4. روی "ثبت‌نام" کلیک کنید
5. فرم را پر کنید و ثبت‌نام کنید
6. یا روی "ورود" کلیک کنید و وارد شوید

## مشکلات احتمالی

1. **خطای CORS**: مطمئن شوید که backend روی port 8000 اجرا می‌شود
2. **خطای API**: مطمئن شوید که تمام dependencies نصب شده‌اند
3. **خطای TypeScript**: مطمئن شوید که types درست import شده‌اند 