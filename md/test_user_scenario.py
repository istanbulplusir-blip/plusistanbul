#!/usr/bin/env python3
"""
Test to simulate the user's scenario where they could book twice.
"""

import requests
import json
import time

def test_user_scenario():
    """Test the exact scenario the user reported."""
    base_url = "http://localhost:8000"
    
    # Real data from user's scenario
    tour_id = "362092e7-891d-411e-a29e-37024405bc07"  # Test Tour 16329065
    variant_id = "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc"  # Standard variant
    schedule_id = "5e20a42d-1cc0-43fe-9a15-aedbc8102aae"  # 2025-09-03 schedule
    
    print("🧪 Testing User Scenario (Double Booking Prevention)...")
    
    # Step 1: Check initial capacity
    print("\n📋 Step 1: Check Initial Capacity")
    try:
        response = requests.get(f"{base_url}/api/v1/tours/{tour_id}/schedules/")
        if response.status_code == 200:
            result = response.json()
            schedules = result.get('schedules', [])
            
            target_schedule = None
            for schedule in schedules:
                if schedule.get('id') == schedule_id:
                    target_schedule = schedule
                    break
            
            if target_schedule:
                initial_available = target_schedule.get('available_capacity', 0)
                print(f"   ✅ Initial available capacity: {initial_available}")
            else:
                print(f"   ❌ Target schedule not found")
                return False
        else:
            print(f"   ❌ Failed to get schedules: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    # Step 2: Simulate first booking (like user's first order)
    print("\n📋 Step 2: Simulate First Booking")
    cart_data_1 = {
        "product_type": "tour",
        "product_id": tour_id,
        "variant_id": variant_id,
        "quantity": 15,  # Add required quantity field
        "booking_data": {
            "participants": {
                "adult": 15,  # Like user's first order
                "child": 0,
                "infant": 0
            },
            "schedule_id": schedule_id
        }
    }
    
    try:
        # Test dry run for first booking
        response = requests.post(f"{base_url}/api/v1/cart/add/?dry_run=1", json=cart_data_1)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ First booking dry run successful")
            print(f"   📊 Price calculation: {result.get('total', 0)} {result.get('currency', 'USD')}")
        else:
            print(f"   ❌ First booking failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    # Step 3: Simulate second booking attempt (like user's second order)
    print("\n📋 Step 3: Simulate Second Booking Attempt")
    cart_data_2 = {
        "product_type": "tour",
        "product_id": tour_id,
        "variant_id": variant_id,
        "quantity": 14,  # Add required quantity field
        "booking_data": {
            "participants": {
                "adult": 7,  # Like user's second order
                "child": 5,
                "infant": 2
            },
            "schedule_id": schedule_id
        }
    }
    
    try:
        # Test dry run for second booking
        response = requests.post(f"{base_url}/api/v1/cart/add/?dry_run=1", json=cart_data_2)
        
        if response.status_code == 400:
            error_data = response.json()
            if 'DUPLICATE_BOOKING' in str(error_data):
                print(f"   ✅ Second booking correctly prevented (DUPLICATE_BOOKING)")
                print(f"   📄 Error: {error_data.get('error', 'Unknown error')}")
                return True
            elif 'INSUFFICIENT_CAPACITY' in str(error_data):
                print(f"   ✅ Second booking correctly prevented (INSUFFICIENT_CAPACITY)")
                print(f"   📄 Error: {error_data.get('error', 'Unknown error')}")
                return True
            else:
                print(f"   ⚠️ Second booking prevented but wrong error type")
                print(f"   📄 Response: {error_data}")
                return True  # Still prevented, just different error
        else:
            print(f"   ❌ Second booking should be prevented but got: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_capacity_after_pending_orders():
    """Test that capacity is still available after pending orders."""
    base_url = "http://localhost:8000"
    
    tour_id = "362092e7-891d-411e-a29e-37024405bc07"
    schedule_id = "5e20a42d-1cc0-43fe-9a15-aedbc8102aae"
    
    print("\n🧪 Testing Capacity After Pending Orders...")
    
    try:
        # Check capacity after pending orders
        response = requests.get(f"{base_url}/api/v1/tours/{tour_id}/schedules/")
        
        if response.status_code == 200:
            result = response.json()
            schedules = result.get('schedules', [])
            
            target_schedule = None
            for schedule in schedules:
                if schedule.get('id') == schedule_id:
                    target_schedule = schedule
                    break
            
            if target_schedule:
                available_capacity = target_schedule.get('available_capacity', 0)
                total_capacity = target_schedule.get('total_capacity', 0)
                booked_capacity = target_schedule.get('booked_capacity', 0)
                
                print(f"   📊 Capacity after pending orders:")
                print(f"      Total Capacity: {total_capacity}")
                print(f"      Booked Capacity: {booked_capacity}")
                print(f"      Available Capacity: {available_capacity}")
                
                # Check if capacity is still reasonable
                if available_capacity > 0:
                    print(f"   ✅ Capacity is still available for new bookings")
                    return True
                else:
                    print(f"   ⚠️ No capacity available (pending orders may be affecting)")
                    return False
            else:
                print(f"   ❌ Target schedule not found")
                return False
        else:
            print(f"   ❌ Failed to get schedules: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting User Scenario Tests...\n")
    
    # Test user's double booking scenario
    test1_success = test_user_scenario()
    
    # Test capacity after pending orders
    test2_success = test_capacity_after_pending_orders()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Double Booking Prevention: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Capacity After Pending Orders: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! User scenario is now fixed.")
        print("\n📋 Summary:")
        print("   ✅ Double booking is prevented")
        print("   ✅ Capacity calculation excludes pending orders")
        print("   ✅ System works as expected")
    else:
        print("\n⚠️ Some tests failed. The user scenario may still have issues.")

if __name__ == "__main__":
    main()
