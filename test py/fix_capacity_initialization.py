#!/usr/bin/env python
"""
بررسی و مقداردهی ظرفیت‌های برنامه زمانی
"""
import os
import sys
import django
from datetime import date

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from tours.models import Tour, TourSchedule, TourVariant

def fix_capacity_initialization():
    """بررسی و مقداردهی ظرفیت‌های برنامه زمانی"""

    print("🔍 بررسی وضعیت ظرفیت‌های تور ۳۰ سپتامبر...")

    try:
        # دریافت تور و برنامه زمانی
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))

        print(f"🏛️ تور: {tour.title}")
        print(f"📅 برنامه زمانی: {schedule.start_date}")
        print(f"🏟️ ظرفیت کل تور: {tour.max_participants}")

        # بررسی واریانت‌ها
        variants = tour.variants.all()
        print(f"\\n🏷️ واریانت‌ها ({variants.count()} عدد):")
        total_variant_capacity = 0

        for variant in variants:
            print(f"   • {variant.name}: {variant.capacity} نفر")
            total_variant_capacity += variant.capacity

        print(f"\\n📊 مجموع ظرفیت واریانت‌ها: {total_variant_capacity}")
        print(f"⚖️ تطابق با ظرفیت تور: {'✅' if total_variant_capacity == tour.max_participants else '❌'}")

        # بررسی وضعیت فعلی ظرفیت برنامه زمانی
        print("\\n📈 وضعیت ظرفیت برنامه زمانی:")
        print(f"   کل ظرفیت: {schedule.compute_total_capacity()}")
        print(f"   ظرفیت موجود: {schedule.available_capacity}")
        print(f"   ظرفیت رزرو شده: {schedule.total_reserved_capacity}")
        print(f"   ظرفیت تأیید شده: {schedule.total_confirmed_capacity}")

        # مقداردهی ظرفیت‌ها
        print("\\n🔄 مقداردهی ظرفیت واریانت‌ها...")

        # پاک کردن ظرفیت‌های قبلی
        schedule.variant_capacities_raw = {}
        schedule.save()

        # مقداردهی مجدد
        for variant in variants:
            schedule.add_variant_capacity(variant.id, variant.capacity)
            print(f"   ✅ {variant.name}: {variant.capacity} نفر اضافه شد")

        print("\\n📊 وضعیت پس از مقداردهی:")

        # نمایش جزئیات ظرفیت هر واریانت
        if schedule.variant_capacities:
            print("\\n🏷️ جزئیات ظرفیت هر واریانت:")
            for variant_id, data in schedule.variant_capacities.items():
                variant = tour.variants.filter(id=variant_id).first()
                if variant:
                    total = data.get('total', 0)
                    available = data.get('available', 0)
                    booked = data.get('booked', 0)
                    utilization = ((total - available) / total * 100) if total > 0 else 0

                    print(f"   {variant.name}:")
                    print(f"      کل ظرفیت: {total}")
                    print(f"      موجود: {available}")
                    print(f"      رزرو شده: {booked}")
                    print(f"      استفاده: {utilization:.1f}%")
                    print()

        # بررسی نهایی
        final_total = schedule.compute_total_capacity()
        final_available = schedule.available_capacity

        print("🎯 بررسی نهایی:")
        print(f"   ظرفیت کل محاسبه شده: {final_total}")
        print(f"   ظرفیت موجود: {final_available}")
        print(f"   وضعیت: {'✅ ظرفیت کامل' if final_total == tour.max_participants else '❌ مشکل ظرفیت'}")

        if final_total == tour.max_participants and final_available == tour.max_participants:
            print("\\n✅ سیستم ظرفیت با موفقیت مقداردهی شد!")
            print("💡 اکنون می‌توانید سفارش‌ها را ثبت کنید و ظرفیت‌ها کاهش خواهند یافت.")
        else:
            print("\\n❌ مشکل در مقداردهی ظرفیت‌ها وجود دارد.")

        return tour, schedule

    except Tour.DoesNotExist:
        print("❌ تور یافت نشد!")
        return None, None
    except TourSchedule.DoesNotExist:
        print("❌ برنامه زمانی یافت نشد!")
        return None, None

def demonstrate_booking_simulation():
    """شبیه‌سازی سفارش و کاهش ظرفیت"""

    print("\\n" + "="*60)
    print("🎯 شبیه‌سازی سفارش و کاهش ظرفیت")
    print("="*60)

    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))
        eco_variant = tour.variants.get(name='ECO')

        print(f"🏛️ تور: {tour.title}")
        print(f"🏷️ واریانت: {eco_variant.name}")
        print(f"📅 تاریخ: {schedule.start_date}")

        # وضعیت قبل از سفارش
        print("\\n📊 وضعیت قبل از سفارش:")
        capacity_before = schedule.variant_capacities.get(str(eco_variant.id), {})
        print(f"   کل ظرفیت ECO: {capacity_before.get('total', 0)}")
        print(f"   ظرفیت موجود ECO: {capacity_before.get('available', 0)}")
        print(f"   ظرفیت رزرو شده ECO: {capacity_before.get('booked', 0)}")

        # شبیه‌سازی رزرو ۲ نفر
        print("\\n🔄 شبیه‌سازی رزرو ۲ نفر در واریانت ECO...")
        success = schedule.reserve_capacity_atomic(eco_variant.id, 2)

        if success:
            print("✅ رزرو با موفقیت انجام شد!")

            # وضعیت پس از سفارش
            print("\\n📊 وضعیت پس از سفارش:")
            capacity_after = schedule.variant_capacities.get(str(eco_variant.id), {})
            print(f"   کل ظرفیت ECO: {capacity_after.get('total', 0)}")
            print(f"   ظرفیت موجود ECO: {capacity_after.get('available', 0)}")
            print(f"   ظرفیت رزرو شده ECO: {capacity_after.get('booked', 0)}")

            print("\\n📈 تغییرات:")
            booked_before = capacity_before.get('booked', 0)
            booked_after = capacity_after.get('booked', 0)
            available_before = capacity_before.get('available', 0)
            available_after = capacity_after.get('available', 0)

            print(f"   رزرو شده: {booked_before} → {booked_after} (+{booked_after - booked_before})")
            print(f"   موجود: {available_before} → {available_after} (-{available_before - available_after})")

            # شبیه‌سازی تأیید سفارش
            print("\\n🔄 شبیه‌سازی تأیید سفارش...")
            schedule.confirm_capacity_atomic(eco_variant.id, 2)

            print("\\n📊 وضعیت پس از تأیید:")
            capacity_final = schedule.variant_capacities.get(str(eco_variant.id), {})
            print(f"   کل ظرفیت ECO: {capacity_final.get('total', 0)}")
            print(f"   ظرفیت موجود ECO: {capacity_final.get('available', 0)}")
            print(f"   ظرفیت رزرو شده ECO: {capacity_final.get('booked', 0)}")
            print(f"   ظرفیت تأیید شده: {schedule.total_confirmed_capacity}")

        else:
            print("❌ رزرو ناموفق بود (ظرفیت کافی نیست)")

    except Exception as e:
        print(f"❌ خطا در شبیه‌سازی: {str(e)}")

if __name__ == '__main__':
    # مقداردهی ظرفیت‌ها
    tour, schedule = fix_capacity_initialization()

    if tour and schedule:
        # شبیه‌سازی سفارش
        demonstrate_booking_simulation()
