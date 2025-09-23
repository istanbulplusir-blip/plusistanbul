#!/usr/bin/env python3
"""
Verify Tour X capacity display fixes
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from tours.models import Tour, TourSchedule, TourVariant

def main():
    print("=== TOUR X CAPACITY VERIFICATION ===")

    try:
        tour = Tour.objects.get(slug='tour-x')
        schedules = tour.schedules.all()
        variants = tour.variants.all()

        print(f"Tour: {tour.title}")
        print(f"Max Participants: {tour.max_participants}")

        for schedule in schedules:
            print(f"\nSchedule {schedule.id} ({schedule.start_date}):")
            print(f"  Available Capacity: {schedule.available_capacity}")
            print(f"  Reserved: {schedule.total_reserved_capacity}")
            print(f"  Confirmed: {schedule.total_confirmed_capacity}")

            for variant in variants:
                variant_capacity = schedule.variant_capacities.get(str(variant.id), {})
                if variant_capacity:
                    available = variant_capacity.get("available", 0)
                    total = variant_capacity.get("total", 0)
                    print(f"  Variant {variant.name}: {available}/{total} available")

        print("\n✅ Capacity verification completed")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
