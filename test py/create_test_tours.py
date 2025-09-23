#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourCategory, TourVariant, TourSchedule, TourOption
from django.utils import timezone

def create_test_tours():
    print("=== Creating Test Tours ===")
    
    # Get or create a category
    category, created = TourCategory.objects.get_or_create(
        slug='cultural',
        defaults={
            'name': 'تورهای فرهنگی',
            'description': 'تورهای فرهنگی و هنری',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created category: {category.name}")
    else:
        print(f"Using existing category: {category.name}")
    
    # Create test tour
    tour_data = {
        'title': 'تور تهران قدیم',
        'description': 'بازدید از اماکن تاریخی تهران',
        'short_description': 'تور یک روزه تهران قدیم',
        'highlights': 'بازدید از کاخ گلستان، بازار تهران، موزه ملی',
        'rules': 'لطفاً لباس مناسب بپوشید',
        'required_items': 'کفش راحت، دوربین',
        'image': 'https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Tehran+Tour',
        'gallery': ['https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Gallery+1'],
        'price': 1500000,
        'currency': 'IRR',
        'duration_hours': 8,
        'max_participants': 20,
        'min_participants': 5,
        'booking_cutoff_hours': 24,
        'cancellation_hours': 48,
        'refund_percentage': 80,
        'includes_transfer': True,
        'includes_guide': True,
        'includes_meal': False,
        'includes_photographer': False,
        'tour_type': 'day',
        'transport_type': 'land',
        'pickup_time': '08:00:00',
        'start_time': '09:00:00',
        'end_time': '17:00:00',
        'is_active': True,
        'category': category
    }
    
    tour, created = Tour.objects.get_or_create(
        slug='tehran-cultural-tour',
        defaults=tour_data
    )
    
    if created:
        print(f"Created tour: {tour.title}")
    else:
        print(f"Tour already exists: {tour.title}")
    
    # Create tour variant
    variant_data = {
        'name': 'پکیج استاندارد',
        'description': 'تور استاندارد با راهنما و حمل و نقل',
        'base_price': 1500000,
        'capacity': 20,
        'is_active': True,
        'includes_transfer': True,
        'includes_guide': True,
        'includes_meal': False,
        'includes_photographer': False,
        'extended_hours': 0,
        'private_transfer': False,
        'expert_guide': False,
        'special_meal': False
    }
    
    variant, created = TourVariant.objects.get_or_create(
        tour=tour,
        name=variant_data['name'],
        defaults=variant_data
    )
    
    if created:
        print(f"Created variant: {variant.name}")
    else:
        print(f"Variant already exists: {variant.name}")
    
    # Create tour schedule
    tomorrow = timezone.now().date() + timedelta(days=1)
    schedule_data = {
        'start_date': tomorrow,
        'end_date': tomorrow,
        'start_time': '09:00:00',
        'end_time': '17:00:00',
        'is_available': True,
        'max_capacity': 20,
        'current_capacity': 0,
        'day_of_week': tomorrow.weekday()
    }
    
    schedule, created = TourSchedule.objects.get_or_create(
        tour=tour,
        start_date=schedule_data['start_date'],
        start_time=schedule_data['start_time'],
        defaults=schedule_data
    )
    
    if created:
        print(f"Created schedule for {schedule.start_date}")
    else:
        print(f"Schedule already exists for {schedule.start_date}")
    
    # Create tour option
    option_data = {
        'name': 'راهنمای خصوصی',
        'description': 'راهنمای خصوصی برای گروه',
        'price': 500000,
        'price_percentage': 33,
        'currency': 'IRR',
        'option_type': 'service',
        'is_available': True,
        'max_quantity': 1
    }
    
    option, created = TourOption.objects.get_or_create(
        tour=tour,
        name=option_data['name'],
        defaults=option_data
    )
    
    if created:
        print(f"Created option: {option.name}")
    else:
        print(f"Option already exists: {option.name}")
    
    print("\n=== Test Tour Creation Complete ===")
    print(f"Tour: {tour.title}")
    print(f"Slug: {tour.slug}")
    print(f"Category: {tour.category.name}")
    print(f"Price: {tour.price} {tour.currency}")
    print(f"Active: {tour.is_active}")
    
    return tour

if __name__ == "__main__":
    create_test_tours()
