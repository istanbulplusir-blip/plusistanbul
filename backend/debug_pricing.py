#!/usr/bin/env python3
"""
Debug pricing calculation
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing
from agents.models import Agent
from agents.pricing_service import AgentPricingService

def debug_pricing():
    """Debug pricing calculation step by step"""
    
    print("🔍 Debug Pricing Calculation")
    print("=" * 50)
    
    # Get test data
    route = TransferRoute.objects.filter(origin="Tehran Airport", destination="Tehran City Center").first()
    pricing = TransferRoutePricing.objects.filter(route=route, vehicle_type='sedan').first()
    agent = Agent.objects.first()
    
    print(f"📍 Route: {route.origin} → {route.destination}")
    print(f"🚗 Vehicle: {pricing.vehicle_type} (${pricing.base_price})")
    print(f"👤 Agent: {agent.company_name}")
    print(f"🔄 Round Trip Discount Enabled: {route.round_trip_discount_enabled}")
    print(f"🔄 Round Trip Discount %: {route.round_trip_discount_percentage}")
    print()
    
    # Test round trip pricing
    print("🧪 Testing Round Trip Pricing:")
    
    # Step 1: Calculate base pricing
    price_data = pricing.calculate_price(
        hour=3,  # Midnight hour
        return_hour=3,  # Midnight hour
        is_round_trip=True,
        selected_options=[]
    )
    
    print("📊 Base Pricing Calculation:")
    print(f"  Base Price: ${price_data['base_price']}")
    print(f"  Outbound Surcharge: ${price_data['outbound_surcharge']}")
    print(f"  Return Surcharge: ${price_data['return_surcharge']}")
    print(f"  Round Trip Discount: ${price_data['round_trip_discount']}")
    print(f"  Final Price: ${price_data['final_price']}")
    print()
    
    # Step 2: Calculate agent pricing
    result = AgentPricingService.calculate_transfer_price_for_agent(
        route=route,
        vehicle_type=pricing.vehicle_type,
        agent=agent,
        passenger_count=2,
        trip_type='round_trip',
        hour=3,
        return_hour=3,
        selected_options=[]
    )
    
    print("📊 Agent Pricing Calculation:")
    print(f"  Base Price: ${result['base_price']}")
    print(f"  Outbound Surcharge: ${result['price_breakdown'].get('outbound_surcharge', 0)}")
    print(f"  Return Surcharge: ${result['price_breakdown'].get('return_surcharge', 0)}")
    print(f"  Round Trip Discount: ${result['price_breakdown'].get('round_trip_discount', 0)}")
    print(f"  Options Total: ${result['options_total']}")
    print(f"  Agent Total: ${result['agent_total']}")
    print(f"  Agent Commission: ${result['savings']}")
    print(f"  Commission %: {result['savings_percentage']:.1f}%")
    print()
    
    # Manual calculation
    print("🧮 Manual Calculation:")
    base_price = float(pricing.base_price)
    outbound_surcharge = float(route.calculate_time_surcharge(pricing.base_price, 3))
    return_surcharge = float(route.calculate_time_surcharge(pricing.base_price, 3))
    
    print(f"  Base Price: ${base_price}")
    print(f"  + Outbound Surcharge (5%): ${outbound_surcharge}")
    print(f"  + Return Surcharge (5%): ${return_surcharge}")
    print(f"  = Subtotal: ${base_price + outbound_surcharge + return_surcharge}")
    
    # Round trip discount
    total_before_discount = base_price + outbound_surcharge + return_surcharge
    round_trip_discount = total_before_discount * (float(route.round_trip_discount_percentage) / 100)
    print(f"  - Round Trip Discount (15%): ${round_trip_discount}")
    print(f"  = Final Price: ${total_before_discount - round_trip_discount}")
    
    # Agent commission
    final_price = total_before_discount - round_trip_discount
    agent_commission = final_price * 0.12  # 12% commission
    agent_price = final_price - agent_commission
    print(f"  - Agent Commission (12%): ${agent_commission}")
    print(f"  = Customer Pays: ${agent_price}")

if __name__ == "__main__":
    debug_pricing()