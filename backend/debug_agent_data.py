#!/usr/bin/env python
"""
Debug script to check agent API data vs database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.views import AgentTransferRoutesView
from django.test import RequestFactory
from django.db.models import Q
from users.models import User

def debug_agent_data():
    """Debug agent API data vs database"""
    
    print("🔍 Debugging Agent API Data vs Database...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='debug_agent',
            defaults={
                'email': 'debug_agent@example.com',
                'role': 'agent',
                'is_active': True
            }
        )
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/agents/transfers/routes/')
        request.user = agent
        
        # Test the view
        view = AgentTransferRoutesView()
        response = view.get(request)
        
        if response.status_code == 200:
            data = response.data
            routes = data.get('routes', [])
            
            print(f"📊 Agent API returned {len(routes)} routes")
            
            # Find Isfahan route
            isfahan_route = None
            for route in routes:
                if 'Isfahan Airport' in route.get('origin', '') and 'Isfahan City Center' in route.get('destination', ''):
                    isfahan_route = route
                    break
            
            if isfahan_route:
                print(f"\n📍 Found Isfahan route: {isfahan_route['origin']} → {isfahan_route['destination']}")
                print(f"🆔 Route ID: {isfahan_route['id']}")
                
                # Check vehicles from API
                vehicles_api = isfahan_route.get('vehicle_types', [])
                print(f"\n🚗 Vehicles from Agent API: {len(vehicles_api)}")
                for i, vehicle in enumerate(vehicles_api, 1):
                    print(f"   {i}. {vehicle['name']} ({vehicle['type']}) - ${vehicle['base_price']}")
                
                # Check vehicles from database
                route_obj = TransferRoute.objects.get(id=isfahan_route['id'])
                vehicles_db = TransferRoutePricing.objects.filter(route=route_obj, is_active=True)
                print(f"\n🗄️ Vehicles from Database: {vehicles_db.count()}")
                for i, vehicle in enumerate(vehicles_db, 1):
                    print(f"   {i}. {vehicle.vehicle_name} ({vehicle.vehicle_type}) - ${vehicle.base_price}")
                
                # Check options from API
                options_api = isfahan_route.get('options', [])
                print(f"\n🎯 Options from Agent API: {len(options_api)}")
                for i, option in enumerate(options_api, 1):
                    print(f"   {i}. {option['name']} - ${option['price']} ({option['option_type']})")
                
                # Check options from database
                options_db = TransferOption.objects.filter(
                    Q(route=route_obj, is_active=True) | Q(route__isnull=True, is_active=True)
                )
                print(f"\n🗄️ Options from Database: {options_db.count()}")
                for i, option in enumerate(options_db, 1):
                    try:
                        name = getattr(option, 'name', None) or f"Option {option.id}"
                        print(f"   {i}. {name} - ${option.price} ({option.option_type})")
                    except Exception as e:
                        print(f"   {i}. Option {option.id} - ${option.price} ({option.option_type}) [Translation Error]")
                
                # Check if there's a mismatch
                if len(vehicles_api) != vehicles_db.count():
                    print(f"\n❌ VEHICLE COUNT MISMATCH!")
                    print(f"   API: {len(vehicles_api)} vehicles")
                    print(f"   DB: {vehicles_db.count()} vehicles")
                else:
                    print(f"\n✅ Vehicle count matches: {len(vehicles_api)}")
                
                if len(options_api) != options_db.count():
                    print(f"\n❌ OPTIONS COUNT MISMATCH!")
                    print(f"   API: {len(options_api)} options")
                    print(f"   DB: {options_db.count()} options")
                else:
                    print(f"\n✅ Options count matches: {len(options_api)}")
                    
            else:
                print("❌ Isfahan route not found in API response")
                
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.data}")
            
        print("\n🎉 Debug completed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_agent_data()
    sys.exit(0 if success else 1)
