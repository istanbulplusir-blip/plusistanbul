#!/usr/bin/env python
"""
Test script for new Tour API endpoints.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOUR_SLUG = "capacity-test-tour"  # Using existing tour slug

def test_tour_endpoints():
    """Test all new tour endpoints."""
    
    print("🧪 Testing New Tour API Endpoints")
    print("=" * 50)
    
    # Test 1: Get tour variants
    print("\n1️⃣ Testing Tour Variants API...")
    try:
        response = requests.get(f"{BASE_URL}/tours/{TOUR_SLUG}/variants/")
        if response.status_code == 200:
            print("✅ Tour Variants API working")
            variants = response.json()
            print(f"   Found {len(variants)} variants")
            for variant in variants[:2]:  # Show first 2
                print(f"     - {variant.get('name', 'Unknown')} (price: {variant.get('base_price', 'N/A')})")
        else:
            print(f"❌ Tour Variants API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Tour Variants API: {e}")
    
    # Test 2: Get tour options
    print("\n2️⃣ Testing Tour Options API...")
    try:
        response = requests.get(f"{BASE_URL}/tours/{TOUR_SLUG}/options/")
        if response.status_code == 200:
            print("✅ Tour Options API working")
            options = response.json()
            print(f"   Found {len(options)} options")
            for option in options[:2]:  # Show first 2
                print(f"     - {option.get('name', 'Unknown')} (price: {option.get('price', 'N/A')})")
        else:
            print(f"❌ Tour Options API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Tour Options API: {e}")
    
    # Test 3: Get tour itinerary
    print("\n3️⃣ Testing Tour Itinerary API...")
    try:
        response = requests.get(f"{BASE_URL}/tours/{TOUR_SLUG}/itinerary/")
        if response.status_code == 200:
            print("✅ Tour Itinerary API working")
            itinerary = response.json()
            print(f"   Found {len(itinerary)} itinerary items")
            for item in itinerary[:2]:  # Show first 2
                print(f"     - {item.get('title', 'Unknown')} (duration: {item.get('duration_minutes', 'N/A')} min)")
        else:
            print(f"❌ Tour Itinerary API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Tour Itinerary API: {e}")
    
    # Test 4: Get tour booking steps
    print("\n4️⃣ Testing Tour Booking Steps API...")
    try:
        response = requests.get(f"{BASE_URL}/tours/{TOUR_SLUG}/booking-steps/")
        if response.status_code == 200:
            print("✅ Tour Booking Steps API working")
            booking_steps = response.json()
            steps = booking_steps.get('booking_steps', [])
            print(f"   Found {len(steps)} booking steps")
            for step in steps[:2]:  # Show first 2
                print(f"     - {step.get('title', 'Unknown')}: {step.get('description', 'N/A')}")
        else:
            print(f"❌ Tour Booking Steps API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Tour Booking Steps API: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    print("🚀 Starting Tour API Endpoints Test")
    print(f"Using tour slug: {TOUR_SLUG}")
    test_tour_endpoints()
