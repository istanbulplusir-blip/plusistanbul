#!/usr/bin/env python3
"""
Test script for date_of_birth field update
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1/auth"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"

def test_date_of_birth_update():
    """Test date_of_birth field update"""
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/login/", json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    login_result = login_response.json()
    access_token = login_result.get('access')
    
    if not access_token:
        print("No access token received")
        return
    
    print("Login successful!")
    
    # Step 2: Get current profile
    print("\n2. Getting current profile...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    profile_response = requests.get(f"{BASE_URL}/profile/", headers=headers)
    print(f"Profile status: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        current_date = profile_data.get('user', {}).get('date_of_birth')
        print(f"Current date_of_birth: {current_date}")
    
    # Step 3: Update date_of_birth
    print("\n3. Updating date_of_birth...")
    update_data = {
        "user_data": {
            "date_of_birth": "1990-05-15"
        },
        "profile": {
            "bio": "Test bio update"
        }
    }
    
    update_response = requests.put(f"{BASE_URL}/profile/", 
                                 json=update_data, 
                                 headers=headers)
    print(f"Update status: {update_response.status_code}")
    print(f"Update response: {update_response.text}")
    
    if update_response.status_code == 200:
        update_result = update_response.json()
        new_date = update_result.get('user', {}).get('date_of_birth')
        print(f"Updated date_of_birth: {new_date}")
        print("✅ date_of_birth update successful!")
    else:
        print("❌ date_of_birth update failed!")

if __name__ == "__main__":
    test_date_of_birth_update() 