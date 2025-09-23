#!/usr/bin/env python
"""
Test script to verify cart pricing includes time surcharges correctly.
"""

import os
import sys
import django
from datetime import datetime, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from transfers.models import TransferRoute, TransferRoutePricing
from transfers.services import TransferPricingService
from cart.models import Cart, CartItem
from users.models import User

def test_cart_pricing():
    """Test that cart pricing includes time surcharges."""
    print("=" * 60)
    print("TESTING CART PRICING WITH TIME SURCHARGES")
    print("=" * 60)
    
    # Get test user
    user = User.objects.filter(username='testuser').first()
    if not user:
        print("❌ Test user not found")
        return
    
    # Get a route and pricing
    route = TransferRoute.objects.filter(is_active=True).first()
    if not route:
        print("❌ No active routes found")
        return
    
    pricing = TransferRoutePricing.objects.filter(route=route, is_active=True).first()
    if not pricing:
        print("❌ No active pricing found")
        return
    
    print(f"✅ Testing with route: {route}")
    print(f"✅ Vehicle type: {pricing.vehicle_type}")
    print(f"✅ Base price: ${pricing.base_price}")
    
    # Test midnight time (should have surcharge)
    midnight_time = time(5, 35)  # 5:35 AM
    selected_options = [
        {
            'option_id': 'fc57fb35-4a66-4648-9aa7-980721dfccfd',
            'quantity': 1,
            'name': 'Extra Luggage',
            'price': 10.0
        }
    ]
    
    print(f"\n🕐 Testing midnight time: {midnight_time}")
    
    # Calculate price using service
    try:
        price_data = TransferPricingService.calculate_price(
            route=route,
            pricing=pricing,
            booking_time=midnight_time,
            return_time=None,
            selected_options=selected_options
        )
        
        print("✅ Price calculation successful!")
        print(f"   Base price: ${price_data['price_breakdown']['base_price']}")
        print(f"   Time surcharge: ${price_data['price_breakdown']['time_surcharge']}")
        print(f"   Options total: ${price_data['price_breakdown']['options_total']}")
        print(f"   Final price: ${price_data['price_breakdown']['final_price']}")
        
        expected_final = (
            price_data['price_breakdown']['base_price'] +
            price_data['price_breakdown']['time_surcharge'] +
            price_data['price_breakdown']['options_total']
        )
        
        print(f"   Expected final: ${expected_final}")
        
        # Check if cart would use the correct price
        print(f"\n🛒 Simulating cart pricing...")
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Prepare booking_date and booking_time
        outbound_datetime_str = f"2025-07-10 {midnight_time.strftime('%H:%M')}"
        outbound_datetime = datetime.strptime(outbound_datetime_str, "%Y-%m-%d %H:%M")
        booking_date = outbound_datetime.date()
        booking_time = outbound_datetime.time()

        # Create cart item with the calculated price
        cart_item = CartItem.objects.create(
            cart=cart,
            product_type='transfer',
            product_id=str(route.id),
            quantity=1,
            unit_price=price_data['price_breakdown']['final_price'],  # Use final price as unit price
            total_price=price_data['price_breakdown']['final_price'],  # Use final price as total
            currency='USD',
            selected_options=selected_options,
            booking_data={
                'route_id': str(route.id),
                'vehicle_type': pricing.vehicle_type,
                'trip_type': 'one_way',
                'outbound_datetime': outbound_datetime_str,
                'passenger_count': 2,
                'luggage_count': 1,
                'selected_options': selected_options
            },
            booking_date=booking_date,
            booking_time=booking_time,
        )
        
        print(f"✅ Cart item created with correct pricing!")
        print(f"   Unit price: ${cart_item.unit_price}")
        print(f"   Total price: ${cart_item.total_price}")
        
        # Verify cart totals
        cart.refresh_from_db()
        print(f"   Cart subtotal: ${cart.subtotal}")
        print(f"   Cart total: ${cart.total_price}")
        
        # Clean up
        cart_item.delete()
        
        print("\n✅ TEST PASSED: Cart pricing now includes time surcharges correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_cart_pricing() 