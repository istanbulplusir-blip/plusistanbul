#!/usr/bin/env python3
"""
Test script for profile API functionality
"""

import requests
import json

def test_profile_api():
    print("🧪 Testing Profile API")
    print("=" * 40)
    
    # Step 1: Login to get token
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
                
                # Step 2: Get current profile
                print("\n2️⃣ Getting current profile...")
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                get_response = requests.get(
                    "http://localhost:8000/api/v1/auth/profile/",
                    headers=headers
                )
                
                print(f"   📊 GET Status: {get_response.status_code}")
                print(f"   📄 GET Response: {get_response.text[:200]}...")
                
                if get_response.status_code == 200:
                    current_profile = get_response.json()
                    print("   ✅ Profile retrieved successfully")
                    
                    # Step 3: Test profile update
                    print("\n3️⃣ Testing profile update...")
                    
                    # Prepare update data
                    update_data = {
                        "first_name": "shahab",
                        "last_name": "shahrokh",
                        "email": "shahabshahrrokhh@gmail.com",
                        "phone_number": "+989123456789",
                        "date_of_birth": "1990-01-01",
                        "bio": "تست ویرایش پروفایل",
                        "address": "تهران، ایران",
                        "city": "تهران",
                        "country": "ایران"
                    }
                    
                    put_response = requests.put(
                        "http://localhost:8000/api/v1/auth/profile/",
                        headers=headers,
                        json=update_data
                    )
                    
                    print(f"   📊 PUT Status: {put_response.status_code}")
                    print(f"   📄 PUT Response: {put_response.text}")
                    
                    if put_response.status_code == 200:
                        print("   ✅ Profile update successful!")
                        return True
                    else:
                        print("   ❌ Profile update failed")
                        return False
                else:
                    print("   ❌ Failed to get profile")
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
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_profile_api()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS: Profile API works correctly!")
    else:
        print("💥 FAILED: Profile API has issues") 