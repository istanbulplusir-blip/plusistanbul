#!/usr/bin/env python
"""
Script to fix pricing issues in tours.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourPricing

def fix_pricing():
    """Fix pricing for all tours."""
    
    print("=" * 80)
    print("FIXING PRICING ISSUES")
    print("=" * 80)
    
    # Fix persepolis tour variants
    tour = Tour.objects.get(slug='persepolis-historical-tour')
    print(f"\n🏛️  Fixing {tour.title}")
    
    # Update variant base prices
    eco_variant = TourVariant.objects.get(tour=tour, name='Eco')
    eco_variant.base_price = Decimal('100.00')
    eco_variant.save()
    print(f"   ✅ Eco variant: {eco_variant.base_price}")
    
    normal_variant = TourVariant.objects.get(tour=tour, name='Normal')
    normal_variant.base_price = Decimal('150.00')
    normal_variant.save()
    print(f"   ✅ Normal variant: {normal_variant.base_price}")
    
    vip_variant = TourVariant.objects.get(tour=tour, name='VIP')
    vip_variant.base_price = Decimal('250.00')
    vip_variant.save()
    print(f"   ✅ VIP variant: {vip_variant.base_price}")
    
    # Fix pricing rules for persepolis tour
    for variant in [eco_variant, normal_variant, vip_variant]:
        # Update adult pricing
        adult_pricing, _ = TourPricing.objects.get_or_create(
            tour=tour,
            variant=variant,
            age_group='adult',
            defaults={'factor': Decimal('1.00'), 'is_free': False}
        )
        adult_pricing.factor = Decimal('1.00')
        adult_pricing.is_free = False
        adult_pricing.save()
        
        # Update child pricing
        child_pricing, _ = TourPricing.objects.get_or_create(
            tour=tour,
            variant=variant,
            age_group='child',
            defaults={'factor': Decimal('0.80'), 'is_free': False}
        )
        child_pricing.factor = Decimal('0.80')
        child_pricing.is_free = False
        child_pricing.save()
        
        # Update infant pricing
        infant_pricing, _ = TourPricing.objects.get_or_create(
            tour=tour,
            variant=variant,
            age_group='infant',
            defaults={'factor': Decimal('0.00'), 'is_free': True}
        )
        infant_pricing.factor = Decimal('0.00')
        infant_pricing.is_free = True
        infant_pricing.save()
        
        print(f"   ✅ Pricing rules updated for {variant.name}")
    
    # Fix other tours that don't have pricing rules
    other_tours = Tour.objects.exclude(slug='persepolis-historical-tour')
    
    for tour in other_tours:
        print(f"\n🏛️  Fixing {tour.title}")
        variants = TourVariant.objects.filter(tour=tour)
        
        for variant in variants:
            # Create pricing rules for all age groups
            for age_group, factor in [('adult', '1.00'), ('child', '0.80'), ('infant', '0.00')]:
                pricing, created = TourPricing.objects.get_or_create(
                    tour=tour,
                    variant=variant,
                    age_group=age_group,
                    defaults={
                        'factor': Decimal(factor),
                        'is_free': age_group == 'infant'
                    }
                )
                if created:
                    print(f"   ✅ Created {age_group} pricing for {variant.name}")
    
    print(f"\n{'='*80}")
    print("PRICING FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_pricing() 