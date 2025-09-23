#!/usr/bin/env python3
"""
Simple test script to debug cart API.
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from tours.models import Tour, TourVariant, TourSchedule

User = get_user_model()

def test_cart_api():
    """Test cart API with simple data."""
    base_url = "http://localhost:8000"
    
    # Get test data
    user = User.objects.filter(username='test_booking_user').first()
    if not user:
        print("❌ Test user not found")
        return
    
    tour = Tour.objects.filter(slug='test-tour-16329065').first()
    if not tour:
        print("❌ Test tour not found")
        return
    
    variant = tour.variants.filter(is_active=True).first()
    if not variant:
        print("❌ Test variant not found")
        return
    
    schedule = TourSchedule.objects.filter(tour=tour).first()
    if not schedule:
        print("❌ Test schedule not found")
        return
    
    print(f"✅ Found tour: {tour.title}")
    print(f"✅ Found variant: {variant.name}")
    print(f"✅ Found schedule: {schedule.start_date}")
    
    # Simple cart data
    cart_data = {
        "product_type": "tour",
        "product_id": str(tour.id),
        "variant_id": str(variant.id),
        "quantity": 1,
        "booking_data": {
            "schedule_id": str(schedule.id),
            "participants": {
                "adult": 1,
                "child": 0,
                "infant": 0
            }
        }
    }
    
    # Test without authentication first
    print("\n🧪 Testing without authentication...")
    response = requests.post(
        f"{base_url}/api/v1/cart/add/",
        json=cart_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 500:
        print("❌ 500 Error - checking response...")
        print(response.text)  # Full response
    else:
        try:
            result = response.json()
            print(f"Response: {result}")
        except:
            print(f"Non-JSON response: {response.text[:200]}")

if __name__ == "__main__":
    test_cart_api() 