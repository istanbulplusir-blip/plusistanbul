#!/usr/bin/env python3
"""
Test script to verify the duplicate booking fix works in the actual API flow
"""

import os
import sys
import django
import requests
import json
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

def test_api_duplicate_booking():
    """Test that the API correctly prevents duplicate bookings"""
    
    # API base URL
    base_url = "http://localhost:8000/api/v1"
    
    # Test user credentials
    username = "test"
    password = "test123"
    
    print("🔍 Testing API duplicate booking prevention...")
    
    # Step 1: Login to get authentication
    print("\n1️⃣ Logging in...")
    login_data = {
        'username': username,
        'password': password
    }
    
    login_response = requests.post(f"{base_url}/auth/login/", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    print("✅ Login successful")
    
    # Get session cookies
    session_cookies = login_response.cookies
    
    # Step 2: Get user's existing orders to find tour and schedule
    print("\n2️⃣ Getting user's existing orders...")
    
    orders_response = requests.get(f"{base_url}/orders/pending/", cookies=session_cookies)
    
    if orders_response.status_code != 200:
        print(f"❌ Failed to get orders: {orders_response.status_code}")
        return
    
    orders_data = orders_response.json()
    pending_orders = orders_data.get('pending_orders', [])
    
    if not pending_orders:
        print("❌ No pending orders found")
        return
    
    # Find a tour order
    tour_order = None
    tour_id = None
    schedule_id = None
    
    for order in pending_orders:
        for item in order.get('items', []):
            if item.get('product_type') == 'tour':
                tour_order = order
                tour_id = item.get('product_id')
                booking_data = item.get('booking_data', {})
                schedule_id = booking_data.get('schedule_id')
                break
        if tour_order:
            break
    
    if not tour_order or not tour_id or not schedule_id:
        print("❌ No tour orders found")
        return
    
    print(f"📋 Found tour order: {tour_order['order_number']}")
    print(f"📅 Schedule ID: {schedule_id}")
    
    # Step 3: Try to add the same tour/schedule to cart (should be blocked)
    print("\n3️⃣ Testing duplicate booking prevention...")
    
    # Get tour details to find variant
    tour_response = requests.get(f"{base_url}/tours/{tour_id}/", cookies=session_cookies)
    
    if tour_response.status_code != 200:
        print(f"❌ Failed to get tour details: {tour_response.status_code}")
        return
    
    tour_data = tour_response.json()
    variants = tour_data.get('variants', [])
    
    if not variants:
        print("❌ No variants found for tour")
        return
    
    variant_id = variants[0].get('id')  # Use first variant
    
    # Prepare cart data for the same tour/schedule
    cart_data = {
        'product_type': 'tour',
        'product_id': tour_id,
        'variant_id': variant_id,
        'quantity': 1,
        'booking_data': {
            'schedule_id': schedule_id,
            'participants': {
                'adult': 1,
                'child': 0,
                'infant': 0
            }
        }
    }
    
    print(f"📤 Attempting to add duplicate booking to cart...")
    print(f"   Tour ID: {tour_id}")
    print(f"   Schedule ID: {schedule_id}")
    print(f"   Variant ID: {variant_id}")
    
    # Try to add to cart
    cart_response = requests.post(f"{base_url}/cart/add/", json=cart_data, cookies=session_cookies)
    
    print(f"📥 Response status: {cart_response.status_code}")
    
    if cart_response.status_code == 400:
        response_data = cart_response.json()
        error_code = response_data.get('code')
        error_message = response_data.get('error')
        
        if error_code == 'DUPLICATE_BOOKING':
            print("✅ SUCCESS: Duplicate booking correctly blocked!")
            print(f"   Error code: {error_code}")
            print(f"   Error message: {error_message}")
        else:
            print(f"⚠️ Unexpected error: {error_code}")
            print(f"   Error message: {error_message}")
    elif cart_response.status_code == 201:
        print("❌ FAILURE: Duplicate booking was allowed!")
        print("   This means the fix is not working correctly")
    else:
        print(f"❌ Unexpected response: {cart_response.status_code}")
        print(f"   Response: {cart_response.text}")

def test_new_booking_allowed():
    """Test that a new booking for a different schedule is allowed"""
    
    # API base URL
    base_url = "http://localhost:8000/api/v1"
    
    # Test user credentials
    username = "test"
    password = "test123"
    
    print("\n🔍 Testing new booking for different schedule...")
    
    # Step 1: Login to get authentication
    print("\n1️⃣ Logging in...")
    login_data = {
        'username': username,
        'password': password
    }
    
    login_response = requests.post(f"{base_url}/auth/login/", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Get session cookies
    session_cookies = login_response.cookies
    
    # Step 2: Get user's existing orders to find tour
    print("\n2️⃣ Getting user's existing orders...")
    
    orders_response = requests.get(f"{base_url}/orders/pending/", cookies=session_cookies)
    
    if orders_response.status_code != 200:
        print(f"❌ Failed to get orders: {orders_response.status_code}")
        return
    
    orders_data = orders_response.json()
    pending_orders = orders_data.get('pending_orders', [])
    
    if not pending_orders:
        print("❌ No pending orders found")
        return
    
    # Find a tour order
    tour_id = None
    used_schedule_ids = set()
    
    for order in pending_orders:
        for item in order.get('items', []):
            if item.get('product_type') == 'tour':
                tour_id = item.get('product_id')
                booking_data = item.get('booking_data', {})
                schedule_id = booking_data.get('schedule_id')
                if schedule_id:
                    used_schedule_ids.add(schedule_id)
    
    if not tour_id:
        print("❌ No tour orders found")
        return
    
    print(f"📋 Tour ID: {tour_id}")
    print(f"📅 Used schedule IDs: {used_schedule_ids}")
    
    # Step 3: Get tour details to find available schedules
    print("\n3️⃣ Getting tour details...")
    
    tour_response = requests.get(f"{base_url}/tours/{tour_id}/", cookies=session_cookies)
    
    if tour_response.status_code != 200:
        print(f"❌ Failed to get tour details: {tour_response.status_code}")
        return
    
    tour_data = tour_response.json()
    schedules = tour_data.get('schedules', [])
    variants = tour_data.get('variants', [])
    
    if not schedules:
        print("❌ No schedules found for tour")
        return
    
    if not variants:
        print("❌ No variants found for tour")
        return
    
    # Find an available schedule
    available_schedule = None
    for schedule in schedules:
        if schedule.get('id') not in used_schedule_ids:
            available_schedule = schedule
            break
    
    if not available_schedule:
        print("⚠️ No available schedules found for testing")
        return
    
    print(f"📅 Found available schedule: {available_schedule['id']} ({available_schedule['start_date']})")
    
    variant_id = variants[0].get('id')
    
    # Step 4: Try to add new booking for available schedule
    print("\n4️⃣ Testing new booking for available schedule...")
    
    cart_data = {
        'product_type': 'tour',
        'product_id': tour_id,
        'variant_id': variant_id,
        'quantity': 1,
        'booking_data': {
            'schedule_id': available_schedule['id'],
            'participants': {
                'adult': 1,
                'child': 0,
                'infant': 0
            }
        }
    }
    
    print(f"📤 Attempting to add new booking to cart...")
    print(f"   Tour ID: {tour_id}")
    print(f"   Schedule ID: {available_schedule['id']}")
    print(f"   Variant ID: {variant_id}")
    
    # Try to add to cart
    cart_response = requests.post(f"{base_url}/cart/add/", json=cart_data, cookies=session_cookies)
    
    print(f"📥 Response status: {cart_response.status_code}")
    
    if cart_response.status_code == 201:
        print("✅ SUCCESS: New booking correctly allowed!")
        response_data = cart_response.json()
        print(f"   Message: {response_data.get('message')}")
    elif cart_response.status_code == 400:
        response_data = cart_response.json()
        error_code = response_data.get('code')
        error_message = response_data.get('error')
        print(f"❌ FAILURE: New booking incorrectly blocked!")
        print(f"   Error code: {error_code}")
        print(f"   Error message: {error_message}")
    else:
        print(f"❌ Unexpected response: {cart_response.status_code}")
        print(f"   Response: {cart_response.text}")

if __name__ == "__main__":
    test_api_duplicate_booking()
    test_new_booking_allowed()
