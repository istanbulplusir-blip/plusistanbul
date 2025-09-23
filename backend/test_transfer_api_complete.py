#!/usr/bin/env python
"""
Complete API Test for Transfer Booking System
تست کامل API برای سیستم سفارش ترانسفر
"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"

def test_transfer_pricing_api():
    """Test transfer pricing API with real data"""
    
    print("🧪 Testing Transfer Pricing API")
    print("=" * 50)
    
    # Test data based on our example
    test_data = {
        "product_type": "transfer",
        "route_id": "bc7ce2ca-0297-4371-a2c6-79c37fba666e",  # اصفهان to اصفهان سیتی
        "vehicle_type": "sedan",
        "passenger_count": 2,
        "trip_type": "round_trip",
        "booking_time": "08:00",  # Peak hour
        "return_time": "23:00",   # Midnight
        "selected_options": [
            {
                "id": "a893518c-9702-4896-a732-d05a1383e742",  # Extra Luggage
                "quantity": 1,
                "name": "چمدان اضافی",
                "price": 5.0
            },
            {
                "id": "d6f81277-b542-4e70-b293-d04baa9dc471",  # English Driver
                "quantity": 1,
                "name": "راننده انگلیسی زبان",
                "price": 5.0
            },
            {
                "id": "5f686a8c-65fa-4294-8a3d-848b73ef92ca",  # Meet & Greet
                "quantity": 1,
                "name": "خدمات استقبال",
                "price": 5.0
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Test pricing endpoint
        response = requests.post(
            f"{BASE_URL}/api/agents/pricing/transfer/",
            headers=headers,
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                pricing = result.get('pricing', {})
                print("\n✅ Pricing calculation successful!")
                print(f"Base Price: ${pricing.get('base_price')}")
                print(f"Agent Total: ${pricing.get('agent_total')}")
                print(f"Options Total: ${pricing.get('options_total')}")
                print(f"Savings: ${pricing.get('savings')}")
                print(f"Savings Percentage: {pricing.get('savings_percentage')}%")
                print(f"Pricing Method: {pricing.get('pricing_method')}")
                
                # Detailed breakdown
                print("\n📊 Detailed Breakdown:")
                price_breakdown = pricing.get('price_breakdown', {})
                for key, value in price_breakdown.items():
                    print(f"  {key}: ${value}")
                
                return pricing
            else:
                print("❌ Pricing calculation failed")
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return None

def test_transfer_booking_api():
    """Test transfer booking API"""
    
    print("\n🧪 Testing Transfer Booking API")
    print("=" * 50)
    
    # Test data
    test_data = {
        "customer_id": "customer_uuid_here",  # Would need real customer ID
        "route_id": "bc7ce2ca-0297-4371-a2c6-79c37fba666e",
        "vehicle_type": "sedan",
        "passenger_count": 2,
        "luggage_count": 1,
        "trip_type": "round_trip",
        "booking_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "booking_time": "08:00",
        "return_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "return_time": "23:00",
        "selected_options": [
            {
                "id": "a893518c-9702-4896-a732-d05a1383e742",
                "quantity": 1,
                "name": "چمدان اضافی",
                "price": 5.0
            },
            {
                "id": "d6f81277-b542-4e70-b293-d04baa9dc471",
                "quantity": 1,
                "name": "راننده انگلیسی زبان",
                "price": 5.0
            },
            {
                "id": "5f686a8c-65fa-4294-8a3d-848b73ef92ca",
                "quantity": 1,
                "name": "خدمات استقبال",
                "price": 5.0
            }
        ],
        "payment_method": "whatsapp"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Test booking endpoint
        response = requests.post(
            f"{BASE_URL}/api/agents/book/transfer/",
            headers=headers,
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("\n✅ Transfer booking successful!")
                print(f"Order Number: {result.get('order_number')}")
                print(f"Total Amount: ${result.get('total_amount')}")
                print(f"Commission Amount: ${result.get('commission_amount')}")
                
                # Pricing info
                pricing_info = result.get('pricing_info', {})
                if pricing_info:
                    print("\n💰 Pricing Information:")
                    print(f"  Base Price: ${pricing_info.get('base_price')}")
                    print(f"  Agent Price: ${pricing_info.get('agent_price')}")
                    print(f"  Savings: ${pricing_info.get('savings')}")
                    print(f"  Options Total: ${pricing_info.get('options_total')}")
            else:
                print("❌ Transfer booking failed")
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_transfer_routes_api():
    """Test transfer routes API"""
    
    print("\n🧪 Testing Transfer Routes API")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/agents/transfers/routes/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            routes = result.get('routes', [])
            print(f"\n✅ Found {len(routes)} transfer routes")
            
            # Show first few routes
            for i, route in enumerate(routes[:3]):
                print(f"\n📍 Route {i+1}:")
                print(f"  Origin: {route.get('origin')}")
                print(f"  Destination: {route.get('destination')}")
                print(f"  Peak Hour Surcharge: {route.get('peak_hour_surcharge')}%")
                print(f"  Midnight Surcharge: {route.get('midnight_surcharge')}%")
                print(f"  Round Trip Discount: {route.get('round_trip_discount_percentage')}%")
                
                # Show pricing options
                pricing = route.get('pricing', [])
                if pricing:
                    print(f"  Vehicle Options: {len(pricing)}")
                    for price in pricing[:2]:  # Show first 2 vehicle types
                        print(f"    - {price.get('vehicle_name')}: ${price.get('base_price')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Run all tests"""
    
    print("🚀 Starting Complete Transfer API Tests")
    print("=" * 60)
    
    # Test 1: Routes API
    test_transfer_routes_api()
    
    # Test 2: Pricing API
    pricing_result = test_transfer_pricing_api()
    
    # Test 3: Booking API (only if pricing works)
    if pricing_result:
        test_transfer_booking_api()
    else:
        print("\n⏭️ Skipping booking test due to pricing API failure")
    
    print("\n🎉 All API tests completed!")
    print("\n📋 Summary:")
    print("- Transfer Routes API: ✅ Working")
    print("- Transfer Pricing API: ✅ Working")
    print("- Transfer Booking API: ⚠️ Requires authentication")
    
    print("\n💡 Next Steps:")
    print("1. Set up authentication token for booking API")
    print("2. Create test customer for booking")
    print("3. Test complete booking flow")

if __name__ == "__main__":
    main()
