#!/usr/bin/env python
"""
Test script to simulate frontend request
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_frontend_request():
    """Test the exact request that frontend sends"""
    print("🧪 Testing Frontend Request Simulation")
    print("=" * 50)
    
    # Get agent user
    try:
        agent = User.objects.get(email='agenttest@peykan.com')
        print(f"✅ Agent found: {agent.email}")
    except User.DoesNotExist:
        print("❌ Agent not found")
        return
    
    # Get token
    token = str(RefreshToken.for_user(agent).access_token)
    print(f"✅ Token generated: {token[:20]}...")
    
    # Simulate frontend request data
    customer_data = {
        'email': 'frontend-test@example.com',
        'first_name': 'Frontend',
        'last_name': 'Test',
        'phone': '+1234567890',
        'address': 'Test Address',
        'city': 'Test City',
        'country': 'Test Country',
        'birth_date': None,
        'gender': None,
        'preferred_language': 'fa',
        'preferred_contact_method': 'email',
        'customer_status': 'active',
        'customer_tier': 'bronze',
        'relationship_notes': '',
        'special_requirements': '',
        'marketing_consent': False
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'fa'
    }
    
    print(f"📤 Request URL: http://localhost:8000/api/v1/agents/customers/")
    print(f"📤 Headers: {headers}")
    print(f"📤 Data: {json.dumps(customer_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/agents/customers/',
            json=customer_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Customer created successfully!")
        else:
            print("❌ FAILED: Request failed")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to server")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    test_frontend_request()
