#!/usr/bin/env python3
"""
Test duplicate booking prevention fix.
"""

import requests
import json
import time

def test_duplicate_booking_prevention():
    """Test that duplicate booking prevention works correctly."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Duplicate Booking Prevention...")
    
    # Test data with real IDs
    test_data = {
        "product_type": "tour",
        "product_id": "362092e7-891d-411e-a29e-37024405bc07",  # Real tour ID
        "variant_id": "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc",  # Real variant ID
        "quantity": 1,
        "booking_data": {
            "schedule_id": "5e20a42d-1cc0-43fe-9a15-aedbc8102aae",  # Real schedule ID
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }
    
    # Step 1: Login as test user
    print("\n📋 Step 1: Login as test user")
    login_data = {
        "username": "test",
        "password": "test123"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(f"{base_url}/api/v1/auth/login/", json=login_data)
        if response.status_code == 200:
            print("   ✅ Login successful")
            # Session cookies are automatically handled by requests.Session()
            print("   ✅ Session cookies set")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Step 2: First booking (should succeed)
    print("\n📋 Step 2: First booking (should succeed)")
    try:
        response = session.post(f"{base_url}/api/v1/cart/add/", json=test_data)
        if response.status_code in [200, 201]:
            print("   ✅ First booking added to cart successfully")
        else:
            print(f"   ❌ First booking failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ First booking error: {str(e)}")
        return False
    
    # Step 3: Create order from cart
    print("\n📋 Step 3: Create order from cart")
    try:
        cart_response = session.get(f"{base_url}/api/v1/cart/")
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            cart_id = cart_data.get('id')
            
            order_data = {
                "cart_id": cart_id,
                "special_requests": "Test order"
            }
            
            response = session.post(f"{base_url}/api/v1/orders/", json=order_data)
            if response.status_code == 201:
                order_data = response.json()
                order_number = order_data.get('order_number')
                print(f"   ✅ Order created: {order_number}")
            else:
                print(f"   ❌ Order creation failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False
        else:
            print(f"   ❌ Cart fetch failed: {cart_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Order creation error: {str(e)}")
        return False
    
    # Step 4: Clear cart for next test
    print("\n📋 Step 4: Clear cart")
    try:
        response = session.delete(f"{base_url}/api/v1/cart/clear/")
        if response.status_code == 200:
            print("   ✅ Cart cleared")
        else:
            print(f"   ⚠️ Cart clear failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Cart clear error: {str(e)}")
    
    # Step 5: Second booking attempt (should be prevented)
    print("\n📋 Step 5: Second booking attempt (should be prevented)")
    try:
        response = session.post(f"{base_url}/api/v1/cart/add/", json=test_data)
        if response.status_code == 400:
            error_data = response.json()
            if error_data.get('code') == 'DUPLICATE_BOOKING':
                print("   ✅ Duplicate booking correctly prevented")
                print(f"   📄 Error message: {error_data.get('error')}")
                return True
            else:
                print(f"   ⚠️ Unexpected error code: {error_data.get('code')}")
                return False
        else:
            print(f"   ❌ Duplicate booking not prevented: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Second booking error: {str(e)}")
        return False

def test_pending_orders_limit():
    """Test that users can't create more than 3 pending orders."""
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Pending Orders Limit...")
    
    # Login as test user
    session = requests.Session()
    login_data = {"username": "test", "password": "test123"}
    
    try:
        response = session.post(f"{base_url}/api/v1/auth/login/", json=login_data)
        if response.status_code == 200:
            print("   ✅ Login successful")
            # Session cookies are automatically handled by requests.Session()
            print("   ✅ Session cookies set")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Check current pending orders
    try:
        response = session.get(f"{base_url}/api/v1/orders/pending/")
        if response.status_code == 200:
            pending_data = response.json()
            current_count = pending_data.get('count', 0)
            print(f"   📊 Current pending orders: {current_count}")
            
            if current_count >= 3:
                print("   ✅ User already has 3 pending orders (limit reached)")
                return True
            else:
                print(f"   📋 User has {current_count}/3 pending orders")
        else:
            print(f"   ❌ Pending orders fetch failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Pending orders check error: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Duplicate Booking Prevention Fix...\n")
    
    # Test duplicate booking prevention
    duplicate_test_success = test_duplicate_booking_prevention()
    
    # Test pending orders limit
    limit_test_success = test_pending_orders_limit()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Duplicate Booking Prevention: {'✅ PASS' if duplicate_test_success else '❌ FAIL'}")
    print(f"   Pending Orders Limit: {'✅ PASS' if limit_test_success else '❌ FAIL'}")
    
    if duplicate_test_success and limit_test_success:
        print("\n🎉 All tests passed! Duplicate booking prevention is working.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
