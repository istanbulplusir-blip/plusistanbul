#!/usr/bin/env python
"""
Simple test script for authentication endpoints
"""

import requests
import json

def test_registration():
    """Test user registration"""
    url = 'http://localhost:8000/api/v1/auth/register/'
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    try:
        print("🧪 Testing Registration...")
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("❌ Registration failed!")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    pass
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login():
    """Test user login"""
    url = 'http://localhost:8000/api/v1/auth/login/'
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    try:
        print("\n🧪 Testing Login...")
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Authentication Tests...\n")
    
    # Test registration
    registration_result = test_registration()
    
    # Test login
    login_result = test_login()
    
    print("\n�� Tests completed!") 