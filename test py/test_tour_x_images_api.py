#!/usr/bin/env python
"""
Test script to verify Tour X images are accessible via API
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def test_tour_images_api():
    """Test if Tour X images are accessible via API"""
    print("🧪 Testing Tour X Images API")
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
            
            # Check main image
            main_image = data.get('image')
            if main_image:
                print(f"✅ Main image URL: {main_image}")
                
                # Test if image is accessible
                if main_image.startswith('http'):
                    image_url = main_image
                else:
                    image_url = f"http://localhost:8000{main_image}"
                
                img_response = requests.head(image_url, timeout=5)
                if img_response.status_code == 200:
                    print(f"✅ Main image accessible: {image_url}")
                else:
                    print(f"❌ Main image not accessible: {image_url}")
            else:
                print("❌ No main image found")
            
            # Check gallery images
            gallery = data.get('gallery', [])
            print(f"📋 Gallery Images: {len(gallery)} items")
            
            for i, img in enumerate(gallery[:3]):  # Test first 3
                if img:
                    if img.startswith('http'):
                        image_url = img
                    else:
                        image_url = f"http://localhost:8000{img}"
                    
                    img_response = requests.head(image_url, timeout=5)
                    if img_response.status_code == 200:
                        print(f"✅ Gallery {i+1} accessible: {image_url}")
                    else:
                        print(f"❌ Gallery {i+1} not accessible: {image_url}")
            
            # Check itinerary images
            itinerary = data.get('itinerary', [])
            print(f"📋 Itinerary Images: {len(itinerary)} items")
            
            for i, item in enumerate(itinerary[:3]):  # Test first 3
                img = item.get('image')
                if img:
                    if img.startswith('http'):
                        image_url = img
                    else:
                        image_url = f"http://localhost:8000{img}"
                    
                    img_response = requests.head(image_url, timeout=5)
                    if img_response.status_code == 200:
                        print(f"✅ Itinerary {i+1} accessible: {image_url}")
                    else:
                        print(f"❌ Itinerary {i+1} not accessible: {image_url}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_tour_images_api()
