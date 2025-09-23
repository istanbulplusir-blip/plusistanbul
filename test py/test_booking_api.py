import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from transfers.models import TransferRoute, TransferBooking

User = get_user_model()

def test_booking_api():
    print("=== Testing Transfer Booking API ===")
    
    # Get the test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"✓ Found test user: {user.email}")
    except User.DoesNotExist:
        print("✗ Test user not found")
        return
    
    # Get a route for testing
    try:
        route = TransferRoute.objects.first()
        print(f"✓ Found route: {route.origin} → {route.destination}")
    except TransferRoute.DoesNotExist:
        print("✗ No routes found")
        return
    
    # Test booking data
    tomorrow = datetime.now().date() + timedelta(days=1)
    booking_data = {
        "route": str(route.id),
        "travel_date": tomorrow.isoformat(),
        "travel_time": "10:00",
        "passengers": 2,
        "contact_name": "Test User",
        "contact_email": "test@example.com",
        "contact_phone": "+989123456789",
        "pickup_location": "Hotel Lobby",
        "dropoff_location": "Airport Terminal 1",
        "special_requests": "Early pickup needed"
    }
    
    print(f"\nBooking data:")
    print(json.dumps(booking_data, indent=2))
    
    # Test creating booking via API
    print("\n=== Testing Booking Creation ===")
    
    # First, let's check if we can authenticate
    auth_url = "http://localhost:8000/api/v1/auth/login/"
    auth_data = {
        "username": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        auth_response = requests.post(auth_url, json=auth_data)
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            token = auth_data.get('access')
            print(f"✓ Authentication successful")
            
            # Test booking creation
            booking_url = "http://localhost:8000/api/v1/transfers/bookings/"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            booking_response = requests.post(booking_url, json=booking_data, headers=headers)
            print(f"Booking API Response Status: {booking_response.status_code}")
            print(f"Booking API Response: {booking_response.text}")
            
            if booking_response.status_code == 201:
                print("✓ Booking created successfully!")
                booking_data = booking_response.json()
                print(f"Booking ID: {booking_data.get('id')}")
                print(f"Booking Number: {booking_data.get('booking_number')}")
            else:
                print("✗ Booking creation failed")
                
        else:
            print(f"✗ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_booking_api() 