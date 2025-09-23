# راهنمای مشارکت در پروژه Peykan Tourism

## 📋 فهرست مطالب
- [مقدمه](#مقدمه)
- [گردش کار مشارکت](#گردش-کار-مشارکت)
- [استانداردهای کدنویسی](#استانداردهای-کدنویسی)
- [تست و کیفیت کد](#تست-و-کیفیت-کد)
- [مستندسازی](#مستندسازی)
- [گزارش مشکلات](#گزارش-مشکلات)
- [درخواست ویژگی‌ها](#درخواست-ویژگی‌ها)
- [ارتباط با تیم](#ارتباط-با-تیم)

## 🎯 مقدمه

از مشارکت شما در پروژه Peykan Tourism سپاسگزاریم! این راهنما به شما کمک می‌کند تا به راحتی در توسعه این پروژه مشارکت کنید.

### پیش‌نیازها
- آشنایی با Git و GitHub
- تجربه کار با Django و Next.js
- آشنایی با Docker
- توانایی خواندن و نوشتن کد به زبان انگلیسی

## 🔄 گردش کار مشارکت

### 1. راه‌اندازی محیط توسعه
```bash
# کلون کردن مخزن
git clone https://github.com/PeykanTravel/peykan-tourism.git
cd peykan-tourism

# راه‌اندازی محیط توسعه
# Windows:
.\setup-dev.ps1

# Linux/Mac:
./setup-dev.sh
```

### 2. ایجاد شاخه جدید
```bash
# بروزرسانی شاخه اصلی
git checkout main
git pull origin main

# ایجاد شاخه جدید
git checkout -b feature/نام-ویژگی
# یا
git checkout -b fix/نام-مشکل
# یا
git checkout -b docs/نام-مستندات
```

### 3. توسعه و تست
```bash
# اجرای تست‌ها
# بک‌اند
docker-compose exec backend python manage.py test

# فرانت‌اند
docker-compose exec frontend npm run test

# بررسی کیفیت کد
docker-compose exec backend flake8 .
docker-compose exec frontend npm run lint
```

### 4. کامیت و پوش
```bash
# اضافه کردن تغییرات
git add .

# کامیت با پیام استاندارد
git commit -m "feat: اضافه کردن ویژگی جدید"
git commit -m "fix: رفع مشکل در صفحه تورها"
git commit -m "docs: بروزرسانی مستندات API"

# پوش کردن شاخه
git push origin feature/نام-ویژگی
```

### 5. ایجاد Pull Request
1. به GitHub بروید
2. روی "New Pull Request" کلیک کنید
3. شاخه خود را انتخاب کنید
4. توضیحات کامل بنویسید
5. Reviewers اضافه کنید
6. Labels مناسب اضافه کنید

## 📝 استانداردهای کدنویسی

### نام‌گذاری شاخه‌ها
```
feature/نام-ویژگی    # ویژگی جدید
fix/نام-مشکل        # رفع مشکل
hotfix/نام-مشکل     # رفع مشکل اضطراری
docs/نام-مستندات    # بروزرسانی مستندات
refactor/نام-بخش    # بازنویسی کد
test/نام-تست        # اضافه کردن تست
chore/نام-کار       # کارهای نگهداری
```

### پیام‌های کامیت (Conventional Commits)
```
feat: اضافه کردن ویژگی جدید
fix: رفع مشکل
docs: بروزرسانی مستندات
style: تغییرات ظاهری (فرمت‌بندی، نقطه‌گذاری)
refactor: بازنویسی کد بدون تغییر عملکرد
test: اضافه کردن یا اصلاح تست‌ها
chore: کارهای نگهداری (به‌روزرسانی dependencies)
perf: بهبود عملکرد
ci: تغییرات در CI/CD
build: تغییرات در سیستم build
```

### استانداردهای Backend (Django/Python)

#### ساختار کد
```python
# imports
import os
from django.conf import settings
from django.db import models

# constants
MAX_LENGTH = 255
DEFAULT_CURRENCY = 'USD'

# classes
class Tour(models.Model):
    """مدل تور با تمام ویژگی‌های مورد نیاز."""
    
    # fields
    title = models.CharField(max_length=MAX_LENGTH)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # meta
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تور'
        verbose_name_plural = 'تورها'
    
    # methods
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('tour_detail', kwargs={'slug': self.slug})
```

#### نام‌گذاری
- **کلاس‌ها**: PascalCase (مثل `TourDetailView`)
- **توابع و متغیرها**: snake_case (مثل `get_tour_price`)
- **ثابت‌ها**: UPPER_CASE (مثل `MAX_LENGTH`)
- **فایل‌ها**: snake_case (مثل `tour_views.py`)

#### مستندات
```python
def calculate_tour_price(tour, currency='USD', discount=0):
    """
    محاسبه قیمت تور با در نظر گرفتن تخفیف و تبدیل ارز.
    
    Args:
        tour (Tour): شیء تور
        currency (str): کد ارز مورد نظر
        discount (float): درصد تخفیف (0-100)
    
    Returns:
        Decimal: قیمت نهایی تور
    
    Raises:
        ValueError: اگر تخفیف منفی باشد
    """
    if discount < 0:
        raise ValueError("تخفیف نمی‌تواند منفی باشد")
    
    # محاسبه قیمت
    base_price = tour.price
    discounted_price = base_price * (1 - discount / 100)
    
    # تبدیل ارز
    converted_price = convert_currency(discounted_price, tour.currency, currency)
    
    return converted_price
```

### استانداردهای Frontend (Next.js/TypeScript)

#### ساختار کامپوننت
```typescript
// imports
import React from 'react';
import { useRouter } from 'next/router';
import { Tour } from '@/types/tour';

// types
interface TourCardProps {
  tour: Tour;
  onBook?: (tourId: string) => void;
  className?: string;
}

// component
export const TourCard: React.FC<TourCardProps> = ({
  tour,
  onBook,
  className = '',
}) => {
  const router = useRouter();
  
  const handleBookClick = () => {
    if (onBook) {
      onBook(tour.id);
    } else {
      router.push(`/tours/${tour.slug}`);
    }
  };
  
  return (
    <div className={`tour-card ${className}`}>
      <img src={tour.image} alt={tour.title} />
      <h3>{tour.title}</h3>
      <p>{tour.description}</p>
      <button onClick={handleBookClick}>
        رزرو تور
      </button>
    </div>
  );
};
```

#### نام‌گذاری
- **کامپوننت‌ها**: PascalCase (مثل `TourCard`)
- **توابع و متغیرها**: camelCase (مثل `handleBookClick`)
- **ثابت‌ها**: UPPER_CASE (مثل `API_BASE_URL`)
- **فایل‌ها**: kebab-case (مثل `tour-card.tsx`)

#### TypeScript
```typescript
// types/tour.ts
export interface Tour {
  id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  currency: string;
  duration: number;
  maxGroupSize: number;
  images: string[];
  category: TourCategory;
  location: Location;
  createdAt: string;
  updatedAt: string;
}

export type TourCategory = 'cultural' | 'adventure' | 'relaxation' | 'food';

export interface Location {
  city: string;
  country: string;
  coordinates: {
    lat: number;
    lng: number;
  };
}
```

## 🧪 تست و کیفیت کد

### تست‌های Backend
```python
# tests/test_tour_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from tours.models import Tour

class TourModelTest(TestCase):
    def setUp(self):
        self.tour_data = {
            'title': 'تور استانبول',
            'slug': 'istanbul-tour',
            'price': 1000.00,
            'currency': 'USD',
        }
    
    def test_create_tour(self):
        tour = Tour.objects.create(**self.tour_data)
        self.assertEqual(tour.title, 'تور استانبول')
        self.assertEqual(tour.slug, 'istanbul-tour')
    
    def test_tour_price_positive(self):
        self.tour_data['price'] = -100
        with self.assertRaises(ValidationError):
            tour = Tour(**self.tour_data)
            tour.full_clean()
```

### تست‌های Frontend
```typescript
// __tests__/components/TourCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TourCard } from '@/components/TourCard';

const mockTour = {
  id: '1',
  title: 'تور استانبول',
  slug: 'istanbul-tour',
  description: 'تور زیبای استانبول',
  price: 1000,
  currency: 'USD',
  // ... other fields
};

describe('TourCard', () => {
  it('renders tour information correctly', () => {
    render(<TourCard tour={mockTour} />);
    
    expect(screen.getByText('تور استانبول')).toBeInTheDocument();
    expect(screen.getByText('تور زیبای استانبول')).toBeInTheDocument();
  });
  
  it('calls onBook when book button is clicked', () => {
    const mockOnBook = jest.fn();
    render(<TourCard tour={mockTour} onBook={mockOnBook} />);
    
    fireEvent.click(screen.getByText('رزرو تور'));
    expect(mockOnBook).toHaveBeenCalledWith('1');
  });
});
```

### کیفیت کد
```bash
# Backend - Flake8
docker-compose exec backend flake8 . --max-line-length=88 --extend-ignore=E203,W503

# Backend - Black (formatting)
docker-compose exec backend black .

# Frontend - ESLint
docker-compose exec frontend npm run lint

# Frontend - Prettier
docker-compose exec frontend npm run format
```

## 📚 مستندسازی

### مستندات کد
- از docstring برای تمام توابع و کلاس‌ها استفاده کنید
- مثال‌های کاربردی اضافه کنید
- پارامترها و مقادیر بازگشتی را مستند کنید

### مستندات API
```python
# views.py
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    summary="دریافت لیست تورها",
    description="دریافت لیست تمام تورهای موجود با امکان فیلتر و صفحه‌بندی",
    parameters=[
        OpenApiParameter(
            name="category",
            type=str,
            description="فیلتر بر اساس دسته‌بندی"
        ),
        OpenApiParameter(
            name="price_min",
            type=float,
            description="حداقل قیمت"
        ),
    ],
    responses={200: TourSerializer(many=True)}
)
@api_view(['GET'])
def tour_list(request):
    """دریافت لیست تورها با فیلترهای مختلف."""
    # implementation
```

### README فایل‌ها
هر فایل مهم باید دارای توضیحات کافی باشد:
```python
"""
مدل‌های مربوط به تورها و محصولات.

این ماژول شامل مدل‌های اصلی برای مدیریت تورها، رویدادها و
انتقالات است. تمام مدل‌ها از UUID به عنوان کلید اصلی استفاده
می‌کنند و دارای ترجمه چندزبانه هستند.

Classes:
    Tour: مدل اصلی تور
    TourVariant: انواع مختلف تور
    TourOption: گزینه‌های اضافی تور
"""
```

## 🐛 گزارش مشکلات

### قالب گزارش مشکل
```markdown
## خلاصه مشکل
توضیح کوتاه از مشکل

## مراحل تکرار
1. به صفحه تورها بروید
2. روی تور "استانبول" کلیک کنید
3. روی دکمه "رزرو" کلیک کنید
4. خطای 500 مشاهده می‌شود

## رفتار مورد انتظار
کاربر باید به صفحه رزرو هدایت شود

## رفتار فعلی
صفحه خطای 500 نمایش داده می‌شود

## اطلاعات محیط
- مرورگر: Chrome 120.0.6099.109
- سیستم عامل: Windows 11
- نسخه: v1.2.0

## لاگ‌ها
```
Error: TypeError: Cannot read property 'price' of undefined
    at TourDetail.js:45:12
```

## تصاویر
[اگر مربوط باشد، اسکرین‌شات اضافه کنید]
```

### برچسب‌های مناسب
- `bug`: مشکل در کد
- `enhancement`: بهبود ویژگی موجود
- `documentation`: مشکل در مستندات
- `good first issue`: مناسب برای مبتدیان
- `help wanted`: نیاز به کمک
- `priority: high`: اولویت بالا
- `priority: low`: اولویت پایین

## 💡 درخواست ویژگی‌ها

### قالب درخواست ویژگی
```markdown
## خلاصه ویژگی
توضیح کوتاه از ویژگی درخواستی

## مشکل حل شده
توضیح اینکه این ویژگی چه مشکلی را حل می‌کند

## راه‌حل پیشنهادی
توضیح جزئیات پیاده‌سازی

## راه‌حل‌های جایگزین
راه‌حل‌های دیگر (اگر وجود دارد)

## اطلاعات اضافی
هر اطلاعات مفید دیگر
```

## 🤝 ارتباط با تیم

### کانال‌های ارتباطی
- **GitHub Issues**: برای مشکلات و درخواست ویژگی‌ها
- **GitHub Discussions**: برای سوالات و بحث‌ها
- **تلگرام**: @PeykanDev
- **ایمیل**: dev@peykantravelistanbul.com

### قوانین ارتباط
- محترمانه و حرفه‌ای باشید
- قبل از پرسش، مستندات را مطالعه کنید
- جزئیات کافی ارائه دهید
- صبور باشید

### زمان‌بندی پاسخ
- **Issues**: 24-48 ساعت
- **Pull Requests**: 1-3 روز کاری
- **سوالات عمومی**: 1-2 روز کاری
- **مشکلات اضطراری**: 4-8 ساعت

## 🎉 شناخت مشارکت‌ها

### انواع مشارکت
- **کد**: پیاده‌سازی ویژگی‌ها و رفع مشکلات
- **مستندات**: بهبود راهنماها و مستندات
- **تست**: نوشتن تست‌ها و گزارش مشکلات
- **طراحی**: بهبود UI/UX
- **ترجمه**: ترجمه محتوا به زبان‌های مختلف

### شناخت
- نام شما در فایل `CONTRIBUTORS.md` اضافه می‌شود
- مشارکت‌های برجسته در README معرفی می‌شوند
- امکان عضویت در تیم اصلی پروژه

---

## 📞 پشتیبانی

اگر سوالی دارید یا به کمک نیاز دارید:
1. ابتدا این راهنما را مطالعه کنید
2. در Issues جستجو کنید
3. Discussion جدید ایجاد کنید
4. با تیم تماس بگیرید

**تیم توسعه Peykan Tourism**
- GitHub: [PeykanTravel/peykan-tourism](https://github.com/PeykanTravel/peykan-tourism)
- تلگرام: @PeykanDev
- ایمیل: dev@peykantravelistanbul.com

**سپاس از مشارکت شما! 🙏** 