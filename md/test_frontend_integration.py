#!/usr/bin/env python3
"""
Test frontend integration with new guest limits and duplicate booking prevention.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_frontend_integration():
    """Test frontend integration with new limits."""
    print("🧪 Frontend Integration Test...")
    
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
    
    # Test 1: Guest user limits
    print("\n1️⃣ Testing Guest User Limits...")
    session = requests.Session()
    
    # Clear cart first
    session.delete(f"{BASE_URL}/cart/clear/")
    
    # Try to add 6 items (should fail on 6th)
    for i in range(6):
        response = session.post(f"{BASE_URL}/cart/add/", json=test_data)
        print(f"   Item {i+1}: {response.status_code}")
        
        if response.status_code == 400:
            error_data = response.json()
            if error_data.get('code') == 'GUEST_LIMIT_EXCEEDED':
                print(f"   ✅ Guest limit correctly enforced: {error_data.get('error')}")
                break
            else:
                print(f"   ❌ Wrong error code: {error_data.get('code')}")
                print(f"   Error message: {error_data.get('error')}")
                break
        elif response.status_code in [200, 201]:
            print(f"   ✅ Item {i+1} added successfully")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            break
    
    # Test 2: Check cart API response structure
    print("\n2️⃣ Testing Cart API Response Structure...")
    
    cart_response = session.get(f"{BASE_URL}/cart/")
    if cart_response.status_code == 200:
        cart_data = cart_response.json()
        print(f"   ✅ Cart API working")
        print(f"   Items count: {len(cart_data.get('items', []))}")
        print(f"   Total price: {cart_data.get('total_price', 0)}")
        
        # Check if items have required fields
        if cart_data.get('items'):
            item = cart_data['items'][0]
            required_fields = ['id', 'product_type', 'product_id', 'quantity', 'total_price']
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                print(f"   ❌ Missing fields in cart item: {missing_fields}")
            else:
                print(f"   ✅ Cart item structure correct")
    else:
        print(f"   ❌ Cart API failed: {cart_response.status_code}")
    
    # Test 3: Test guest cart total limit
    print("\n3️⃣ Testing Guest Cart Total Limit...")
    
    # Clear cart first
    session.delete(f"{BASE_URL}/cart/clear/")
    
    # Try to add expensive item
    expensive_data = {
        "product_type": "tour",
        "product_id": "362092e7-891d-411e-a29e-37024405bc07",
        "variant_id": "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc",
        "quantity": 100,  # Large quantity to exceed $1000 limit
        "booking_data": {
            "schedule_id": "6b40dbdd-b545-4969-adfc-4ca3145767f6",
            "participants": {
                "adult": 100,
                "child": 0,
                "infant": 0
            }
        }
    }
    
    response = session.post(f"{BASE_URL}/cart/add/", json=expensive_data)
    print(f"   Expensive item: {response.status_code}")
    
    if response.status_code == 400:
        error_data = response.json()
        if error_data.get('code') == 'GUEST_LIMIT_EXCEEDED':
            print(f"   ✅ Guest cart total limit correctly enforced: {error_data.get('error')}")
        else:
            print(f"   ❌ Wrong error code: {error_data.get('code')}")
            print(f"   Error message: {error_data.get('error')}")
    else:
        print(f"   ❌ Guest cart total limit not enforced")
    
    # Test 4: Check tours API
    print("\n4️⃣ Testing Tours API...")
    
    tours_response = session.get(f"{BASE_URL}/tours/")
    if tours_response.status_code == 200:
        tours_data = tours_response.json()
        print(f"   ✅ Tours API working")
        print(f"   Tours count: {len(tours_data)}")
    else:
        print(f"   ❌ Tours API failed: {tours_response.status_code}")
    
    print("\n🎉 Frontend integration test completed!")
    return True

if __name__ == "__main__":
    test_frontend_integration() 