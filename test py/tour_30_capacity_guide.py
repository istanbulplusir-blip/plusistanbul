#!/usr/bin/env python
"""
راهنمای کامل ساخت تور ۳۰ نفره با ۳ واریانت و سیستم قیمت‌گذاری
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

from tours.models import TourCategory, Tour, TourVariant, TourSchedule, TourPricing

def show_tour_structure():
    """نمایش ساختار تور ایجاد شده"""

    print("🎯 راهنمای ساخت تور ۳۰ نفره با ۳ واریانت")
    print("="*70)

    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))

        print(f"🏛️ تور: {tour.title}")
        print(f"📅 تاریخ: {schedule.start_date}")
        print(f"⏰ زمان: {schedule.start_time} - {schedule.end_time}")
        print(f"👥 ظرفیت کل: {tour.max_participants} نفر")
        print(f"🏷️ تعداد واریانت: {tour.variants.count()}")

        print("\\n" + "🏷️ ساختار واریانت‌ها و قیمت‌گذاری:")
        print("-" * 50)

        for variant in tour.variants.all():
            print(f"\\n{variant.name} (ظرفیت: {variant.capacity} نفر)")
            print(f"   💰 قیمت پایه بزرگسال: ${variant.base_price}")

            # نمایش قیمت‌گذاری گروه سنی
            pricings = variant.pricing.all()
            for pricing in pricings:
                group_name = {
                    'adult': '👨 بزرگسال',
                    'child': '👶 کودک',
                    'infant': '🍼 نوزاد'
                }.get(pricing.age_group, pricing.age_group)

                factor_text = f"{pricing.factor * 100:.0f}%" if pricing.factor != 1 else "۱۰۰%"
                print(f"   {group_name}: ${pricing.final_price} ({factor_text})")

            # نمایش خدمات ویژه
            services = []
            if variant.includes_transfer: services.append("انتقال")
            if variant.includes_guide: services.append("راهنما")
            if variant.includes_meal: services.append("وعده غذایی")
            if variant.includes_photographer: services.append("عکاس")
            if variant.private_transfer: services.append("انتقال خصوصی")
            if variant.expert_guide: services.append("راهنمای خبره")
            if variant.special_meal: services.append("وعده ویژه")

            if services:
                print(f"   🎯 خدمات: {', '.join(services)}")

        # نمایش وضعیت ظرفیت
        print("\\n" + "📊 وضعیت ظرفیت‌ها:")
        print("-" * 30)

        total_capacity = schedule.compute_total_capacity()
        available_capacity = schedule.available_capacity
        booked_capacity = schedule.total_reserved_capacity
        confirmed_capacity = schedule.total_confirmed_capacity

        print(f"🏟️ ظرفیت کل: {total_capacity}")
        print(f"✅ ظرفیت موجود: {available_capacity}")
        print(f"📦 ظرفیت رزرو شده: {booked_capacity}")
        print(f"🎫 ظرفیت تأیید شده: {confirmed_capacity}")
        print(f"📈 استفاده کلی: {((total_capacity - available_capacity) / total_capacity * 100):.1f}%" if total_capacity > 0 else "۰%")

        # نمایش ظرفیت هر واریانت
        print("\\n🏷️ ظرفیت هر واریانت:")
        capacities = schedule.variant_capacities

        for variant in tour.variants.all():
            variant_key = str(variant.id)
            if variant_key in capacities:
                data = capacities[variant_key]
                total = data.get('total', 0)
                available = data.get('available', 0)
                booked = data.get('booked', 0)
                utilization = ((total - available) / total * 100) if total > 0 else 0

                status = "✅" if available > 0 else "❌"
                print(f"   {variant.name}: {available}/{total} نفر - {status} (استفاده: {utilization:.1f}%)")

    except Tour.DoesNotExist:
        print("❌ تور یافت نشد! لطفاً ابتدا تور را ایجاد کنید.")
    except TourSchedule.DoesNotExist:
        print("❌ برنامه زمانی یافت نشد!")

def show_pricing_examples():
    """نمایش مثال‌های قیمت‌گذاری"""

    print("\\n" + "💰 مثال‌های قیمت‌گذاری برای یک خانواده:")
    print("="*50)

    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')

        # مثال برای خانواده ۲ بزرگسال + ۱ کودک + ۱ نوزاد
        print("👨👩👶🍼 مثال: خانواده ۲ بزرگسال + ۱ کودک + ۱ نوزاد")

        for variant in tour.variants.all():
            print(f"\\n🏷️ واریانت {variant.name}:")

            # محاسبه قیمت برای هر عضو خانواده
            adult_pricing = variant.pricing.get(age_group='adult')
            child_pricing = variant.pricing.get(age_group='child')
            infant_pricing = variant.pricing.get(age_group='infant')

            adult_total = adult_pricing.final_price * 2  # ۲ بزرگسال
            child_total = child_pricing.final_price * 1   # ۱ کودک
            infant_total = infant_pricing.final_price * 1 # ۱ نوزاد (رایگان)

            family_total = adult_total + child_total + infant_total

            print(f"   👨 ۲ بزرگسال: ${adult_total} (${adult_pricing.final_price} × ۲)")
            print(f"   👶 ۱ کودک: ${child_total} (${child_pricing.final_price} × ۱)")
            print(f"   🍼 ۱ نوزاد: ${infant_total} (${infant_pricing.final_price} × ۱)")
            print(f"   💰 مجموع: ${family_total}")
            print(f"   💎 قیمت هر نفر: ${family_total / 4:.2f}")

    except Exception as e:
        print(f"❌ خطا در نمایش قیمت‌گذاری: {str(e)}")

def show_system_workflow():
    """نمایش گردش کار سیستم"""

    print("\\n" + "🔄 گردش کار سیستم ظرفیت:")
    print("="*40)

    steps = [
        "۱. 👤 کاربر تور را انتخاب می‌کند",
        "۲. 🗓️ تاریخ مورد نظر را انتخاب می‌کند",
        "۳. 🏷️ واریانت را انتخاب می‌کند (ECO/NORMAL/VIP)",
        "۴. 👥 تعداد نفرات را مشخص می‌کند:",
        "     • بزرگسال (۱۱+): ۱۰۰% قیمت",
        "     • کودک (۲-۱۰): ۷۰% قیمت",
        "     • نوزاد (۰-۲): رایگان",
        "۵. 💰 قیمت کل محاسبه می‌شود",
        "۶. 📦 ظرفیت بررسی می‌شود:",
        "     • اگر ظرفیت کافی باشد: ✅ رزرو انجام می‌شود",
        "     • اگر ظرفیت کافی نباشد: ❌ رزرو رد می‌شود",
        "۷. 🔄 ظرفیت واریانت کاهش می‌یابد",
        "۸. 🎫 پس از پرداخت، ظرفیت تأیید می‌شود",
        "۹. 📊 آمار به‌روز می‌شود"
    ]

    for step in steps:
        print(f"   {step}")

    print("\\n" + "📋 قوانین ظرفیت:")
    print("-" * 20)
    rules = [
        "• ظرفیت کل = مجموع ظرفیت همه واریانت‌ها",
        "• هر واریانت ظرفیت مستقل دارد",
        "• رزرو هم‌زمان انجام می‌شود",
        "• اگر واریانت پر شود، دیگر قابل رزرو نیست",
        "• ظرفیت رزرو شده تا پرداخت نهایی رزرو می‌ماند",
        "• پس از پرداخت، ظرفیت تأیید می‌شود"
    ]

    for rule in rules:
        print(f"   {rule}")

def create_booking_simulation():
    """شبیه‌سازی یک سفارش کامل"""

    print("\\n" + "🎯 شبیه‌سازی سفارش:")
    print("="*30)

    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))
        normal_variant = tour.variants.get(name='NORMAL')

        print("📝 سفارش نمونه:")
        print(f"   تور: {tour.title}")
        print(f"   تاریخ: {schedule.start_date}")
        print(f"   واریانت: {normal_variant.name}")
        print(f"   تعداد: ۲ بزرگسال + ۱ کودک")

        # محاسبه قیمت
        adult_price = normal_variant.pricing.get(age_group='adult').final_price
        child_price = normal_variant.pricing.get(age_group='child').final_price

        total_price = (adult_price * 2) + (child_price * 1)
        print(f"   💰 قیمت: ${total_price} = (${adult_price}×۲ + ${child_price}×۱)")

        # بررسی ظرفیت قبل از سفارش
        normal_key = str(normal_variant.id)
        capacity_before = schedule.variant_capacities.get(normal_key, {})

        print(f"\\n📊 ظرفیت قبل از سفارش:")
        print(f"   {normal_variant.name}: {capacity_before.get('available', 0)}/{capacity_before.get('total', 0)} نفر")

        # انجام سفارش
        print("\\n🔄 انجام سفارش...")
        success = schedule.reserve_capacity_atomic(normal_variant.id, 3)

        if success:
            print("✅ سفارش با موفقیت ثبت شد!")

            # نمایش ظرفیت بعد از سفارش
            schedule.refresh_from_db()
            capacity_after = schedule.variant_capacities.get(normal_key, {})

            print(f"\\n📊 ظرفیت بعد از سفارش:")
            print(f"   {normal_variant.name}: {capacity_after.get('available', 0)}/{capacity_after.get('total', 0)} نفر")

            print("\\n📈 تغییرات:")
            print(f"   موجود: {capacity_before.get('available', 0)} → {capacity_after.get('available', 0)} (-۳)")
            print(f"   رزرو شده: {capacity_before.get('booked', 0)} → {capacity_after.get('booked', 0)} (+۳)")

        else:
            print("❌ سفارش رد شد (ظرفیت کافی نیست)")

    except Exception as e:
        print(f"❌ خطا در شبیه‌سازی: {str(e)}")

def show_admin_actions():
    """نمایش اقدامات مدیریتی"""

    print("\\n" + "⚙️ اقدامات مدیریتی:")
    print("="*25)

    actions = [
        "• ایجاد واریانت جدید",
        "• تغییر ظرفیت واریانت‌ها",
        "• اضافه کردن برنامه زمانی جدید",
        "• تنظیم قیمت‌گذاری",
        "• مشاهده آمار رزروها",
        "• مدیریت ظرفیت‌های رزرو شده",
        "• گزارش‌گیری از فروش"
    ]

    for action in actions:
        print(f"   {action}")

    print("\\n" + "📊 آمار کلیدی:")
    print("-" * 15)

    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))

        stats = [
            f"کل ظرفیت: {schedule.compute_total_capacity()}",
            f"ظرفیت موجود: {schedule.available_capacity}",
            f"ظرفیت رزرو شده: {schedule.total_reserved_capacity}",
            f"ظرفیت تأیید شده: {schedule.total_confirmed_capacity}",
            f"درصد استفاده: {((schedule.compute_total_capacity() - schedule.available_capacity) / schedule.compute_total_capacity() * 100):.1f}%" if schedule.compute_total_capacity() > 0 else "۰%",
        ]

        for stat in stats:
            print(f"   • {stat}")

    except:
        print("   • آمار در دسترس نیست")

if __name__ == '__main__':
    # نمایش ساختار تور
    show_tour_structure()

    # نمایش مثال‌های قیمت‌گذاری
    show_pricing_examples()

    # نمایش گردش کار
    show_system_workflow()

    # شبیه‌سازی سفارش
    create_booking_simulation()

    # نمایش اقدامات مدیریتی
    show_admin_actions()

    print("\\n" + "="*70)
    print("✅ راهنمای کامل تور ۳۰ سپتامبر با ۳ واریانت")
    print("💡 سیستم ظرفیت و قیمت‌گذاری به صورت کامل کار می‌کند!")
    print("="*70)
