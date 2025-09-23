#!/usr/bin/env python3
"""
Debug script to check cart response
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login to get token"""
    login_data = {
        "username": "test@example.com",
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

def debug_cart_response(token):
    """Debug what the cart endpoint returns"""
    print("\n=== Debug Cart Response ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    
    print(f"Cart response status: {response.status_code}")
    print(f"Cart response headers: {dict(response.headers)}")
    print(f"Cart response content length: {len(response.content)}")
    
    if response.status_code == 200:
        try:
            cart_data = response.json()
            print(f"Cart response JSON: {json.dumps(cart_data, indent=2)}")
            
            # Check if items exist
            items = cart_data.get('items', [])
            print(f"Number of items in cart: {len(items)}")
            
            if items:
                print("First item details:")
                print(json.dumps(items[0], indent=2))
            else:
                print("Cart is empty!")
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw response: {response.text}")
    else:
        print(f"Failed to get cart: {response.text}")

def main():
    print("=== Cart Response Debug ===")
    
    # Test login
    token = test_login()
    if not token:
        print("Cannot proceed without authentication token")
        return
    
    # Debug cart response
    debug_cart_response(token)

if __name__ == "__main__":
    main() 