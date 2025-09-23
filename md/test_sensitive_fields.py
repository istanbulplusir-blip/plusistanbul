#!/usr/bin/env python3
"""
Test script for sensitive field update functionality
"""

import requests
import json

def test_sensitive_field_update():
    print("🧪 Testing Sensitive Field Update System")
    print("=" * 50)
    
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
                
                # Test 1: Try to update non-sensitive fields (should work)
                print("\n2️⃣ Testing non-sensitive field update...")
                test_non_sensitive_update(access_token)
                
                # Test 2: Try to update sensitive fields (should require OTP)
                print("\n3️⃣ Testing sensitive field update...")
                test_sensitive_field_request(access_token)
                
            else:
                print("   ❌ No access token found")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")

def test_non_sensitive_update(token):
    """Test updating non-sensitive fields"""
    try:
        update_data = {
            "date_of_birth": "1990-01-01",
            "profile": {
                "bio": "This is a test bio",
                "address": "Test Address",
                "city": "Tehran",
                "country": "Iran"
            }
        }
        
        response = requests.put(
            "http://localhost:8000/api/v1/auth/profile/",
            json=update_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Non-sensitive fields updated successfully")
            print(f"   📝 Response: {result.get('message')}")
        else:
            result = response.json()
            print(f"   ❌ Update failed: {response.status_code}")
            print(f"   📝 Response: {result}")
            
    except Exception as e:
        print(f"   ❌ Update error: {str(e)}")

def test_sensitive_field_request(token):
    """Test requesting sensitive field update"""
    try:
        # Test email update request
        request_data = {
            "field": "email",
            "new_value": "newemail@test.com"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/profile/sensitive/request/",
            json=request_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Sensitive field update request successful")
            print(f"   📝 Message: {result.get('message')}")
            print(f"   📝 Field: {result.get('field')}")
            print(f"   📝 New Value: {result.get('new_value')}")
            print(f"   📝 OTP ID: {result.get('otp_id')}")
            
            # Test OTP verification (with fake OTP)
            print("\n4️⃣ Testing OTP verification (with fake OTP)...")
            test_otp_verification(token, result.get('field'), result.get('new_value'), "123456")
            
        else:
            result = response.json()
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   📝 Response: {result}")
            
    except Exception as e:
        print(f"   ❌ Request error: {str(e)}")

def test_otp_verification(token, field, new_value, otp_code):
    """Test OTP verification"""
    try:
        verify_data = {
            "field": field,
            "new_value": new_value,
            "otp_code": otp_code
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/profile/sensitive/verify/",
            json=verify_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ OTP verification successful")
            print(f"   📝 Message: {result.get('message')}")
        else:
            result = response.json()
            print(f"   ❌ OTP verification failed: {response.status_code}")
            print(f"   📝 Response: {result}")
            
    except Exception as e:
        print(f"   ❌ OTP verification error: {str(e)}")

def test_profile_get(token):
    """Test getting user profile"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/auth/profile/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Profile retrieved successfully")
            print(f"   📝 User: {result.get('user', {}).get('email')}")
            print(f"   📝 Profile: {result.get('profile', {}).get('bio', 'No bio')}")
        else:
            result = response.json()
            print(f"   ❌ Profile retrieval failed: {response.status_code}")
            print(f"   📝 Response: {result}")
            
    except Exception as e:
        print(f"   ❌ Profile retrieval error: {str(e)}")

if __name__ == "__main__":
    test_sensitive_field_update() 