#!/usr/bin/env python
"""
Check available tours in API.
"""

import requests
import json

def check_available_tours():
    """Check what tours are available in the API."""
    
    print("🔍 Checking Available Tours in API")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8000/api/v1/tours/')
        if response.status_code == 200:
            data = response.json()
            
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict):
                tours = data.get('results', [])
            else:
                tours = data
            
            print(f"Found {len(tours)} tours:")
            for i, tour in enumerate(tours[:5]):  # Show first 5
                print(f"\n{i+1}. {tour.get('title', 'Unknown')}")
                print(f"   Slug: {tour.get('slug', 'N/A')}")
                print(f"   Price: {tour.get('price', 'N/A')}")
                print(f"   Currency: {tour.get('currency', 'N/A')}")
                print(f"   Duration: {tour.get('duration_hours', 'N/A')} hours")
                print(f"   Category: {tour.get('category_name', 'N/A')}")
        else:
            print(f"❌ Failed to get tours: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_available_tours()
