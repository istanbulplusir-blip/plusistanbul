#!/usr/bin/env python
"""
Check existing tours in database.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourCategory, TourVariant, TourSchedule, TourOption, TourReview, TourItinerary
from django.db import connection

def check_existing_tours():
    """Check what tours exist in the database."""
    
    print("🔍 Checking Existing Tours in Database")
    print("=" * 50)
    
    # Check tour categories
    print("\n📂 Tour Categories:")
    categories = TourCategory.objects.all()
    if categories.exists():
        for cat in categories:
            print(f"   - {cat.name} (slug: {cat.slug}, active: {cat.is_active})")
    else:
        print("   ❌ No tour categories found")
    
    # Check tours
    print("\n🏛️ Tours:")
    tours = Tour.objects.all()
    if tours.exists():
        for tour in tours:
            print(f"   - {tour.title} (slug: {tour.slug}, active: {tour.is_active})")
            print(f"     Price: {tour.price}, Currency: {tour.currency}")
            print(f"     Duration: {tour.duration_hours} hours")
            print(f"     Category: {tour.category.name if tour.category else 'None'}")
            
            # Check variants
            variants = tour.variants.all()
            if variants.exists():
                print(f"     Variants: {variants.count()}")
                for variant in variants[:3]:  # Show first 3
                    print(f"       - {variant.name} (price: {variant.base_price}, capacity: {variant.capacity})")
            else:
                print("     ❌ No variants found")
            
            # Check schedules
            schedules = tour.schedules.all()
            if schedules.exists():
                print(f"     Schedules: {schedules.count()}")
                for schedule in schedules[:3]:  # Show first 3
                    print(f"       - {schedule.start_date} at {schedule.start_time} (available: {schedule.is_available})")
            else:
                print("     ❌ No schedules found")
            
            # Check options
            options = tour.options.all()
            if options.exists():
                print(f"     Options: {options.count()}")
                for option in options[:3]:  # Show first 3
                    print(f"       - {option.name} (price: {option.price})")
            else:
                print("     ❌ No options found")
            
            # Check reviews
            reviews = tour.reviews.all()
            if reviews.exists():
                print(f"     Reviews: {reviews.count()}")
            else:
                print("     ❌ No reviews found")
            
            # Check itinerary
            itinerary = tour.itinerary.all()
            if itinerary.exists():
                print(f"     Itinerary: {itinerary.count()} items")
            else:
                print("     ❌ No itinerary found")
            
            print()
    else:
        print("   ❌ No tours found")
    
    # Check database structure
    print("\n🗄️ Database Structure:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'tours_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   Table: {table_name}")
            for col in columns:
                col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                pk_mark = " 🔑" if pk else ""
                print(f"     - {col_name}: {col_type}{pk_mark}")
            print()
    
    print("=" * 50)
    print("🏁 Database check completed!")

if __name__ == "__main__":
    check_existing_tours()
