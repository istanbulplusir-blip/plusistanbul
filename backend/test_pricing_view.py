#!/usr/bin/env python
"""
Test AgentPricingPreviewView with proper DRF request
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

def test_pricing_view():
    """Test AgentPricingPreviewView"""
    
    print("🧪 Testing AgentPricingPreviewView...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='test_pricing_agent',
            defaults={
                'email': 'test_pricing_agent@example.com',
                'role': 'agent',
                'is_active': True
            }
        )
        
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
        
        # Test with APIRequestFactory (proper DRF request)
        factory = APIRequestFactory()
        
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
        
        # Create DRF request
        request = factory.post('/agents/pricing/preview/', 
                              data=request_data,
                              format='json')
        force_authenticate(request, user=agent)
        
        # Manually set user for WSGI request
        request.user = agent
        
        # Test the view
        view = AgentPricingPreviewView()
        response = view.post(request)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Success!")
            print(f"📋 Response Data: {response.data}")
        else:
            print(f"❌ Error: {response.data}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_pricing_view()
    sys.exit(0 if success else 1)
