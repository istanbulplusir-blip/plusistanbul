#!/usr/bin/env python3
"""
Comprehensive test scenarios for transfer pricing
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
from agents.models import Agent, AgentProfile, AgentPricingRule
from agents.pricing_service import AgentPricingService

def create_test_data():
    """Create comprehensive test data"""
    
    # Create test route
    route, created = TransferRoute.objects.get_or_create(
        origin="Tehran Airport",
        destination="Tehran City Center",
        defaults={
            'distance': 30,
            'duration': 45,
            'is_active': True,
            'peak_hour_surcharge': 10.0,
            'midnight_surcharge': 5.0,
            'round_trip_discount_enabled': True,
            'round_trip_discount_percentage': 15.0
        }
    )
    
    # Create pricing for different vehicle types
    vehicle_types = [
        ('sedan', 'Economy Sedan', Decimal('30.00'), 4),
        ('suv', 'SUV', Decimal('45.00'), 6),
        ('van', 'Van', Decimal('60.00'), 8),
        ('sprinter', 'Sprinter', Decimal('80.00'), 12)
    ]
    
    pricings = {}
    for vehicle_type, name, price, capacity in vehicle_types:
        pricing, created = TransferRoutePricing.objects.get_or_create(
            route=route,
            vehicle_type=vehicle_type,
            defaults={
                'base_price': price,
                'max_passengers': capacity,
                'max_luggage': 2,
                'is_active': True
            }
        )
        pricings[vehicle_type] = pricing
    
    # Create test agent
    agent, created = Agent.objects.get_or_create(
        company_name="Test Agent Company",
        defaults={
            'license_number': 'TEST123',
            'email': 'test@agent.com',
            'phone': '+989120220122',
            'is_active': True
        }
    )
    
    # Create agent profile with pricing rules (if needed)
    # Note: AgentProfile is linked to User, not Agent directly
    # We'll use AgentPricingRule instead
    
    # Note: AgentPricingRule is linked to User, not Agent directly
    # We'll test without specific pricing rules for now
    
    # Create test options
    options = []
    option_data = [
        ('child-seat', 'Child Seat', Decimal('15.00'), 'safety'),
        ('extra-luggage', 'Extra Luggage', Decimal('5.00'), 'luggage'),
        ('english-driver', 'English Driver', Decimal('10.00'), 'service'),
        ('wifi', 'WiFi', Decimal('8.00'), 'service')
    ]
    
    for slug, name, price, option_type in option_data:
        option, created = TransferOption.objects.get_or_create(
            slug=slug,
            defaults={
                'price': price,
                'is_active': True,
                'option_type': option_type
            }
        )
        if created:
            option.set_current_language('en')
            option.name = name
            option.description = f'{name} service'
            option.save()
        options.append(option)
    
    return route, pricings, agent, options

def test_scenario(scenario_name, route, pricing, agent, options, selected_options=None, **kwargs):
    """Test a specific scenario"""
    
    print(f"\n🧪 {scenario_name}")
    print("=" * 60)
    
    # Prepare selected options
    selected_options_list = []
    if selected_options:
        for option_slug, quantity in selected_options:
            option = next((opt for opt in options if opt.slug == option_slug), None)
            if option:
                # Get option name safely
                try:
                    option_name = option.name
                except:
                    option_name = f"Option {option.slug}"
                
                selected_options_list.append({
                    'id': str(option.id),
                    'quantity': quantity,
                    'name': option_name,
                    'price': float(option.price)
                })
    
    # Calculate pricing
    result = AgentPricingService.calculate_transfer_price_for_agent(
        route=route,
        vehicle_type=pricing.vehicle_type,
        agent=agent,
        passenger_count=kwargs.get('passengers', 2),
        trip_type=kwargs.get('trip_type', 'one_way'),
        hour=kwargs.get('hour'),
        return_hour=kwargs.get('return_hour'),
        selected_options=selected_options_list
    )
    
    # Display results
    print(f"📍 Route: {route.origin} → {route.destination}")
    print(f"🚗 Vehicle: {pricing.vehicle_type} (${pricing.base_price})")
    print(f"👥 Passengers: {kwargs.get('passengers', 2)}")
    print(f"🔄 Trip Type: {kwargs.get('trip_type', 'one_way')}")
    
    if kwargs.get('hour'):
        print(f"⏰ Outbound Time: {kwargs['hour']}:00")
    if kwargs.get('return_hour'):
        print(f"⏰ Return Time: {kwargs['return_hour']}:00")
    
    if selected_options_list:
        print(f"🎯 Options: {len(selected_options_list)}")
        for opt in selected_options_list:
            print(f"   - {opt['name']}: ${opt['price']} × {opt['quantity']}")
    
    print(f"\n📊 Pricing Results:")
    print(f"   Base Price: ${result['base_price']}")
    print(f"   Outbound Surcharge: ${result['price_breakdown'].get('outbound_surcharge', 0)}")
    print(f"   Return Surcharge: ${result['price_breakdown'].get('return_surcharge', 0)}")
    print(f"   Round Trip Discount: ${result['price_breakdown'].get('round_trip_discount', 0)}")
    print(f"   Options Total: ${result['options_total']}")
    print(f"   Agent Total: ${result['agent_total']}")
    print(f"   Agent Commission: ${result['savings']}")
    print(f"   Commission %: {result['savings_percentage']:.1f}%")
    
    return result

def run_all_scenarios():
    """Run all test scenarios"""
    
    print("🚀 Transfer Pricing Test Scenarios")
    print("=" * 80)
    
    # Create test data
    route, pricings, agent, options = create_test_data()
    
    # Scenario 1: One way trip, no surcharge, no options
    test_scenario(
        "Scenario 1: One Way Trip - No Surcharge - No Options",
        route, pricings['sedan'], agent, options,
        trip_type='one_way',
        hour=12,  # Normal hour
        passengers=2
    )
    
    # Scenario 2: One way trip, peak hour surcharge, no options
    test_scenario(
        "Scenario 2: One Way Trip - Peak Hour Surcharge - No Options",
        route, pricings['sedan'], agent, options,
        trip_type='one_way',
        hour=8,  # Peak hour
        passengers=2
    )
    
    # Scenario 3: One way trip, midnight surcharge, with options
    test_scenario(
        "Scenario 3: One Way Trip - Midnight Surcharge - With Options",
        route, pricings['sedan'], agent, options,
        trip_type='one_way',
        hour=3,  # Midnight hour
        passengers=2,
        selected_options=[('child-seat', 1), ('extra-luggage', 1)]
    )
    
    # Scenario 4: Round trip, no surcharge, no options
    test_scenario(
        "Scenario 4: Round Trip - No Surcharge - No Options",
        route, pricings['sedan'], agent, options,
        trip_type='round_trip',
        hour=12,  # Normal hour
        return_hour=14,  # Normal hour
        passengers=2
    )
    
    # Scenario 5: Round trip, with surcharges, with options, with discount
    test_scenario(
        "Scenario 5: Round Trip - With Surcharges - With Options - With Discount",
        route, pricings['sedan'], agent, options,
        trip_type='round_trip',
        hour=3,  # Midnight hour
        return_hour=3,  # Midnight hour
        passengers=2,
        selected_options=[('child-seat', 2), ('english-driver', 1)]
    )
    
    # Scenario 6: Different vehicle types
    for vehicle_type in ['suv', 'van', 'sprinter']:
        test_scenario(
            f"Scenario 6: {vehicle_type.upper()} - Round Trip - Peak Hours",
            route, pricings[vehicle_type], agent, options,
            trip_type='round_trip',
            hour=8,  # Peak hour
            return_hour=18,  # Peak hour
            passengers=4,
            selected_options=[('wifi', 1)]
        )
    
    # Scenario 7: High passenger count
    test_scenario(
        "Scenario 7: High Passenger Count - Sprinter - Multiple Options",
        route, pricings['sprinter'], agent, options,
        trip_type='round_trip',
        hour=10,  # Normal hour
        return_hour=16,  # Normal hour
        passengers=10,
        selected_options=[('child-seat', 3), ('extra-luggage', 2), ('english-driver', 1), ('wifi', 1)]
    )

if __name__ == "__main__":
    run_all_scenarios()
