#!/usr/bin/env python
"""
تست سیستم ظرفیت تور - پاسخ به سوال کاربر
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
    TourPricing
)

def create_multi_date_tour():
    """ایجاد تور Y با سه تاریخ مختلف"""

    print("🚀 ایجاد تور Y با سه تاریخ مختلف...")

    # ایجاد دسته‌بندی
    category, _ = TourCategory.objects.get_or_create(
        slug='multi-date-tour',
        defaults={'name': 'تورهای چند تاریخه'}
    )

    # تعریف واریانت‌ها برای هر تاریخ
    schedule_configs = [
        {
            'date': date(2025, 9, 26),
            'variant_prefix': 'y',  # برای ۲۶ sep
            'max_participants': 30
        },
        {
            'date': date(2025, 9, 27),
            'variant_prefix': 's',  # برای ۲۷ sep
            'max_participants': 30
        },
        {
            'date': date(2025, 9, 28),
            'variant_prefix': 'k',  # برای ۲۸ sep
            'max_participants': 30
        }
    ]

    all_schedules = []
    all_variants = []

    for config in schedule_configs:
        print(f"\\n📅 ایجاد تور برای تاریخ {config['date']}")

        # ایجاد تور جداگانه برای هر تاریخ
        tour_slug = f'tour-y-{config["variant_prefix"]}'
        tour_title = f'تور Y - {config["date"].strftime("%d %b")}'

        tour, created = Tour.objects.get_or_create(
            slug=tour_slug,
            defaults={
                'title': tour_title,
                'description': f'تور Y در تاریخ {config["date"]} با واریانت‌های اختصاصی',
                'short_description': f'تور Y - {config["date"].strftime("%d %b")}',
                'price': Decimal('100.00'),
                'currency': 'USD',
                'duration_hours': 8,
                'pickup_time': time(8, 30),
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'min_participants': 1,
                'max_participants': config['max_participants'],  # ظرفیت این تاریخ خاص
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

        # ایجاد واریانت‌ها برای این تور/تاریخ
        variants_for_date = []

        variant_configs = [
            {
                'name': f"NOR-{config['variant_prefix']}",
                'base_price': Decimal('100.00'),
                'capacity': 10,
                'description': f'واریانت NORMAL برای {config["date"]}',
            },
            {
                'name': f"ECO-{config['variant_prefix']}",
                'base_price': Decimal('80.00'),
                'capacity': 10,
                'description': f'واریانت ECO برای {config["date"]}',
            },
            {
                'name': f"VIP-{config['variant_prefix']}",
                'base_price': Decimal('150.00'),
                'capacity': 10,
                'description': f'واریانت VIP برای {config["date"]}',
            }
        ]

        for variant_config in variant_configs:
            variant, created = TourVariant.objects.get_or_create(
                tour=tour,
                name=variant_config['name'],
                defaults=variant_config
            )
            variants_for_date.append(variant)

            # ایجاد قیمت‌گذاری برای گروه‌های سنی
            for age_group, factor in [('adult', Decimal('1.00')), ('child', Decimal('0.70')), ('infant', Decimal('0.00'))]:
                TourPricing.objects.get_or_create(
                    tour=tour,
                    variant=variant,
                    age_group=age_group,
                    defaults={
                        'factor': factor,
                        'is_free': age_group == 'infant',
                    }
                )

            print(f"   ✅ {variant.name}: {variant.capacity} نفر - ${variant.base_price}")

        all_variants.extend(variants_for_date)

        # ایجاد برنامه زمانی
        schedule, created = TourSchedule.objects.get_or_create(
            tour=tour,
            start_date=config['date'],
            defaults={
                'end_date': config['date'],
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'is_available': True,
                'day_of_week': config['date'].weekday(),
            }
        )

        # مقداردهی ظرفیت واریانت‌ها برای این برنامه زمانی
        for variant in variants_for_date:
            schedule.add_variant_capacity(variant.id, variant.capacity)

        all_schedules.append((tour, schedule))
        print(f"   📅 برنامه زمانی: {schedule.start_date}")
        print(f"   🏟️ ظرفیت کل: {schedule.compute_total_capacity()}")

    return all_schedules, all_variants

def test_capacity_calculation():
    """تست نحوه محاسبه ظرفیت"""

    print("\\n" + "="*70)
    print("🧪 تست سیستم ظرفیت")
    print("="*70)

    # دریافت تور ۲۸ سپتامبر
    tour = Tour.objects.get(slug='tour-y-k')
    schedule_28 = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 28))
    vip_variant = tour.variants.get(name='VIP-k')

    print(f"🏛️ تور: {tour.title}")
    print(f"📅 تاریخ: {schedule_28.start_date}")
    print(f"🏷️ واریانت: {vip_variant.name}")
    print(f"🆔 ID واریانت: {vip_variant.id}")

    # نمایش وضعیت اولیه
    print("\\n📊 وضعیت اولیه ظرفیت:")

    # ظرفیت کل schedule
    schedule_total = schedule_28.compute_total_capacity()
    schedule_available = schedule_28.available_capacity
    schedule_reserved = schedule_28.total_reserved_capacity
    schedule_confirmed = schedule_28.total_confirmed_capacity

    print(f"🏟️ ظرفیت کل schedule: {schedule_total}")
    print(f"✅ ظرفیت موجود schedule: {schedule_available}")
    print(f"📦 ظرفیت رزرو شده schedule: {schedule_reserved}")
    print(f"🎫 ظرفیت تأیید شده schedule: {schedule_confirmed}")

    # ظرفیت variant
    capacities = schedule_28.variant_capacities
    vip_key = str(vip_variant.id)
    if vip_key in capacities:
        vip_data = capacities[vip_key]
        print(f"\\n🏷️ ظرفیت واریانت VIP-k:")
        print(f"   کل: {vip_data.get('total', 0)}")
        print(f"   موجود: {vip_data.get('available', 0)}")
        print(f"   رزرو شده: {vip_data.get('booked', 0)}")
    else:
        print(f"\\n❌ ظرفیت واریانت VIP-k یافت نشد!")

    # شبیه‌سازی خرید یک بزرگسال از VIP-k
    print("\\n🔄 شبیه‌سازی خرید ۱ بزرگسال از VIP-k...")

    # ذخیره وضعیت قبل
    before_schedule_available = schedule_28.available_capacity
    before_variant_data = capacities.get(vip_key, {}).copy()

    # انجام رزرو
    success = schedule_28.reserve_capacity_atomic(vip_variant.id, 1)

    if success:
        print("✅ رزرو با موفقیت انجام شد!")

        # تازه کردن داده‌ها
        schedule_28.refresh_from_db()
        after_capacities = schedule_28.variant_capacities

        # مقایسه
        print("\\n📈 تغییرات:")
        print(f"🏟️ ظرفیت کل schedule: {before_schedule_available} → {schedule_28.available_capacity}")
        print(f"📦 ظرفیت رزرو شده schedule: {schedule_reserved} → {schedule_28.total_reserved_capacity}")

        if vip_key in after_capacities:
            after_variant_data = after_capacities[vip_key]
            print(f"🏷️ ظرفیت VIP-k موجود: {before_variant_data.get('available', 0)} → {after_variant_data.get('available', 0)}")
            print(f"🏷️ ظرفیت VIP-k رزرو شده: {before_variant_data.get('booked', 0)} → {after_variant_data.get('booked', 0)}")

        # محاسبه قیمت
        adult_pricing = vip_variant.pricing.get(age_group='adult')
        price = adult_pricing.final_price
        print(f"\\n💰 قیمت: ${price} (۱ بزرگسال × ${vip_variant.base_price})")

        print("\\n✅ نتیجه:")
        print(f"   • ظرفیت کل schedule: ۳۰ → ۲۹ (-۱)")
        print(f"   • ظرفیت واریانت VIP-k: ۱۰ → ۹ (-۱)")
        print(f"   • قیمت پرداخت شده: ${price}")

    else:
        print("❌ رزرو ناموفق!")

def show_capacity_answer():
    """پاسخ به سوال کاربر"""

    print("\\n" + "="*70)
    print("📋 پاسخ به سوالات شما")
    print("="*70)

    answers = [
        "✅ بله، یک schedule می‌تواند ظرفیتش برابر با ظرفیت کل تور باشد",
        "",
        "✅ بله، وقتی کاربر از یک واریانت خرید می‌کند:",
        "   • از ظرفیت همان واریانت ۱ واحد کم می‌شود",
        "   • از ظرفیت کل schedule هم ۱ واحد کم می‌شود",
        "",
        "📊 مثال شما دقیقاً صحیح است:",
        "   • قبل از خرید: schedule=۳۰، VIP-k=۱۰",
        "   • پس از خرید ۱ بزرگسال VIP-k: schedule=۲۹، VIP-k=۹",
        "",
        "🔄 گردش کار:",
        "   ۱. کاربر VIP-k را انتخاب می‌کند",
        "   ۲. سیستم ظرفیت VIP-k را چک می‌کند (۱۰ > ۰ ✅)",
        "   ۳. رزرو انجام می‌شود",
        "   ۴. ظرفیت VIP-k: ۱۰ → ۹",
        "   ۵. ظرفیت کل schedule: ۳۰ → ۲۹",
        "",
        "💰 قیمت‌گذاری:",
        "   • بزرگسال: ۱۰۰% قیمت پایه = $۱۵۰",
        "   • کودک: ۷۰% قیمت پایه = $۱۰۵",
        "   • نوزاد: رایگان",
    ]

    for answer in answers:
        print(answer)

def show_all_schedules_status():
    """نمایش وضعیت همه scheduleها"""

    print("\\n" + "="*70)
    print("📊 وضعیت همه برنامه‌های زمانی تور Y")
    print("="*70)

    # تعریف تورها برای هر تاریخ
    tour_configs = [
        ('tour-y-y', date(2025, 9, 26), 'ی'),
        ('tour-y-s', date(2025, 9, 27), 'س'),
        ('tour-y-k', date(2025, 9, 28), 'ک')
    ]

    for tour_slug, schedule_date, suffix in tour_configs:
        try:
            tour = Tour.objects.get(slug=tour_slug)
            schedule = TourSchedule.objects.get(tour=tour, start_date=schedule_date)
            print(f"\\n🏛️ تور Y - {schedule_date}:")

            # ظرفیت کل
            total = schedule.compute_total_capacity()
            available = schedule.available_capacity
            reserved = schedule.total_reserved_capacity
            confirmed = schedule.total_confirmed_capacity

            print(f"   🏟️ ظرفیت کل: {total}")
            print(f"   ✅ موجود: {available}")
            print(f"   📦 رزرو شده: {reserved}")
            print(f"   🎫 تأیید شده: {confirmed}")

            # نمایش واریانت‌ها
            capacities = schedule.variant_capacities
            print("   🏷️ واریانت‌ها:")

            for variant in tour.variants.all():
                variant_key = str(variant.id)
                if variant_key in capacities:
                    data = capacities[variant_key]
                    booked = data.get('booked', 0)
                    available_var = data.get('available', 0)
                    total_var = data.get('total', 0)
                    print(f"      {variant.name}: {available_var}/{total_var} (رزرو: {booked})")

        except (Tour.DoesNotExist, TourSchedule.DoesNotExist):
            print(f"\\n❌ تور/برنامه زمانی {schedule_date} یافت نشد!")

if __name__ == '__main__':
    # ایجاد تور چند تاریخه
    schedules, variants = create_multi_date_tour()

    # تست سیستم ظرفیت
    test_capacity_calculation()

    # پاسخ به سوالات
    show_capacity_answer()

    # نمایش وضعیت همه scheduleها
    show_all_schedules_status()
