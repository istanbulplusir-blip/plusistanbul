#!/usr/bin/env python
"""
Script to fix pricing data issues and validate tour variants.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourPricing, TourSchedule
from django.core.exceptions import ValidationError
from django.db import models

def fix_variant_pricing():
    """Fix variant pricing issues."""
    print("🔧 Fixing variant pricing issues...")
    
    # Fix variants with zero or None base_price
    variants = TourVariant.objects.filter(
        models.Q(base_price__isnull=True) | 
        models.Q(base_price__lte=0)
    )
    
    print(f"Found {variants.count()} variants with invalid base_price")
    
    for variant in variants:
        # Set a default price based on tour type
        if variant.tour.tour_type == 'day':
            default_price = Decimal('50.00')
        else:
            default_price = Decimal('100.00')
        
        variant.base_price = default_price
        try:
            variant.full_clean()
            variant.save()
            print(f"✅ Fixed variant {variant.name} - base_price: {default_price}")
        except ValidationError as e:
            print(f"❌ Failed to fix variant {variant.name}: {e}")
    
    # Fix pricing factors that are strings or invalid
    pricings = TourPricing.objects.all()
    print(f"Checking {pricings.count()} pricing records...")
    
    for pricing in pricings:
        try:
            # Ensure factor is a valid decimal
            if isinstance(pricing.factor, str):
                try:
                    pricing.factor = Decimal(pricing.factor)
                except (ValueError, TypeError):
                    pricing.factor = Decimal('1.00')
            
            # Validate factor range
            if pricing.factor <= 0 or pricing.factor > 2:
                pricing.factor = Decimal('1.00')
            
            pricing.full_clean()
            pricing.save()
            print(f"✅ Fixed pricing {pricing} - factor: {pricing.factor}")
        except ValidationError as e:
            print(f"❌ Failed to fix pricing {pricing}: {e}")

def validate_schedule_capacities():
    """Validate and fix schedule capacities."""
    print("\n🔧 Validating schedule capacities...")
    
    schedules = TourSchedule.objects.all()
    print(f"Checking {schedules.count()} schedules...")
    
    for schedule in schedules:
        try:
            capacities = schedule.variant_capacities_raw
            
            if not isinstance(capacities, dict):
                schedule.variant_capacities_raw = {}
                schedule.save()
                print(f"✅ Fixed schedule {schedule} - reset capacities")
                continue
            
            # Validate each variant capacity
            fixed_capacities = {}
            for variant_id, capacity_data in capacities.items():
                if not isinstance(capacity_data, dict):
                    continue
                
                total = capacity_data.get('total', 0)
                booked = capacity_data.get('booked', 0)
                
                # Ensure positive integers
                try:
                    total = max(0, int(total))
                    booked = max(0, int(booked))
                    booked = min(booked, total)  # booked cannot exceed total
                except (ValueError, TypeError):
                    total = 10
                    booked = 0
                
                fixed_capacities[str(variant_id)] = {
                    'total': total,
                    'booked': booked,
                    'available': total - booked
                }
            
            schedule.variant_capacities_raw = fixed_capacities
            schedule.save()
            print(f"✅ Fixed schedule {schedule} - {len(fixed_capacities)} variants")
            
        except Exception as e:
            print(f"❌ Failed to fix schedule {schedule}: {e}")

def create_default_pricing():
    """Create default pricing for variants that don't have it."""
    print("\n🔧 Creating default pricing...")
    
    variants = TourVariant.objects.all()
    
    for variant in variants:
        # Check if pricing exists for all age groups
        existing_pricing = TourPricing.objects.filter(variant=variant)
        existing_age_groups = set(pricing.age_group for pricing in existing_pricing)
        
        required_age_groups = {'infant', 'child', 'adult'}
        missing_age_groups = required_age_groups - existing_age_groups
        
        for age_group in missing_age_groups:
            # Set default factors
            if age_group == 'infant':
                factor = Decimal('0.00')  # Free
                is_free = True
            elif age_group == 'child':
                factor = Decimal('0.75')  # 75% of adult price
                is_free = False
            else:  # adult
                factor = Decimal('1.00')  # Full price
                is_free = False
            
            try:
                pricing = TourPricing.objects.create(
                    tour=variant.tour,
                    variant=variant,
                    age_group=age_group,
                    factor=factor,
                    is_free=is_free,
                    requires_services=True
                )
                print(f"✅ Created pricing for {variant.name} - {age_group}: {factor}")
            except Exception as e:
                print(f"❌ Failed to create pricing for {variant.name} - {age_group}: {e}")

def main():
    """Main function to run all fixes."""
    print("🚀 Starting pricing data fixes...")
    print("=" * 50)
    
    try:
        fix_variant_pricing()
        validate_schedule_capacities()
        create_default_pricing()
        
        print("\n" + "=" * 50)
        print("✅ All pricing fixes completed successfully!")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   - TourVariants: {TourVariant.objects.count()}")
        print(f"   - TourPricing: {TourPricing.objects.count()}")
        print(f"   - TourSchedules: {TourSchedule.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error during fixes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 