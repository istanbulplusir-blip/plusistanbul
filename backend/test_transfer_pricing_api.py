#!/usr/bin/env python
"""
Test script for Transfer Pricing API
"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"
AGENT_TOKEN = "your_agent_token_here"  # Replace with actual token

def test_transfer_pricing_api():
    """Test the transfer pricing API endpoint"""
    
    # Test data
    test_data = {
        "product_type": "transfer",
        "route_id": 1,  # Replace with actual route ID
        "vehicle_type": "sedan",
        "passenger_count": 2,
        "trip_type": "one_way",
        "booking_time": "14:00",
        "selected_options": [
            {
                "id": "1",  # Replace with actual option ID
                "quantity": 1,
                "name": "Extra Luggage",
                "price": 10.00
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {AGENT_TOKEN}",
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
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                pricing = result.get('pricing', {})
                print("\n✅ Pricing calculation successful!")
                print(f"Base Price: {pricing.get('base_price')}")
                print(f"Agent Total: {pricing.get('agent_total')}")
                print(f"Options Total: {pricing.get('options_total')}")
                print(f"Savings: {pricing.get('savings')}")
                print(f"Savings Percentage: {pricing.get('savings_percentage')}%")
            else:
                print("❌ Pricing calculation failed")
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_transfer_booking_api():
    """Test the transfer booking API endpoint"""
    
    # Test data
    test_data = {
        "customer_id": "customer_uuid_here",  # Replace with actual customer ID
        "route_id": 1,  # Replace with actual route ID
        "vehicle_type": "sedan",
        "passenger_count": 2,
        "luggage_count": 1,
        "trip_type": "one_way",
        "booking_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "booking_time": "14:00",
        "selected_options": [
            {
                "id": "1",  # Replace with actual option ID
                "quantity": 1,
                "name": "Extra Luggage",
                "price": 10.00
            }
        ],
        "payment_method": "whatsapp"
    }
    
    headers = {
        "Authorization": f"Bearer {AGENT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test booking endpoint
        response = requests.post(
            f"{BASE_URL}/api/agents/book/transfer/",
            headers=headers,
            json=test_data
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("\n✅ Transfer booking successful!")
                print(f"Order Number: {result.get('order_number')}")
                print(f"Total Amount: {result.get('total_amount')}")
                print(f"Commission Amount: {result.get('commission_amount')}")
            else:
                print("❌ Transfer booking failed")
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Transfer Pricing API...")
    test_transfer_pricing_api()
    
    print("\n🧪 Testing Transfer Booking API...")
    test_transfer_booking_api()
    
    print("\n✅ Tests completed!")
