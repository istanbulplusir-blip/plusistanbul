#!/usr/bin/env python3
"""
Simple test to check data consistency between frontend and backend
Tests the option names fix we implemented
"""

import requests
import json
import time

def test_option_names_consistency():
    """Test if option names are properly passed from frontend to backend"""
    base_url = "http://localhost:8000"

    print("🧪 Testing Option Names Consistency...")

    try:
        # Step 1: Get tours list
        print("\n1️⃣ Getting tours list...")
        response = requests.get(f"{base_url}/api/v1/tours/")
        if response.status_code != 200:
            print(f"❌ Failed to get tours: {response.status_code}")
            return False

        tours = response.json()
        if not tours:
            print("❌ No tours found")
            return False

        tour = tours[0]
        print(f"✅ Found tour: {tour.get('title', 'Unknown')}")

        # Step 2: Get tour details
        print("\n2️⃣ Getting tour details...")
        tour_slug = tour['slug']
        print(f"Tour slug: {tour_slug}")
        response = requests.get(f"{base_url}/api/v1/tours/{tour_slug}/")
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response content: {response.text[:200]}")
            return False

        tour_detail = response.json()
        options = tour_detail.get('options', [])
        variants = tour_detail.get('variants', [])

        if not options:
            print("⚠️ No options found for this tour")
            return True  # Not a failure, just no options to test

        if not variants:
            print("❌ No variants found for this tour")
            return False

        print(f"✅ Found {len(options)} options and {len(variants)} variants")

        # Step 3: Test cart addition with options
        print("\n3️⃣ Testing cart addition with options...")

        # Select first option
        option = options[0]
        variant = variants[0]

        cart_data = {
            'product_type': 'tour',
            'product_id': tour_detail['id'],
            'variant_id': variant['id'],
            'variant_name': variant.get('name', ''),
            'quantity': 2,
            'unit_price': float(variant.get('base_price', 0)),
            'selected_options': [{
                'option_id': option['id'],
                'name': option.get('name', f'Option {option["id"][:8]}'),
                'price': option.get('price', 0),
                'quantity': 1
            }],
            'booking_data': {
                'schedule_id': tour_detail.get('schedules', [{}])[0].get('id'),
                'participants': {
                    'adult': 2,
                    'child': 0,
                    'infant': 0
                },
                'special_requests': 'Test for option names consistency'
            }
        }

        print(f"📤 Sending option: {cart_data['selected_options'][0]['name']}")

        response = requests.post(f"{base_url}/api/v1/cart/add/", json=cart_data)

        if response.status_code not in [200, 201]:
            print(f"❌ Failed to add to cart: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        cart_result = response.json()
        cart_item = cart_result.get('cart_item', {})

        print("✅ Successfully added to cart")
        # Step 4: Check if option names are preserved
        print("\n4️⃣ Checking option names consistency...")

        cart_options = cart_item.get('selected_options', [])
        if not cart_options:
            print("❌ No options in cart item")
            return False

        cart_option = cart_options[0]
        original_name = cart_data['selected_options'][0]['name']
        cart_name = cart_option.get('name', '')

        print(f"📊 Original option name: '{original_name}'")
        print(f"📊 Cart option name: '{cart_name}'")

        if original_name == cart_name:
            print("✅ Option names are consistent!")
            return True
        else:
            print("❌ Option names are inconsistent!")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_order_creation_consistency():
    """Test if option names are preserved when creating orders"""
    base_url = "http://localhost:8000"

    print("\n🧪 Testing Order Creation Consistency...")

    try:
        # First create a cart item
        success = test_option_names_consistency()
        if not success:
            print("❌ Cart consistency test failed, skipping order test")
            return False

        # Get cart
        response = requests.get(f"{base_url}/api/v1/cart/")
        if response.status_code != 200:
            print(f"❌ Failed to get cart: {response.status_code}")
            return False

        cart_data = response.json()
        cart_id = cart_data.get('id')
        items = cart_data.get('items', [])

        if not items:
            print("❌ No items in cart")
            return False

        item = items[0]
        cart_option_name = item.get('selected_options', [{}])[0].get('name', '')

        print(f"📊 Cart option name: '{cart_option_name}'")

        # Create order
        print("\n5️⃣ Creating order...")
        order_data = {
            'cart_id': cart_id,
            'special_requests': 'Test order for consistency'
        }

        response = requests.post(f"{base_url}/api/v1/orders/create/", json=order_data)

        if response.status_code not in [200, 201]:
            print(f"❌ Failed to create order: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        order_result = response.json()
        order_number = order_result.get('order_number')

        print(f"✅ Order created: {order_number}")

        # Get order details
        print("\n6️⃣ Getting order details...")
        response = requests.get(f"{base_url}/api/v1/orders/{order_number}/")

        if response.status_code != 200:
            print(f"❌ Failed to get order details: {response.status_code}")
            return False

        order_detail = response.json()
        order_items = order_detail.get('items', [])

        if not order_items:
            print("❌ No items in order")
            return False

        order_item = order_items[0]
        order_options = order_item.get('selected_options', [])
        order_option_name = order_options[0].get('name', '') if order_options else ''

        print(f"📊 Order option name: '{order_option_name}'")

        # Compare names
        if cart_option_name == order_option_name:
            print("✅ Option names are consistent from cart to order!")
            return True
        else:
            print("❌ Option names are inconsistent between cart and order!")
            print(f"   Cart: '{cart_option_name}'")
            print(f"   Order: '{order_option_name}'")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Data Consistency Tests...\n")

    # Test 1: Cart option names consistency
    test1_success = test_option_names_consistency()

    # Test 2: Order creation consistency
    test2_success = test_order_creation_consistency()

    # Results
    print(f"\n" + "="*60)
    print("📊 Test Results:")
    print(f"   Cart Option Names: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Order Creation Consistency: {'✅ PASS' if test2_success else '❌ FAIL'}")
    print("="*60)

    if test1_success and test2_success:
        print("\n🎉 All tests passed! Data consistency is working correctly.")
        return True
    else:
        print("\n⚠️ Some tests failed. There may be data consistency issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
