#!/usr/bin/env python
"""
Debug script to check Tour X images
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourItinerary

def debug_tour_images():
    """Debug tour images"""
    print("🔍 Debugging Tour X Images")
    print("=" * 60)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return
    
    print(f"✅ Found Tour X: {tour.title}")
    
    # Check main tour image
    print(f"\n📸 Main Tour Image:")
    print(f"   Image: {tour.image}")
    
    # Check gallery
    print(f"\n🖼️ Gallery Images:")
    if tour.gallery:
        for i, img in enumerate(tour.gallery):
            print(f"   {i+1}. {img}")
    else:
        print("   No gallery images")
    
    # Check itinerary images
    print(f"\n🗺️ Itinerary Images:")
    itinerary_items = TourItinerary.objects.filter(tour=tour).order_by('order')
    for item in itinerary_items:
        print(f"   Item {item.order}: {item.title}")
        print(f"   Image: {item.image}")
        print("   ---")

if __name__ == "__main__":
    debug_tour_images()
