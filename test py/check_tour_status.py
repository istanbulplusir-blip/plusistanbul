#!/usr/bin/env python
"""
Script to check tour status and identify issues.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourSchedule, TourPricing
from tours.serializers import TourDetailSerializer
import json

def check_tour_status():
    """Check status of all tours."""
    
    print("=" * 80)
    print("TOUR STATUS ANALYSIS")
    print("=" * 80)
    
    tours = Tour.objects.all()
    
    for tour in tours:
        print(f"\n{'='*60}")
        print(f"🚩 Tour: {tour.title}")
        print(f"   Slug: {tour.slug}")
        print(f"   Is Active: {tour.is_active}")
        
        # Check schedules
        schedules = tour.schedules.all()
        print(f"   📅 Schedules: {schedules.count()}")
        if schedules.exists():
            active_schedules = schedules.filter(is_available=True)
            print(f"      Active Schedules: {active_schedules.count()}")
            if active_schedules.exists():
                print(f"      Next Schedule: {active_schedules.first().start_date}")
        
        # Check variants
        variants = tour.variants.all()
        print(f"   🎫 Variants: {variants.count()}")
        
        tour_has_pricing_issues = False
        tour_has_active_variants = False
        
        for variant in variants:
            print(f"      - {variant.name}:")
            print(f"        Active: {variant.is_active}")
            print(f"        Base Price: {variant.base_price}")
            print(f"        Capacity: {variant.capacity}")
            
            if variant.is_active:
                tour_has_active_variants = True
            
            # Check pricing
            pricing = variant.pricing.all()
            print(f"        Pricing Rules: {pricing.count()}")
            
            if pricing.count() == 0:
                print(f"        ⚠️  NO PRICING RULES!")
                tour_has_pricing_issues = True
            else:
                for price_rule in pricing:
                    print(f"          {price_rule.age_group}: factor={price_rule.factor}, is_free={price_rule.is_free}")
                    if hasattr(price_rule, 'final_price'):
                        print(f"            Final Price: {price_rule.final_price}")
            
            # Check if base_price is zero
            if variant.base_price == 0:
                print(f"        ⚠️  BASE PRICE IS ZERO!")
                tour_has_pricing_issues = True
        
        # Determine tour status
        print(f"\n   📊 TOUR STATUS:")
        
        if not tour.is_active:
            print(f"      ❌ TOUR INACTIVE")
        elif schedules.count() == 0:
            print(f"      ❌ NO SCHEDULES")
        elif active_schedules.count() == 0:
            print(f"      ❌ NO ACTIVE SCHEDULES")
        elif variants.count() == 0:
            print(f"      ❌ NO VARIANTS")
        elif not tour_has_active_variants:
            print(f"      ❌ NO ACTIVE VARIANTS")
        elif tour_has_pricing_issues:
            print(f"      ⚠️  PRICING ISSUES (NaN possible)")
        else:
            print(f"      ✅ TOUR READY FOR BOOKING")
        
        # Test API response
        print(f"\n   🔍 API TEST:")
        try:
            serializer = TourDetailSerializer(tour)
            data = serializer.data
            
            # Check pricing_summary
            pricing_summary = data.get('pricing_summary', {})
            print(f"      Pricing Summary Keys: {list(pricing_summary.keys())}")
            
            if pricing_summary:
                for variant_id, variant_data in pricing_summary.items():
                    age_groups = variant_data.get('age_groups', {})
                    print(f"        Variant {variant_id}: {len(age_groups)} age groups")
                    
                    for age_group, age_data in age_groups.items():
                        final_price = age_data.get('final_price')
                        if final_price is None or final_price == 0:
                            print(f"          ⚠️  {age_group}: final_price={final_price}")
                        else:
                            print(f"          ✅ {age_group}: final_price={final_price}")
            else:
                print(f"      ⚠️  NO PRICING SUMMARY")
            
            # Check if tour has any valid pricing
            has_valid_pricing = False
            for variant_data in pricing_summary.values():
                for age_data in variant_data.get('age_groups', {}).values():
                    if age_data.get('final_price', 0) > 0:
                        has_valid_pricing = True
                        break
                if has_valid_pricing:
                    break
            
            if not has_valid_pricing:
                print(f"      ⚠️  NO VALID PRICING (all prices are 0 or None)")
            
        except Exception as e:
            print(f"      ❌ API ERROR: {e}")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_tour_status() 