#!/usr/bin/env python3
"""
Test the full Tour X booking flow from frontend to backend
"""

import requests
import json
import time

def test_tour_x_booking_flow():
    """Test the complete Tour X booking flow"""

    base_url = 'http://localhost:8000/api/v1'
    frontend_url = 'http://localhost:3000'

    print("=== TOUR X BOOKING FLOW TEST ===")

    # Step 1: Get Tour X data
    print("\n1. Getting Tour X data...")
    try:
        response = requests.get(f'{base_url}/tours/tour-x/')
        if response.status_code == 200:
            tour_data = response.json()
            print(f"✅ Tour X found: {tour_data.get('title')}")

            # Get first schedule and variant
            schedules = tour_data.get('schedules', [])
            variants = tour_data.get('variants', [])

            if schedules and variants:
                schedule = schedules[0]
                variant = variants[0]

                print(f"   Schedule: {schedule.get('id')} - {schedule.get('start_date')}")
                print(f"   Variant: {variant.get('id')} - {variant.get('name')}")

                # Step 2: Test capacity check
                print("\n2. Testing capacity check...")
                capacity_data = {
                    'product_type': 'tour',
                    'product_id': tour_data['id'],
                    'variant_id': variant['id'],
                    'booking_data': {
                        'schedule_id': schedule['id'],
                        'participants': {
                            'adult': 1,
                            'child': 1,
                            'infant': 0
                        }
                    }
                }

                capacity_response = requests.post(f'{base_url}/cart/check-capacity/', json=capacity_data)
                if capacity_response.status_code == 200:
                    capacity_result = capacity_response.json()
                    print(f"✅ Capacity check: {capacity_result}")
                else:
                    print(f"❌ Capacity check failed: {capacity_response.status_code} - {capacity_response.text}")
                    return False

                # Step 3: Test add to cart
                print("\n3. Testing add to cart...")
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

                cart_response = requests.post(f'{base_url}/cart/add/', json=cart_data)
                print(f"Add to cart status: {cart_response.status_code}")

                if cart_response.status_code == 201:
                    cart_result = cart_response.json()
                    print("✅ Item added to cart successfully!"                    print(f"   Cart item ID: {cart_result.get('cart_item', {}).get('id')}")
                    return True
                else:
                    print(f"❌ Add to cart failed: {cart_response.status_code}")
                    print(f"   Response: {cart_response.text}")
                    return False

            else:
                print("❌ No schedules or variants available")
                return False
        else:
            print(f"❌ Tour X not found: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure backend is running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tour_x_booking_flow()
    if success:
        print("\n🎉 TOUR X BOOKING FLOW TEST PASSED!")
    else:
        print("\n❌ TOUR X BOOKING FLOW TEST FAILED!")
        exit(1)
