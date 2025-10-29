# User Role Assignment Fix

## مشکل (Problem)

کاربرانی که از طریق Google OAuth یا OTP (ایمیل/شماره موبایل) ثبت‌نام یا لاگین می‌کردند، با role='guest' ثبت می‌شدند به جای 'customer'. این باعث می‌شد که:
- کاربران احراز هویت شده همچنان به عنوان مهمان شناخته شوند
- ممکن بود مشکلاتی در دسترسی به checkout و سایر امکانات ایجاد شود

Users who registered or logged in via Google OAuth or OTP (email/phone) were being assigned role='guest' instead of 'customer'. This caused:
- Authenticated users to still be recognized as guests
- Potential issues with checkout and other feature access

## علت ریشه‌ای (Root Cause)

در کد authentication، هنگام ایجاد کاربر جدید یا ورود کاربر موجود، role به صورت صریح به 'customer' تنظیم نمی‌شد. User model دارای `default='guest'` برای role field است، بنابراین تمام کاربران جدید به صورت پیش‌فرض guest می‌شدند.

In the authentication code, when creating new users or logging in existing users, the role was not explicitly set to 'customer'. The User model has `default='guest'` for the role field, so all new users defaulted to guest.

## راه‌حل (Solution)

### 1. GoogleLoginView (users/views.py)

**کاربر جدید (New User):**
```python
user = User(
    username=email,
    email=email,
    first_name=first_name,
    last_name=last_name,
    role='customer',  # ✅ اضافه شد
    is_active=True,
)
```

**کاربر موجود (Existing User):**
```python
# Upgrade guest users to customer role
if user.role == 'guest':
    user.role = 'customer'
    updated = True
```

### 2. OTPVerifyView (users/views.py)

**برای login با شماره موبایل (Phone Login):**
```python
user = User.objects.get(profile__phone=target)
# Upgrade guest users to customer role
if user.role == 'guest':
    user.role = 'customer'
    user.save()
```

**برای تایید ایمیل (Email Verification):**
```python
if otp.user:
    otp.user.is_email_verified = True
    otp.user.is_active = True
    # Upgrade guest users to customer role
    if otp.user.role == 'guest':
        otp.user.role = 'customer'
    otp.user.save()
```

### 3. UserCreateSerializer (users/serializers.py)

**برای ثبت‌نام معمولی (Regular Registration):**
```python
def create(self, validated_data):
    profile_data = validated_data.pop('profile', None)
    validated_data.pop('password_confirm', None)
    
    # Set role to 'customer' if not provided
    if 'role' not in validated_data or validated_data.get('role') == 'guest':
        validated_data['role'] = 'customer'
    
    user = User.objects.create_user(**validated_data)
    # ...
```

## تغییرات اعمال شده (Changes Applied)

1. ✅ `plusistanbul/backend/users/views.py` - GoogleLoginView
2. ✅ `plusistanbul/backend/users/views.py` - OTPVerifyView (login)
3. ✅ `plusistanbul/backend/users/views.py` - OTPVerifyView (email verification)
4. ✅ `plusistanbul/backend/users/serializers.py` - UserCreateSerializer

## استقرار (Deployment)

1. Built new backend image
2. Stopped and removed old container
3. Started new container with fixes

## تست (Testing)

کاربران اکنون باید بتوانند:
- ✅ با Google OAuth ثبت‌نام کنند و role='customer' داشته باشند
- ✅ با OTP (ایمیل یا شماره) ثبت‌نام کنند و role='customer' داشته باشند
- ✅ کاربران موجود با role='guest' به 'customer' ارتقا یابند
- ✅ به checkout و سایر امکانات دسترسی داشته باشند

Users should now be able to:
- ✅ Register via Google OAuth and have role='customer'
- ✅ Register via OTP (email or phone) and have role='customer'
- ✅ Existing users with role='guest' get upgraded to 'customer'
- ✅ Access checkout and other features

## تاریخ (Date)

Fixed: October 26, 2025 (00:00 UTC)
