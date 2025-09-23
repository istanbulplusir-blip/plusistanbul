#!/usr/bin/env python
"""
Script to analyze tours and their schedules for variant_capacities issues.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourSchedule, TourVariant
from django.core.serializers.json import DjangoJSONEncoder
import json

def analyze_tours():
    """Analyze all tours and their schedules."""
    
    print("=" * 80)
    print("TOUR ANALYSIS REPORT")
    print("=" * 80)
    
    # Get all tours
    tours = Tour.objects.all().order_by('created_at')
    print(f"\n📊 Total Tours: {tours.count()}")
    
    for tour in tours:
        print(f"\n{'='*60}")
        print(f"🏛️  Tour: {tour.slug}")
        print(f"   ID: {tour.id}")
        print(f"   Created: {tour.created_at}")
        print(f"   Title: {tour.title}")
        
        # Get variants
        variants = TourVariant.objects.filter(tour=tour)
        print(f"   Variants: {variants.count()}")
        for v in variants:
            print(f"     - {v.name} (ID: {v.id})")
        
        # Get schedules
        schedules = TourSchedule.objects.filter(tour=tour)
        print(f"   Schedules: {schedules.count()}")
        
        if schedules.exists():
            for i, schedule in enumerate(schedules[:3]):  # Show first 3
                print(f"\n     📅 Schedule {i+1}:")
                print(f"       ID: {schedule.id}")
                print(f"       Date: {schedule.start_date}")
                
                # Analyze variant_capacities_raw
                raw_data = schedule.variant_capacities_raw
                print(f"       variant_capacities_raw: {raw_data}")
                
                if raw_data:
                    keys = list(raw_data.keys())
                    key_types = [type(k).__name__ for k in keys]
                    print(f"       Keys: {keys}")
                    print(f"       Key types: {key_types}")
                    
                    # Check if any keys are UUID
                    uuid_keys = [k for k in keys if hasattr(k, 'hex')]
                    if uuid_keys:
                        print(f"       ⚠️  PROBLEM: Found UUID keys: {uuid_keys}")
                    else:
                        print(f"       ✅ All keys are strings")
                else:
                    print(f"       ℹ️  No variant_capacities_raw data")
                
                # Test property
                safe_data = schedule.variant_capacities
                print(f"       Property variant_capacities: {safe_data}")
                
                # Test JSON serialization
                try:
                    json_str = json.dumps(safe_data, cls=DjangoJSONEncoder)
                    print(f"       ✅ JSON serialization: OK")
                except Exception as e:
                    print(f"       ❌ JSON serialization failed: {e}")
        else:
            print(f"   ⚠️  No schedules found for this tour")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_tours() 