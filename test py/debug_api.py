#!/usr/bin/env python
"""
Debug API responses.
"""

import requests

def debug_api():
    """Debug API responses."""
    
    base_url = "http://localhost:8000/api/v1"
    tour_slug = "capacity-test-tour"
    
    print("🔍 Debugging API Responses")
    print("=" * 50)
    
    # Test variants API
    print("\n1️⃣ Testing Variants API...")
    try:
        response = requests.get(f"{base_url}/tours/{tour_slug}/variants/")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response type: {type(response.text)}")
        print(f"Response length: {len(response.text)}")
        print(f"First 200 chars: {response.text[:200]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON parsed successfully: {type(data)}")
                print(f"Data: {data}")
            except Exception as e:
                print(f"JSON parsing failed: {e}")
        else:
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_api()
