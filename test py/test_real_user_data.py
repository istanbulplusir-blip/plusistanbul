#!/usr/bin/env python
"""
Test with real user data from the cart.
"""

import requests
import json

def test_real_user_data():
    """Test with the exact data from user's cart."""
    
    base_url = "http://localhost:8000/api/v1/transfers/routes/calculate_price_public/"
    
    # Real user data from the cart
    data = {
        "origin": "Tehran Imam Khomeini International Airport",
        "destination": "Shiraz International Airport",
        "vehicle_type": "minivan",
        "trip_type": "round_trip",
        "outbound_time": "04:59",
        "return_time": "06:59",
        "selected_options": ["meet_greet", "child_seat", "extra_luggage"]
    }
    
    print("=== Testing Real User Data ===")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    response = requests.post(base_url, json=data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResponse:")
        print(f"  Base Price: ${result.get('base_price', 0)}")
        print(f"  Outbound Surcharge: ${result.get('outbound_surcharge', 0)}")
        print(f"  Return Surcharge: ${result.get('return_surcharge', 0)}")
        print(f"  Round Trip Discount: ${result.get('round_trip_discount', 0)}")
        print(f"  Options Total: ${result.get('options_total', 0)}")
        print(f"  Final Price: ${result.get('final_price', 0)}")
        
        # Manual calculation verification
        base = result.get('base_price', 0)
        outbound_surcharge = result.get('outbound_surcharge', 0)
        return_surcharge = result.get('return_surcharge', 0)
        discount = result.get('round_trip_discount', 0)
        options = result.get('options_total', 0)
        final = result.get('final_price', 0)
        
        calculated = (base + outbound_surcharge + base + return_surcharge) - discount + options
        print(f"\nVerification:")
        print(f"  Manual calculation: ${calculated}")
        print(f"  Matches API: {abs(calculated - final) < 0.01}")
        
        print(f"\nExpected Results:")
        print(f"  Frontend shows: $789.00")
        print(f"  Backend API: ${final}")
        print(f"  Cart shows: $408 (should be ${final})")
        
    else:
        print(f"Error: {response.text}")

if __name__ == '__main__':
    test_real_user_data() 