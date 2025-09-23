#!/usr/bin/env python
"""
نمونه کد برای ایجاد یک تور کامل با همه اجزاء
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
    TourPricing, TourOption, TourItinerary, TourGallery
)

def create_complete_tour():
    """ایجاد یک تور کامل با همه اجزاء"""

    print("🚀 شروع ایجاد تور نمونه...")

    # مرحله 1: ایجاد دسته‌بندی
    print("\n📁 مرحله 1: ایجاد دسته‌بندی")
    category, created = TourCategory.objects.get_or_create(
        slug='cultural-tours',
        defaults={
            'name': 'تورهای فرهنگی',
            'description': 'تورهای فرهنگی و تاریخی'
        }
    )
    print(f"✅ دسته‌بندی: {category.name}")

    # مرحله 2: ایجاد تور پایه
    print("\n🏛️ مرحله 2: ایجاد تور پایه")
    tour, created = Tour.objects.get_or_create(
        slug='persian-garden-tour',
        defaults={
            'title': 'تور باغ‌های ایرانی',
            'description': 'پیمایش باغ‌های زیبای ایرانی و آثار تاریخی',
            'short_description': 'یک روز پیمایش میراث باغ‌سازی ایران',
            'highlights': 'باغ‌های ایرانی، آثار تاریخی، راهنمای محلی',
            'rules': 'لطفاً 15 دقیقه قبل از زمان حرکت حاضر شوید',
            'required_items': 'کفش راحت، دوربین، بطری آب',
            'price': Decimal('75.00'),
            'currency': 'USD',
            'duration_hours': 8,
            'pickup_time': time(8, 30),
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'min_participants': 2,
            'max_participants': 20,  # ظرفیت کل = مجموع ظرفیت variantها
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
    print(f"✅ تور ایجاد شد: {tour.title}")
    print(f"📊 ظرفیت کل تور: {tour.max_participants} نفر")

    # مرحله 3: ایجاد variantها
    print("\n🏷️ مرحله 3: ایجاد variantها (پکیج‌های مختلف)")
    variants_data = [
        {
            'name': 'اکونومی',
            'base_price': Decimal('75.00'),
            'capacity': 8,  # ظرفیت این variant
            'description': 'پکیج اقتصادی با خدمات پایه',
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
        },
        {
            'name': 'استاندارد',
            'base_price': Decimal('95.00'),
            'capacity': 8,
            'description': 'پکیج استاندارد با خدمات کامل',
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'expert_guide': True,
        },
        {
            'name': 'VIP',
            'base_price': Decimal('125.00'),
            'capacity': 4,
            'description': 'پکیج VIP با خدمات ویژه',
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
    for variant_data in variants_data:
        variant, created = TourVariant.objects.get_or_create(
            tour=tour,
            name=variant_data['name'],
            defaults=variant_data
        )
        variants.append(variant)
        print(f"✅ Variant: {variant.name} - قیمت: ${variant.base_price} - ظرفیت: {variant.capacity}")

    # بررسی مجموع ظرفیت‌ها
    total_variant_capacity = sum(v.capacity for v in variants)
    print(f"📊 مجموع ظرفیت variantها: {total_variant_capacity}")
    print(f"📊 ظرفیت تور: {tour.max_participants}")
    print(f"⚖️ تطابق ظرفیت: {'✅' if total_variant_capacity == tour.max_participants else '❌'}")

    # مرحله 4: ایجاد pricing برای هر variant و گروه سنی
    print("\n💰 مرحله 4: ایجاد قیمت‌گذاری بر اساس گروه سنی")
    for variant in variants:
        for age_group, factor in [('infant', 0.0), ('child', 0.7), ('adult', 1.0)]:
            pricing, created = TourPricing.objects.get_or_create(
                tour=tour,
                variant=variant,
                age_group=age_group,
                defaults={
                    'factor': Decimal(str(factor)),
                    'is_free': age_group == 'infant',
                    'requires_services': age_group != 'infant',
                }
            )
            final_price = pricing.final_price
            print(f"✅ قیمت‌گذاری: {variant.name} - {age_group} - ${final_price}")

    # مرحله 5: ایجاد برنامه زمانی (schedule)
    print("\n📅 مرحله 5: ایجاد برنامه زمانی")
    base_date = date.today() + timedelta(days=7)  # یک هفته بعد

    # ایجاد schedule برای 3 روز متوالی
    schedules = []
    for i in range(3):
        schedule_date = base_date + timedelta(days=i)
        schedule, created = TourSchedule.objects.get_or_create(
            tour=tour,
            start_date=schedule_date,
            defaults={
                'end_date': schedule_date,
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'is_available': True,
                'day_of_week': schedule_date.weekday(),
            }
        )

        # مقداردهی ظرفیت variantها برای این schedule
        schedule.initialize_variant_capacities()

        schedules.append(schedule)
        print(f"✅ برنامه زمانی: {schedule.start_date} - ظرفیت: {schedule.compute_total_capacity()}")

    # مرحله 6: ایجاد گزینه‌های اضافی (options)
    print("\n🎯 مرحله 6: ایجاد گزینه‌های اضافی")
    options_data = [
        {
            'name': 'راهنمای خصوصی',
            'description': 'راهنمای اختصاصی برای گروه شما',
            'price': Decimal('30.00'),
            'option_type': 'service',
            'max_quantity': 1,
        },
        {
            'name': 'نهار ویژه',
            'description': 'نهار در رستوران منتخب',
            'price': Decimal('15.00'),
            'option_type': 'food',
            'max_quantity': 10,
        },
        {
            'name': 'پکیج عکس',
            'description': 'خدمات عکاسی حرفه‌ای',
            'price': Decimal('20.00'),
            'option_type': 'equipment',
            'max_quantity': 5,
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

    # مرحله 7: ایجاد itinerary (برنامه سفر)
    print("\n🗺️ مرحله 7: ایجاد برنامه سفر")
    itinerary_data = [
        {
            'order': 1,
            'title': 'دریافت از هتل',
            'description': 'دریافت مهمانان از هتل و انتقال به محل شروع تور',
            'duration_minutes': 30,
            'location': 'هتل مرکزی',
        },
        {
            'order': 2,
            'title': 'بازدید از باغ شاهزاده ماهان',
            'description': 'پیمایش باغ زیبای شاهزاده ماهان و آشنایی با معماری ایرانی',
            'duration_minutes': 120,
            'location': 'باغ شاهزاده ماهان',
        },
        {
            'order': 3,
            'title': 'ناهار سنتی',
            'description': 'نهار سنتی ایرانی در فضای باز',
            'duration_minutes': 60,
            'location': 'رستوران سنتی',
        },
        {
            'order': 4,
            'title': 'بازدید از باغ ارم',
            'description': 'پیمایش بزرگترین باغ ایرانی',
            'duration_minutes': 90,
            'location': 'باغ ارم',
        },
        {
            'order': 5,
            'title': 'بازگشت به هتل',
            'description': 'انتقال به هتل و پایان تور',
            'duration_minutes': 30,
            'location': 'هتل مرکزی',
        }
    ]

    for item_data in itinerary_data:
        # برای مدل‌های translatable باید از روش متفاوتی استفاده کنیم
        itinerary, created = TourItinerary.objects.get_or_create(
            tour=tour,
            order=item_data['order'],
            defaults={
                'duration_minutes': item_data['duration_minutes'],
                'location': item_data['location'],
            }
        )

        # تنظیم فیلدهای translatable
        itinerary.title = item_data['title']
        itinerary.description = item_data['description']
        itinerary.save()

        print(f"✅ ایستگاه {item_data['order']}: {item_data['title']}")

    print("\n" + "="*60)
    print("📊 خلاصه تور ایجاد شده")
    print("="*60)
    print(f"🏛️ تور: {tour.title}")
    print(f"💰 قیمت پایه: ${tour.price}")
    print(f"⏰ مدت زمان: {tour.duration_hours} ساعت")
    print(f"👥 ظرفیت کل: {tour.max_participants} نفر")
    print(f"🏷️ تعداد variantها: {len(variants)}")
    print(f"📅 تعداد برنامه‌های زمانی: {len(schedules)}")
    print(f"🎯 تعداد گزینه‌های اضافی: {len(options_data)}")
    print(f"🗺️ تعداد ایستگاه‌های برنامه سفر: {len(itinerary_data)}")

    print("\n✅ تور کامل با موفقیت ایجاد شد!")
    print("💡 نکات مهم:")
    print("   - ظرفیت کل تور باید برابر مجموع ظرفیت variantها باشد")
    print("   - هر variant باید قیمت‌گذاری برای همه گروه‌های سنی داشته باشد")
    print("   - برنامه‌های زمانی باید ظرفیت variantها را مقداردهی کنند")
    print("   - گزینه‌های اضافی باید قیمت‌گذاری شوند")

if __name__ == '__main__':
    create_complete_tour()
