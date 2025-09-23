#!/usr/bin/env python3
"""
Final integration test for duplicate booking prevention.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_final_integration():
    """Final integration test for duplicate booking prevention."""
    print("🧪 Final Integration Test...")
    
    # Test data
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
    
    # Step 2: Clear cart first
    print("\n2️⃣ Clearing cart...")
    clear_response = session.delete(f"{BASE_URL}/cart/clear/")
    print(f"   Clear cart status: {clear_response.status_code}")
    
    # Step 3: Try to add to cart (should be prevented due to existing pending order)
    print("\n3️⃣ Trying to add to cart (should be prevented due to pending order)...")
    cart_response = session.post(f"{BASE_URL}/cart/add/", json=test_data)
    print(f"   Cart add status: {cart_response.status_code}")
    
    if cart_response.status_code == 400:
        error_data = cart_response.json()
        if error_data.get('code') == 'DUPLICATE_BOOKING':
            print("   ✅ Duplicate booking correctly prevented!")
            print(f"   Error message: {error_data.get('error')}")
        else:
            print(f"   ❌ Wrong error code: {error_data.get('code')}")
            print(f"   Error message: {error_data.get('error')}")
            return False
    else:
        print(f"   ❌ Duplicate booking not prevented (status: {cart_response.status_code})")
        print(f"   Response: {cart_response.text}")
        return False
    
    # Step 4: Test with different schedule (should work)
    print("\n4️⃣ Testing with different schedule (should work)...")
    different_test_data = {
        "product_type": "tour",
        "product_id": "362092e7-891d-411e-a29e-37024405bc07",
        "variant_id": "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc",
        "quantity": 1,
        "booking_data": {
            "schedule_id": "5e20a42d-1cc0-43fe-9a15-aedbc8102aae",  # Different schedule
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }
    
    cart_response2 = session.post(f"{BASE_URL}/cart/add/", json=different_test_data)
    print(f"   Cart add status: {cart_response2.status_code}")
    
    if cart_response2.status_code in [200, 201]:
        print("   ✅ Different schedule allowed!")
    else:
        print(f"   ❌ Different schedule not allowed: {cart_response2.text}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test_final_integration()
    if success:
        print("\n🎉 Final Integration Test PASSED!")
    else:
        print("\n❌ Final Integration Test FAILED!")
