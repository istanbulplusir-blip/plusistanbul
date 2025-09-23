#!/usr/bin/env python
"""
Check tour pricing data.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourPricing

def check_tour_pricing():
    """Check pricing data for tours."""
    
    print("🔍 Checking Tour Pricing Data")
    print("=" * 50)
    
    # Check capacity-test-tour
    print("\n1️⃣ capacity-test-tour:")
    try:
        tour = Tour.objects.get(slug='capacity-test-tour')
        print(f"   Title: {tour.title}")
        variants = tour.variants.all()
        print(f"   Variants: {variants.count()}")
        
        for variant in variants:
            print(f"     - {variant.name}: pricing count = {variant.pricing.count()}")
            if variant.pricing.count() > 0:
                for pricing in variant.pricing.all():
                    print(f"       * {pricing.age_group}: factor={pricing.factor}, is_free={pricing.is_free}")
            else:
                print(f"       * No pricing data!")
                
    except Tour.DoesNotExist:
        print("   ❌ Tour not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check isfahan-historical-tour
    print("\n2️⃣ isfahan-historical-tour:")
    try:
        tour = Tour.objects.get(slug='isfahan-historical-tour')
        print(f"   Title: {tour.title}")
        variants = tour.variants.all()
        print(f"   Variants: {variants.count()}")
        
        for variant in variants:
            print(f"     - {variant.name}: pricing count = {variant.pricing.count()}")
            if variant.pricing.count() > 0:
                for pricing in variant.pricing.all():
                    print(f"       * {pricing.age_group}: factor={pricing.factor}, is_free={pricing.is_free}")
            else:
                print(f"       * No pricing data!")
                
    except Tour.DoesNotExist:
        print("   ❌ Tour not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check all TourPricing records
    print("\n3️⃣ All TourPricing Records:")
    all_pricing = TourPricing.objects.all()
    print(f"   Total pricing records: {all_pricing.count()}")
    
    if all_pricing.count() > 0:
        for pricing in all_pricing[:5]:  # Show first 5
            print(f"     - {pricing.variant.name} ({pricing.age_group}): factor={pricing.factor}")
    
    # Check variants without pricing
    print("\n4️⃣ Variants Without Pricing:")
    variants_without_pricing = TourVariant.objects.filter(pricing__isnull=True)
    print(f"   Variants without pricing: {variants_without_pricing.count()}")
    
    for variant in variants_without_pricing:
        print(f"     - {variant.name} (Tour: {variant.tour.title})")

if __name__ == "__main__":
    check_tour_pricing()
