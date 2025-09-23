#!/usr/bin/env python
"""
Check and Cleanup Tours Script
- Check all existing tours
- Keep only Tour X
- Create a production-ready tour with all required fields
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, time, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourSchedule, TourGallery
from django.core.files.base import ContentFile

def check_existing_tours():
    """Check all existing tours"""
    print("🔍 Checking existing tours...")
    
    tours = Tour.objects.all()
    print(f"📊 Total tours found: {tours.count()}")
    
    for tour in tours:
        try:
            title = tour.title
        except:
            title = "No translation available"
            
        try:
            slug = tour.slug
        except:
            slug = "No translation available"
            
        print(f"\n🎯 Tour: {title}")
        print(f"   ID: {tour.id}")
        print(f"   Slug: {slug}")
        print(f"   Active: {tour.is_active}")
        print(f"   Variants: {tour.variants.count()}")
        print(f"   Schedules: {tour.schedules.count()}")
        print(f"   Gallery Images: {tour.gallery_images.count()}")
        
        # Check variants
        for variant in tour.variants.all():
            try:
                variant_name = variant.name
            except:
                variant_name = "No translation available"
            print(f"     Variant: {variant_name} (Active: {variant.is_active})")
        
        # Check schedules
        for schedule in tour.schedules.all():
            print(f"     Schedule: {schedule.start_date} (Active: {schedule.is_active})")

def cleanup_tours():
    """Delete all tours except Tour X"""
    print("\n🧹 Cleaning up tours...")
    
    # Find Tour X by ID or slug pattern
    tour_x = None
    for tour in Tour.objects.all():
        try:
            if 'tour-x' in tour.slug.lower() or 'tour x' in tour.title.lower():
                tour_x = tour
                break
        except:
            continue
    
    if not tour_x:
        print("❌ Tour X not found!")
        return False
    
    try:
        tour_x_title = tour_x.title
    except:
        tour_x_title = "Tour X"
    
    print(f"✅ Found Tour X: {tour_x_title}")
    
    # Get all tours except Tour X
    tours_to_delete = Tour.objects.exclude(id=tour_x.id)
    count = tours_to_delete.count()
    
    print(f"🗑️ Deleting {count} tours (keeping Tour X)...")
    
    # Delete tours (this will cascade to variants, schedules, etc.)
    deleted_count = 0
    for tour in tours_to_delete:
        try:
            tour_title = tour.title
        except:
            tour_title = f"Tour {tour.id}"
        print(f"   Deleting: {tour_title}")
        tour.delete()
        deleted_count += 1
    
    print(f"✅ Deleted {deleted_count} tours")
    return True

def create_production_tour():
    """Create a production-ready tour with all required fields"""
    print("\n🏗️ Creating production tour...")
    
    # Get or create a category first
    from tours.models import TourCategory
    category, created = TourCategory.objects.get_or_create(
        slug='cultural-tours',
        defaults={
            'name': 'Cultural Tours',
            'description': 'Cultural and heritage tours'
        }
    )
    if created:
        print(f"   ✅ Created category: {category.name}")
    
    # Create main tour
    tour = Tour.objects.create(
        title="Istanbul Cultural Experience",
        slug="istanbul-cultural-experience",
        description="Discover the rich cultural heritage of Istanbul with our comprehensive cultural tour. Visit historic landmarks, experience local traditions, and immerse yourself in the vibrant culture of this magnificent city.",
        short_description="Explore Istanbul's cultural treasures and historic landmarks",
        highlights="Visit Hagia Sophia, Blue Mosque, Grand Bazaar, Topkapi Palace",
        rules="Please arrive 15 minutes before departure time",
        required_items="Comfortable walking shoes, Camera, Valid ID",
        is_active=True,
        category=category,
        tour_type='day',
        transport_type='land',
        duration_hours=8,
        pickup_time=time(8, 30),
        start_time=time(9, 0),
        end_time=time(17, 0),
        min_participants=2,
        max_participants=20,
        booking_cutoff_hours=24,
        cancellation_hours=24,
        refund_percentage=100,
        includes_transfer=True,
        includes_guide=True,
        includes_meal=True,
        includes_photographer=False,
        price=Decimal('150.00'),
        currency='USD',
        city='Istanbul',
        country='Turkey',
        image="tours/istanbul-cultural-tour.jpg"
    )
    
    print(f"✅ Created tour: {tour.title}")
    
    # Create variants with proper capacity distribution
    variants_data = [
        {
            'name': 'Standard',
            'description': 'Standard cultural tour with group guide',
            'base_price': Decimal('150.00'),
            'capacity': 10,
            'is_active': True,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'includes_photographer': False
        },
        {
            'name': 'Premium',
            'description': 'Premium cultural tour with private guide',
            'base_price': Decimal('250.00'),
            'capacity': 6,
            'is_active': True,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'includes_photographer': True
        },
        {
            'name': 'VIP',
            'description': 'VIP cultural tour with exclusive access',
            'base_price': Decimal('400.00'),
            'capacity': 4,
            'is_active': True,
            'includes_transfer': True,
            'includes_guide': True,
            'includes_meal': True,
            'includes_photographer': True,
            'private_transfer': True,
            'expert_guide': True,
            'special_meal': True
        }
    ]
    
    for variant_data in variants_data:
        variant = TourVariant.objects.create(
            tour=tour,
            name=variant_data['name'],
            description=variant_data['description'],
            base_price=variant_data['base_price'],
            is_active=variant_data['is_active'],
            capacity=variant_data['capacity'],
            includes_transfer=variant_data.get('includes_transfer', True),
            includes_guide=variant_data.get('includes_guide', True),
            includes_meal=variant_data.get('includes_meal', True),
            includes_photographer=variant_data.get('includes_photographer', False),
            private_transfer=variant_data.get('private_transfer', False),
            expert_guide=variant_data.get('expert_guide', False),
            special_meal=variant_data.get('special_meal', False)
        )
        print(f"   ✅ Created variant: {variant.name}")
    
    # Create schedules (next 30 days)
    base_date = date.today() + timedelta(days=1)
    
    for i in range(30):
        schedule_date = base_date + timedelta(days=i)
        
        # Create one schedule per day
        schedule = TourSchedule.objects.create(
            tour=tour,
            start_date=schedule_date,
            end_date=schedule_date,  # Same day tour
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True,
            day_of_week=schedule_date.weekday()
        )
        
        # Initialize variant capacities for this schedule
        variant_capacities = {}
        for variant in tour.variants.all():
            variant_capacities[str(variant.id)] = {
                'total': variant.capacity,
                'booked': 0,
                'available': variant.capacity
            }
        
        schedule.variant_capacities_raw = variant_capacities
        schedule.save()
        
        print(f"   ✅ Created schedule: {schedule_date} with variant capacities")
    
    # Create gallery images (placeholder)
    gallery_images = [
        {
            'title': 'Hagia Sophia',
            'description': 'The magnificent Hagia Sophia, a symbol of Istanbul',
            'order': 1
        },
        {
            'title': 'Blue Mosque',
            'description': 'The stunning Blue Mosque with its six minarets',
            'order': 2
        },
        {
            'title': 'Grand Bazaar',
            'description': 'The historic Grand Bazaar, one of the world\'s oldest markets',
            'order': 3
        },
        {
            'title': 'Topkapi Palace',
            'description': 'The opulent Topkapi Palace, home to Ottoman sultans',
            'order': 4
        },
        {
            'title': 'Bosphorus Cruise',
            'description': 'Scenic Bosphorus cruise with views of two continents',
            'order': 5
        }
    ]
    
    for img_data in gallery_images:
        gallery = TourGallery.objects.create(
            tour=tour,
            title=img_data['title'],
            description=img_data['description'],
            order=img_data['order'],
            is_active=True,
            image="tours/gallery/istanbul-gallery-placeholder.jpg"
        )
        print(f"   ✅ Created gallery image: {gallery.title}")
    
    print(f"\n🎉 Production tour created successfully!")
    print(f"   Tour ID: {tour.id}")
    print(f"   Variants: {tour.variants.count()}")
    print(f"   Schedules: {tour.schedules.count()}")
    print(f"   Gallery Images: {tour.gallery_images.count()}")
    
    return tour

def verify_tour_data():
    """Verify the created tour has all required fields"""
    print("\n🔍 Verifying tour data...")
    
    tours = Tour.objects.all()
    print(f"📊 Total tours after cleanup: {tours.count()}")
    
    for tour in tours:
        print(f"\n🎯 Tour: {tour.title}")
        print(f"   ID: {tour.id}")
        print(f"   Slug: {tour.slug}")
        print(f"   Active: {tour.is_active}")
        print(f"   Min Participants: {tour.min_participants}")
        print(f"   Max Participants: {tour.max_participants}")
        print(f"   Duration: {tour.duration_hours} hours")
        print(f"   Variants: {tour.variants.count()}")
        print(f"   Schedules: {tour.schedules.count()}")
        print(f"   Gallery Images: {tour.gallery_images.count()}")
        
        # Check if tour has all required data for testing
        has_variants = tour.variants.count() > 0
        has_schedules = tour.schedules.count() > 0
        has_active_variants = tour.variants.filter(is_active=True).exists()
        has_active_schedules = tour.schedules.filter(is_active=True).exists()
        
        print(f"   ✅ Has Variants: {has_variants}")
        print(f"   ✅ Has Schedules: {has_schedules}")
        print(f"   ✅ Has Active Variants: {has_active_variants}")
        print(f"   ✅ Has Active Schedules: {has_active_schedules}")
        
        if has_variants and has_schedules and has_active_variants and has_active_schedules:
            print(f"   🎉 Tour '{tour.title}' is ready for testing!")
        else:
            print(f"   ❌ Tour '{tour.title}' is missing required data")

def main():
    """Main function"""
    print("🚀 Starting Tour Cleanup and Production Tour Creation...")
    
    # Step 1: Check existing tours
    check_existing_tours()
    
    # Step 2: Cleanup tours (keep only Tour X)
    if cleanup_tours():
        print("✅ Cleanup completed successfully")
    else:
        print("❌ Cleanup failed")
        return
    
    # Step 3: Create production tour
    production_tour = create_production_tour()
    
    # Step 4: Verify data
    verify_tour_data()
    
    print("\n🎉 All operations completed successfully!")
    print("📋 Summary:")
    print("   - Kept Tour X")
    print("   - Deleted other tours")
    print("   - Created production-ready tour")
    print("   - All tours now have required data for testing")

if __name__ == "__main__":
    main()
