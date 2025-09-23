#!/usr/bin/env python3
"""
Test Tour X booking flow API
"""

import requests
import json
import sys

def test_tour_x():
    """Test Tour X API and booking flow"""
    base_url = 'http://localhost:8000/api/v1'

    print("=== Testing Tour X API ===")

    try:
        # Test Tour X endpoint
        response = requests.get(f'{base_url}/tours/tour-x/')
        print(f"Tour X API Status: {response.status_code}")

        if response.status_code == 200:
            tour_data = response.json()
            print(f"Tour ID: {tour_data.get('id')}")
            print(f"Tour Title: {tour_data.get('title')}")
            print(f"Schedules: {len(tour_data.get('schedules', []))}")
            print(f"Variants: {len(tour_data.get('variants', []))}")

            # Show first schedule and variant
            schedules = tour_data.get('schedules', [])
            variants = tour_data.get('variants', [])

            if schedules:
                schedule = schedules[0]
                print(f"\nFirst Schedule:")
                print(f"  ID: {schedule.get('id')}")
                print(f"  Date: {schedule.get('start_date')}")
                print(f"  Available: {schedule.get('available_capacity')}")

            if variants:
                variant = variants[0]
                print(f"\nFirst Variant:")
                print(f"  ID: {variant.get('id')}")
                print(f"  Name: {variant.get('name')}")
                print(f"  Capacity: {variant.get('capacity')}")

        else:
            print(f"Error: {response.text}")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure backend is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_add_to_cart():
    """Test add to cart functionality"""
    base_url = 'http://localhost:8000/api/v1'

    print("\n=== Testing Add to Cart ===")

    try:
        # First get tour data
        tour_response = requests.get(f'{base_url}/tours/tour-x/')
        if tour_response.status_code != 200:
            print("❌ Cannot get tour data")
            return False

        tour_data = tour_response.json()
        schedules = tour_data.get('schedules', [])
        variants = tour_data.get('variants', [])

        if not schedules or not variants:
            print("❌ No schedules or variants available")
            return False

        schedule = schedules[0]
        variant = variants[0]

        # Test add to cart
        cart_data = {
            'product_type': 'tour',
            'product_id': tour_data['id'],
            'variant_id': variant['id'],
            'quantity': 2,
            'booking_data': {
                'schedule_id': schedule['id'],
                'participants': {
                    'adult': 1,
                    'child': 1,
                    'infant': 0
                }
            }
        }

        print(f"Adding to cart: {json.dumps(cart_data, indent=2)}")

        response = requests.post(f'{base_url}/cart/add/', json=cart_data)
        print(f"Add to Cart Status: {response.status_code}")

        if response.status_code == 201:
            result = response.json()
            print("✅ Item added to cart successfully")
            print(f"Cart item ID: {result.get('cart_item', {}).get('id')}")
            return True
        else:
            print(f"❌ Add to cart failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success1 = test_tour_x()
    if success1:
        success2 = test_add_to_cart()
        if success2:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Add to cart test failed")
            sys.exit(1)
    else:
        print("\n❌ Tour X test failed")
        sys.exit(1)
