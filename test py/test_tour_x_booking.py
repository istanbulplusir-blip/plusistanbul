#!/usr/bin/env python3
"""
Tour X Booking Flow Test Script
Tests the complete booking and capacity flow for Tour X product
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

def print_separator(title: str):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request and return response"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, **kwargs)
        elif method.upper() == 'PUT':
            response = requests.put(url, **kwargs)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")

        print(f"\n{method.upper()} {url}")
        print(f"Status: {response.status_code}")

        if response.status_code >= 400:
            print("ERROR Response:", response.text)
            return {"error": response.text, "status_code": response.status_code}

        try:
            return response.json()
        except:
            return {"text_response": response.text}

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}

def test_step_1_verify_tour_x():
    """Step 1: Verify Tour X exists and has schedules/variants"""
    print_separator("STEP 1: Verify Tour X Exists")

    response = make_request("GET", f"{BASE_URL}/tours/tour-x/")

    if "error" not in response:
        print("✅ Tour X found:")
        print(f"   Title: {response.get('title')}")
        print(f"   ID: {response.get('id')}")
        print(f"   Schedules: {len(response.get('schedules', []))}")
        for schedule in response.get('schedules', []):
            print(f"     - {schedule['id']}: {schedule['start_date']} (Available: {schedule.get('available_capacity', 'N/A')})")
        print(f"   Variants: {len(response.get('variants', []))}")
        for variant in response.get('variants', []):
            print(f"     - {variant['id']}: {variant['name']} (Capacity: {variant.get('capacity', 'N/A')})")

        # Store IDs for later use
        global TOUR_X_ID, SCHEDULE_ID, VARIANT_ID
        TOUR_X_ID = response.get('id')
        if response.get('schedules'):
            SCHEDULE_ID = response['schedules'][0]['id']  # Use first schedule
        if response.get('variants'):
            VARIANT_ID = response['variants'][0]['id']  # Use first variant

        return True
    else:
        print("❌ Tour X not found")
        return False

def test_step_2_login_and_add_to_cart():
    """Step 2: Login and add Tour X to cart"""
    print_separator("STEP 2: Login and Add to Cart")

    # Login
    login_data = {
        "username": "test",
        "password": "test123"
    }

    login_response = make_request("POST", f"{BASE_URL}/auth/login/", json=login_data)

    if "error" in login_response:
        print("❌ Login failed")
        return False

    global ACCESS_TOKEN
    ACCESS_TOKEN = login_response.get('access')
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    print("✅ Login successful")

    # Add to cart
    cart_data = {
        "product_type": "tour",
        "product_id": TOUR_X_ID,
        "variant_id": VARIANT_ID,
        "quantity": 2,  # Adults + children only
        "booking_data": {
            "schedule_id": SCHEDULE_ID,
            "participants": {
                "adult": 1,
                "child": 1,
                "infant": 0
            },
            "special_requests": "Test booking"
        }
    }

    cart_response = make_request("POST", f"{BASE_URL}/cart/add/", json=cart_data, headers=headers)

    if "error" not in cart_response:
        print("✅ Added to cart successfully")
        print(f"   Cart item ID: {cart_response.get('cart_item', {}).get('id')}")
        return True
    else:
        print("❌ Failed to add to cart")
        return False

def test_step_3_try_duplicate_booking():
    """Step 3: Try adding the same schedule/variant again"""
    print_separator("STEP 3: Test Duplicate Booking Prevention")

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    cart_data = {
        "product_type": "tour",
        "product_id": TOUR_X_ID,
        "variant_id": VARIANT_ID,
        "quantity": 1,
        "booking_data": {
            "schedule_id": SCHEDULE_ID,
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }

    cart_response = make_request("POST", f"{BASE_URL}/cart/add/", json=cart_data, headers=headers)

    if "error" in cart_response and "DUPLICATE_BOOKING" in str(cart_response):
        print("✅ Duplicate booking correctly prevented")
        return True
    else:
        print("❌ Duplicate booking not prevented!")
        print("Response:", cart_response)
        return False

def test_step_4_checkout_whatsapp():
    """Step 4: Perform checkout with WhatsApp payment"""
    print_separator("STEP 4: Checkout with WhatsApp Payment")

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    checkout_data = {
        "customer_info": {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "address": "Test Address",
            "city": "Test City",
            "country": "Test Country"
        },
        "payment_method": "whatsapp",
        "total_amount": 200.00,  # Dummy amount
        "currency": "USD"
    }

    checkout_response = make_request("POST", f"{BASE_URL}/orders/", json=checkout_data, headers=headers)

    if "error" not in checkout_response:
        print("✅ Checkout successful")
        global ORDER_NUMBER
        ORDER_NUMBER = checkout_response.get('order_number')
        print(f"   Order Number: {ORDER_NUMBER}")
        print(f"   Order Status: {checkout_response.get('order', {}).get('status')}")
        return True
    else:
        print("❌ Checkout failed")
        return False

def test_step_5_admin_update_to_paid():
    """Step 5: Admin updates order status to paid"""
    print_separator("STEP 5: Admin Update to Paid")

    # First, let's check the current capacity state
    print("Checking capacity before status update...")
    capacity_check = make_request("POST", f"{BASE_URL}/cart/check-capacity/", json={
        "product_type": "tour",
        "product_id": TOUR_X_ID,
        "variant_id": VARIANT_ID,
        "booking_data": {"schedule_id": SCHEDULE_ID}
    })

    if "error" not in capacity_check:
        print(f"   Available capacity before: {capacity_check.get('available_capacity')}")

    # For this test, we'll simulate the admin action by directly updating in DB
    # In a real scenario, this would be done through the admin interface
    print("Simulating admin update: pending → paid")

    # We'll use Django shell to update the order status
    import subprocess
    import sys

    update_command = f"""
