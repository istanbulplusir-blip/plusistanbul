#!/usr/bin/env python
"""
الگوی آماده برای ایجاد تور - کپی و استفاده کنید
"""
import os
import sys
import django
from datetime import date, time, timedelta
from decimal import Decimal

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from tours.models import (
    TourCategory, Tour, TourVariant, TourSchedule,
    TourPricing, TourOption, TourItinerary
)

def create_tour_template():
    """الگوی ایجاد تور - مقادیر را تغییر دهید"""

    # ===== تنظیمات تور =====
    TOUR_CONFIG = {
        'slug': 'your-tour-slug',
        'title': 'عنوان تور شما',
        'description': 'توضیحات کامل تور',
        'short_description': 'توضیحات کوتاه',
        'price': Decimal('100.00'),  # قیمت پایه
        'max_participants': 20,  # ظرفیت کل
        'duration_hours': 8,
        'start_time': time(9, 0),
        'end_time': time(17, 0),
        'category_slug': 'cultural-tours',
    }

    # ===== تنظیمات variantها =====
    VARIANTS_CONFIG = [
        {
            'name': 'اکونومی',
            'base_price': Decimal('100.00'),
            'capacity': 10,
            'description': 'پکیج اقتصادی',
        },
        {
            'name': 'VIP',
            'base_price': Decimal('150.00'),
            'capacity': 10,
            'description': 'پکیج VIP',
            'includes_photographer': True,
            'private_transfer': True,
        },
    ]

    # ===== تنظیمات برنامه زمانی =====
    SCHEDULE_DAYS = 7  # چند روز بعد شروع شود
    SCHEDULE_COUNT = 5  # چند روز متوالی

    # ===== تنظیمات گزینه‌های اضافی =====
    OPTIONS_CONFIG = [
        {
            'name': 'راهنمای خصوصی',
            'price': Decimal('30.00'),
            'option_type': 'service',
            'max_quantity': 1,
        },
    ]

    # ===== اجرای ایجاد تور =====

    # 1. ایجاد/دریافت دسته‌بندی
    category, _ = TourCategory.objects.get_or_create(
        slug=TOUR_CONFIG['category_slug'],
        defaults={'name': 'دسته‌بندی پیش‌فرض'}
    )

    # 2. ایجاد تور
    tour, created = Tour.objects.get_or_create(
        slug=TOUR_CONFIG['slug'],
        defaults={
            'title': TOUR_CONFIG['title'],
            'description': TOUR_CONFIG['description'],
            'short_description': TOUR_CONFIG['short_description'],
            'price': TOUR_CONFIG['price'],
            'currency': 'USD',
            'max_participants': TOUR_CONFIG['max_participants'],
            'duration_hours': TOUR_CONFIG['duration_hours'],
            'start_time': TOUR_CONFIG['start_time'],
            'end_time': TOUR_CONFIG['end_time'],
            'min_participants': 1,
            'booking_cutoff_hours': 24,
            'cancellation_hours': 48,
            'refund_percentage': 70,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'tour_type': 'day',
            'transport_type': 'land',
            'is_active': True,
            'category': category,
        }
    )

    # 3. ایجاد variantها
    variants = []
    for variant_config in VARIANTS_CONFIG:
        variant, _ = TourVariant.objects.get_or_create(
            tour=tour,
            name=variant_config['name'],
            defaults=variant_config
        )
        variants.append(variant)

    # 4. ایجاد pricing برای همه variantها
    for variant in variants:
        for age_group, factor in [('infant', 0.0), ('child', 0.7), ('adult', 1.0)]:
            TourPricing.objects.get_or_create(
                tour=tour,
                variant=variant,
                age_group=age_group,
                defaults={
                    'factor': Decimal(str(factor)),
                    'is_free': age_group == 'infant',
                }
            )

    # 5. ایجاد schedules
    base_date = date.today() + timedelta(days=SCHEDULE_DAYS)
    for i in range(SCHEDULE_COUNT):
        schedule_date = base_date + timedelta(days=i)
        schedule, _ = TourSchedule.objects.get_or_create(
            tour=tour,
            start_date=schedule_date,
            defaults={
                'end_date': schedule_date,
                'start_time': TOUR_CONFIG['start_time'],
                'end_time': TOUR_CONFIG['end_time'],
                'is_available': True,
                'day_of_week': schedule_date.weekday(),
            }
        )
        schedule.initialize_variant_capacities()

    # 6. ایجاد options
    for option_config in OPTIONS_CONFIG:
        TourOption.objects.get_or_create(
            tour=tour,
            name=option_config['name'],
            defaults={
                **option_config,
                'currency': 'USD',
                'is_available': True,
            }
        )

    print(f"✅ تور '{tour.title}' با موفقیت ایجاد شد!")
    print(f"📊 ظرفیت کل: {tour.max_participants}")
    print(f"🏷️ تعداد variantها: {len(variants)}")
    print(f"📅 تعداد برنامه‌های زمانی: {SCHEDULE_COUNT}")

if __name__ == '__main__':
    create_tour_template()
