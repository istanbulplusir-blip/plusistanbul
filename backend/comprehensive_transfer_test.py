#!/usr/bin/env python
"""
Comprehensive test for transfer pricing with time surcharges, round trip discounts, and options
Tests the complete pricing calculation including all components
"""

import os
import sys
import django
from datetime import datetime, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.pricing_service import AgentPricingService
from users.models import User

def test_comprehensive_transfer_pricing():
    """Test comprehensive transfer pricing with all components"""
    
    print("🧪 Comprehensive Transfer Pricing Test")
    print("=" * 60)
    
    try:
        # Create a test agent user
        agent, created = User.objects.get_or_create(
            username='comprehensive_test_agent',
            defaults={
                'email': 'comprehensive_test_agent@example.com',
                'role': 'agent',
                'is_active': True
            }
        )
        
        print(f"👤 Test Agent: {agent.username}")
        
        # Get Isfahan route
        route = TransferRoute.objects.filter(
            origin__icontains='Isfahan Airport',
            destination__icontains='Isfahan City Center'
        ).first()
        
        if not route:
            print("❌ Isfahan route not found")
            return False
            
        print(f"📍 Route: {route.origin} → {route.destination}")
        print(f"🕐 Round Trip Discount Enabled: {route.round_trip_discount_enabled}")
        print(f"💰 Round Trip Discount: {route.round_trip_discount_percentage}%")
        
        # Get SUV pricing
        suv_pricing = TransferRoutePricing.objects.filter(
            route=route,
            vehicle_type='suv'
        ).first()
        
        if not suv_pricing:
            print("❌ SUV pricing not found")
            return False
            
        print(f"🚗 Vehicle: {suv_pricing.vehicle_name} ({suv_pricing.vehicle_type})")
        print(f"💰 Base Price: ${suv_pricing.base_price}")
        print(f"👥 Max Passengers: {suv_pricing.max_passengers}")
        
        # Get available options
        options = TransferOption.objects.filter(
            route=route,
            is_active=True
        )[:5]  # Get first 5 options
        
        print(f"\n🎯 Available Options ({options.count()}):")
        for i, option in enumerate(options, 1):
            try:
                name = getattr(option, 'name', None) or f"Option {option.id}"
                print(f"   {i}. {name} - ${option.price} ({option.option_type})")
            except Exception as e:
                print(f"   {i}. Option {option.id} - ${option.price} ({option.option_type}) [Translation Error]")
        
        # Test scenarios
        test_scenarios = [
            {
                'name': 'Basic One-Way Transfer (Normal Time)',
                'passenger_count': 2,
                'luggage_count': 1,
                'trip_type': 'one_way',
                'booking_time': time(14, 0),  # 2 PM - normal time
                'return_time': None,
                'selected_options': [],
                'expected_components': ['base_price', 'outbound_surcharge']
            },
            {
                'name': 'One-Way Transfer (Peak Time - 10% surcharge)',
                'passenger_count': 2,
                'luggage_count': 1,
                'trip_type': 'one_way',
                'booking_time': time(22, 0),  # 10 PM - peak time
                'return_time': None,
                'selected_options': [],
                'expected_components': ['base_price', 'outbound_surcharge']
            },
            {
                'name': 'Round Trip (Normal + Peak Time + Discount)',
                'passenger_count': 2,
                'luggage_count': 1,
                'trip_type': 'round_trip',
                'booking_time': time(14, 0),  # 2 PM - normal time
                'return_time': time(6, 0),    # 6 AM - peak time
                'selected_options': [],
                'expected_components': ['base_price', 'outbound_surcharge', 'return_surcharge', 'round_trip_discount']
            },
            {
                'name': 'Round Trip with Options (Peak Times + Discount + Options)',
                'passenger_count': 4,
                'luggage_count': 2,
                'trip_type': 'round_trip',
                'booking_time': time(22, 0),  # 10 PM - peak time
                'return_time': time(6, 0),    # 6 AM - peak time
                'selected_options': [
                    {'option_id': str(options[0].id), 'quantity': 1} if options.count() > 0 else None,
                    {'option_id': str(options[1].id), 'quantity': 1} if options.count() > 1 else None,
                    {'option_id': str(options[2].id), 'quantity': 1} if options.count() > 2 else None,
                ],
                'expected_components': ['base_price', 'outbound_surcharge', 'return_surcharge', 'round_trip_discount', 'options_total']
            }
        ]
        
        # Filter out None options
        for scenario in test_scenarios:
            scenario['selected_options'] = [opt for opt in scenario['selected_options'] if opt is not None]
        
        print(f"\n🧮 Testing {len(test_scenarios)} Scenarios:")
        print("=" * 60)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['name']}")
            print("-" * 50)
            
            # Test direct pricing calculation
            print("🔍 Direct Pricing Calculation:")
            try:
                price_data = suv_pricing._calculate_transfer_price(
                    hour=scenario['booking_time'].hour,
                    return_hour=scenario['return_time'].hour if scenario['return_time'] else None,
                    is_round_trip=(scenario['trip_type'] == 'round_trip'),
                    selected_options=scenario['selected_options']
                )
                
                print(f"   Base Price: ${price_data['base_price']}")
                print(f"   Outbound Surcharge: ${price_data['outbound_surcharge']}")
                print(f"   Return Surcharge: ${price_data['return_surcharge']}")
                print(f"   Round Trip Discount: ${price_data['round_trip_discount']}")
                print(f"   Options Total: ${price_data['options_total']}")
                print(f"   Subtotal: ${price_data['subtotal']}")
                print(f"   Final Price: ${price_data['final_price']}")
                
                # Check if all expected components are present
                missing_components = []
                for component in scenario['expected_components']:
                    if component not in price_data:
                        missing_components.append(component)
                
                if missing_components:
                    print(f"   ⚠️  Missing components: {missing_components}")
                else:
                    print(f"   ✅ All expected components present")
                
            except Exception as e:
                print(f"   ❌ Direct pricing failed: {str(e)}")
                continue
            
            # Test agent pricing
            print("\n👤 Agent Pricing Calculation:")
            try:
                agent_result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route,
                    vehicle_type='suv',
                    agent=agent,
                    passenger_count=scenario['passenger_count'],
                    trip_type=scenario['trip_type'],
                    hour=scenario['booking_time'].hour,
                    return_hour=scenario['return_time'].hour if scenario['return_time'] else None,
                    selected_options=scenario['selected_options']
                )
                
                print(f"   Base Price: ${agent_result.get('base_price', 0)}")
                print(f"   Agent Price: ${agent_result.get('agent_price', 0)}")
                print(f"   Total: ${agent_result.get('total', 0)}")
                print(f"   Savings: ${agent_result.get('savings', 0)}")
                print(f"   Savings %: {agent_result.get('savings_percentage', 0)}%")
                
                # Check price breakdown
                breakdown = agent_result.get('price_breakdown', {})
                print(f"   Price Breakdown:")
                print(f"     - Outbound Surcharge: ${breakdown.get('outbound_surcharge', 0)}")
                print(f"     - Return Surcharge: ${breakdown.get('return_surcharge', 0)}")
                print(f"     - Round Trip Discount: ${breakdown.get('round_trip_discount', 0)}")
                print(f"     - Options Total: ${breakdown.get('options_total', 0)}")
                
                # Verify pricing logic
                expected_base = price_data['final_price']
                actual_agent = agent_result.get('agent_price', 0)
                
                if abs(expected_base - actual_agent) < 0.01:
                    print(f"   ✅ Agent pricing matches direct calculation")
                else:
                    print(f"   ⚠️  Agent pricing differs: Expected ${expected_base}, Got ${actual_agent}")
                
            except Exception as e:
                print(f"   ❌ Agent pricing failed: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Test the specific scenario mentioned by user
        print(f"\n🎯 User's Specific Scenario Test:")
        print("=" * 60)
        print("Isfahan Airport → Isfahan City Center")
        print("Vehicle: SUV")
        print("Outbound: Sep 17, 22:00 (Peak Time - 10% surcharge)")
        print("Return: Sep 18, 06:00 (Peak Time - 5% surcharge)")
        print("Round Trip Discount: 10%")
        print("Options: 3 options totaling $14")
        
        try:
            # Test with peak times
            user_options = []
            if options.count() > 0:
                user_options.append({'option_id': str(options[0].id), 'quantity': 1})
            if options.count() > 1:
                user_options.append({'option_id': str(options[1].id), 'quantity': 1})
            if options.count() > 2:
                user_options.append({'option_id': str(options[2].id), 'quantity': 1})
            
            user_scenario_result = suv_pricing._calculate_transfer_price(
                hour=22,  # 10 PM - peak time
                return_hour=6,  # 6 AM - peak time
                is_round_trip=True,
                selected_options=user_options
            )
            
            # Filter out None options
            user_scenario_result['selected_options'] = [opt for opt in user_scenario_result.get('selected_options', []) if opt is not None]
            
            print(f"\n📊 User Scenario Results:")
            print(f"   Base Price: ${user_scenario_result['base_price']}")
            print(f"   Outbound Surcharge (22:00): ${user_scenario_result['outbound_surcharge']}")
            print(f"   Return Surcharge (06:00): ${user_scenario_result['return_surcharge']}")
            print(f"   Round Trip Discount: ${user_scenario_result['round_trip_discount']}")
            print(f"   Options Total: ${user_scenario_result['options_total']}")
            print(f"   Subtotal: ${user_scenario_result['subtotal']}")
            print(f"   Final Price: ${user_scenario_result['final_price']}")
            
            # Calculate expected total
            base_price = user_scenario_result['base_price']
            outbound_surcharge = user_scenario_result['outbound_surcharge']
            return_surcharge = user_scenario_result['return_surcharge']
            options_total = user_scenario_result['options_total']
            round_trip_discount = user_scenario_result['round_trip_discount']
            
            expected_total = base_price + outbound_surcharge + base_price + return_surcharge + options_total - round_trip_discount
            
            print(f"\n🧮 Manual Calculation Verification:")
            print(f"   Outbound: ${base_price} + ${outbound_surcharge} = ${base_price + outbound_surcharge}")
            print(f"   Return: ${base_price} + ${return_surcharge} = ${base_price + return_surcharge}")
            print(f"   Options: ${options_total}")
            print(f"   Subtotal: ${base_price + outbound_surcharge + base_price + return_surcharge + options_total}")
            print(f"   Round Trip Discount: -${round_trip_discount}")
            print(f"   Final Total: ${expected_total}")
            
            if abs(expected_total - user_scenario_result['final_price']) < 0.01:
                print(f"   ✅ Calculation is correct!")
            else:
                print(f"   ❌ Calculation mismatch: Expected ${expected_total}, Got ${user_scenario_result['final_price']}")
                
        except Exception as e:
            print(f"   ❌ User scenario test failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🎉 Comprehensive Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_comprehensive_transfer_pricing()
    sys.exit(0 if success else 1)
