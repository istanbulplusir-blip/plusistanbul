#!/usr/bin/env python
"""
Verify Tour X capacity setup
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourSchedule

def verify_tour_x():
    """Verify Tour X capacity setup"""
    print("🔍 Verifying Tour X Capacity Setup")
    print("=" * 50)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return False
    
    print(f"✅ Found Tour X: {tour.title}")
    print(f"   Total Capacity: {tour.max_participants}")
    print(f"   Currency: {tour.currency}")
    print(f"   Duration: {tour.duration_hours} hours")
    
    # Check variants
    print("\n🎫 Variants:")
    variants = tour.variants.filter(is_active=True)
    if variants.count() != 3:
        print(f"❌ Expected 3 variants, found {variants.count()}")
        return False
    
    variant_capacities = {}
    for variant in variants:
        print(f"   - {variant.name}: ${variant.base_price} (Capacity: {variant.capacity})")
        variant_capacities[variant.name] = variant.capacity
    
    # Check schedules
    print("\n📅 Schedules:")
    schedules = tour.schedules.filter(is_available=True)
    if schedules.count() != 2:
        print(f"❌ Expected 2 schedules, found {schedules.count()}")
        return False
    
    expected_dates = [date(2024, 5, 20), date(2024, 5, 21)]
    for schedule in schedules:
        print(f"   - {schedule.start_date}: {schedule.max_capacity} capacity")
        if schedule.start_date not in expected_dates:
            print(f"❌ Unexpected date: {schedule.start_date}")
            return False
    
    # Verify capacity requirements
    print("\n✅ CAPACITY VERIFICATION:")
    
    # Check total tour capacity
    if tour.max_participants != 60:
        print(f"❌ Tour total capacity should be 60, got {tour.max_participants}")
        return False
    print(f"   ✅ Tour Total Capacity: {tour.max_participants}")
    
    # Check variant capacities
    expected_variant_capacities = {
        'VIP': 10,
        'ECO': 10,
        'NORMAL': 10
    }
    
    for variant_name, expected_capacity in expected_variant_capacities.items():
        if variant_capacities.get(variant_name) != expected_capacity:
            print(f"❌ {variant_name} capacity should be {expected_capacity}, got {variant_capacities.get(variant_name)}")
            return False
        print(f"   ✅ {variant_name} Capacity: {expected_capacity}")
    
    # Check schedule capacities
    for schedule in schedules:
        if schedule.max_capacity != 30:
            print(f"❌ {schedule.start_date} capacity should be 30, got {schedule.max_capacity}")
            return False
        print(f"   ✅ {schedule.start_date} Capacity: {schedule.max_capacity}")
    
    # Check variant capacities in schedules
    print("\n🔍 Checking variant capacities in schedules:")
    for schedule in schedules:
        print(f"   📅 {schedule.start_date}:")
        variant_caps = schedule.variant_capacities
        for variant in variants:
            variant_cap = variant_caps.get(str(variant.id), {})
            total = variant_cap.get('total', 0)
            available = variant_cap.get('available', 0)
            booked = variant_cap.get('booked', 0)
            print(f"     - {variant.name}: Total={total}, Available={available}, Booked={booked}")
            
            if total != variant.capacity:
                print(f"       ❌ Expected {variant.capacity}, got {total}")
                return False
    
    print("\n🎯 FINAL VERIFICATION:")
    print("   ✅ Tour X Total Capacity: 60")
    print("   ✅ May 20 Capacity: 30 (10 VIP + 10 ECO + 10 NORMAL)")
    print("   ✅ May 21 Capacity: 30 (10 VIP + 10 ECO + 10 NORMAL)")
    print("   ✅ All variant capacities properly initialized")
    
    print("\n✅ Tour X capacity setup is correct!")
    return True

if __name__ == "__main__":
    verify_tour_x()
