#!/usr/bin/env python
"""
Test script to check the API endpoint directly.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferOption

def test_api_endpoint():
    """Test the API endpoint directly."""
    try:
        # Get first available route
        route = TransferRoute.objects.filter(is_active=True).first()
        if not route:
            print("No active routes found")
            return
        
        # Get available options
        options = TransferOption.objects.filter(is_active=True)[:2]
        if not options:
            print("No active options found")
            return
        
        print(f"Testing API for route: {route.origin} → {route.destination}")
        print(f"Route ID: {route.id}")
        print(f"Available options: {[opt.name for opt in options]}")
        
        # Prepare request data
        request_data = {
            'vehicle_type': 'sedan',
            'trip_type': 'one_way',
            'booking_time': '14:30',
            'selected_options': [
                {'option_id': str(opt.id), 'quantity': 1}
                for opt in options
            ]
        }
        
        print(f"\nRequest data: {json.dumps(request_data, indent=2)}")
        
        # Make API request
        url = f'http://localhost:8000/api/transfers/routes/{route.id}/calculate_price/'
        response = requests.post(url, json=request_data)
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse data: {json.dumps(data, indent=2)}")
            
            # Check options breakdown
            if 'options_breakdown' in data:
                print(f"\nOptions breakdown found with {len(data['options_breakdown'])} items:")
                for option in data['options_breakdown']:
                    print(f"- {option['name']}: ${option['price']} x {option['quantity']} = ${option['total']}")
            else:
                print("\nNo options_breakdown found in response!")
        else:
            print(f"Error response: {response.text}")
        
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == '__main__':
    test_api_endpoint() 