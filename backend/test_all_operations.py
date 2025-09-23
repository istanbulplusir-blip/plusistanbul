#!/usr/bin/env python
"""
Test script for all customer operations
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

def test_all_operations():
    """Test all customer operations"""
    print("🧪 Testing All Customer Operations")
    print("=" * 60)
    
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
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'fa'
    }
    
    # Test 1: Create Customer
    print("\n1️⃣ Testing Customer Creation")
    print("-" * 40)
    
    customer_data = {
        'email': 'test-all-ops@example.com',
        'first_name': 'Test',
        'last_name': 'AllOps',
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
        'relationship_notes': 'Test customer for all operations',
        'special_requirements': '',
        'marketing_consent': False
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/agents/customers/',
            json=customer_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            customer_id = response.json()['data']['customer']['id']
            print(f"✅ Customer created: {customer_id}")
        else:
            print(f"❌ Failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Send Verification
    print("\n2️⃣ Testing Send Verification")
    print("-" * 40)
    
    try:
        response = requests.post(
            f'http://localhost:8000/api/v1/agents/customers/{customer_id}/verification/',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Verification sent successfully")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Send Credentials
    print("\n3️⃣ Testing Send Credentials")
    print("-" * 40)
    
    try:
        response = requests.post(
            f'http://localhost:8000/api/v1/agents/customers/{customer_id}/credentials/',
            json={'method': 'email'},
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Credentials sent successfully")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Edit Customer
    print("\n4️⃣ Testing Edit Customer")
    print("-" * 40)
    
    edit_data = {
        'first_name': 'Updated',
        'last_name': 'Customer',
        'phone': '+9876543210',
        'address': 'Updated Address',
        'city': 'Updated City',
        'customer_status': 'vip',
        'customer_tier': 'gold',
        'relationship_notes': 'Updated notes'
    }
    
    try:
        response = requests.put(
            f'http://localhost:8000/api/v1/agents/customers/{customer_id}/',
            json=edit_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Customer updated successfully")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get Customer Details
    print("\n5️⃣ Testing Get Customer Details")
    print("-" * 40)
    
    try:
        response = requests.get(
            f'http://localhost:8000/api/v1/agents/customers/{customer_id}/',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Customer details retrieved successfully")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Delete Customer
    print("\n6️⃣ Testing Delete Customer")
    print("-" * 40)
    
    try:
        response = requests.delete(
            f'http://localhost:8000/api/v1/agents/customers/{customer_id}/',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Customer deleted successfully")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All operations tested!")

if __name__ == '__main__':
    test_all_operations()
