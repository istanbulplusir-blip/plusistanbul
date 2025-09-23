#!/usr/bin/env python
"""
Final test for agent transfer booking fix
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

def test_final_fix():
    """Test the final fix for agent transfer booking"""
    
    print("🧪 Testing Final Agent Transfer Booking Fix...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='final_test_agent',
            defaults={
                'email': 'final_test_agent@example.com',
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
                
                # Check vehicles
                vehicles_api = isfahan_route.get('vehicle_types', [])
                print(f"\n🚗 Vehicles from Agent API: {len(vehicles_api)}")
                for i, vehicle in enumerate(vehicles_api, 1):
                    print(f"   {i}. {vehicle['name']} ({vehicle['type']}) - ${vehicle['base_price']}")
                
                # Check options
                options_api = isfahan_route.get('options', [])
                print(f"\n🎯 Options from Agent API: {len(options_api)}")
                for i, option in enumerate(options_api[:5], 1):  # Show first 5 options
                    print(f"   {i}. {option['name']} - ${option['price']} ({option['option_type']})")
                if len(options_api) > 5:
                    print(f"   ... and {len(options_api) - 5} more options")
                
                # Verify the fix
                if len(vehicles_api) == 3:
                    print(f"\n✅ SUCCESS: Correct number of vehicles ({len(vehicles_api)})")
                else:
                    print(f"\n❌ FAILED: Wrong number of vehicles ({len(vehicles_api)})")
                
                if len(options_api) >= 10:
                    print(f"✅ SUCCESS: Options are available ({len(options_api)})")
                else:
                    print(f"❌ FAILED: Not enough options ({len(options_api)})")
                
                # Check if the route has the expected structure
                required_fields = ['id', 'origin', 'destination', 'vehicle_types', 'options']
                missing_fields = [field for field in required_fields if field not in isfahan_route]
                
                if not missing_fields:
                    print(f"✅ SUCCESS: Route has all required fields")
                else:
                    print(f"❌ FAILED: Missing fields: {missing_fields}")
                    
            else:
                print("❌ FAILED: Isfahan route not found")
                
        else:
            print(f"❌ FAILED: API returned status {response.status_code}")
            
        print("\n🎉 Final Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_final_fix()
    sys.exit(0 if success else 1)
