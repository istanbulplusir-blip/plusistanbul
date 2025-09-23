#!/usr/bin/env python
"""
Debug script to check API response for Tour X
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def debug_api_response():
    """Debug API response for Tour X"""
    print("🔍 Debugging API Response for Tour X")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        response = requests.get(
            f"{base_url}/tours/tour-x/",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received")
            print(f"📋 Tour Title: {data.get('title', 'N/A')}")
            print(f"📋 Main Image: {data.get('image', 'N/A')}")
            
            # Check gallery
            gallery = data.get('gallery', [])
            print(f"📋 Gallery: {gallery}")
            
            # Check itinerary
            itinerary = data.get('itinerary', [])
            print(f"📋 Itinerary count: {len(itinerary)}")
            if itinerary:
                print(f"📋 First itinerary image: {itinerary[0].get('image', 'N/A')}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_api_response()
