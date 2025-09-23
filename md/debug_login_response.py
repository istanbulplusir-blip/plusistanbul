#!/usr/bin/env python3
"""
Debug script to examine login response structure
"""

import requests
import json

def debug_login_response():
    print("🔍 Debugging Login Response")
    print("=" * 40)
    
    login_data = {
        "username": "shahrokh",
        "password": "Test@123456"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse JSON:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\nKeys in response:")
            for key in result.keys():
                print(f"  - {key}: {type(result[key])}")
                
            # Check for tokens in different possible locations
            possible_token_keys = ['access', 'access_token', 'token', 'jwt', 'auth_token']
            for key in possible_token_keys:
                if key in result:
                    print(f"\n✅ Found token in '{key}': {result[key][:30]}...")
                    
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_login_response() 