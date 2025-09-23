#!/usr/bin/env python
"""
Test script to verify Accept-Language header handling
"""
import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

def test_language_header():
    """Test if Accept-Language header is properly handled"""
    print("🧪 Testing Accept-Language Header Handling")
    print("=" * 60)
    
    # Test URLs
    base_url = "http://localhost:8000/api/v1"
    
    # Test cases
    test_cases = [
        {
            'name': 'Persian Language',
            'headers': {'Accept-Language': 'fa'},
            'expected_lang': 'fa'
        },
        {
            'name': 'English Language',
            'headers': {'Accept-Language': 'en'},
            'expected_lang': 'en'
        },
        {
            'name': 'Turkish Language',
            'headers': {'Accept-Language': 'tr'},
            'expected_lang': 'tr'
        },
        {
            'name': 'No Header (Default)',
            'headers': {},
            'expected_lang': 'fa'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"   Headers: {test_case['headers']}")
        
        try:
            # Test with tour detail endpoint
            response = requests.get(
                f"{base_url}/tours/tour-x/",
                headers=test_case['headers'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                # Check if we can see the language in response
                if 'data' in data and 'title' in data['data']:
                    title = data['data']['title']
                    print(f"   📝 Tour Title: {title[:50]}...")
                    
                    # Check if title contains Persian characters
                    has_persian = any('\u0600' <= char <= '\u06FF' for char in title)
                    expected_persian = test_case['expected_lang'] == 'fa'
                    
                    if has_persian == expected_persian:
                        print(f"   ✅ Language Match: {'Persian' if has_persian else 'English'}")
                    else:
                        print(f"   ⚠️ Language Mismatch: Expected {'Persian' if expected_persian else 'English'}, got {'Persian' if has_persian else 'English'}")
                
                # Check itinerary items
                if 'data' in data and 'itinerary' in data['data']:
                    itinerary = data['data']['itinerary']
                    if itinerary:
                        first_item = itinerary[0]
                        item_title = first_item.get('title', '')
                        has_persian_item = any('\u0600' <= char <= '\u06FF' for char in item_title)
                        expected_persian_item = test_case['expected_lang'] == 'fa'
                        
                        if has_persian_item == expected_persian_item:
                            print(f"   ✅ Itinerary Language Match: {'Persian' if has_persian_item else 'English'}")
                        else:
                            print(f"   ⚠️ Itinerary Language Mismatch: Expected {'Persian' if expected_persian_item else 'English'}, got {'Persian' if has_persian_item else 'English'}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Language Header Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_language_header()
