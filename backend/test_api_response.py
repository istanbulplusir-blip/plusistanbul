#!/usr/bin/env python3
"""
Test API response to see what's being returned
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

def test_api_response():
    """Test what the API returns"""
    
    print("🧪 Testing API Response")
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
        
        # Test with options
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
        
        # Test pricing calculation
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=route,
            vehicle_type=pricing.vehicle_type,
            agent=agent,
            passenger_count=2,
            trip_type='one_way',
            hour=19,  # Peak hour (7 PM)
            selected_options=selected_options
        )
        
        print("📊 API Response:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        # Check what frontend receives
        print("🔍 Frontend receives:")
        print(f"  base_price: {result['base_price']}")
        print(f"  price_breakdown.outbound_surcharge: {result['price_breakdown'].get('outbound_surcharge', 0)}")
        print(f"  options_total: {result['options_total']}")
        print(f"  agent_total: {result['agent_total']}")
        print(f"  savings: {result['savings']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_response()
