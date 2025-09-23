#!/usr/bin/env python3
"""
Create a pending order for testing duplicate booking prevention.
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
from datetime import date, time

User = get_user_model()

def create_pending_order():
    """Create a pending order for testing."""
    print("🔧 Creating Pending Order for Testing...")
    
    # Get test user
    user = User.objects.get(username='test')
    print(f"   📋 Using user: {user.username}")
    
    # Get schedule for 2025-09-23
    schedule_id = "6b40dbdd-b545-4969-adfc-4ca3145767f6"
    schedule = TourSchedule.objects.get(id=schedule_id)
    print(f"   📅 Using schedule: {schedule.id} (Start Date: {schedule.start_date})")
    
    # Create order
    order = Order.objects.create(
        user=user,
        status='pending',
        subtotal=100.00,
        tax_amount=0.00,
        discount_amount=0.00,
        total_amount=100.00
    )
    print(f"   📋 Created order: {order.order_number}")
    
    # Create order item
    order_item = OrderItem.objects.create(
        order=order,
        product_type='tour',
        product_id='362092e7-891d-411e-a29e-37024405bc07',
        variant_id='dfbf8292-caa3-4ecd-9f36-feb85c02b4fc',
        quantity=1,
        unit_price=100.00,
        total_price=100.00,
        currency='USD',
        booking_date=date(2025, 9, 23),
        booking_time=time(10, 0),  # 10:00 AM
        booking_data={
            'schedule_id': schedule_id,
            'participants': {
                'adult': 1,
                'child': 0,
                'infant': 0
            }
        }
    )
    print(f"   📦 Created order item: {order_item.id}")
    
    print(f"   ✅ Pending order created successfully!")
    return order

if __name__ == "__main__":
    create_pending_order()
