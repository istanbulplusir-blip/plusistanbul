#!/usr/bin/env python
"""
Script to fix variant_capacities keys in all TourSchedule objects.
This ensures all keys are strings for JSON serialization compatibility.
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.db import transaction
from tours.models import TourSchedule

def fix_variant_capacities():
    """Fix all variant_capacities to ensure keys are strings."""
    print("Starting to fix variant_capacities...")
    
    schedules = TourSchedule.objects.all()
    fixed_count = 0
    
    for schedule in schedules:
        try:
            # Get the current variant_capacities
            current_vc = schedule.variant_capacities
            
            if not isinstance(current_vc, dict):
                # If it's not a dict, set it to empty dict
                schedule.variant_capacities = {}
                schedule.save(update_fields=['variant_capacities'])
                fixed_count += 1
                print(f"Fixed schedule {schedule.id}: converted non-dict to empty dict")
                continue
            
            # Convert all keys to strings
            new_vc = {}
            for key, value in current_vc.items():
                new_key = str(key)
                new_vc[new_key] = value
            
            # Only update if there are changes
            if new_vc != current_vc:
                schedule.variant_capacities = new_vc
                schedule.save(update_fields=['variant_capacities'])
                fixed_count += 1
                print(f"Fixed schedule {schedule.id}: converted keys to strings")
            
        except Exception as e:
            print(f"Error fixing schedule {schedule.id}: {e}")
            # If there's any error, set to empty dict
            try:
                schedule.variant_capacities = {}
                schedule.save(update_fields=['variant_capacities'])
                fixed_count += 1
                print(f"Fixed schedule {schedule.id}: set to empty dict due to error")
            except Exception as e2:
                print(f"Failed to fix schedule {schedule.id}: {e2}")
    
    print(f"Fixed {fixed_count} TourSchedule objects.")
    return fixed_count

def verify_fix():
    """Verify that all variant_capacities have string keys."""
    print("Verifying fix...")
    
    schedules = TourSchedule.objects.all()
    verified_count = 0
    error_count = 0
    
    for schedule in schedules:
        try:
            vc = schedule.variant_capacities
            
            if not isinstance(vc, dict):
                print(f"Warning: Schedule {schedule.id} has non-dict variant_capacities: {type(vc)}")
                error_count += 1
                continue
            
            # Check if all keys are strings
            for key in vc.keys():
                if not isinstance(key, str):
                    print(f"Error: Schedule {schedule.id} has non-string key: {key} (type: {type(key)})")
                    error_count += 1
                    break
            else:
                verified_count += 1
                
        except Exception as e:
            print(f"Error verifying schedule {schedule.id}: {e}")
            error_count += 1
    
    print(f"Verified {verified_count} schedules successfully.")
    if error_count > 0:
        print(f"Found {error_count} schedules with issues.")
    else:
        print("✅ All schedules verified successfully!")
    
    return error_count == 0

if __name__ == "__main__":
    with transaction.atomic():
        fixed_count = fix_variant_capacities()
        success = verify_fix()
        
        if success:
            print("✅ All variant_capacities fixed successfully!")
        else:
            print("❌ Some issues remain. Please check the output above.") 