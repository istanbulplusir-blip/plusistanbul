#!/usr/bin/env python
"""
Debug live request from frontend
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute
from agents.views import AgentPricingPreviewView
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import User

def debug_live_request():
    """Debug the exact request from frontend"""
    
    print("🔍 Debugging Live Frontend Request...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='agenttest',
            defaults={
                'email': 'agenttest@peykan.com',
                'role': 'agent',
                'is_active': True
            }
        )
        
        print(f"👤 Agent: {agent.username} (Role: {agent.role})")
        
        # Get Isfahan route
        route = TransferRoute.objects.filter(
            origin__icontains='Isfahan Airport',
            destination__icontains='Isfahan City Center'
        ).first()
        
        if not route:
            print("❌ Route not found")
            return False
            
        print(f"📍 Route: {route.origin} → {route.destination}")
        print(f"🆔 Route ID: {route.id}")
        
        # Simulate the exact request from frontend
        request_data = {
            'product_type': 'transfer',
            'route_id': str(route.id),  # String format as sent by frontend
            'vehicle_type': 'sedan',
            'passenger_count': 3,
            'trip_type': 'one_way',
            'booking_time': '09:32',
            'selected_options': []
        }
        
        print(f"📤 Request Data: {request_data}")
        
        # Test with different request methods
        factory = APIRequestFactory()
        
        # Method 1: JSON format
        print(f"\n🧪 Method 1: JSON format")
        request = factory.post('/agents/pricing/preview/', 
                              data=json.dumps(request_data),
                              content_type='application/json')
        force_authenticate(request, user=agent)
        request.user = agent
        
        view = AgentPricingPreviewView()
        response = view.post(request)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Success: ${response.data.get('pricing', {}).get('total', 0)}")
        else:
            print(f"   ❌ Error: {response.data}")
        
        # Method 2: Form data
        print(f"\n🧪 Method 2: Form data")
        request = factory.post('/agents/pricing/preview/', 
                              data=request_data)
        force_authenticate(request, user=agent)
        request.user = agent
        
        response = view.post(request)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Success: ${response.data.get('pricing', {}).get('total', 0)}")
        else:
            print(f"   ❌ Error: {response.data}")
        
        # Method 3: Test with missing fields
        print(f"\n🧪 Method 3: Missing vehicle_type")
        incomplete_data = {
            'product_type': 'transfer',
            'route_id': str(route.id),
            'passenger_count': 3,
            'trip_type': 'one_way',
            'booking_time': '09:32',
            'selected_options': []
        }
        
        request = factory.post('/agents/pricing/preview/', 
                              data=json.dumps(incomplete_data),
                              content_type='application/json')
        force_authenticate(request, user=agent)
        request.user = agent
        
        response = view.post(request)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_live_request()
    sys.exit(0 if success else 1)
