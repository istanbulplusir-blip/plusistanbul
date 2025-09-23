#!/usr/bin/env python
"""
Test frontend-backend integration for Tour system.
"""

import requests
import json

def test_frontend_backend_integration():
    """Test that frontend can properly communicate with backend."""
    
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    tour_slug = "capacity-test-tour"
    
    # Test 1: Tour Detail API
    print("\n1️⃣ Testing Tour Detail API...")
    try:
        response = requests.get(f"{base_url}/tours/{tour_slug}/")
        if response.status_code == 200:
            tour_data = response.json()
            print("✅ Tour Detail API working")
            print(f"   Tour: {tour_data.get('title', 'Unknown')}")
            print(f"   Variants: {len(tour_data.get('variants', []))}")
            print(f"   Schedules: {len(tour_data.get('schedules', []))}")
            print(f"   Options: {len(tour_data.get('options', []))}")
        else:
            print(f"❌ Tour Detail API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tour Detail API: {e}")
        return False
    
    # Test 2: Tour Variants API
    print("\n2️⃣ Testing Tour Variants API...")
    try:
        response = requests.get(f"{base_url}/tours/{tour_slug}/variants/")
        if response.status_code == 200:
            data = response.json()
            variants = data.get('results', [])
            print("✅ Tour Variants API working")
            print(f"   Found {len(variants)} variants")
            for i, variant in enumerate(variants):
                if i >= 2:  # Show only first 2
                    break
                print(f"     - {variant.get('name', 'Unknown')} (price: {variant.get('base_price', 'N/A')})")
        else:
            print(f"❌ Tour Variants API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tour Variants API: {e}")
        return False
    
    # Test 3: Tour Options API
    print("\n3️⃣ Testing Tour Options API...")
    try:
        response = requests.get(f"{base_url}/tours/{tour_slug}/options/")
        if response.status_code == 200:
            data = response.json()
            options = data.get('results', [])
            print("✅ Tour Options API working")
            print(f"   Found {len(options)} options")
            for i, option in enumerate(options):
                if i >= 2:  # Show only first 2
                    break
                print(f"     - {option.get('name', 'Unknown')} (price: {option.get('price', 'N/A')})")
        else:
            print(f"❌ Tour Options API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tour Options API: {e}")
        return False
    
    # Test 4: Tour Booking Steps API
    print("\n4️⃣ Testing Tour Booking Steps API...")
    try:
        response = requests.get(f"{base_url}/tours/{tour_slug}/booking-steps/")
        if response.status_code == 200:
            booking_steps = response.json()
            steps = booking_steps.get('booking_steps', [])
            print("✅ Tour Booking Steps API working")
            print(f"   Found {len(steps)} booking steps")
            for step in steps:
                print(f"     - {step.get('title', 'Unknown')}: {step.get('description', 'N/A')}")
        else:
            print(f"❌ Tour Booking Steps API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tour Booking Steps API: {e}")
        return False
    
    # Test 5: Frontend Accessibility
    print("\n5️⃣ Testing Frontend Accessibility...")
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing frontend accessibility: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All integration tests passed!")
    return True

if __name__ == "__main__":
    test_frontend_backend_integration()
