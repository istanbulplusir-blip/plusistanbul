#!/usr/bin/env python
"""
Simple test script for authentication endpoints with CSRF handling
"""

import requests
import json

def test_registration_simple():
    """Test user registration with CSRF token"""
    
    # First get CSRF token
    session = requests.Session()
    
    try:
        print("🧪 Testing Registration with CSRF...")
        
        # Get CSRF token
        csrf_url = 'http://localhost:8000/api/v1/auth/register/'
        csrf_response = session.get(csrf_url)
        print(f"CSRF Request Status: {csrf_response.status_code}")
        
        # Extract CSRF token from cookies
        csrf_token = session.cookies.get('csrftoken', '')
        print(f"CSRF Token: {csrf_token[:20]}..." if csrf_token else "No CSRF token found")
        
        # Registration data
        data = {
            'username': 'testuser123',
            'email': 'test123@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,
            'Referer': 'http://localhost:8000/api/v1/auth/register/'
        }
        
        # Make registration request
        response = session.post(csrf_url, json=data, headers=headers)
        print(f"Registration Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # Check if it's JSON
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"Response: {response.text}")
            if response.status_code == 201:
                print("✅ Registration successful!")
                return response.json()
            else:
                print("❌ Registration failed!")
                return None
        else:
            print(f"❌ Unexpected response type. First 300 chars:")
            print(response.text[:300])
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Simple Authentication Test...\n")
    result = test_registration_simple()
    print("\n🏁 Test completed!") 