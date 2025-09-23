#!/usr/bin/env python3
"""
Test complete flow to see what's happening
"""

import os
import sys
import django
import json
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent
from agents.pricing_service import AgentPricingService

def test_complete_flow():
    """Test complete flow"""
    
    print("🧪 Testing Complete Flow")
    print("=" * 50)
    
    try:
        # Get test data
        route = TransferRoute.objects.filter(origin="Isfahan Airport", destination="Mashhad Airport").first()
        if not route:
            print("❌ Route not found")
            return
            
        pricing = TransferRoutePricing.objects.filter(route=route, vehicle_type='sedan').first()
        if not pricing:
            print("❌ Pricing not found")
            return
            
        agent = Agent.objects.first()
        if not agent:
            print("❌ Agent not found")
            return
            
        print(f"📍 Route: {route.origin} → {route.destination}")
        print(f"🚗 Vehicle: {pricing.vehicle_type}")
        print(f"💰 Base Price: ${pricing.base_price}")
        print()
        
        # Test with options (similar to user's scenario)
        options = TransferOption.objects.filter(is_active=True)[:2]
        selected_options = []
        for option in options:
            selected_options.append({
                'id': str(option.id),
                'quantity': 1,
                'name': option.name,
                'price': float(option.price)
            })
        
        print(f"🎯 Selected Options: {len(selected_options)}")
        for opt in selected_options:
            print(f"  - {opt['name']}: ${opt['price']}")
        print()
        
        # Test pricing calculation (similar to user's scenario)
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=route,
            vehicle_type=pricing.vehicle_type,
            agent=agent,
            passenger_count=2,
            trip_type='one_way',
            hour=19,  # Peak hour (7 PM) - similar to user's 19:33
            selected_options=selected_options
        )
        
        print("📊 Pricing Calculation Results:")
        print(f"  Base Price: ${result['base_price']}")
        print(f"  Outbound Surcharge: ${result['price_breakdown'].get('outbound_surcharge', 0)}")
        print(f"  Options Total: ${result['options_total']}")
        print(f"  Agent Total: ${result['agent_total']}")
        print(f"  Agent Commission: ${result['savings']}")
        print()
        
        # Manual calculation
        base_price = float(pricing.base_price)
        surcharge = float(route.calculate_time_surcharge(pricing.base_price, 19))
        options_total = sum(float(opt['price']) for opt in selected_options)
        subtotal = base_price + surcharge + options_total
        
        print("🧮 Manual Calculation:")
        print(f"  Base Price: ${base_price}")
        print(f"  + Peak Hour Surcharge (10%): ${surcharge}")
        print(f"  + Options Total: ${options_total}")
        print(f"  = Subtotal: ${subtotal}")
        print(f"  - Agent Commission: ${result['savings']}")
        print(f"  = Customer Pays: ${result['agent_total']}")
        print()
        
        # Check if this matches user's scenario
        print("🔍 User's Scenario Analysis:")
        print(f"  User reported base price: $92")
        print(f"  Actual base price: ${result['base_price']}")
        print(f"  User reported final price: $78")
        print(f"  Actual final price: ${result['agent_total']}")
        print()
        
        if result['base_price'] == 92:
            print("✅ Base price matches user's report")
        else:
            print(f"❌ Base price doesn't match user's report")
            print(f"   User reported: $92")
            print(f"   Actual: ${result['base_price']}")
            
        if result['agent_total'] == 78:
            print("✅ Final price matches user's report")
        else:
            print(f"❌ Final price doesn't match user's report")
            print(f"   User reported: $78")
            print(f"   Actual: ${result['agent_total']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_flow()
