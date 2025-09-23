
#!/usr/bin/env python3
"""
Create test data for tours and schedules.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourVariant, TourSchedule, TourCategory
from django.contrib.auth import get_user_model

User = get_user_model()

def check_existing_data():
    """Check existing tours and variants."""
    print("🔍 Checking existing data...")
    
    # Check tours
    tours = Tour.objects.all()
    print(f"📊 Found {tours.count()} tours:")
    for tour in tours:
        try:
            title = tour.title
        except:
            title = f"Tour {tour.id}"
        print(f"   - {title} (ID: {tour.id}, Slug: {tour.slug})")
    
    # Check variants
    variants = TourVariant.objects.all()
    print(f"📊 Found {variants.count()} variants:")
    for variant in variants:
        try:
            name = variant.name
        except:
            name = f"Variant {variant.id}"
        print(f"   - {name} (ID: {variant.id})")
    
    # Check schedules
    schedules = TourSchedule.objects.all()
    print(f"📊 Found {schedules.count()} schedules:")
    for schedule in schedules:
        try:
            title = schedule.tour.title
        except:
            title = f"Tour {schedule.tour.id}"
        print(f"   - {title} (ID: {schedule.id}, Date: {schedule.start_date})")

def get_test_data():
    """Get existing tour, variant, and schedule."""
    print("\n🔧 Getting test data...")
    
    # Use existing tour
    tour = Tour.objects.first()
    if not tour:
        print("   ❌ No tours found in database")
        return None, None, None
    
    print(f"   📋 Using tour: {tour.id}")
    
    # Use existing variant
    variant = TourVariant.objects.filter(tour=tour).first()
    if not variant:
        print("   ❌ No variants found for tour")
        return tour, None, None
    
    print(f"   📋 Using variant: {variant.id}")
    
    # Use existing schedule
    schedule = TourSchedule.objects.filter(tour=tour).first()
    if not schedule:
        print("   ❌ No schedules found for tour")
        return tour, variant, None
    
    print(f"   📋 Using schedule: {schedule.id}")
    
    return tour, variant, schedule

def create_test_user():
    """Create a test user if it doesn't exist."""
    print("\n👤 Creating test user...")
    
    user, created = User.objects.get_or_create(
        username='test',
            defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
            }
        )
        
        if created:
        user.set_password('test123')
        user.save()
        print(f"   ✅ Created user: {user.username}")
    else:
        print(f"   📋 Using existing user: {user.username}")
    
    return user

def main():
    """Main function."""
    print("🚀 Creating Test Data for Duplicate Booking Tests...\n")
    
    # Check existing data
    check_existing_data()
    
    # Get test data
    tour, variant, schedule = get_test_data()
    
    if not tour or not variant or not schedule:
        print("❌ Failed to get test data")
        return
    
    # Create test user
    user = create_test_user()
    
    # Summary
    print(f"\n📋 Test Data Summary:")
    print(f"   Tour ID: {tour.id}")
    print(f"   Tour Slug: {tour.slug}")
    print(f"   Variant ID: {variant.id}")
    print(f"   Schedule ID: {schedule.id}")
    print(f"   Schedule Date: {schedule.start_date}")
    print(f"   User: {user.username}")
    
    print(f"\n🔧 Test Data Ready!")
    print(f"   Use these IDs in your tests:")
    print(f"   - product_id: '{tour.id}'")
    print(f"   - variant_id: '{variant.id}'")
    print(f"   - schedule_id: '{schedule.id}'")
    print(f"   - username: '{user.username}'")
    print(f"   - password: 'test123'")

if __name__ == "__main__":
    main() 