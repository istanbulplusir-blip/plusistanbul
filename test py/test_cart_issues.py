#!/usr/bin/env python3
"""
Test script to debug cart issues:
1. Adding items with options
2. Updating cart items
3. Cart persistence after refresh
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login to get token"""
    login_data = {
        "username": "testuser@example.com",
        "password": "123789"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        return data.get('tokens', {}).get('access')
    else:
        print(f"Login failed: {response.text}")
        return None

def test_add_item_with_options(token):
    """Test adding a tour item with options"""
    print("\n=== Testing Add Item with Options ===")
    
    # Get a tour first
    tours_response = requests.get(f"{BASE_URL}/tours/")
    if tours_response.status_code != 200:
        print(f"Failed to get tours: {tours_response.text}")
        return
    
    tours = tours_response.json()
    if not tours:
        print("No tours available")
        return
    
    tour = tours[0]
    print(f"Using tour: {tour['title']}")
    
    # Get tour details to see options
    tour_detail_response = requests.get(f"{BASE_URL}/tours/{tour['slug']}/")
    if tour_detail_response.status_code != 200:
        print(f"Failed to get tour details: {tour_detail_response.text}")
        return
    
    tour_detail = tour_detail_response.json()
    print(f"Tour has {len(tour_detail.get('options', []))} options")
    
    # Prepare cart data with options
    cart_data = {
        "product_type": "tour",
        "product_id": tour['id'],
        "variant_id": tour_detail['variants'][0]['id'] if tour_detail['variants'] else None,
        "quantity": 2,  # 1 adult + 1 child
        "selected_options": [],
        "booking_data": {
            "schedule_id": tour_detail['schedules'][0]['id'] if tour_detail['schedules'] else None,
            "participants": {
                "adult": 1,
                "child": 1,
                "infant": 0
            },
            "special_requests": "Test booking with options"
        }
    }
    
    # Add options if available
    if tour_detail.get('options'):
        for option in tour_detail['options'][:2]:  # Add first 2 options
            cart_data["selected_options"].append({
                "option_id": option['id'],
                "quantity": 1,
                "price": option['price']
            })
    
    print(f"Cart data: {json.dumps(cart_data, indent=2)}")
    
    # Add to cart
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/cart/add/", json=cart_data, headers=headers)
    
    print(f"Add to cart response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Cart item ID: {result.get('cart_item', {}).get('id')}")
        return result.get('cart_item', {}).get('id')
    else:
        print(f"Failed to add to cart: {response.text}")
        return None

def test_update_cart_item(token, item_id):
    """Test updating a cart item"""
    print(f"\n=== Testing Update Cart Item {item_id} ===")
    
    update_data = {
        "quantity": 3,  # Increase quantity
        "selected_options": [
            {
                "option_id": "test-option-id",
                "quantity": 2,
                "price": 50.0
            }
        ],
        "booking_data": {
            "participants": {
                "adult": 2,
                "child": 1,
                "infant": 0
            },
            "special_requests": "Updated booking request"
        }
    }
    
    print(f"Update data: {json.dumps(update_data, indent=2)}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/cart/items/{item_id}/", json=update_data, headers=headers)
    
    print(f"Update response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Updated item: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Failed to update cart item: {response.text}")
        return False

def test_get_cart(token):
    """Test getting cart contents"""
    print("\n=== Testing Get Cart ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    
    print(f"Get cart response: {response.status_code}")
    if response.status_code == 200:
        cart = response.json()
        print(f"Cart contents: {json.dumps(cart, indent=2)}")
        return cart
    else:
        print(f"Failed to get cart: {response.text}")
        return None

def main():
    print("=== Cart Issues Test Script ===")
    
    # Test login
    token = test_login()
    if not token:
        print("Cannot proceed without authentication token")
        return
    
    # Test adding item with options
    item_id = test_add_item_with_options(token)
    if not item_id:
        print("Cannot proceed without cart item")
        return
    
    # Test getting cart
    test_get_cart(token)
    
    # Test updating cart item
    test_update_cart_item(token, item_id)
    
    # Test getting cart again
    test_get_cart(token)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 