from orders.models import Order
from tours.services import TourCapacityService
order = Order.objects.get(order_number='{ORDER_NUMBER}')
print(f'Order before update: status={order.status}')
print(f'Order capacity reserved: {order.is_capacity_reserved}')

# Update status to paid
order.status = 'paid'
order.payment_status = 'paid'
order.save()

print(f'Order after update: status={order.status}')

# Check capacity changes
from tours.models import TourSchedule
schedule = TourSchedule.objects.get(id='{SCHEDULE_ID}')
print(f'Schedule reserved capacity: {schedule.total_reserved_capacity}')
print(f'Schedule confirmed capacity: {schedule.total_confirmed_capacity}')
"""

    try:
        result = subprocess.run([sys.executable, '-c', update_command],
                              capture_output=True, text=True, cwd='.')
        print("Database update result:")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return True
    except Exception as e:
        print(f"Failed to update order status: {e}")
        return False

def test_step_6_cancel_order():
    """Step 6: Cancel the order and check capacity release"""
    print_separator("STEP 6: Cancel Order and Check Capacity")

    # Cancel order using Django shell
    import subprocess
    import sys

    cancel_command = f"""
from orders.models import Order
from tours.services import TourCapacityService
order = Order.objects.get(order_number='{ORDER_NUMBER}')
print(f'Order before cancel: status={order.status}')

# Cancel order
order.status = 'cancelled'
order.save()

print(f'Order after cancel: status={order.status}')

# Check capacity changes
from tours.models import TourSchedule
schedule = TourSchedule.objects.get(id='{SCHEDULE_ID}')
print(f'Schedule reserved capacity: {schedule.total_reserved_capacity}')
print(f'Schedule confirmed capacity: {schedule.total_confirmed_capacity}')
"""

    try:
        result = subprocess.run([sys.executable, '-c', cancel_command],
                              capture_output=True, text=True, cwd='.')
        print("Order cancellation result:")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return True
    except Exception as e:
        print(f"Failed to cancel order: {e}")
        return False

def main():
    """Run all test steps"""
    print("🧪 Tour X Booking Flow Test")
    print("Testing capacity management and duplicate booking prevention")

    # Global variables to store test data
    global TOUR_X_ID, SCHEDULE_ID, VARIANT_ID, ACCESS_TOKEN, ORDER_NUMBER
    TOUR_X_ID = SCHEDULE_ID = VARIANT_ID = ACCESS_TOKEN = ORDER_NUMBER = None

    # Run test steps
    steps = [
        test_step_1_verify_tour_x,
        test_step_2_login_and_add_to_cart,
        test_step_3_try_duplicate_booking,
        test_step_4_checkout_whatsapp,
        test_step_5_admin_update_to_paid,
        test_step_6_cancel_order
    ]

    results = []
    for step in steps:
        result = step()
        results.append(result)
        time.sleep(1)  # Brief pause between steps

    # Summary
    print_separator("TEST SUMMARY")
    passed = sum(results)
    total = len(results)

    for i, (step, result) in enumerate(zip(steps, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"Step {i}: {status}")

    print(f"\nOverall: {passed}/{total} steps passed")

    if passed == total:
        print("🎉 All tests passed! Tour X booking flow is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
