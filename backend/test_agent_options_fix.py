#!/usr/bin/env python
"""
Test script for agent transfer options fix
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferOption
from agents.views import AgentTransferRoutesView
from django.test import RequestFactory
from django.db.models import Q
from users.models import User

def test_agent_options_fix():
    """Test that agent API now returns options"""
    
    print("🧪 Testing Agent Transfer Options Fix...")
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='test_agent_options',
            defaults={
                'email': 'test_agent_options@example.com',
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
            
            print(f"✅ Agent API returned {len(routes)} routes")
            
            # Find Isfahan route
            isfahan_route = None
            for route in routes:
                if 'Isfahan Airport' in route.get('origin', '') and 'Isfahan City Center' in route.get('destination', ''):
                    isfahan_route = route
                    break
            
            if isfahan_route:
                print(f"📍 Found Isfahan route: {isfahan_route['origin']} → {isfahan_route['destination']}")
                
                # Check if options are included
                options = isfahan_route.get('options', [])
                print(f"🎯 Route has {len(options)} options")
                
                if len(options) > 0:
                    print("✅ SUCCESS: Agent API now returns options!")
                    for option in options[:3]:  # Show first 3 options
                        print(f"   - {option['name']}: ${option['price']} ({option['option_type']})")
                else:
                    print("❌ FAILED: No options returned")
                    
                # Check if options match database
                route_obj = TransferRoute.objects.get(id=isfahan_route['id'])
                db_options = TransferOption.objects.filter(
                    Q(route=route_obj, is_active=True) | Q(route__isnull=True, is_active=True)
                )
                print(f"📊 Database has {db_options.count()} options for this route")
                
                if len(options) == db_options.count():
                    print("✅ SUCCESS: Options count matches database")
                else:
                    print("❌ FAILED: Options count doesn't match database")
                    
            else:
                print("❌ FAILED: Isfahan route not found")
                
        else:
            print(f"❌ FAILED: API returned status {response.status_code}")
            
        print("\n🎉 Agent Transfer Options Fix Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_agent_options_fix()
    sys.exit(0 if success else 1)
