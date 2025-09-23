#!/usr/bin/env python3
"""
Simple test script for logout functionality using requests
"""

import requests
import json

def test_logout():
    print("🧪 Testing Logout Functionality")
    print("=" * 40)
    
    # Step 1: Login
    print("1️⃣ Logging in...")
    login_data = {
        "username": "shahrokh",
        "password": "Test@123456"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            print("   ✅ Login successful")
            
            # Extract token
            access_token = result.get('tokens', {}).get('access')
            if access_token:
                print(f"   📝 Token: {access_token[:30]}...")
                
                # Step 2: Test logout
                print("\n2️⃣ Testing logout...")
                logout_response = requests.post(
                    "http://localhost:8000/api/v1/auth/logout",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                print(f"   📊 Status: {logout_response.status_code}")
                print(f"   📄 Response: {logout_response.text}")
                
                if logout_response.status_code == 200:
                    print("   ✅ Logout successful!")
                    return True
                else:
                    print("   ❌ Logout failed")
                    return False
            else:
                print("   ❌ No access token in response")
                return False
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   📄 Response: {login_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - Server not running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_logout()
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS: Logout works correctly!")
    else:
        print("💥 FAILED: Logout still has issues") 