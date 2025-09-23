#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import OrderItem
from django.contrib.auth.models import User

def test_transfer_comprehensive():
    """Test comprehensive transfer booking data display."""
    print("=== Testing Comprehensive Transfer Data ===\n")

    # Create a comprehensive transfer order item
    transfer_item = OrderItem(
        product_type='transfer',
        product_id='route_123',
        product_title='فرودگاه اصفهان به مرکز شهر',
        variant_id='van',
        variant_name='Van',
        quantity=2,
        unit_price=80.00,
        currency='USD',
        options_total=0.00,
        selected_options=[],
        booking_data={
            # Basic info
            'passenger_count': 2,
            'luggage_count': 1,
            'vehicle_type': 'van',
            'vehicle_name': 'Mercedes Sprinter Van',
            'max_passengers': 12,
            'max_luggage': 8,
            'base_price': '80.00',
            'currency': 'USD',
            'estimated_duration': 45,
            'route_origin': 'فرودگاه اصفهان',
            'route_destination': 'مرکز شهر اصفهان',
            'route_name': 'اصفهان Airport Transfer',

            # Trip details - Round Trip
            'trip_type': 'round_trip',
            'outbound_date': '2025-09-09',
            'outbound_time': '06:30',
            'return_date': '2025-09-10',
            'return_time': '07:30',
            'outbound_price': '80.00',
            'return_price': '80.00',

            # Addresses
            'pickup_address': 'فرودگاه بین‌المللی اصفهان، ترمینال 1',
            'dropoff_address': 'هتل عباسی، میدان نقش جهان',
            'pickup_instructions': 'در ورودی اصلی منتظر باشید',
            'dropoff_instructions': 'در لابی هتل تحویل دهید',

            # Contact info
            'contact_name': 'علی احمدی',
            'contact_phone': '+989123456789',

            # Special requirements
            'special_requirements': 'نیاز به صندلی کودک دارم',

            # Pricing details
            'surcharges': {
                'peak_hour_surcharge': '12.00',
                'midnight_surcharge': '15.00'
            },
            'discounts': {
                'round_trip_discount': '21.60'
            },
            'round_trip_discount': '21.60',
            'options_total': '0.00',
            'final_price': '158.40',
            'calculated_total': '158.40'
        }
    )

    transfer_item.total_price = 158.40

    print("✅ Comprehensive Transfer OrderItem created!")
    print("📋 Booking Summary should display:")
    print(f"   - Route: {transfer_item.booking_data['route_name']}")
    print(f"   - Date: {transfer_item.booking_data['outbound_date']} (Outbound)")
    print(f"   - Return Date: {transfer_item.booking_data['return_date']} (Return)")
    print(f"   - Time: {transfer_item.booking_data['outbound_time']} (Outbound)")
    print(f"   - Return Time: {transfer_item.booking_data['return_time']} (Return)")
    print(f"   - Passengers: {transfer_item.booking_data['passenger_count']} passengers")
    print(f"   - Vehicle: {transfer_item.booking_data['vehicle_name']} (max {transfer_item.booking_data['max_passengers']} passengers)")
    print(f"   - Pickup: {transfer_item.booking_data['pickup_address']}")

    print("
📋 Transfer Details should display:")
    print(f"   - Trip Type: {transfer_item.booking_data['trip_type'].replace('_', ' ').title()}")
    print("   - Outbound Trip:")
    print(f"     * Date: {transfer_item.booking_data['outbound_date']}")
    print(f"     * Time: {transfer_item.booking_data['outbound_time']}")
    print(f"     * Price: ${transfer_item.booking_data['outbound_price']}")
    print("   - Return Trip:")
    print(f"     * Date: {transfer_item.booking_data['return_date']}")
    print(f"     * Time: {transfer_item.booking_data['return_time']}")
    print(f"     * Price: ${transfer_item.booking_data['return_price']}")
    print(f"   - Passengers: {transfer_item.booking_data['passenger_count']}")
    print(f"   - Luggage: {transfer_item.booking_data['luggage_count']} piece(s)")
    print(f"   - Pickup Address: {transfer_item.booking_data['pickup_address']}")
    print(f"   - Drop-off Address: {transfer_item.booking_data['dropoff_address']}")
    print(f"   - Special Requirements: {transfer_item.booking_data['special_requirements']}")
    print("   - Pricing Details:"
    print(f"     * Surcharges: Peak Hour (+${transfer_item.booking_data['surcharges']['peak_hour_surcharge']}), Midnight (+${transfer_item.booking_data['surcharges']['midnight_surcharge']})")
    print(f"     * Discounts: Round Trip (-${transfer_item.booking_data['discounts']['round_trip_discount']})")
    print(f"   - Total: ${transfer_item.total_price}")

    print("
✅ Test data created successfully!")
    print("🎯 Frontend should now display comprehensive transfer booking information!")

if __name__ == '__main__':
    test_transfer_comprehensive()
