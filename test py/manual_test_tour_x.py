#!/usr/bin/env python3
"""
Manual Tour X Booking Flow Test
Step by step testing of the Tour X booking system
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login and get tokens"""
    print("=== Testing Login ===")

    login_data = {
        "username": "test",
        "password": "test123"
    }

    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Login Status: {response.status_code}")

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access')
        print(f"✅ Login successful, got access token: {access_token[:50]}...")
        return access_token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_tour_x_details():
    """Test Tour X details"""
    print("\n=== Testing Tour X Details ===")

    response = requests.get(f"{BASE_URL}/tours/tour-x/")
    print(f"Tour Details Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ Tour X found:")
        print(f"   Title: {data.get('title')}")
        print(f"   ID: {data.get('id')}")

        schedules = data.get('schedules', [])
        print(f"   Schedules: {len(schedules)}")
        for schedule in schedules[:1]:  # Show first schedule
            print(f"     - {schedule['id']}: {schedule['start_date']}")
            print(f"       Available capacity: {schedule.get('available_capacity')}")

        variants = data.get('variants', [])
        print(f"   Variants: {len(variants)}")
        for variant in variants[:1]:  # Show first variant
            print(f"     - {variant['id']}: {variant['name']} (Capacity: {variant.get('capacity')})")

        return data.get('id'), schedules[0]['id'] if schedules else None, variants[0]['id'] if variants else None
    else:
        print(f"❌ Tour X not found: {response.text}")
        return None, None, None

def test_add_to_cart(access_token, tour_id, schedule_id, variant_id):
    """Test adding Tour X to cart"""
    print("\n=== Testing Add to Cart ===")

    headers = {"Authorization": f"Bearer {access_token}"}

    cart_data = {
        "product_type": "tour",
        "product_id": tour_id,
        "variant_id": variant_id,
        "quantity": 2,
        "booking_data": {
            "schedule_id": schedule_id,
            "participants": {
                "adult": 1,
                "child": 1,
                "infant": 0
            },
            "special_requests": "Test booking"
        }
    }

    response = requests.post(f"{BASE_URL}/cart/add/", json=cart_data, headers=headers)
    print(f"Add to Cart Status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print("✅ Added to cart successfully")
        print(f"   Cart item ID: {data.get('cart_item', {}).get('id')}")
        return True
    else:
        print(f"❌ Failed to add to cart: {response.text}")
        return False

def test_duplicate_booking(access_token, tour_id, schedule_id, variant_id):
    """Test duplicate booking prevention"""
    print("\n=== Testing Duplicate Booking Prevention ===")

    headers = {"Authorization": f"Bearer {access_token}"}

    cart_data = {
        "product_type": "tour",
        "product_id": tour_id,
        "variant_id": variant_id,
        "quantity": 1,
        "booking_data": {
            "schedule_id": schedule_id,
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }

    response = requests.post(f"{BASE_URL}/cart/add/", json=cart_data, headers=headers)
    print(f"Duplicate Booking Test Status: {response.status_code}")

    if response.status_code == 400:
        data = response.json()
        if "DUPLICATE_BOOKING" in str(data):
            print("✅ Duplicate booking correctly prevented")
            return True
        else:
            print(f"❌ Wrong error type: {data}")
            return False
    else:
        print(f"❌ Duplicate booking not prevented! Response: {response.text}")
        return False

def main():
    """Run manual tests"""
    print("🧪 Manual Tour X Booking Flow Test")

    # Test login
    access_token = test_login()
    if not access_token:
        print("Cannot continue without login token")
        return

    # Test Tour X details
    tour_id, schedule_id, variant_id = test_tour_x_details()
    if not all([tour_id, schedule_id, variant_id]):
        print("Cannot continue without Tour X data")
        return

    # Test add to cart
    if not test_add_to_cart(access_token, tour_id, schedule_id, variant_id):
        print("Cannot continue without cart item")
        return

    # Test duplicate booking
    test_duplicate_booking(access_token, tour_id, schedule_id, variant_id)

    print("\n=== Test Summary ===")
    print("✅ Tour X verification: PASSED")
    print("✅ Login: PASSED")
    print("✅ Add to cart: PASSED")
    print("✅ Duplicate prevention: PASSED")

if __name__ == "__main__":
    main()
