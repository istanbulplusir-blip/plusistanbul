#!/usr/bin/env python3
"""
Debug script to reproduce duplicate booking issue
"""

import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import authenticate
from orders.models import Order, OrderItem
from tours.models import Tour, TourSchedule, TourVariant
from cart.models import Cart, CartItem

def debug_duplicate_booking():
    """Debug the duplicate booking check logic"""
    
    # Authenticate as test user
    user = authenticate(username='test', password='test123')
    if not user:
        print("❌ Failed to authenticate user 'test'")
        return
    
    print(f"✅ Authenticated as: {user.username}")
    
    # Get the tour and schedule from the user's report
    tour_id = "163290658"  # From the order items
    schedule_id = None
    
    # Find the schedule for this tour
    try:
        tour = Tour.objects.get(id=tour_id)
        print(f"✅ Found tour: {tour.title}")
        
        # Get schedules for this tour
        schedules = TourSchedule.objects.filter(tour=tour)
        print(f"📅 Found {schedules.count()} schedules for this tour")
        
        for schedule in schedules:
            print(f"  - Schedule {schedule.id}: {schedule.start_date}")
        
        # Use the first schedule for testing
        if schedules.exists():
            schedule = schedules.first()
            schedule_id = schedule.id
            booking_date = schedule.start_date
            print(f"🎯 Using schedule {schedule_id} with booking_date: {booking_date}")
        else:
            print("❌ No schedules found for this tour")
            return
            
    except Tour.DoesNotExist:
        print(f"❌ Tour with ID {tour_id} not found")
        return
    
    # Check existing pending orders for this user/tour/date
    print("\n🔍 Checking existing pending orders...")
    
    existing_pending_orders = Order.objects.filter(
        user=user,
        items__product_type='tour',
        items__product_id=tour_id,
        items__booking_date=booking_date,
        status='pending'
    )
    
    print(f"📊 Found {existing_pending_orders.count()} pending orders")
    
    for order in existing_pending_orders:
        print(f"  - Order {order.order_number}: {order.created_at}")
        for item in order.items.all():
            print(f"    * {item.product_title} - {item.booking_date}")
    
    # Now let's test the exact query from check_duplicate_booking
    print("\n🔍 Testing check_duplicate_booking logic...")
    
    # This is the exact query from the method
    existing_confirmed_orders = Order.objects.filter(
        user=user,
        items__product_type='tour',
        items__product_id=tour_id,
        items__booking_date=booking_date,
        status__in=['confirmed', 'paid', 'completed']
    ).exists()
    
    print(f"✅ Confirmed orders exist: {existing_confirmed_orders}")
    
    existing_pending_orders = Order.objects.filter(
        user=user,
        items__product_type='tour',
        items__product_id=tour_id,
        items__booking_date=booking_date,
        status='pending'
    ).exists()
    
    print(f"✅ Pending orders exist: {existing_pending_orders}")
    
    # Let's also check if there are any orders with the specific schedule_id
    print("\n🔍 Checking orders with specific schedule_id...")
    
    orders_with_schedule = Order.objects.filter(
        user=user,
        items__product_type='tour',
        items__product_id=tour_id,
        items__booking_data__schedule_id=schedule_id,
        status='pending'
    )
    
    print(f"📊 Found {orders_with_schedule.count()} orders with schedule_id {schedule_id}")
    
    for order in orders_with_schedule:
        print(f"  - Order {order.order_number}: {order.created_at}")
        for item in order.items.all():
            print(f"    * Schedule ID: {item.booking_data.get('schedule_id')}")
            print(f"    * Booking date: {item.booking_date}")
    
    # Test the exact product_data that would be passed to check_duplicate_booking
    print("\n🔍 Testing with exact product_data...")
    
    product_data = {
        'product_type': 'tour',
        'product_id': tour_id,
        'variant_id': None,  # We need to find the variant
        'booking_data': {
            'schedule_id': schedule_id,
            'participants': {'adult': 1, 'child': 0, 'infant': 0}
        }
    }
    
    # Find the variant
    try:
        variant = TourVariant.objects.filter(tour=tour).first()
        if variant:
            product_data['variant_id'] = str(variant.id)
            print(f"✅ Using variant: {variant.id}")
    except Exception as e:
        print(f"⚠️ Could not find variant: {e}")
    
    # Now let's simulate the check_duplicate_booking logic
    print("\n🔍 Simulating check_duplicate_booking...")
    
    # Get booking_date from schedule
    try:
        schedule = TourSchedule.objects.get(id=schedule_id)
        booking_date = schedule.start_date
        print(f"📅 Booking date from schedule: {booking_date}")
    except Exception as e:
        print(f"❌ Error getting schedule: {e}")
        booking_date = None
    
    if booking_date:
        # Check for existing orders with same tour and date
        existing_confirmed_orders = Order.objects.filter(
            user=user,
            items__product_type='tour',
            items__product_id=tour_id,
            items__booking_date=booking_date,
            status__in=['confirmed', 'paid', 'completed']
        ).exists()
        
        print(f"🔍 Confirmed orders check: {existing_confirmed_orders}")
        
        existing_pending_orders = Order.objects.filter(
            user=user,
            items__product_type='tour',
            items__product_id=tour_id,
            items__booking_date=booking_date,
            status='pending'
        ).exists()
        
        print(f"🔍 Pending orders check: {existing_pending_orders}")
        
        duplicate_result = existing_confirmed_orders or existing_pending_orders
        print(f"🎯 Final duplicate result: {duplicate_result}")
        
        if not duplicate_result:
            print("❌ BUG: Duplicate check returned False but pending orders exist!")
            print("🔍 This suggests the query is not finding the existing orders")
            
            # Let's check what's actually in the database
            print("\n🔍 Detailed database inspection...")
            
            all_user_orders = Order.objects.filter(user=user, status='pending')
            print(f"📊 User has {all_user_orders.count()} total pending orders")
            
            for order in all_user_orders:
                print(f"  - Order {order.order_number}: {order.created_at}")
                for item in order.items.all():
                    print(f"    * Product: {item.product_title} (ID: {item.product_id})")
                    print(f"    * Type: {item.product_type}")
                    print(f"    * Date: {item.booking_date}")
                    print(f"    * Booking data: {item.booking_data}")
        else:
            print("✅ Duplicate check working correctly")

if __name__ == "__main__":
    debug_duplicate_booking()
