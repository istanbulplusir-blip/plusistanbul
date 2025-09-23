#!/usr/bin/env python
"""
ایجاد تور ۳۰ نفره با ۳ واریانت و قیمت‌گذاری گروه سنی
"""
import os
import sys
import django
from datetime import date, time
from decimal import Decimal

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from tours.models import (
    TourCategory, Tour, TourVariant, TourSchedule,
    TourPricing, TourOption
)

def create_30_capacity_tour():
    """ایجاد تور ۳۰ نفره با ۳ واریانت و قیمت‌گذاری گروه سنی"""

    print("🚀 ایجاد تور ۳۰ نفره با ۳ واریانت...")

    # مرحله 1: ایجاد دسته‌بندی
    print("\n📁 مرحله ۱: ایجاد دسته‌بندی")
    category, _ = TourCategory.objects.get_or_create(
        slug='cultural-tours',
        defaults={'name': 'تورهای فرهنگی'}
    )

    # مرحله 2: ایجاد تور پایه
    print("\n🏛️ مرحله ۲: ایجاد تور پایه")
    tour, created = Tour.objects.get_or_create(
        slug='30-capacity-tour-sep',
        defaults={
            'title': 'تور فرهنگی ۳۰ سپتامبر',
            'description': 'تور فرهنگی با ظرفیت ۳۰ نفر در تاریخ ۳۰ سپتامبر',
            'short_description': 'تور ۳۰ سپتامبر - ظرفیت محدود',
            'price': Decimal('100.00'),  # قیمت پایه برای بزرگسالان
            'currency': 'USD',
            'duration_hours': 8,
            'pickup_time': time(8, 30),
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'min_participants': 1,
            'max_participants': 30,  # ظرفیت کل = ۱۰ + ۱۰ + ۱۰
            'booking_cutoff_hours': 24,
            'cancellation_hours': 48,
            'refund_percentage': 80,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'tour_type': 'day',
            'transport_type': 'land',
            'is_active': True,
            'category': category,
        }
    )
    print(f"✅ تور ایجاد شد: {tour.title}")
    print(f"📊 ظرفیت کل تور: {tour.max_participants} نفر")

    # مرحله 3: ایجاد ۳ واریانت با ظرفیت ۱۰ نفر هر کدام
    print("\n🏷️ مرحله ۳: ایجاد ۳ واریانت با ظرفیت ۱۰ نفر هر کدام")
    variants_data = [
        {
            'name': 'ECO',
            'base_price': Decimal('80.00'),  # قیمت پایه برای بزرگسالان در این واریانت
            'capacity': 10,  # ظرفیت این واریانت
            'description': 'واریانت اقتصادی با خدمات پایه',
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
        },
        {
            'name': 'NORMAL',
            'base_price': Decimal('100.00'),  # قیمت پایه برای بزرگسالان
            'capacity': 10,
            'description': 'واریانت استاندارد با خدمات کامل',
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'expert_guide': True,
        },
        {
            'name': 'VIP',
            'base_price': Decimal('150.00'),  # قیمت پایه برای بزرگسالان
            'capacity': 10,
            'description': 'واریانت VIP با خدمات ویژه',
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'includes_photographer': True,
            'private_transfer': True,
            'expert_guide': True,
            'special_meal': True,
        }
    ]

    variants = []
    total_capacity = 0

    for variant_data in variants_data:
        variant, created = TourVariant.objects.get_or_create(
            tour=tour,
            name=variant_data['name'],
            defaults=variant_data
        )
        variants.append(variant)
        total_capacity += variant.capacity
        print(f"✅ واریانت: {variant.name}")
        print(f"   💰 قیمت پایه (بزرگسال): ${variant.base_price}")
        print(f"   👥 ظرفیت: {variant.capacity} نفر")
        print(f"   🎯 خدمات ویژه: {', '.join([k for k, v in variant_data.items() if k.startswith('includes_') or k.startswith('expert_') or k.startswith('private_') or k.startswith('special_') and v == True])}")
        print()

    print(f"📊 مجموع ظرفیت واریانت‌ها: {total_capacity}")
    print(f"📊 ظرفیت تور: {tour.max_participants}")
    print(f"⚖️ تطابق ظرفیت: {'✅' if total_capacity == tour.max_participants else '❌'}")

    # مرحله ۴: ایجاد قیمت‌گذاری برای هر واریانت و گروه سنی
    print("\n💰 مرحله ۴: ایجاد قیمت‌گذاری بر اساس گروه سنی")
    print("📋 سیستم قیمت‌گذاری:")
    print("   • بزرگسال (۱۱+): ۱۰۰% قیمت پایه")
    print("   • کودک (۲-۱۰): ۷۰% قیمت پایه")
    print("   • نوزاد (۰-۲): رایگان (۰%)")
    print()

    for variant in variants:
        print(f"🏷️ واریانت: {variant.name} (قیمت پایه: ${variant.base_price})")

        # بزرگسالان
        pricing_adult, _ = TourPricing.objects.get_or_create(
            tour=tour,
            variant=variant,
            age_group='adult',
            defaults={
                'factor': Decimal('1.00'),  # ۱۰۰%
                'is_free': False,
                'requires_services': True,
            }
        )
        print(f"   👨 بزرگسال: ${pricing_adult.final_price} (۱۰۰%)")

        # کودکان
        pricing_child, _ = TourPricing.objects.get_or_create(
            tour=tour,
            variant=variant,
            age_group='child',
            defaults={
                'factor': Decimal('0.70'),  # ۷۰%
                'is_free': False,
                'requires_services': True,
            }
        )
        print(f"   👶 کودک: ${pricing_child.final_price} (۷۰%)")

        # نوزادان
        pricing_infant, _ = TourPricing.objects.get_or_create(
            tour=tour,
            variant=variant,
            age_group='infant',
            defaults={
                'factor': Decimal('0.00'),  # ۰%
                'is_free': True,
                'requires_services': False,
            }
        )
        print(f"   🍼 نوزاد: ${pricing_infant.final_price} (رایگان)")
        print()

    # مرحله ۵: ایجاد برنامه زمانی برای ۳۰ سپتامبر
    print("\n📅 مرحله ۵: ایجاد برنامه زمانی برای ۳۰ سپتامبر")

    # تاریخ ۳۰ سپتامبر ۲۰۲۵
    schedule_date = date(2025, 9, 30)

    schedule, created = TourSchedule.objects.get_or_create(
        tour=tour,
        start_date=schedule_date,
        defaults={
            'end_date': schedule_date,
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'is_available': True,
            'day_of_week': schedule_date.weekday(),
            'price_adjustment': Decimal('0.00'),
            'price_adjustment_type': 'fixed',
        }
    )

    print(f"✅ برنامه زمانی ایجاد شد: {schedule.start_date}")
    print(f"📅 روز هفته: {schedule.get_day_of_week_display()}")
    print(f"⏰ زمان: {schedule.start_time} - {schedule.end_time}")

    # مقداردهی ظرفیت واریانت‌ها برای این برنامه زمانی
    print("\n🔄 مقداردهی ظرفیت واریانت‌ها...")
    schedule.initialize_variant_capacities()

    print("📊 ظرفیت‌های اولیه برنامه زمانی:")
    if schedule.variant_capacities:
        for variant_id, data in schedule.variant_capacities.items():
            variant = tour.variants.filter(id=variant_id).first()
            if variant:
                print(f"   {variant.name}: {data.get('available', 0)}/{data.get('total', 0)} نفر")

    print(f"🏟️ ظرفیت کل برنامه زمانی: {schedule.compute_total_capacity()} نفر")

    # مرحله ۶: ایجاد گزینه‌های اضافی
    print("\n🎯 مرحله ۶: ایجاد گزینه‌های اضافی")
    options_data = [
        {
            'name': 'صبحانه اضافی',
            'description': 'صبحانه ویژه در هتل',
            'price': Decimal('15.00'),
            'option_type': 'food',
            'max_quantity': 30,
        },
        {
            'name': 'راهنمای خصوصی',
            'description': 'راهنمای اختصاصی برای گروه شما',
            'price': Decimal('50.00'),
            'option_type': 'service',
            'max_quantity': 1,
        },
        {
            'name': 'پکیج عکس حرفه‌ای',
            'description': 'عکس‌برداری حرفه‌ای در طول تور',
            'price': Decimal('30.00'),
            'option_type': 'equipment',
            'max_quantity': 10,
        }
    ]

    for option_data in options_data:
        option, created = TourOption.objects.get_or_create(
            tour=tour,
            name=option_data['name'],
            defaults={
                **option_data,
                'currency': 'USD',
                'is_available': True,
            }
        )
        print(f"✅ گزینه: {option.name} - ${option.price}")

    # خلاصه نهایی
    print("\n" + "="*60)
    print("📊 خلاصه تور ۳۰ سپتامبر")
    print("="*60)
    print(f"🏛️ تور: {tour.title}")
    print(f"📅 تاریخ: {schedule_date}")
    print(f"👥 ظرفیت کل: {tour.max_participants} نفر")
    print(f"🏷️ واریانت‌ها: {len(variants)}")
    print(f"   • ECO: ۱۰ نفر - ${variants[0].base_price}")
    print(f"   • NORMAL: ۱۰ نفر - ${variants[1].base_price}")
    print(f"   • VIP: ۱۰ نفر - ${variants[2].base_price}")
    print(f"💰 قیمت‌گذاری:")
    print(f"   • بزرگسال: ۱۰۰% قیمت پایه")
    print(f"   • کودک: ۷۰% قیمت پایه")
    print(f"   • نوزاد: رایگان")
    print(f"🎯 گزینه‌های اضافی: {len(options_data)}")

    print("\n✅ تور ۳۰ سپتامبر با موفقیت ایجاد شد!")
    print("\n💡 نحوه کار سیستم ظرفیت:")
    print("   ۱. هر سفارش، ظرفیت واریانت مربوطه را کاهش می‌دهد")
    print("   ۲. اگر واریانت پر شود، دیگر قابل رزرو نیست")
    print("   ۳. ظرفیت کل تور = مجموع ظرفیت همه واریانت‌ها")
    print("   ۴. سیستم به صورت هم‌زمان ظرفیت را مدیریت می‌کند")

    return tour, variants, schedule

