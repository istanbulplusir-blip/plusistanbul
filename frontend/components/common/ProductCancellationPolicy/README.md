# ProductCancellationPolicy Component

## Overview
`ProductCancellationPolicy` یک کامپوننت مشترک و قابل استفاده مجدد است که برای نمایش قوانین لغو (Cancellation Policies) در صفحات مختلف محصولات استفاده می‌شود.

## Features
- **پشتیبانی از 3 نوع محصول**: تور، رویداد، و ترانسفر
- **طراحی تطبیقی**: هر محصول رنگ و آیکون مخصوص خود را دارد
- **نمایش اطلاعات محصول**: تاریخ، محل، مدت زمان و سایر اطلاعات مرتبط
- **قابلیت گسترش**: نمایش جزئیات کامل قوانین لغو
- **پشتیبانی از Dark Mode**: سازگار با تم تاریک
- **بین‌المللی‌سازی**: پشتیبانی از چند زبان

## Props

### Required Props
- `policies`: آرایه‌ای از قوانین لغو
- `productType`: نوع محصول (`'tour' | 'event' | 'transfer'`)

### Optional Props
- `productData`: اطلاعات محصول (تاریخ، محل، مدت زمان و...)
- `showDetails`: نمایش جزئیات (برای کنترل خارجی)
- `onToggleDetails`: تابع تغییر وضعیت نمایش جزئیات
- `className`: کلاس‌های CSS اضافی

## Usage Examples

### تور
```tsx
<ProductCancellationPolicy
  policies={[
    {
      hours_before: 24,
      refund_percentage: 100,
      description: 'لغو رایگان تا 24 ساعت قبل از شروع تور'
    },
    {
      hours_before: 12,
      refund_percentage: 50,
      description: '50% بازگشت وجه تا 12 ساعت قبل از شروع تور'
    }
  ]}
  productType="tour"
  productData={{
    date: '2024-01-15',
    location: 'تهران',
    duration: '8 ساعت'
  }}
/>
```

### رویداد
```tsx
<ProductCancellationPolicy
  policies={[
    {
      hours_before: 48,
      refund_percentage: 100,
      description: 'لغو رایگان تا 48 ساعت قبل از اجرا'
    }
  ]}
  productType="event"
  productData={{
    date: '2024-01-20',
    venue: 'سالن همایش',
    duration: '2 ساعت'
  }}
/>
```

### ترانسفر
```tsx
<ProductCancellationPolicy
  policies={[
    {
      hours_before: 24,
      refund_percentage: 100,
      description: 'لغو رایگان تا 24 ساعت قبل از سرویس'
    }
  ]}
  productType="transfer"
  productData={{
    date: '2024-01-15',
    location: 'فرودگاه امام',
    venue: 'تهران',
    duration: '45 دقیقه'
  }}
/>
```

## Styling
کامپوننت از Tailwind CSS استفاده می‌کند و شامل:
- رنگ‌های مخصوص هر محصول
- آیکون‌های مناسب
- انیمیشن‌های نرم
- پشتیبانی از حالت تاریک

## Integration
این کامپوننت در صفحات زیر استفاده شده است:
- `app/[locale]/tours/[slug]/page.tsx` - صفحه جزئیات تور
- `app/[locale]/events/[slug]/page.tsx` - صفحه جزئیات رویداد  
- `app/[locale]/transfers/booking/page.tsx` - صفحه رزرو ترانسفر

## Dependencies
- `next-intl` برای بین‌المللی‌سازی
- `lucide-react` برای آیکون‌ها
- `react` برای state management
