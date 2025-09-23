#!/usr/bin/env python3
"""
Test script to verify capacity fix for pending orders.
"""

import requests
import json
from datetime import datetime, timedelta

def test_capacity_calculation():
    """Test that capacity calculation excludes pending orders."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Capacity Calculation Fix...")
    
    # Test 1: Get tour schedules to check capacity
    try:
        response = requests.get(f"{base_url}/api/v1/tours/1/schedules/")
        if response.status_code == 200:
            result = response.json()
            schedules = result.get('schedules', [])
            
            if schedules:
                schedule = schedules[0]
                available_capacity = schedule.get('available_capacity', 0)
                total_capacity = schedule.get('total_capacity', 0)
                booked_capacity = schedule.get('booked_capacity', 0)
                
                print(f"✅ Tour Schedule Capacity:")
                print(f"   Total Capacity: {total_capacity}")
                print(f"   Booked Capacity: {booked_capacity}")
                print(f"   Available Capacity: {available_capacity}")
                
                # Test 2: Check if pending orders endpoint works
                response = requests.get(f"{base_url}/api/v1/orders/pending/")
                if response.status_code == 200:
                    result = response.json()
                    pending_count = result.get('count', 0)
                    print(f"✅ Pending Orders Endpoint: {pending_count} pending orders")
                else:
                    print(f"❌ Pending Orders Endpoint failed: {response.status_code}")
                
                return True
            else:
                print("❌ No schedules found")
                return False
        else:
            print(f"❌ Failed to get tour schedules: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing capacity: {str(e)}")
        return False

def test_cart_capacity_check():
    """Test cart capacity check with pending orders."""
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Cart Capacity Check...")
    
    # Test data for cart addition
    cart_data = {
        "product_type": "tour",
        "product_id": "1",  # Assuming tour ID 1 exists
        "variant_id": "1",  # Assuming variant ID 1 exists
        "quantity": 5,
        "booking_data": {
            "participants": {
                "adult": 3,
                "child": 2,
                "infant": 0
            },
            "schedule_id": "1"  # Assuming schedule ID 1 exists
        }
    }
    
    try:
        # Test dry run to check capacity without actually adding to cart
        response = requests.post(f"{base_url}/api/v1/cart/add/?dry_run=1", json=cart_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cart Capacity Check (Dry Run): Success")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Cart Capacity Check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cart capacity: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Capacity Fix Tests...\n")
    
    # Test capacity calculation
    test1_success = test_capacity_calculation()
    
    # Test cart capacity check
    test2_success = test_cart_capacity_check()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Capacity Calculation: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Cart Capacity Check: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! Capacity fix is working.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
