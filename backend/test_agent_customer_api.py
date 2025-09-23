#!/usr/bin/env python
"""
Test script for Agent Customer Creation API
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

def create_test_agent():
    """Create a test agent user"""
    try:
        agent = User.objects.get(email='test-agent@example.com')
        print(f"Using existing agent: {agent.email}")
    except User.DoesNotExist:
        agent = User.objects.create_user(
            username='test-agent@example.com',
            email='test-agent@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Agent',
            role='agent',
            is_active=True
        )
        print(f"Created new agent: {agent.email}")
    
    return agent

def get_agent_token(agent):
    """Get JWT token for agent"""
    refresh = RefreshToken.for_user(agent)
    return str(refresh.access_token)

def test_create_customer():
    """Test customer creation API"""
    print("=" * 50)
    print("Testing Agent Customer Creation API")
    print("=" * 50)
    
    # Create test agent
    agent = create_test_agent()
    token = get_agent_token(agent)
    
    # Test data
    customer_data = {
        'email': 'test-customer@example.com',
        'first_name': 'Test',
        'last_name': 'Customer',
        'phone': '+1234567890',
        'address': 'Test Address',
        'city': 'Test City',
        'country': 'Test Country',
        'customer_status': 'active',
        'customer_tier': 'bronze',
        'relationship_notes': 'Test customer created by agent'
    }
    
    # API endpoint
    url = 'http://localhost:8000/api/v1/agents/customers/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(customer_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=customer_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Customer created successfully!")
            response_data = response.json()
            print(f"Customer ID: {response_data.get('data', {}).get('customer', {}).get('id')}")
        else:
            print("❌ FAILED: Customer creation failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Django server is not running")
        print("Please start the server with: python manage.py runserver 8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_without_auth():
    """Test API without authentication"""
    print("\n" + "=" * 50)
    print("Testing API without Authentication")
    print("=" * 50)
    
    customer_data = {
        'email': 'test-customer2@example.com',
        'first_name': 'Test',
        'last_name': 'Customer2'
    }
    
    url = 'http://localhost:8000/api/v1/agents/customers/'
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=customer_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Authentication required (as expected)")
        else:
            print("❌ FAILED: Should require authentication")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    test_create_customer()
    test_without_auth()
