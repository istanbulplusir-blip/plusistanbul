#!/usr/bin/env python3
"""
Debug user orders to understand why duplicate check is not working.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from tours.models import TourSchedule
from datetime import date

User = get_user_model()

def debug_user_orders():
    """Debug user orders to understand duplicate check issue."""
    print("🔍 Debugging User Orders...")
    
    # Get test user
    user = User.objects.get(username='test')
    print(f"   📋 User: {user.username}")
    
    # Get all orders for this user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    print(f"\n📊 Total orders: {orders.count()}")
    
    # Check specific test data
    test_product_id = "362092e7-891d-411e-a29e-37024405bc07"
    test_schedule_id = "5e20a42d-1cc0-43fe-9a15-aedbc8102aae"
    
    print(f"\n🔍 Looking for orders with:")
    print(f"   Product ID: {test_product_id}")
    print(f"   Schedule ID: {test_schedule_id}")
    
    # Check orders with this product
    orders_with_product = Order.objects.filter(
        user=user,
        items__product_id=test_product_id
    ).distinct()
    
    print(f"\n📋 Orders with this product: {orders_with_product.count()}")
    
    # Check for orders with specific date (2025-09-23)
    target_date = date(2025, 9, 23)
    orders_with_date = Order.objects.filter(
        user=user,
        items__product_id=test_product_id,
        items__booking_date=target_date
    ).distinct()
    
    print(f"\n📅 Orders with product and date {target_date}: {orders_with_date.count()}")
    for order in orders_with_date:
        print(f"   - {order.order_number} ({order.status})")
        for item in order.items.filter(product_id=test_product_id, booking_date=target_date):
            print(f"     * Booking Date: {item.booking_date}")
            print(f"     * Schedule ID: {item.booking_data.get('schedule_id') if item.booking_data else 'None'}")
    
    # Check for pending orders with same product and date
    pending_orders = Order.objects.filter(
        user=user,
        status='pending',
        items__product_id=test_product_id,
        items__booking_date=target_date
    ).distinct()
    
    print(f"\n🔍 Pending orders with same product and date: {pending_orders.count()}")
    for order in pending_orders:
        print(f"   - {order.order_number}")
    
    # Check for ANY pending orders with this product (regardless of date)
    any_pending_orders = Order.objects.filter(
        user=user,
        status='pending',
        items__product_id=test_product_id
    ).distinct()
    
    print(f"\n🔍 ANY pending orders with this product: {any_pending_orders.count()}")
    for order in any_pending_orders:
        print(f"   - {order.order_number}")
        for item in order.items.filter(product_id=test_product_id):
            print(f"     * Booking Date: {item.booking_date}")
            print(f"     * Schedule ID: {item.booking_data.get('schedule_id') if item.booking_data else 'None'}")
    
    # Check schedule
    try:
        schedule = TourSchedule.objects.get(id=test_schedule_id)
        print(f"\n📅 Schedule: {schedule.id}")
        print(f"   Tour: {schedule.tour.title}")
        print(f"   Start Date: {schedule.start_date}")
    except TourSchedule.DoesNotExist:
        print(f"\n❌ Schedule {test_schedule_id} not found")
    
    # Check the other schedule
    other_schedule_id = "6b40dbdd-b545-4969-adfc-4ca3145767f6"
    try:
        other_schedule = TourSchedule.objects.get(id=other_schedule_id)
        print(f"\n📅 Other Schedule: {other_schedule.id}")
        print(f"   Tour: {other_schedule.tour.title}")
        print(f"   Start Date: {other_schedule.start_date}")
    except TourSchedule.DoesNotExist:
        print(f"\n❌ Other Schedule {other_schedule_id} not found")

if __name__ == "__main__":
    debug_user_orders()
