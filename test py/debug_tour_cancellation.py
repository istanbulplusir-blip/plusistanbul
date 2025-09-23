#!/usr/bin/env python
"""
Debug script to check Tour X cancellation policy
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour

def debug_tour_cancellation():
    """Debug tour cancellation policy"""
    print("🔍 Debugging Tour X Cancellation Policy")
    print("=" * 60)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return
    
    print(f"✅ Found Tour X: {tour.title}")
    
    # Check cancellation policy fields
    print("\n📋 Cancellation Policy Fields:")
    print(f"   cancellation_hours: {tour.cancellation_hours}")
    print(f"   refund_percentage: {tour.refund_percentage}")
    
    # Check if they have default values
    if tour.cancellation_hours == 48:
        print("   ⚠️ Using default cancellation_hours (48)")
    else:
        print("   ✅ Custom cancellation_hours set")
    
    if tour.refund_percentage == 50:
        print("   ⚠️ Using default refund_percentage (50)")
    else:
        print("   ✅ Custom refund_percentage set")
    
    # Check if policy is meaningful
    if tour.cancellation_hours > 0 and tour.refund_percentage >= 0:
        print("   ✅ Cancellation policy is defined")
        print(f"   📝 Policy: {tour.refund_percentage}% refund up to {tour.cancellation_hours} hours before tour")
    else:
        print("   ❌ Cancellation policy is not properly defined")

if __name__ == "__main__":
    debug_tour_cancellation()
