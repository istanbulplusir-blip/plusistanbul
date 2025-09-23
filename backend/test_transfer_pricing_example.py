#!/usr/bin/env python
"""
Test script for Transfer Pricing Calculation Example
مثال کامل محاسبه قیمت ترانسفر: اصفهان به اصفهان سیتی
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent
from agents.pricing_service import AgentPricingService

def create_test_data():
    """Create test data for pricing calculation"""
    
    # Create test route: اصفهان به اصفهان سیتی
    route, created = TransferRoute.objects.get_or_create(
        origin="اصفهان",
        destination="اصفهان سیتی",
        defaults={
            'name': 'اصفهان به اصفهان سیتی',
            'description': 'ترانسفر از اصفهان به اصفهان سیتی',
            'estimated_duration_minutes': 45,
            'peak_hour_surcharge': Decimal('5.00'),  # 5% surcharge for peak hours
            'midnight_surcharge': Decimal('10.00'),  # 10% surcharge for midnight
            'round_trip_discount_enabled': True,
            'round_trip_discount_percentage': Decimal('15.00'),  # 15% discount for round trip
            'is_active': True
        }
    )
    
    # Create pricing for sedan
    pricing, created = TransferRoutePricing.objects.get_or_create(
        route=route,
        vehicle_type='sedan',
        defaults={
            'vehicle_name': 'سدان استاندارد',
            'vehicle_description': 'خودروی سدان با راننده حرفه‌ای',
            'base_price': Decimal('50.00'),  # Base price: $50
            'currency': 'USD',
            'max_passengers': 4,
            'max_luggage': 4,
            'features': ['AC', 'WiFi', 'Professional Driver'],
            'amenities': ['Water', 'Tissue', 'USB Charger'],
            'is_active': True,
            'pricing_metadata': {
                "pricing_type": "transfer",
                "calculation_method": "base_plus_surcharges",
                "version": "1.0",
                "features": {
                    "time_based_surcharges": True,
                    "round_trip_discounts": True,
                    "options_support": True
                }
            }
        }
    )
    
    # Create test options
    options = []
    
    # Option 1: Extra Luggage
    option1, created = TransferOption.objects.get_or_create(
        route=route,
        option_type='extra_luggage',
        slug='extra-luggage-esfahan',
        defaults={
            'name': 'چمدان اضافی',
            'description': 'اضافه کردن چمدان اضافی',
            'price_type': 'fixed',
            'price': Decimal('5.00'),
            'max_quantity': 3,
            'is_active': True
        }
    )
    options.append(option1)
    
    # Option 2: English Driver
    option2, created = TransferOption.objects.get_or_create(
        route=route,
        option_type='english_driver',
        slug='english-driver-esfahan',
        defaults={
            'name': 'راننده انگلیسی زبان',
            'description': 'راننده مسلط به زبان انگلیسی',
            'price_type': 'fixed',
            'price': Decimal('5.00'),
            'max_quantity': 1,
            'is_active': True
        }
    )
    options.append(option2)
    
    # Option 3: Meet & Greet
    option3, created = TransferOption.objects.get_or_create(
        route=route,
        option_type='meet_greet',
        slug='meet-greet-esfahan',
        defaults={
            'name': 'خدمات استقبال',
            'description': 'استقبال در فرودگاه یا هتل',
            'price_type': 'fixed',
            'price': Decimal('5.00'),
            'max_quantity': 1,
            'is_active': True
        }
    )
    options.append(option3)
    
    return route, pricing, options

def test_pricing_calculation():
    """Test pricing calculation with example scenario"""
    
    print("🧪 Testing Transfer Pricing Calculation")
    print("=" * 50)
    
    # Create test data
    route, pricing, options = create_test_data()
    
    print(f"📍 Route: {route.origin} → {route.destination}")
    print(f"🚗 Vehicle: {pricing.vehicle_name}")
    print(f"💰 Base Price: ${pricing.base_price}")
    print(f"⏰ Peak Hour Surcharge: {route.peak_hour_surcharge}%")
    print(f"🌙 Midnight Surcharge: {route.midnight_surcharge}%")
    print(f"🔄 Round Trip Discount: {route.round_trip_discount_percentage}%")
    print()
    
    # Test scenario: Round trip with surcharges and options
    print("📋 Test Scenario:")
    print("- Trip Type: Round Trip")
    print("- Outbound Time: 8:00 AM (Peak Hour - +5%)")
    print("- Return Time: 11:00 PM (Midnight - +10%)")
    print("- Options: 3 options × $5 each = $15")
    print()
    
    # Prepare selected options
    selected_options = [
        {
            'id': str(options[0].id),
            'quantity': 1,
            'name': options[0].name,
            'price': float(options[0].price)
        },
        {
            'id': str(options[1].id),
            'quantity': 1,
            'name': options[1].name,
            'price': float(options[1].price)
        },
        {
            'id': str(options[2].id),
            'quantity': 1,
            'name': options[2].name,
            'price': float(options[2].price)
        }
    ]
    
    # Calculate pricing using the pricing model
    print("🔢 Step-by-Step Calculation:")
    print("-" * 30)
    
    # Step 1: Base price
    base_price = pricing.base_price
    print(f"1. Base Price: ${base_price}")
    
    # Step 2: Outbound surcharge (8 AM = peak hour)
    outbound_surcharge = route.calculate_time_surcharge(base_price, 8)
    print(f"2. Outbound Surcharge (8 AM - Peak): ${outbound_surcharge}")
    
    # Step 3: Return surcharge (11 PM = midnight)
    return_surcharge = route.calculate_time_surcharge(base_price, 23)
    print(f"3. Return Surcharge (11 PM - Midnight): ${return_surcharge}")
    
    # Step 4: Options total
    options_total = Decimal(str(sum(option['price'] * option['quantity'] for option in selected_options)))
    print(f"4. Options Total (3 × $5): ${options_total}")
    
    # Step 5: Subtotal before discount
    outbound_price = base_price + outbound_surcharge
    return_price = base_price + return_surcharge
    subtotal = outbound_price + return_price + options_total
    print(f"5. Subtotal: ${outbound_price} + ${return_price} + ${options_total} = ${subtotal}")
    
    # Step 6: Round trip discount
    total_before_discount = outbound_price + return_price
    round_trip_discount = total_before_discount * (route.round_trip_discount_percentage / Decimal('100'))
    print(f"6. Round Trip Discount (15% of ${total_before_discount}): -${round_trip_discount}")
    
    # Step 7: Final price
    final_price = subtotal - round_trip_discount
    print(f"7. Final Price: ${subtotal} - ${round_trip_discount} = ${final_price}")
    
    print()
    print("📊 Detailed Breakdown:")
    print("-" * 30)
    print(f"Outbound Trip: ${base_price} + ${outbound_surcharge} = ${outbound_price}")
    print(f"Return Trip: ${base_price} + ${return_surcharge} = ${return_price}")
    print(f"Options: {options_total}")
    print(f"Subtotal: ${subtotal}")
    print(f"Round Trip Discount: -${round_trip_discount}")
    print(f"Final Price: ${final_price}")
    
    # Test with Agent Pricing Service
    print()
    print("🤖 Agent Pricing Service Test:")
    print("-" * 30)
    
    # Create test agent
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    agent_user, created = User.objects.get_or_create(
        username='test_agent',
        defaults={
            'email': 'agent@test.com',
            'role': 'agent',
            'is_active': True
        }
    )
    
    agent, created = Agent.objects.get_or_create(
        user=agent_user,
        defaults={
            'company_name': 'Test Agent Company',
            'license_number': 'TEST123',
            'email': 'agent@test.com',
            'phone': '+1234567890',
            'is_active': True,
            'is_verified': True
        }
    )
    
    # Calculate agent pricing
    try:
        agent_pricing = AgentPricingService.calculate_transfer_price_for_agent(
            route=route,
            vehicle_type='sedan',
            agent=agent,
            passenger_count=2,
            trip_type='round_trip',
            hour=8,  # 8 AM
            return_hour=23,  # 11 PM
            selected_options=selected_options
        )
        
        print(f"✅ Agent Pricing Calculation Successful!")
        print(f"Base Price: ${agent_pricing['base_price']}")
        print(f"Agent Total: ${agent_pricing['agent_total']}")
        print(f"Options Total: ${agent_pricing['options_total']}")
        print(f"Savings: ${agent_pricing['savings']}")
        print(f"Savings Percentage: {agent_pricing['savings_percentage']:.1f}%")
        print(f"Pricing Method: {agent_pricing['pricing_method']}")
        
    except Exception as e:
        print(f"❌ Agent Pricing Calculation Failed: {e}")
    
    print()
    print("🎯 Summary:")
    print("-" * 30)
    print(f"Customer pays: ${final_price}")
    print(f"Agent commission: ${agent_pricing.get('savings', 0)}")
    print(f"Net revenue: ${final_price - Decimal(str(agent_pricing.get('savings', 0)))}")

def test_agent_booking_flow():
    """Test complete agent booking flow"""
    
    print()
    print("🔄 Testing Agent Booking Flow")
    print("=" * 50)
    
    # Create test data
    route, pricing, options = create_test_data()
    
    # Simulate agent booking data
    booking_data = {
        'route_id': route.id,
        'vehicle_type': 'sedan',
        'passenger_count': 2,
        'luggage_count': 1,
        'trip_type': 'round_trip',
        'booking_date': '2024-01-15',
        'booking_time': '08:00',
        'return_date': '2024-01-15',
        'return_time': '23:00',
        'selected_options': [
            {
                'id': str(options[0].id),
                'quantity': 1,
                'name': options[0].name,
                'price': float(options[0].price)
            },
            {
                'id': str(options[1].id),
                'quantity': 1,
                'name': options[1].name,
                'price': float(options[1].price)
            },
            {
                'id': str(options[2].id),
                'quantity': 1,
                'name': options[2].name,
                'price': float(options[2].price)
            }
        ],
        'payment_method': 'whatsapp'
    }
    
    print("📝 Booking Data:")
    for key, value in booking_data.items():
        print(f"  {key}: {value}")
    
    print()
    print("✅ Booking flow test completed!")
    print("This data would be sent to the agent booking API endpoint.")

if __name__ == "__main__":
    try:
        test_pricing_calculation()
        test_agent_booking_flow()
        print()
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
