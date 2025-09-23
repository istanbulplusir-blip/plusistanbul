#!/usr/bin/env python
"""
Test URL patterns for authentication
"""

import requests

def test_url_patterns():
    """Test different URL patterns"""
    base_url = 'http://localhost:8000'
    
    urls_to_test = [
        '/api/v1/auth/',
        '/api/v1/auth/register/',
        '/api/v1/auth/login/',
        '/api/v1/auth/logout/',
    ]
    
    for url in urls_to_test:
        full_url = f"{base_url}{url}"
        try:
            print(f"\n🧪 Testing: {full_url}")
            response = requests.get(full_url)
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Print first 200 chars of response
            content = response.text[:200]
            print(f"Response Preview: {content}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing URL Patterns...\n")
    test_url_patterns()
    print("\n🏁 URL Testing completed!") 