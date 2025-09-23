#!/usr/bin/env python3
"""
Test script to verify logout functionality fix
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login/"
LOGOUT_URL = f"{BASE_URL}/api/v1/auth/logout"

def test_logout_fix():
    print("🧪 Testing Logout Functionality Fix")
    print("=" * 50)
    
    # Test credentials
    login_data = {
        "username": "shahrokh",
        "password": "Test@123456"
    }
    
    try:
        # Step 1: Login to get token
        print("1️⃣ Logging in...")
        login_response = requests.post(LOGIN_URL, json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access')
            
            if access_token:
                print("   ✅ Login successful")
                print(f"   📝 Token received: {access_token[:20]}...")
                
                # Step 2: Test logout
                print("\n2️⃣ Testing logout...")
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                logout_response = requests.post(LOGOUT_URL, headers=headers)
                
                print(f"   📊 Status Code: {logout_response.status_code}")
                print(f"   📄 Response: {logout_response.text}")
                
                if logout_response.status_code == 200:
                    print("   ✅ Logout successful - No more APPEND_SLASH error!")
                    return True
                else:
                    print("   ❌ Logout failed")
                    return False
            else:
                print("   ❌ No access token received")
                return False
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   📄 Response: {login_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - Make sure Django server is running")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_logout_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Logout fix test PASSED!")
        print("✅ The APPEND_SLASH issue has been resolved")
    else:
        print("💥 Logout fix test FAILED!")
        print("❌ There might still be issues with the logout functionality") 