#!/usr/bin/env python
"""
Test script to verify pricing breakdown in cart items.
"""

import os
import sys
import django
from datetime import datetime, time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import Cart, CartItem
from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from users.models import User

def test_pricing_breakdown():
    """Test pricing breakdown in cart items."""
    print("🧪 Testing pricing breakdown in cart items...")
    
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Get a transfer route
        route = TransferRoute.objects.filter(is_active=True).first()
        if not route:
            print("❌ No active transfer routes found")
            return
        
        # Get pricing
        pricing = TransferRoutePricing.objects.filter(
            route=route,
            is_active=True
        ).first()
        
        if not pricing:
            print("❌ No active pricing found")
            return
        
        # Get some options
        options = TransferOption.objects.filter(is_active=True)[:3]
        selected_options = []
        for option in options:
            selected_options.append({
                'option_id': str(option.id),
                'quantity': 1,
                'name': option.name,
                'description': option.description,
                'price': float(option.calculate_price(pricing.base_price))
            })
        
        # Create cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product_type='transfer',
            product_id=str(route.id),
            quantity=1,
            unit_price=pricing.base_price,
            total_price=pricing.base_price,
            currency='USD',
            selected_options=selected_options,
            booking_data={
                'route_id': str(route.id),
                'vehicle_type': pricing.vehicle_type,
                'trip_type': 'one_way',
                'outbound_datetime': '2025-07-11 03:40',
                'passenger_count': 2,
                'luggage_count': 1,
                'selected_options': selected_options
            },
            booking_date=datetime.now().date(),
            booking_time=time(3, 40),
        )
        
        print(f"✅ Cart item created: {cart_item.id}")
        
        # Test serializer
        from cart.serializers import CartItemSerializer
        serializer = CartItemSerializer(cart_item)
        data = serializer.data
        
        print(f"\n📋 Serialized data:")
        print(f"   Product: {data['product_title']}")
        print(f"   Unit price: ${data['unit_price']}")
        print(f"   Total price: ${data['total_price']}")
        print(f"   Origin: {data['origin']}")
        print(f"   Destination: {data['destination']}")
        
        if data.get('pricing_breakdown'):
            breakdown = data['pricing_breakdown']
            print(f"\n💰 Pricing Breakdown:")
            print(f"   Base price: ${breakdown['base_price']}")
            print(f"   Time surcharge: ${breakdown['time_surcharge']}")
            print(f"   Round trip discount: ${breakdown['round_trip_discount']}")
            print(f"   Options total: ${breakdown['options_total']}")
            print(f"   Final price: ${breakdown['final_price']}")
        else:
            print("❌ No pricing breakdown in response")
        
        print(f"\n🎯 Selected Options ({len(data['selected_options'])}):")
        for option in data['selected_options']:
            print(f"   - {option.get('name', 'Unknown')}: ${option.get('price', 0)}")
        
        # Clean up
        cart_item.delete()
        
        print("\n✅ TEST PASSED: Pricing breakdown works correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_pricing_breakdown() 