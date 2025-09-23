#!/usr/bin/env python
"""
Debug pricing request to see what data is being sent
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing
from agents.views import AgentPricingPreviewView
from django.test import RequestFactory
from users.models import User

def debug_pricing_request():
    """Debug pricing request"""
    
    print("🔍 Debugging Pricing Request...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='debug_pricing_agent',
            defaults={
                'email': 'debug_pricing_agent@example.com',
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
        print(f"🆔 Route ID: {route.id} (Type: {type(route.id)})")
        
        # Test different route_id formats
        test_cases = [
            {
                'name': 'String route_id',
                'route_id': str(route.id),
                'vehicle_type': 'sedan'
            },
            {
                'name': 'UUID route_id',
                'route_id': route.id,
                'vehicle_type': 'sedan'
            },
            {
                'name': 'Invalid route_id',
                'route_id': 'invalid-id',
                'vehicle_type': 'sedan'
            }
        ]
        
        factory = RequestFactory()
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            print(f"   Route ID: {test_case['route_id']} (Type: {type(test_case['route_id'])})")
            
            # Create request
            request_data = {
                'product_type': 'transfer',
                'route_id': test_case['route_id'],
                'vehicle_type': test_case['vehicle_type'],
                'passenger_count': 2,
                'trip_type': 'one_way',
                'booking_time': '09:32',
                'selected_options': []
            }
            
            # Test the service directly
            from agents.pricing_service import AgentPricingService
            
            try:
                if test_case['route_id'] == 'invalid-id':
                    print(f"   ❌ Expected error for invalid route_id")
                    continue
                    
                # Convert string route_id to UUID if needed
                route_id = test_case['route_id']
                if isinstance(route_id, str):
                    try:
                        import uuid
                        route_id = uuid.UUID(route_id)
                    except ValueError:
                        print(f"   ❌ Invalid UUID format")
                        continue
                
                # Get route object
                route_obj = TransferRoute.objects.get(id=route_id)
                
                # Test pricing calculation
                result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route_obj,
                    vehicle_type=test_case['vehicle_type'],
                    agent=agent,
                    passenger_count=2,
                    trip_type='one_way',
                    hour=9,  # 09:32
                    selected_options=[]
                )
                
                print(f"   ✅ Success: ${result.get('total', 0)}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_pricing_request()
    sys.exit(0 if success else 1)
