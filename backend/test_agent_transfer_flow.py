#!/usr/bin/env python
"""
Comprehensive test for agent transfer booking flow
Tests the complete flow from route selection to pricing calculation
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.views import AgentTransferRoutesView, AgentPricingPreviewView
from django.test import RequestFactory
from django.db.models import Q
from users.models import User
from django.contrib.auth import get_user_model

def test_agent_transfer_flow():
    """Test the complete agent transfer booking flow"""
    
    print("🧪 Testing Complete Agent Transfer Booking Flow...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='flow_test_agent',
            defaults={
                'email': 'flow_test_agent@example.com',
                'role': 'agent',
                'is_active': True
            }
        )
        
        print(f"👤 Created test agent: {agent.username}")
        
        # Step 1: Test route selection
        print("\n📍 Step 1: Testing Route Selection...")
        factory = RequestFactory()
        request = factory.get('/agents/transfers/routes/')
        request.user = agent
        
        view = AgentTransferRoutesView()
        response = view.get(request)
        
        if response.status_code != 200:
            print(f"❌ Route selection failed: {response.status_code}")
            return False
            
        data = response.data
        routes = data.get('routes', [])
        print(f"✅ Found {len(routes)} routes")
        
        # Find Isfahan route
        isfahan_route = None
        for route in routes:
            if 'Isfahan Airport' in route.get('origin', '') and 'Isfahan City Center' in route.get('destination', ''):
                isfahan_route = route
                break
        
        if not isfahan_route:
            print("❌ Isfahan route not found")
            return False
            
        print(f"✅ Found Isfahan route: {isfahan_route['origin']} → {isfahan_route['destination']}")
        
        # Step 2: Test vehicle selection
        print("\n🚗 Step 2: Testing Vehicle Selection...")
        vehicles = isfahan_route.get('vehicle_types', [])
        print(f"✅ Found {len(vehicles)} vehicles")
        
        for i, vehicle in enumerate(vehicles, 1):
            print(f"   {i}. {vehicle['name']} ({vehicle['type']}) - ${vehicle['base_price']}")
        
        # Select first vehicle
        selected_vehicle = vehicles[0]
        print(f"✅ Selected vehicle: {selected_vehicle['name']}")
        
        # Step 3: Test options
        print("\n🎯 Step 3: Testing Options...")
        options = isfahan_route.get('options', [])
        print(f"✅ Found {len(options)} options")
        
        for i, option in enumerate(options[:3], 1):  # Show first 3
            print(f"   {i}. {option['name']} - ${option['price']} ({option['option_type']})")
        
        # Step 4: Test pricing calculation
        print("\n💰 Step 4: Testing Pricing Calculation...")
        
        # Test pricing with different scenarios
        test_scenarios = [
            {
                'name': 'Basic Transfer',
                'passenger_count': 2,
                'luggage_count': 1,
                'trip_type': 'one_way',
                'selected_options': []
            },
            {
                'name': 'Transfer with Options',
                'passenger_count': 4,
                'luggage_count': 2,
                'trip_type': 'one_way',
                'selected_options': [{'option_id': options[0]['id'], 'quantity': 1}] if options else []
            },
            {
                'name': 'Round Trip',
                'passenger_count': 3,
                'luggage_count': 1,
                'trip_type': 'round_trip',
                'selected_options': []
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n   Testing: {scenario['name']}")
            
            # Test pricing calculation directly using the service
            from agents.pricing_service import AgentPricingService
            from transfers.models import TransferRoute
            
            try:
                route_obj = TransferRoute.objects.get(id=isfahan_route['id'])
                
                # Debug: Check what we're passing
                print(f"      Debug: route_id={isfahan_route['id']}")
                print(f"      Debug: vehicle_type={selected_vehicle['type']}")
                print(f"      Debug: passenger_count={scenario['passenger_count']}")
                print(f"      Debug: selected_options={scenario['selected_options']}")
                
                # Calculate pricing using the service
                pricing_result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route_obj,
                    vehicle_type=selected_vehicle['type'],
                    agent=agent,
                    passenger_count=scenario['passenger_count'],
                    trip_type=scenario['trip_type'],
                    selected_options=scenario['selected_options']
                )
                
                print(f"   ✅ Pricing calculated successfully")
                print(f"      Base Price: ${pricing_result.get('base_price', 0)}")
                print(f"      Agent Price: ${pricing_result.get('agent_price', 0)}")
                print(f"      Options Total: ${pricing_result.get('price_breakdown', {}).get('options_total', 0)}")
                print(f"      Final Total: ${pricing_result.get('total', 0)}")
                
            except Exception as e:
                print(f"   ❌ Pricing calculation failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        # Step 5: Test validation
        print("\n✅ Step 5: Testing Validation...")
        
        # Test invalid passenger count
        try:
            route_obj = TransferRoute.objects.get(id=isfahan_route['id'])
            
            # This should fail because passenger count exceeds vehicle capacity
            AgentPricingService.calculate_transfer_price_for_agent(
                route=route_obj,
                vehicle_type=selected_vehicle['type'],
                agent=agent,
                passenger_count=20,  # More than vehicle capacity
                trip_type='one_way',
                selected_options=[]
            )
            print("   ❌ Validation failed: Should reject invalid passenger count")
            return False
            
        except Exception as e:
            if "ظرفیت" in str(e) or "capacity" in str(e).lower():
                print("   ✅ Validation working: Rejected invalid passenger count")
            else:
                print(f"   ❌ Unexpected error: {str(e)}")
                return False
        
        print("\n🎉 All tests passed! Agent transfer flow is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_agent_transfer_flow()
    sys.exit(0 if success else 1)
