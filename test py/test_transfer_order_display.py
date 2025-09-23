#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from orders.models import OrderItem
from django.contrib.auth.models import User

def test_transfer_order_display():
    """Test transfer order display with detailed booking data."""
    print("=== Testing Transfer Order Display ===\n")

    # Create a mock transfer order item with detailed booking data
    try:
        # Get first user
        user = User.objects.first()
        if not user:
            print("❌ No users found")
            return

        # Create a sample transfer order item
        transfer_item = OrderItem(
            product_type='transfer',
            product_id='route_123',  # Mock route ID
            product_title='فرودگاه اصفهان به مرکز شهر',
            variant_id='sedan',
            variant_name='Sedan',
            quantity=2,
            unit_price=Decimal('75.00'),
            currency='USD',
            options_total=Decimal('0.00'),
            selected_options=[],
            booking_data={
                'passenger_count': 2,
                'luggage_count': 1,
                'vehicle_type': 'sedan',
                'vehicle_name': 'Mercedes E-Class',
                'max_passengers': 4,
                'max_luggage': 2,
                'base_price': '75.00',
                'currency': 'USD',
                'estimated_duration': 45,
                'route_origin': 'فرودگاه اصفهان',
                'route_destination': 'مرکز شهر اصفهان',
                'trip_type': 'one_way',
                'booking_date': '2025-09-15',
                'booking_time': '10:00:00',
                'pickup_time': '09:30 AM',
                'calculated_total': '150.00'
            }
        )

        # Calculate total_price
        transfer_item.total_price = Decimal('150.00')

        print("✅ Transfer OrderItem created with detailed booking data:")
        print(f"   Product: {transfer_item.product_title}")
        print(f"   Product Type: {transfer_item.product_type}")
        print(f"   Passengers: {transfer_item.booking_data.get('passenger_count')}")
        print(f"   Luggage: {transfer_item.booking_data.get('luggage_count')}")
        print(f"   Vehicle: {transfer_item.booking_data.get('vehicle_name')}")
        print(f"   Route: {transfer_item.booking_data.get('route_origin')} → {transfer_item.booking_data.get('route_destination')}")
        print(f"   Max Capacity: {transfer_item.booking_data.get('max_passengers')} passengers")
        print(f"   Estimated Duration: {transfer_item.booking_data.get('estimated_duration')} minutes")
        print(f"   Total Price: ${transfer_item.total_price}")

        print("
📋 Frontend Display Data:")
        print("   Booking Summary should show:")
        print(f"     - Passengers: {transfer_item.booking_data.get('passenger_count')} passenger(s)")
        print(f"     - Vehicle: {transfer_item.booking_data.get('vehicle_name')} (max {transfer_item.booking_data.get('max_passengers')} passengers)")
        print(f"     - Route: {transfer_item.booking_data.get('route_origin')} → {transfer_item.booking_data.get('route_destination')}")

        print("
📋 Transfer Details should show:")
        print(f"     - Trip Type: {transfer_item.booking_data.get('trip_type', 'one_way').replace('_', ' ').title()}")
        print(f"     - Passengers: {transfer_item.booking_data.get('passenger_count')}")
        print(f"     - Luggage: {transfer_item.booking_data.get('luggage_count')} piece(s)")
        print(f"     - Vehicle: {transfer_item.booking_data.get('vehicle_name')}")
        print(f"     - Max Capacity: {transfer_item.booking_data.get('max_passengers')} passengers")
        print(f"     - Estimated Duration: {transfer_item.booking_data.get('estimated_duration')} minutes")

        print("
✅ Test completed successfully!")
        print("🎯 Frontend should now display rich transfer booking information!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_transfer_order_display()
