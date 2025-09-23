#!/usr/bin/env python3
"""
Test checkout authentication issue.
"""

import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def test_checkout_auth():
    """Test checkout authentication."""
    base_url = "http://localhost:8000"
    
    # Get test user
    user = User.objects.filter(username='test_booking_user').first()
    if not user:
        print("❌ Test user not found")
        return
    
    print(f"✅ Found user: {user.username}")
    
    # Login
    session = requests.Session()
    auth_data = {
        "username": user.username,
        "password": "testpass123"
    }
    
    response = session.post(
        f"{base_url}/api/v1/auth/login/",
        json=auth_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Login response: {result}")
        token = result.get('tokens', {}).get('access')
        if token:
            print(f"✅ Got token: {token[:50]}...")
        else:
            print("❌ No access token in response")
            return
        
        # Test checkout
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        # Add CSRF token
        csrf_token = session.cookies.get('csrftoken')
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token
            print(f"✅ Added CSRF token: {csrf_token}")
        
        checkout_data = {
            "payment_method": "test",
            "customer_notes": "Test order"
        }
        
        response = session.post(
            f"{base_url}/api/v1/orders/create/",
            json=checkout_data,
            headers=headers
        )
        
        print(f"Checkout Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 401:
            print("❌ Still 401 - authentication issue")
        elif response.status_code == 400:
            print("✅ Authentication works, but cart is empty")
        else:
            print(f"✅ Checkout response: {response.status_code}")
    else:
        print(f"❌ Login failed: {response.status_code}")

if __name__ == "__main__":
    test_checkout_auth()
