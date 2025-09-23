#!/usr/bin/env python
"""
Test script to verify cart item update endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_cart_item_update():
    """Test cart item update functionality."""
    print("🧪 Testing Cart Item Update Endpoints")
    print("=" * 50)
    
    session = requests.Session()
    
    # Step 1: Login
    print("📝 Step 1: Login...")
    login_data = {
        'username': 'testuser_simple',
        'password': 'testpass123'
    }
    
    response = session.post(
        f"{BASE_URL}/auth/login/",
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    data = response.json()
    token = data.get('tokens', {}).get('access')
    if not token:
        print("❌ No access token in response")
        return False
    
    session.headers.update({'Authorization': f'Bearer {token}'})
    print("✅ Login successful")
    
    # Step 2: Add item to cart if empty
    print("\n📝 Step 2: Add item to cart...")
    response = session.get(f"{BASE_URL}/cart/")
    
    if response.status_code != 200:
        print(f"❌ Failed to get cart: {response.status_code}")
        return False
    
    cart_data = response.json()
    items = cart_data.get('items', [])
    
    if not items:
        print("   Cart is empty, adding test item...")
        
        # Get a tour to add
        tours_response = session.get(f"{BASE_URL}/tours/tours/")
        if tours_response.status_code != 200:
            print("❌ Failed to get tours")
            return False
        
        tours_data = tours_response.json()
        if not tours_data:
            print("❌ No tours available")
            return False
        
        tour = tours_data[0]
        
        # Add tour to cart
        add_data = {
            'product_type': 'tour',
            'product_id': str(tour['id']),
            'quantity': 1,
            'selected_options': [],
            'booking_data': {}
        }
        
        add_response = session.post(
            f"{BASE_URL}/cart/add/",
            json=add_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if add_response.status_code != 201:
            print(f"❌ Failed to add item: {add_response.status_code}")
            return False
        
        print("✅ Item added to cart")
        
        # Get updated cart
        response = session.get(f"{BASE_URL}/cart/")
        cart_data = response.json()
        items = cart_data.get('items', [])
    
    cart_item = items[0]
    item_id = cart_item['id']
    current_quantity = cart_item['quantity']
    
    print(f"✅ Found cart item: {item_id} with quantity: {current_quantity}")
    
    # Step 3: Test PATCH method on /items/{id}/update/
    print(f"\n📝 Step 3: Test PATCH /items/{item_id}/update/")
    update_data = {
        'quantity': current_quantity + 1
    }
    
    response = session.patch(
        f"{BASE_URL}/cart/items/{item_id}/update/",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ PATCH /items/{id}/update/ works!")
        result = response.json()
        print(f"   Updated quantity: {result['cart_item']['quantity']}")
    else:
        print(f"❌ PATCH failed: {response.text}")
    
    # Step 4: Test PUT method on /items/{id}/update/
    print(f"\n📝 Step 4: Test PUT /items/{item_id}/update/")
    update_data = {
        'quantity': current_quantity + 2
    }
    
    response = session.put(
        f"{BASE_URL}/cart/items/{item_id}/update/",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ PUT /items/{id}/update/ works!")
        result = response.json()
        print(f"   Updated quantity: {result['cart_item']['quantity']}")
    else:
        print(f"❌ PUT failed: {response.text}")
    
    # Step 5: Test PATCH method on /items/{id}/
    print(f"\n📝 Step 5: Test PATCH /items/{item_id}/")
    update_data = {
        'quantity': current_quantity + 3
    }
    
    response = session.patch(
        f"{BASE_URL}/cart/items/{item_id}/",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ PATCH /items/{id}/ works!")
        result = response.json()
        print(f"   Updated quantity: {result['cart_item']['quantity']}")
    else:
        print(f"❌ PATCH failed: {response.text}")
    
    # Step 6: Test PUT method on /items/{id}/
    print(f"\n📝 Step 6: Test PUT /items/{item_id}/")
    update_data = {
        'quantity': current_quantity + 4
    }
    
    response = session.put(
        f"{BASE_URL}/cart/items/{item_id}/",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ PUT /items/{id}/ works!")
        result = response.json()
        print(f"   Updated quantity: {result['cart_item']['quantity']}")
    else:
        print(f"❌ PUT failed: {response.text}")
    
    # Step 7: Test partial update with only selected_options
    print(f"\n📝 Step 7: Test partial update with only selected_options")
    update_data = {
        'selected_options': [{'name': 'Test Option', 'price': 10.00}]
    }
    
    response = session.patch(
        f"{BASE_URL}/cart/items/{item_id}/update/",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Partial update works!")
        result = response.json()
        print(f"   Updated options: {result['cart_item']['selected_options']}")
    else:
        print(f"❌ Partial update failed: {response.text}")
    
    print("\n🎉 Cart item update testing completed!")
    return True

if __name__ == "__main__":
    test_cart_item_update() 