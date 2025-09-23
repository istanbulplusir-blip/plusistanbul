#!/usr/bin/env python3
"""
Test script to verify the duplicate booking fix
"""

import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import authenticate
from orders.models import Order, OrderItem
from tours.models import Tour, TourSchedule, TourVariant
from cart.models import Cart, CartItem
from cart.views import AddToCartView
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_duplicate_booking_fix():
    """Test that the duplicate booking fix works correctly"""
    
    # Authenticate as test user
    user = authenticate(username='test', password='test123')
    if not user:
        print("❌ Failed to authenticate user 'test'")
        return
    
    print(f"✅ Authenticated as: {user.username}")
    
    # Get the tour and schedule from the user's existing orders
    user_orders = Order.objects.filter(user=user, status='pending')
    tour_id = None
    schedule_id = None
    
    for order in user_orders:
        for item in order.items.all():
            if item.product_type == 'tour':
                tour_id = item.product_id
                if item.booking_data and 'schedule_id' in item.booking_data:
                    schedule_id = item.booking_data['schedule_id']
                break
        if tour_id and schedule_id:
            break
    
    if not tour_id or not schedule_id:
        print("❌ No tour found in user's pending orders")
        return
    
    print(f"📋 Using tour ID: {tour_id}")
    print(f"📅 Using schedule ID: {schedule_id}")
    
    # Create a mock request and view instance
    factory = RequestFactory()
    request = factory.post('/api/v1/cart/add/')
    request.user = user
    
    view = AddToCartView()
    
    # Test product_data that should trigger duplicate detection
    product_data = {
        'product_type': 'tour',
        'product_id': tour_id,
        'variant_id': None,  # We'll find this
        'booking_data': {
            'schedule_id': schedule_id,
            'participants': {'adult': 1, 'child': 0, 'infant': 0}
        }
    }
    
    # Find the variant
    try:
        tour = Tour.objects.get(id=tour_id)
        variant = TourVariant.objects.filter(tour=tour).first()
        if variant:
            product_data['variant_id'] = str(variant.id)
            print(f"✅ Using variant: {variant.id}")
    except Exception as e:
        print(f"⚠️ Could not find variant: {e}")
    
    # Test the check_duplicate_booking method
    print("\n🔍 Testing check_duplicate_booking method...")
    
    duplicate_result = view.check_duplicate_booking(request, user, product_data)
    
    print(f"🎯 Duplicate check result: {duplicate_result}")
    
    if duplicate_result:
        print("✅ SUCCESS: Duplicate booking correctly detected!")
        
        # Verify that there are indeed existing orders
        existing_orders = Order.objects.filter(
            user=user,
            items__product_type='tour',
            items__product_id=tour_id,
            items__booking_data__schedule_id=schedule_id,
            status='pending'
        )
        
        print(f"📊 Found {existing_orders.count()} existing pending orders for this schedule")
        
        for order in existing_orders:
            print(f"  - Order {order.order_number}: {order.created_at}")
            for item in order.items.all():
                print(f"    * Schedule ID: {item.booking_data.get('schedule_id')}")
                print(f"    * Booking date: {item.booking_date}")
        
    else:
        print("❌ FAILURE: Duplicate booking not detected!")
        
        # Check what orders exist
        existing_orders = Order.objects.filter(
            user=user,
            items__product_type='tour',
            items__product_id=tour_id,
            items__booking_data__schedule_id=schedule_id,
            status='pending'
        )
        
        print(f"📊 Found {existing_orders.count()} orders that should have been detected")
        
        if existing_orders.count() > 0:
            print("🔍 This suggests the fix is not working correctly")
        else:
            print("🔍 No existing orders found - this might be expected if orders were cleared")

def test_new_booking_allowed():
    """Test that a new booking for a different schedule is allowed"""
    
    # Authenticate as test user
    user = authenticate(username='test', password='test123')
    if not user:
        print("❌ Failed to authenticate user 'test'")
        return
    
    print(f"\n🔍 Testing new booking for different schedule...")
    
    # Get a different schedule for the same tour
    user_orders = Order.objects.filter(user=user, status='pending')
    tour_id = None
    
    for order in user_orders:
        for item in order.items.all():
            if item.product_type == 'tour':
                tour_id = item.product_id
                break
        if tour_id:
            break
    
    if not tour_id:
        print("❌ No tour found")
        return
    
    # Get all schedules for this tour
    try:
        tour = Tour.objects.get(id=tour_id)
        schedules = TourSchedule.objects.filter(tour=tour)
        
        # Find a schedule that the user doesn't have orders for
        used_schedule_ids = set()
        for order in user_orders:
            for item in order.items.all():
                if item.product_type == 'tour' and item.product_id == tour_id:
                    if item.booking_data and 'schedule_id' in item.booking_data:
                        used_schedule_ids.add(item.booking_data['schedule_id'])
        
        available_schedule = None
        for schedule in schedules:
            if str(schedule.id) not in used_schedule_ids:
                available_schedule = schedule
                break
        
        if not available_schedule:
            print("⚠️ No available schedules found for testing")
            return
        
        print(f"📅 Testing with available schedule: {available_schedule.id} ({available_schedule.start_date})")
        
        # Create a mock request and view instance
        factory = RequestFactory()
        request = factory.post('/api/v1/cart/add/')
        request.user = user
        
        view = AddToCartView()
        
        # Test product_data for the available schedule
        product_data = {
            'product_type': 'tour',
            'product_id': tour_id,
            'variant_id': None,
            'booking_data': {
                'schedule_id': str(available_schedule.id),
                'participants': {'adult': 1, 'child': 0, 'infant': 0}
            }
        }
        
        # Find the variant
        variant = TourVariant.objects.filter(tour=tour).first()
        if variant:
            product_data['variant_id'] = str(variant.id)
        
        # Test the check_duplicate_booking method
        duplicate_result = view.check_duplicate_booking(request, user, product_data)
        
        print(f"🎯 Duplicate check result for new schedule: {duplicate_result}")
        
        if not duplicate_result:
            print("✅ SUCCESS: New booking correctly allowed!")
        else:
            print("❌ FAILURE: New booking incorrectly blocked!")
            
    except Exception as e:
        print(f"❌ Error testing new booking: {e}")

if __name__ == "__main__":
    test_duplicate_booking_fix()
    test_new_booking_allowed()
