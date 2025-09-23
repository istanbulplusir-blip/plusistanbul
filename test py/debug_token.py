#!/usr/bin/env python
"""
Debug JWT Token Issues
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

def debug_token():
    print("🔍 Debugging JWT Token Issues...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='debug_user',
        defaults={
            'email': 'debug@example.com',
            'first_name': 'Debug',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('debugpass123')
        user.save()
        print("✅ Created debug user")
    else:
        print("✅ Using existing debug user")
    
    # Generate token manually
    token = AccessToken.for_user(user)
    token_str = str(token)
    
    print(f"🔑 Generated token: {token_str[:50]}...")
    print(f"⏰ Token expires at: {token['exp']}")
    print(f"📅 Current time: {datetime.now().timestamp()}")
    
    # Test token with API
    base_url = "http://127.0.0.1:8000"
    
    # Test with manual token
    headers = {
        'Authorization': f'Bearer {token_str}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        f"{base_url}/api/v1/cart/",
        headers=headers
    )
    
    print(f"🧪 Manual token test: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.text}")
    
    # Test with login endpoint
    login_data = {
        'username': 'debug_user',
        'password': 'debugpass123'
    }
    
    session = requests.Session()
    login_response = session.post(
        f"{base_url}/api/v1/auth/login/",
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        data = login_response.json()
        print(f"📋 Login response: {data}")
        
        login_token = data.get('access')
        if login_token:
            print(f"🔑 Login token: {login_token[:50]}...")
            
            # Test with login token
            login_headers = {
                'Authorization': f'Bearer {login_token}',
                'Content-Type': 'application/json'
            }
            
            cart_response = session.get(
                f"{base_url}/api/v1/cart/",
                headers=login_headers
            )
            
            print(f"🧪 Login token test: {cart_response.status_code}")
            if cart_response.status_code != 200:
                print(f"   Response: {cart_response.text}")
        else:
            print("❌ No access token in login response")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")

if __name__ == "__main__":
    debug_token()
