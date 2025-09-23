#!/usr/bin/env python3
"""
Test script with real data to verify pricing calculation
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

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent

def create_test_data():
    """Create test data similar to user's scenario"""
    
    # Create or get route: Isfahan Airport → Mashhad Airport
    route, created = TransferRoute.objects.get_or_create(
        origin="Isfahan Airport",
        destination="Mashhad Airport",
        defaults={
            'distance': 500,
            'duration': 45,
            'is_active': True,
            'peak_hour_surcharge': 10.0,
            'midnight_surcharge': 5.0,
            'round_trip_discount_enabled': True,
            'round_trip_discount_percentage': 15.0
        }
    )
    
    # Create or get pricing for sedan
    pricing, created = TransferRoutePricing.objects.get_or_create(
        route=route,
        vehicle_type='sedan',
        defaults={
            'base_price': Decimal('65.00'),
            'max_passengers': 4,
            'max_luggage': 2,
            'is_active': True
        }
    )
    
    # Create or get agent
    agent, created = Agent.objects.get_or_create(
        company_name="Test Agent Company",
        defaults={
            'license_number': 'TEST123',
            'email': 'test@agent.com',
            'phone': '+989120220122',
            'is_active': True
        }
    )
    
    # Create test options
    option1, created = TransferOption.objects.get_or_create(
        slug='extra-luggage',
        defaults={
            'price': Decimal('2.00'),
            'is_active': True,
            'option_type': 'luggage'
        }
    )
    if created:
        option1.set_current_language('fa')
        option1.name = "چمدان اضافی"
        option1.description = 'حمل چمدان اضافی (بیش از حد مجاز)'
        option1.save()
    
    option2, created = TransferOption.objects.get_or_create(
        slug='child-seat',
        defaults={
            'price': Decimal('15.00'),
            'is_active': True,
            'option_type': 'safety'
        }
    )
    if created:
        option2.set_current_language('en')
        option2.name = "Child Seat"
        option2.description = 'Child safety seat for children under 4 years'
        option2.save()
    
    return route, pricing, agent, [option1, option2]

def test_real_pricing():
    """Test pricing with real data"""
    
    print("🧪 Testing Real Pricing Calculation")
    print("=" * 50)
    
    try:
        # Create test data
        route, pricing, agent, options = create_test_data()
        
        print(f"📍 Route: {route.origin} → {route.destination}")
        print(f"🚗 Vehicle: {pricing.vehicle_type}")
        print(f"💰 Base Price: ${pricing.base_price}")
        print(f"👤 Agent: {agent.company_name}")
        print()
        
        # Test with options
        selected_options = [
            {'id': str(options[0].id), 'quantity': 1, 'name': options[0].name, 'price': float(options[0].price)},
            {'id': str(options[1].id), 'quantity': 1, 'name': options[1].name, 'price': float(options[1].price)}
        ]
        
        from agents.pricing_service import AgentPricingService
        
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
        options_total = float(options[0].price) + float(options[1].price)
        subtotal = base_price + surcharge + options_total
        
        print("🧮 Manual Calculation:")
        print(f"  Base Price: ${base_price}")
        print(f"  + Peak Hour Surcharge (10%): ${surcharge}")
        print(f"  + Options Total: ${options_total}")
        print(f"  = Subtotal: ${subtotal}")
        print(f"  - Agent Commission: ${result['savings']}")
        print(f"  = Customer Pays: ${result['agent_total']}")
        print()
        
        # Verify calculations
        expected_base = base_price
        actual_base = result['base_price']
        
        if abs(expected_base - actual_base) < 0.01:
            print("✅ Base price calculation is CORRECT")
        else:
            print(f"❌ Base price calculation is WRONG")
            print(f"   Expected: ${expected_base}")
            print(f"   Actual: ${actual_base}")
            
        expected_surcharge = surcharge
        actual_surcharge = result['price_breakdown'].get('outbound_surcharge', 0)
        
        if abs(expected_surcharge - actual_surcharge) < 0.01:
            print("✅ Surcharge calculation is CORRECT")
        else:
            print(f"❌ Surcharge calculation is WRONG")
            print(f"   Expected: ${expected_surcharge}")
            print(f"   Actual: ${actual_surcharge}")
            
        expected_options = options_total
        actual_options = result['options_total']
        
        if abs(expected_options - actual_options) < 0.01:
            print("✅ Options calculation is CORRECT")
        else:
            print(f"❌ Options calculation is WRONG")
            print(f"   Expected: ${expected_options}")
            print(f"   Actual: ${actual_options}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_pricing()
