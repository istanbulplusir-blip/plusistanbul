#!/usr/bin/env python
"""
Test script for agent transfer pricing functionality
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing
from agents.pricing_service import AgentPricingService
from users.models import User

def test_agent_transfer_pricing():
    """Test agent transfer pricing calculation"""
    
    print("🧪 Testing Agent Transfer Pricing...")
    
    try:
        # Get a test route
        route = TransferRoute.objects.filter(is_active=True).first()
        if not route:
            print("❌ No active transfer routes found")
            return False
            
        print(f"📍 Testing route: {route.origin} → {route.destination}")
        
        # Get pricing for this route
        pricing = TransferRoutePricing.objects.filter(route=route, is_active=True).first()
        if not pricing:
            print("❌ No pricing found for this route")
            return False
            
        print(f"🚗 Testing vehicle: {pricing.vehicle_name} ({pricing.vehicle_type})")
        print(f"💰 Base price: ${pricing.base_price}")
        print(f"👥 Max passengers: {pricing.max_passengers}")
        
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='test_agent',
            defaults={
                'email': 'test_agent@example.com',
                'role': 'agent',
                'is_active': True
            }
        )
        
        if created:
            print("👤 Created test agent user")
        else:
            print("👤 Using existing test agent user")
        
        # Test pricing calculation with different passenger counts
        test_cases = [
            {'passengers': 1, 'expected_behavior': 'should_work'},
            {'passengers': pricing.max_passengers, 'expected_behavior': 'should_work'},
            {'passengers': pricing.max_passengers + 1, 'expected_behavior': 'should_fail'},
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {test_case['passengers']} passengers")
            
            try:
                result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route,
                    vehicle_type=pricing.vehicle_type,
                    agent=agent,
                    passenger_count=test_case['passengers'],
                    trip_type='one_way'
                )
                
                if test_case['expected_behavior'] == 'should_work':
                    print(f"✅ SUCCESS: Price calculated = ${result['agent_price']}")
                    print(f"   Base price: ${result['base_price']}")
                    print(f"   Agent price: ${result['agent_price']}")
                    print(f"   Savings: ${result['savings']}")
                else:
                    print(f"❌ UNEXPECTED: Should have failed but didn't")
                    
            except Exception as e:
                if test_case['expected_behavior'] == 'should_fail':
                    print(f"✅ SUCCESS: Correctly failed with error: {str(e)}")
                else:
                    print(f"❌ FAILED: Unexpected error: {str(e)}")
        
        # Test that price doesn't change with passenger count (within capacity)
        print(f"\n🔍 Testing price consistency...")
        
        prices = []
        for passengers in range(1, min(pricing.max_passengers + 1, 5)):
            try:
                result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route,
                    vehicle_type=pricing.vehicle_type,
                    agent=agent,
                    passenger_count=passengers,
                    trip_type='one_way'
                )
                prices.append(result['agent_price'])
                print(f"   {passengers} passengers: ${result['agent_price']}")
            except Exception as e:
                print(f"   {passengers} passengers: ERROR - {str(e)}")
        
        if len(set(prices)) == 1:
            print("✅ SUCCESS: Price is consistent regardless of passenger count")
        else:
            print("❌ FAILED: Price varies with passenger count")
            
        print("\n🎉 Agent Transfer Pricing Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_agent_transfer_pricing()
    sys.exit(0 if success else 1)
