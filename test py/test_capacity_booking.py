#!/usr/bin/env python
"""
تست سیستم ظرفیت و کاهش آن پس از سفارش
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

def test_capacity_booking():
    """تست رزرو و کاهش ظرفیت"""

    print("🧪 تست سیستم ظرفیت و سفارش...")
    print("="*60)

    try:
        # دریافت تور و اجزاء
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))
        eco_variant = tour.variants.get(name='ECO')

        print(f"🏛️ تور: {tour.title}")
        print(f"🏷️ واریانت: {eco_variant.name}")
        print(f"📅 تاریخ: {schedule.start_date}")
        print(f"🆔 ID واریانت: {eco_variant.id}")

        # نمایش وضعیت اولیه
        print("\\n📊 وضعیت اولیه ظرفیت‌ها:")
        schedule.refresh_from_db()  # تازه کردن داده‌ها از دیتابیس

        print(f"کل ظرفیت برنامه: {schedule.compute_total_capacity()}")
        print(f"ظرفیت موجود برنامه: {schedule.available_capacity}")

        # نمایش ظرفیت واریانت ECO
        capacities = schedule.variant_capacities
        eco_key = str(eco_variant.id)
        if eco_key in capacities:
            eco_data = capacities[eco_key]
            print(f"\\n🏷️ ظرفیت واریانت ECO:")
            print(f"   کل: {eco_data.get('total', 0)}")
            print(f"   موجود: {eco_data.get('available', 0)}")
            print(f"   رزرو شده: {eco_data.get('booked', 0)}")
        else:
            print(f"\\n❌ ظرفیت واریانت ECO یافت نشد!")
            print(f"کلیدهای موجود: {list(capacities.keys())}")
            return

        # تست رزرو ظرفیت
        print("\\n🔄 تست رزرو ۳ نفر در واریانت ECO...")

        # ذخیره وضعیت قبل
        before_data = capacities[eco_key].copy()

        # انجام رزرو
        success = schedule.reserve_capacity_atomic(eco_variant.id, 3)

        if success:
            print("✅ رزرو با موفقیت انجام شد!")

            # تازه کردن داده‌ها
            schedule.refresh_from_db()
            capacities_after = schedule.variant_capacities

            if eco_key in capacities_after:
                after_data = capacities_after[eco_key]

                print("\\n📊 مقایسه قبل و بعد:")
                print(f"کل ظرفیت: {before_data.get('total', 0)} → {after_data.get('total', 0)}")
                print(f"موجود: {before_data.get('available', 0)} → {after_data.get('available', 0)}")
                print(f"رزرو شده: {before_data.get('booked', 0)} → {after_data.get('booked', 0)}")

                print("\\n📈 تغییرات:")
                booked_change = after_data.get('booked', 0) - before_data.get('booked', 0)
                available_change = after_data.get('available', 0) - before_data.get('available', 0)
                print(f"رزرو شده: +{booked_change}")
                print(f"موجود: {available_change}")

                # تست تأیید ظرفیت
                print("\\n🔄 تست تأیید رزرو...")
                schedule.confirm_capacity_atomic(eco_variant.id, 3)

                schedule.refresh_from_db()
                final_capacities = schedule.variant_capacities

                if eco_key in final_capacities:
                    final_data = final_capacities[eco_key]
                    print("\\n📊 وضعیت نهایی پس از تأیید:")
                    print(f"کل ظرفیت: {final_data.get('total', 0)}")
                    print(f"موجود: {final_data.get('available', 0)}")
                    print(f"رزرو شده: {final_data.get('booked', 0)}")
                    print(f"تأیید شده در برنامه: {schedule.total_confirmed_capacity}")

                # نمایش وضعیت کلی برنامه
                print("\\n🏟️ وضعیت کلی برنامه زمانی:")
                print(f"کل ظرفیت: {schedule.compute_total_capacity()}")
                print(f"موجود: {schedule.available_capacity}")
                print(f"رزرو شده: {schedule.total_reserved_capacity}")
                print(f"تأیید شده: {schedule.total_confirmed_capacity}")

            else:
                print("❌ داده‌های پس از رزرو یافت نشد!")

        else:
            print("❌ رزرو ناموفق بود!")

        # تست رزرو بیش از ظرفیت
        print("\\n🔄 تست رزرو بیش از ظرفیت (۸ نفر)...")
        success2 = schedule.reserve_capacity_atomic(eco_variant.id, 8)
        if not success2:
            print("✅ سیستم به درستی رزرو بیش از ظرفیت را رد کرد!")
        else:
            print("❌ سیستم اجازه رزرو بیش از ظرفیت را داد!")

    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()

def show_all_variant_capacities():
    """نمایش ظرفیت همه واریانت‌ها"""

    print("\\n" + "="*60)
    print("📊 ظرفیت همه واریانت‌ها")
    print("="*60)

    try:
        tour = Tour.objects.get(slug='30-capacity-tour-sep')
        schedule = TourSchedule.objects.get(tour=tour, start_date=date(2025, 9, 30))

        print(f"🏛️ تور: {tour.title}")
        print(f"📅 تاریخ: {schedule.start_date}")
        print(f"🏟️ ظرفیت کل: {schedule.compute_total_capacity()}")
        print(f"✅ موجود: {schedule.available_capacity}")
        print(f"📦 رزرو شده: {schedule.total_reserved_capacity}")
        print(f"🎫 تأیید شده: {schedule.total_confirmed_capacity}")

        print("\\n🏷️ جزئیات هر واریانت:")
        capacities = schedule.variant_capacities

        for variant in tour.variants.all():
            variant_key = str(variant.id)
            if variant_key in capacities:
                data = capacities[variant_key]
                total = data.get('total', 0)
                available = data.get('available', 0)
                booked = data.get('booked', 0)
                utilization = ((total - available) / total * 100) if total > 0 else 0

                print(f"\\n{variant.name}:")
                print(f"   💰 قیمت پایه: ${variant.base_price}")
                print(f"   👥 کل ظرفیت: {total}")
                print(f"   ✅ موجود: {available}")
                print(f"   📦 رزرو شده: {booked}")
                print(f"   📊 استفاده: {utilization:.1f}%")
                print(f"   🟢 وضعیت: {'✅' if available > 0 else '❌ پر شده'}")
            else:
                print(f"\\n{variant.name}: ❌ ظرفیت مقداردهی نشده")

    except Exception as e:
        print(f"❌ خطا: {str(e)}")

if __name__ == '__main__':
    # تست رزرو ظرفیت
    test_capacity_booking()

    # نمایش همه ظرفیت‌ها
    show_all_variant_capacities()
