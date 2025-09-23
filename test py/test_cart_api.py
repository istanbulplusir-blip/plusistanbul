#!/usr/bin/env python
"""
Test Cart API
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def test_cart_api():
    print("=== Testing Cart API ===")
    
    # Test data
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUxNzYwNzc3LCJpYXQiOjE3NTE3NTcxNzcsImp0aSI6ImQ0YTRhNjNlODlmODQ1NjJhZjg5ZTBkZDIzOTUyZTg0IiwidXNlcl9pZCI6ImUzMDQ4YWZkLWZiN2MtNGZhNy1hNmE3LTFiNjI5NjdiMmNjZCJ9.yJ9lWH1DtcTIqj2WgmVcQI-iedCFboP2COnHiUh17BQ'
    
    data = {
        'product_type': 'tour',
        'product_id': '14bd6232-2a43-405c-87f7-d755c5691a58',
        'variant_id': '8ff4e0d7-f52c-4b21-95b6-70f7eeec3062',
        'quantity': 3,
        'selected_options': [],
        'booking_data': {
            'schedule_id': 'd96e2d65-613c-4557-a05c-8a5f968c2b76',
            'participants': {
                'adult': 2,
                'child': 1,
                'infant': 0
            },
            'special_requests': ''
        }
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/cart/add/',
            json=data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ API call successful!")
            result = response.json()
            if 'cart_item' in result:
                print(f"✅ Cart item created with ID: {result['cart_item']['id']}")
        else:
            print("❌ API call failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cart_api() 