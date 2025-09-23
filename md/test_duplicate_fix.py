#!/usr/bin/env python3
"""
Test duplicate booking prevention after the fix.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_duplicate_booking_prevention():
    """Test that duplicate booking prevention works correctly."""
    print("🧪 Testing Duplicate Booking Prevention...")
    
    # Test data
    test_data = {
        "product_type": "tour",
        "product_id": "362092e7-891d-411e-a29e-37024405bc07",
        "variant_id": "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc",
        "quantity": 1,
        "booking_data": {
            "schedule_id": "5e20a42d-1cc0-43fe-9a15-aedbc8102aae",
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    session = requests.Session()
    login_data = {
        "username": "test",
        "password": "test123"
    }
    
    login_response = session.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("   ❌ Login failed")
        return False
    
    # Extract JWT token
    login_data = login_response.json()
    access_token = login_data.get('tokens', {}).get('access')
    if not access_token:
        print("   ❌ No access token received")
        return False
    
    # Set authorization header
    session.headers.update({'Authorization': f'Bearer {access_token}'})
    print("   ✅ JWT token set")
    
    # Step 2: Add to cart (first time)
    print("\n2️⃣ Adding to cart (first time)...")
    cart_response = session.post(f"{BASE_URL}/cart/add/", json=test_data)
    print(f"   Cart add status: {cart_response.status_code}")
    
    if cart_response.status_code not in [200, 201]:
        print(f"   ❌ First cart add failed: {cart_response.text}")
        return False
    
    # Step 3: Create order (pending)
    print("\n3️⃣ Creating order (pending)...")
    order_data = {
        "special_requests": "Test order"
    }
    
    order_response = session.post(f"{BASE_URL}/orders/cart/", json=order_data)
    print(f"   Order creation status: {order_response.status_code}")
    print(f"   Order response: {order_response.text}")
    
    if order_response.status_code not in [200, 201]:
        print(f"   ❌ Order creation failed: {order_response.text}")
        return False
    
    # Get order number
    order_data = order_response.json()
    order_number = order_data.get('order_number')
    print(f"   Order created: {order_number}")
    
    # Step 4: Clear cart
    print("\n4️⃣ Clearing cart...")
    clear_response = session.delete(f"{BASE_URL}/cart/clear/")
    print(f"   Clear cart status: {clear_response.status_code}")
    
    # Step 5: Try to add to cart again (should be prevented)
    print("\n5️⃣ Trying to add to cart again (should be prevented)...")
    cart_response2 = session.post(f"{BASE_URL}/cart/add/", json=test_data)
    print(f"   Second cart add status: {cart_response2.status_code}")
    
    if cart_response2.status_code == 400:
        error_data = cart_response2.json()
        if error_data.get('code') == 'DUPLICATE_BOOKING':
            print("   ✅ Duplicate booking correctly prevented!")
            return True
        else:
            print(f"   ❌ Wrong error code: {error_data.get('code')}")
            return False
    else:
        print(f"   ❌ Duplicate booking not prevented (status: {cart_response2.status_code})")
        print(f"   Response: {cart_response2.text}")
        return False

if __name__ == "__main__":
    success = test_duplicate_booking_prevention()
    if success:
        print("\n🎉 Test PASSED: Duplicate booking prevention is working!")
    else:
        print("\n❌ Test FAILED: Duplicate booking prevention is not working!")
