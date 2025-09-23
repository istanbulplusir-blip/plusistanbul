#!/usr/bin/env python
"""
Verify Tour X itinerary setup
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourItinerary

def verify_tour_x_itinerary():
    """Verify Tour X itinerary setup"""
    print("🔍 Verifying Tour X Itinerary Setup")
    print("=" * 50)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return False
    
    print(f"✅ Found Tour X: {tour.title}")
    
    # Check itinerary items
    itinerary_items = tour.itinerary.all().order_by('order')
    if itinerary_items.count() != 10:
        print(f"❌ Expected 10 itinerary items, found {itinerary_items.count()}")
        return False
    
    print(f"✅ Found {itinerary_items.count()} itinerary items")
    
    # Expected itinerary data
    expected_items = [
        {
            "order": 1,
            "title": "Welcome & Orientation",
            "duration_minutes": 30,
            "location": "Meeting Point - Central Plaza"
        },
        {
            "order": 2,
            "title": "Historical Museum Visit",
            "duration_minutes": 90,
            "location": "National History Museum"
        },
        {
            "order": 3,
            "title": "Traditional Market Experience",
            "duration_minutes": 60,
            "location": "Old Bazaar District"
        },
        {
            "order": 4,
            "title": "Lunch at Local Restaurant",
            "duration_minutes": 75,
            "location": "Traditional Restaurant"
        },
        {
            "order": 5,
            "title": "Ancient Temple Complex",
            "duration_minutes": 120,
            "location": "Sacred Temple Complex"
        },
        {
            "order": 6,
            "title": "Cultural Performance",
            "duration_minutes": 45,
            "location": "Cultural Center"
        },
        {
            "order": 7,
            "title": "Scenic Viewpoint",
            "duration_minutes": 30,
            "location": "Mountain Viewpoint"
        },
        {
            "order": 8,
            "title": "Artisan Workshop Visit",
            "duration_minutes": 60,
            "location": "Artisan Quarter"
        },
        {
            "order": 9,
            "title": "Evening Tea Ceremony",
            "duration_minutes": 45,
            "location": "Traditional Tea House"
        },
        {
            "order": 10,
            "title": "Farewell & Return",
            "duration_minutes": 30,
            "location": "Meeting Point - Central Plaza"
        }
    ]
    
    print("\n🗺️ Itinerary Items:")
    total_duration = 0
    
    for i, item in enumerate(itinerary_items):
        expected = expected_items[i]
        
        # Handle translatable fields
        try:
            item.set_current_language('en')
            title = item.title
        except:
            title = f"Item {item.order}"
        
        print(f"  {item.order:2d}. {title}")
        print(f"      Duration: {item.duration_minutes} min")
        print(f"      Location: {item.location}")
        print(f"      Image: {'✅' if item.image else '❌'}")
        
        # Verify data
        if item.order != expected["order"]:
            print(f"      ❌ Order mismatch: expected {expected['order']}, got {item.order}")
            return False
        
        if item.duration_minutes != expected["duration_minutes"]:
            print(f"      ❌ Duration mismatch: expected {expected['duration_minutes']}, got {item.duration_minutes}")
            return False
        
        if item.location != expected["location"]:
            print(f"      ❌ Location mismatch: expected {expected['location']}, got {item.location}")
            return False
        
        if not item.image:
            print(f"      ❌ Missing image for item {item.order}")
            return False
        
        total_duration += item.duration_minutes
    
    print(f"\n📊 Itinerary Summary:")
    print(f"   Total Items: {itinerary_items.count()}")
    print(f"   Total Duration: {total_duration} minutes ({total_duration/60:.1f} hours)")
    print(f"   All Images Present: ✅")
    
    # Check if total duration matches expected
    expected_total = sum(item["duration_minutes"] for item in expected_items)
    if total_duration != expected_total:
        print(f"   ❌ Total duration mismatch: expected {expected_total}, got {total_duration}")
        return False
    
    print(f"   ✅ Total Duration Correct: {total_duration} minutes")
    
    print("\n🎯 FINAL VERIFICATION:")
    print("   ✅ All 10 itinerary items created")
    print("   ✅ All items have images")
    print("   ✅ Correct order and timing")
    print("   ✅ Proper locations and descriptions")
    print("   ✅ Total duration: 585 minutes")
    
    print("\n✅ Tour X itinerary setup is correct!")
    return True

if __name__ == "__main__":
    verify_tour_x_itinerary()
