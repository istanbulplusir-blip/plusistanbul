#!/usr/bin/env python
"""
Debug script to see the actual API response structure
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def debug_response():
    """Debug the API response structure"""
    print("🔍 Debugging API Response Structure")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    headers = {'Accept-Language': 'fa'}
    
    try:
        response = requests.get(
            f"{base_url}/tours/tour-x/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse Structure:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Check if data exists
            if 'data' in data:
                print(f"\n✅ 'data' key exists")
                tour_data = data['data']
                print(f"Tour data keys: {list(tour_data.keys())}")
                
                if 'title' in tour_data:
                    print(f"Title: {tour_data['title']}")
                
                if 'itinerary' in tour_data:
                    itinerary = tour_data['itinerary']
                    print(f"Itinerary count: {len(itinerary)}")
                    if itinerary:
                        print(f"First item: {itinerary[0]}")
            else:
                print(f"\n❌ 'data' key not found")
                print(f"Available keys: {list(data.keys())}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_response()
