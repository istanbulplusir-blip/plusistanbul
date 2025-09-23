#!/usr/bin/env python
"""
Test car rental API endpoints.
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from car_rentals.models import CarRental, CarRentalLocation

def test_car_rental_api():
    """Test car rental API endpoints."""
    print("Testing Car Rental API...")
    print("=" * 50)
    
    # Test 1: Get car rental locations
    print("1. Testing car rental locations API...")
    try:
        response = requests.get('http://localhost:8000/api/v1/car-rentals/locations/')
        if response.status_code == 200:
            locations = response.json()
            print(f"✅ Found {len(locations)} locations")
            for location in locations[:3]:  # Show first 3
                print(f"   - {location['name']} ({location['location_type']})")
        else:
            print(f"❌ Locations API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Locations API error: {e}")
    
    print()
    
    # Test 2: Get car rentals
    print("2. Testing car rentals API...")
    try:
        response = requests.get('http://localhost:8000/api/v1/car-rentals/')
        if response.status_code == 200:
            cars = response.json()
            print(f"✅ Found {len(cars)} car rentals")
            for car in cars[:3]:  # Show first 3
                print(f"   - {car['brand']} {car['model']} ({car['year']}) - ${car['price_per_day']}/day")
                if car.get('default_pickup_locations'):
                    print(f"     Pickup locations: {len(car['default_pickup_locations'])}")
        else:
            print(f"❌ Car rentals API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Car rentals API error: {e}")
    
    print()
    
    # Test 3: Get specific car rental detail
    print("3. Testing car rental detail API...")
    try:
        car = CarRental.objects.first()
        if car:
            response = requests.get(f'http://localhost:8000/api/v1/car-rentals/{car.slug}/')
            if response.status_code == 200:
                car_detail = response.json()
                print(f"✅ Car detail loaded: {car_detail['brand']} {car_detail['model']}")
                print(f"   - Price: ${car_detail['price_per_day']}/day")
                print(f"   - Min rental: {car_detail['min_rent_days']} days")
                print(f"   - Max rental: {car_detail['max_rent_days']} days")
                print(f"   - Pickup locations: {len(car_detail.get('default_pickup_locations', []))}")
                print(f"   - Dropoff locations: {len(car_detail.get('default_dropoff_locations', []))}")
                print(f"   - Custom pickup allowed: {car_detail.get('allow_custom_pickup_location', False)}")
                print(f"   - Custom dropoff allowed: {car_detail.get('allow_custom_dropoff_location', False)}")
            else:
                print(f"❌ Car detail API failed: {response.status_code}")
        else:
            print("❌ No car rentals found")
    except Exception as e:
        print(f"❌ Car detail API error: {e}")
    
    print()
    
    # Test 4: Test cart API with car rental
    print("4. Testing cart API with car rental...")
    try:
        car = CarRental.objects.first()
        location = CarRentalLocation.objects.first()
        
        if car and location:
            # Calculate dates
            pickup_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            dropoff_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            pickup_time = '10:00'
            dropoff_time = '10:00'
            
            cart_data = {
                'product_type': 'car_rental',
                'product_id': str(car.id),
                'pickup_date': pickup_date,
                'dropoff_date': dropoff_date,
                'pickup_time': pickup_time,
                'dropoff_time': dropoff_time,
                'pickup_location_type': 'predefined',
                'pickup_location_id': str(location.id),
                'dropoff_location_type': 'same_as_pickup',
                'quantity': 1,
                'session_id': 'test_session_123'
            }
            
            response = requests.post('http://localhost:8000/api/v1/cart/add/', json=cart_data)
            if response.status_code == 201:
                cart_item = response.json()
                print(f"✅ Car rental added to cart successfully")
                print(f"   - Cart item ID: {cart_item['cart_item']['id']}")
                print(f"   - Total price: ${cart_item['cart_item']['total_price']}")
                print(f"   - Pickup: {pickup_date} at {pickup_time}")
                print(f"   - Dropoff: {dropoff_date} at {dropoff_time}")
            else:
                print(f"❌ Cart API failed: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print("❌ No car or location found for testing")
    except Exception as e:
        print(f"❌ Cart API error: {e}")
    
    print()
    print("=" * 50)
    print("Car Rental API Test Completed!")

if __name__ == '__main__':
    test_car_rental_api()
