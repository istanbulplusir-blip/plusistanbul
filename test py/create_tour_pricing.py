#!/usr/bin/env python
"""
Create tour pricing data for capacity-test-tour.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourPricing

def create_tour_pricing():
    """Create pricing data for capacity-test-tour."""
    
    print("🔧 Creating Tour Pricing Data")
    print("=" * 50)
    
    try:
        # Get the tour
        tour = Tour.objects.get(slug='capacity-test-tour')
        print(f"Tour: {tour.title}")
        
        # Get all variants
        variants = tour.variants.all()
        print(f"Found {variants.count()} variants")
        
        # Pricing structure for each variant
        pricing_data = {
            'Eco': {'base_price': 120.0, 'adult_factor': 1.0, 'child_factor': 0.7, 'infant_factor': 0.0},
            'Normal': {'base_price': 150.0, 'adult_factor': 1.0, 'child_factor': 0.7, 'infant_factor': 0.0},
            'VIP': {'base_price': 220.0, 'adult_factor': 1.0, 'child_factor': 0.7, 'infant_factor': 0.0},
            'VVIP': {'base_price': 300.0, 'adult_factor': 1.0, 'child_factor': 0.7, 'infant_factor': 0.0}
        }
        
        created_count = 0
        
        for variant in variants:
            print(f"\nProcessing variant: {variant.name}")
            
            if variant.pricing.count() > 0:
                print(f"  ⚠️ Variant already has {variant.pricing.count()} pricing records, skipping...")
                continue
            
            # Get pricing data for this variant
            variant_pricing = pricing_data.get(variant.name, {})
            if not variant_pricing:
                print(f"  ❌ No pricing data found for variant {variant.name}")
                continue
            
            # Create pricing records
            age_groups = [
                ('adult', variant_pricing['adult_factor'], False),
                ('child', variant_pricing['child_factor'], False),
                ('infant', variant_pricing['infant_factor'], True)
            ]
            
            for age_group, factor, is_free in age_groups:
                pricing = TourPricing.objects.create(
                    tour=tour,
                    variant=variant,
                    age_group=age_group,
                    factor=factor,
                    is_free=is_free,
                    requires_services=True
                )
                print(f"    ✅ Created pricing for {age_group}: factor={factor}, is_free={is_free}")
                created_count += 1
        
        print(f"\n🎉 Successfully created {created_count} pricing records!")
        
        # Verify the creation
        print("\n🔍 Verification:")
        for variant in variants:
            print(f"  {variant.name}: {variant.pricing.count()} pricing records")
            
    except Tour.DoesNotExist:
        print("❌ Tour 'capacity-test-tour' not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tour_pricing()
