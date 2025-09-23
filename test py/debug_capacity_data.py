#!/usr/bin/env python
"""
Debug script to check capacity data consistency
"""
import os
import sys
import django
from datetime import date

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from tours.models import Tour, TourSchedule

def debug_capacity_data():
    """Debug capacity data for test tour"""

    print("🔍 Debugging Capacity Data")
    print("="*50)

    try:
        # پیدا کردن تور تست
        tours = Tour.objects.filter(is_active=True)
        print(f"Found {tours.count()} active tours")

        for tour in tours:
            print(f"\\n🏷️ Tour: {tour.title} ({tour.slug})")
            print(f"   Max participants: {tour.max_participants}")

            schedules = tour.schedules.all()
            print(f"   Schedules: {schedules.count()}")

            for schedule in schedules:
                print(f"\\n   📅 Schedule: {schedule.start_date}")
                print(f"      Raw variant_capacities: {schedule.variant_capacities_raw}")
                print(f"      Processed variant_capacities: {schedule.variant_capacities}")
                print(f"      Available capacity: {schedule.available_capacity}")
                print(f"      Current capacity: {schedule.current_capacity}")
                print(f"      Max capacity: {schedule.max_capacity}")

                # بررسی consistency
                variant_caps = schedule.variant_capacities
                if variant_caps:
                    total_available = sum(v.get('available', 0) for v in variant_caps.values())
                    total_booked = sum(v.get('booked', 0) for v in variant_caps.values())
                    total_max = sum(v.get('total', 0) for v in variant_caps.values())

                    print(f"      Variant totals - Available: {total_available}, Booked: {total_booked}, Max: {total_max}")

                    if schedule.available_capacity != total_available:
                        print(f"      ❌ MISMATCH: Schedule available ({schedule.available_capacity}) != Variant total available ({total_available})")
                    else:
                        print("      ✅ Capacity data is consistent")
                # بررسی هر variant
                for variant_id, cap_data in variant_caps.items():
                    total = cap_data.get('total', 0)
                    available = cap_data.get('available', 0)
                    booked = cap_data.get('booked', 0)

                    if total != (available + booked):
                        print(f"      ❌ Variant {variant_id} inconsistency: {total} != {available} + {booked}")
                    else:
                        print(f"      ✅ Variant {variant_id}: {total} = {available} + {booked}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_capacity_data()
