#!/usr/bin/env python
"""
Fix missing tour data (variants and schedules)
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourSchedule, TourPricing
from django.utils import timezone

def fix_isfahan_tour():
    """Fix Isfahan Cultural Tour"""
    print("Fixing Isfahan Cultural Tour...")
    
    tour = Tour.objects.get(slug='isfahan-cultural-tour')
    
    # Create variants
    variants_data = [
        {
            'name': 'Standard',
            'base_price': Decimal('120.00'),
            'capacity': 15,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'includes_photographer': False,
        },
        {
            'name': 'Premium',
            'base_price': Decimal('180.00'),
            'capacity': 10,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'includes_photographer': True,
        }
    ]
    
    for variant_data in variants_data:
        variant, created = TourVariant.objects.get_or_create(
            tour=tour,
            name=variant_data['name'],
            defaults=variant_data
        )
        if created:
            print(f"  Created variant: {variant.name}")
        
        # Create pricing for each age group
        pricing_data = [
            {'age_group': 'adult', 'factor': Decimal('1.00'), 'is_free': False},
            {'age_group': 'child', 'factor': Decimal('0.80'), 'is_free': False},
            {'age_group': 'infant', 'factor': Decimal('0.00'), 'is_free': True},
        ]
        
        for pricing_info in pricing_data:
            pricing, created = TourPricing.objects.get_or_create(
                tour=tour,
                variant=variant,
                age_group=pricing_info['age_group'],
                defaults=pricing_info
            )
            if created:
                print(f"    Created pricing: {pricing.age_group}")
    
    # Create schedules
    from datetime import date
    today = date.today()
    
    for i in range(7):  # Next 7 days
        schedule_date = today + timedelta(days=i)
        schedule, created = TourSchedule.objects.get_or_create(
            tour=tour,
            start_date=schedule_date,
            defaults={
                'end_date': schedule_date,
                'start_time': datetime.strptime('09:00', '%H:%M').time(),
                'end_time': datetime.strptime('17:00', '%H:%M').time(),
                'max_capacity': 15,
                'current_capacity': 0,
                'is_available': True,
                'day_of_week': schedule_date.weekday(),
            }
        )
        if created:
            print(f"  Created schedule: {schedule.start_date}")
    
    print("✅ Isfahan tour fixed!")

def fix_istanbul_tour():
    """Fix Istanbul City Tour schedules"""
    print("Fixing Istanbul City Tour...")
    
    tour = Tour.objects.get(slug='istanbul-city-tour')
    
    # Create schedules
    from datetime import date
    today = date.today()
    
    for i in range(7):  # Next 7 days
        schedule_date = today + timedelta(days=i)
        schedule, created = TourSchedule.objects.get_or_create(
            tour=tour,
            start_date=schedule_date,
            defaults={
                'end_date': schedule_date,
                'start_time': datetime.strptime('08:00', '%H:%M').time(),
                'end_time': datetime.strptime('16:00', '%H:%M').time(),
                'max_capacity': 20,
                'current_capacity': 0,
                'is_available': True,
                'day_of_week': schedule_date.weekday(),
            }
        )
        if created:
            print(f"  Created schedule: {schedule.start_date}")
    
    print("✅ Istanbul tour fixed!")

def main():
    """Fix all tour data"""
    print("🔧 Fixing tour data...")
    
    try:
        fix_isfahan_tour()
        fix_istanbul_tour()
        
        print("\n✅ All tour data fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing tour data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 