def demonstrate_capacity_system():
    """نمایش نحوه کارکرد سیستم ظرفیت"""

    print("\n" + "="*60)
    print("🎯 نمایش سیستم ظرفیت")
    print("="*60)

    # دریافت تور ایجاد شده
    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))

        print(f"🏛️ تور: {tour.title}")
        print(f"📅 تاریخ: {schedule.start_date}")

        print("\n📊 وضعیت فعلی ظرفیت:")
        total_capacity = schedule.compute_total_capacity()
        available_capacity = schedule.available_capacity

        print(f"🏟️ ظرفیت کل: {total_capacity}")
        print(f"✅ ظرفیت موجود: {available_capacity}")
        print(f"📦 ظرفیت رزرو شده: {total_capacity - available_capacity}")

        print("\n🏷️ جزئیات ظرفیت هر واریانت:")
        if schedule.variant_capacities:
            for variant_id, data in schedule.variant_capacities.items():
                variant = tour.variants.filter(id=variant_id).first()
                if variant:
                    total = data.get('total', 0)
                    booked = data.get('booked', 0)
                    available = data.get('available', 0)
                    print(f"   {variant.name}:")
                    print(f"      کل: {total}")
                    print(f"      رزرو شده: {booked}")
                    print(f"      موجود: {available}")
                    print(f"      استفاده: {((total - available) / total * 100):.1f}%" if total > 0 else "      استفاده: ۰%")
                    print()

    except Tour.DoesNotExist:
        print("❌ تور یافت نشد. ابتدا تور را ایجاد کنید.")

if __name__ == '__main__':
    # ایجاد تور
    tour, variants, schedule = create_30_capacity_tour()

    # نمایش سیستم ظرفیت
    demonstrate_capacity_system()
