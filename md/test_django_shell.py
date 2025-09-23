#!/usr/bin/env python3
"""
Test duplicate booking check directly with Django shell.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.peykan.settings')
django.setup()

from cart.views import AddToCartView
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.common import CommonMiddleware

User = get_user_model()

def test_duplicate_check():
    """Test duplicate booking check directly."""
    print("🧪 Testing Duplicate Booking Check with Django Shell...")
    
    # Get test user
    user = User.objects.get(username='test')
    print(f"   📋 Using user: {user.username}")
    
    # Create test data
    test_data = {
        "product_type": "tour",
        "product_id": "362092e7-891d-411e-a29e-37024405bc07",
        "variant_id": "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc",
        "quantity": 1,
        "booking_data": {
            "schedule_id": "6b40dbdd-b545-4969-adfc-4ca3145767f6",
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }
    
    # Create request
    factory = RequestFactory()
    request = factory.post('/api/v1/cart/add/', test_data, HTTP_HOST='localhost:8000')
    
    # Add session middleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Add common middleware
    common_middleware = CommonMiddleware(lambda x: None)
    common_middleware.process_request(request)
    
    # Set user
    request.user = user
    
    # Create view instance
    view = AddToCartView()
    
    # Test duplicate check
    print("\n📋 Testing duplicate booking check...")
    duplicate_result = view.check_duplicate_booking(request, user, test_data)
    print(f"   Result: {duplicate_result}")
    
    if duplicate_result:
        print("   ✅ Duplicate booking detected!")
    else:
        print("   ❌ No duplicate booking detected")
    
    # Check if user has any orders
    from orders.models import Order
    orders = Order.objects.filter(user=user)
    print(f"\n📊 User has {orders.count()} orders:")
    for order in orders:
        print(f"   - {order.order_number}: {order.status}")
    
    return duplicate_result

if __name__ == "__main__":
    test_duplicate_check()
