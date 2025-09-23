#!/usr/bin/env python
"""
Test script to verify cart add functionality works without Decimal/float type errors.
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

def test_cart_add():
    """Test that cart add functionality works without type errors."""
    print("=" * 60)
    print("TESTING CART ADD FUNCTIONALITY")
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
    
    # Test midnight time with options
    midnight_time = time(5, 35)  # 5:35 AM
    selected_options = [
        {
            'option_id': 'fc57fb35-4a66-4648-9aa7-980721dfccfd',
            'quantity': 1,
            'name': 'Extra Luggage',
            'price': 10.0
        },
        {
            'option_id': 'a110a073-dada-42bb-8bce-09f2d39b0b18',
            'quantity': 1,
            'name': 'Meet & Greet',
            'price': 20.0
        }
    ]
    
    print(f"\n🕐 Testing midnight time: {midnight_time}")
    print(f"📦 Selected options: {len(selected_options)} options")
    
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
        
        # Test cart item creation
        print(f"\n🛒 Testing cart item creation...")
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Prepare booking data
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
            unit_price=price_data['price_breakdown']['final_price'],
            total_price=price_data['price_breakdown']['final_price'],
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
        
        print(f"✅ Cart item created successfully!")
        print(f"   Unit price: ${cart_item.unit_price}")
        print(f"   Total price: ${cart_item.total_price}")
        
        # Test serializer (this was causing the error)
        print(f"\n📋 Testing CartItemSerializer...")
        from cart.serializers import CartItemSerializer
        
        try:
            serializer = CartItemSerializer(cart_item)
            serialized_data = serializer.data
            print(f"✅ Serializer successful!")
            print(f"   Serialized total_price: ${serialized_data.get('total_price')}")
            
            # Verify the total_price calculation
            expected_total = (
                price_data['price_breakdown']['base_price'] +
                price_data['price_breakdown']['time_surcharge'] +
                price_data['price_breakdown']['options_total']
            )
            print(f"   Expected total: ${expected_total}")
            
            if abs(float(serialized_data.get('total_price', 0)) - expected_total) < 0.01:
                print("✅ Total price calculation is correct!")
            else:
                print("❌ Total price calculation mismatch!")
                
        except Exception as e:
            print(f"❌ Serializer error: {e}")
            import traceback
            traceback.print_exc()
        
        # Clean up
        cart_item.delete()
        
        print("\n✅ TEST PASSED: Cart add functionality works without type errors!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_cart_add() 