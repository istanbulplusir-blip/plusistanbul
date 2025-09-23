#!/usr/bin/env python3
"""
Complete test for duplicate booking prevention with order creation.
"""

import requests
import json

def test_complete_duplicate():
    """Complete test for duplicate booking prevention."""
    base_url = "http://localhost:8000"
    
    print("🧪 Complete Duplicate Booking Test...")
    
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
    
    session = requests.Session()
    
    # Login first
    print("\n📋 Step 1: Login as test user...")
    login_data = {
        "username": "test",
        "password": "test123"
    }
    
    login_response = session.post(f"{base_url}/api/v1/auth/login/", json=login_data)
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        return False
    
    print("   ✅ Login successful")
    
    # First booking
    print("\n📋 Step 2: First booking...")
    response1 = session.post(f"{base_url}/api/v1/cart/add/", json=test_data)
    print(f"   Status: {response1.status_code}")
    if response1.status_code not in [200, 201]:
        print(f"   ❌ First booking failed: {response1.text}")
        return False
    print("   ✅ First booking successful")
    
    # Create order from cart
    print("\n📋 Step 3: Create order from cart...")
    cart_response = session.get(f"{base_url}/api/v1/cart/")
    if cart_response.status_code != 200:
        print(f"   ❌ Cart fetch failed: {cart_response.status_code}")
        return False
    
    cart_data = cart_response.json()
    cart_id = cart_data.get('id')
    
    order_data = {
        "cart_id": cart_id,
        "special_requests": "Test order for duplicate check"
    }
    
    order_response = session.post(f"{base_url}/api/v1/orders/", json=order_data)
    if order_response.status_code != 201:
        print(f"   ❌ Order creation failed: {order_response.status_code}")
        print(f"   📄 Response: {order_response.text}")
        return False
    
    order_data = order_response.json()
    order_number = order_data.get('order_number')
    print(f"   ✅ Order created: {order_number}")
    
    # Clear cart
    print("\n📋 Step 4: Clear cart...")
    clear_response = session.delete(f"{base_url}/api/v1/cart/clear/")
    if clear_response.status_code == 200:
        print("   ✅ Cart cleared")
    else:
        print(f"   ⚠️ Cart clear failed: {clear_response.status_code}")
    
    # Second booking attempt (should be prevented)
    print("\n📋 Step 5: Second booking attempt (should be prevented)...")
    response2 = session.post(f"{base_url}/api/v1/cart/add/", json=test_data)
    print(f"   Status: {response2.status_code}")
    print(f"   Response: {response2.text[:200]}...")
    
    # Check if duplicate was prevented
    if response2.status_code == 400:
        try:
            error_data = response2.json()
            if error_data.get('code') == 'DUPLICATE_BOOKING':
                print("\n✅ SUCCESS: Duplicate booking correctly prevented!")
                print(f"   📄 Error message: {error_data.get('error')}")
                return True
            else:
                print(f"\n⚠️ Unexpected error code: {error_data.get('code')}")
                return False
        except:
            print("\n⚠️ Could not parse error response")
            return False
    else:
        print(f"\n❌ FAIL: Duplicate booking not prevented (status: {response2.status_code})")
        return False

if __name__ == "__main__":
    test_complete_duplicate()
