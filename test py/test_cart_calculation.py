#!/usr/bin/env python
"""
Test script to check cart calculation.
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import Cart, CartItem
from users.models import User

def test_cart_calculation():
    """Test cart calculation."""
    print("🔍 Testing cart calculation...")
    
    # Get the test user
    user = User.objects.filter(username='testuser').first()
    if not user:
        print("❌ Test user not found!")
        return
    
    # Get user's cart
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if not cart:
        print("❌ No active cart found!")
        return
    
    print(f"✅ Found cart: {cart.id}")
    print(f"   Session ID: {cart.session_id}")
    print(f"   User: {cart.user.username}")
    
    # Check items
    items = cart.items.all()
    print(f"\n📦 Cart items: {items.count()}")
    
    for item in items:
        print(f"\n   Item: {item.id}")
        print(f"   Product: {item.product_type} - {item.product_id}")
        print(f"   Unit Price: {item.unit_price}")
        print(f"   Total Price: {item.total_price}")
        print(f"   Options Total: {item.options_total}")
        print(f"   Selected Options: {len(item.selected_options)}")
        
        # Calculate expected total
        expected_total = Decimal(str(item.unit_price)) * item.quantity
        if item.selected_options:
            for option in item.selected_options:
                option_price = Decimal(str(option.get('price', 0)))
                option_quantity = int(option.get('quantity', 1))
                expected_total += option_price * option_quantity
        
        print(f"   Expected Total: {expected_total}")
        print(f"   Match: {'✅' if abs(item.total_price - expected_total) < 0.01 else '❌'}")
    
    # Check cart totals
    print(f"\n💰 Cart Totals:")
    print(f"   Subtotal (property): {cart.subtotal}")
    print(f"   Total (property): {cart.total}")
    print(f"   Total Items: {cart.total_items}")
    
    # Manual calculation
    manual_subtotal = sum(item.total_price for item in items)
    print(f"   Manual Subtotal: {manual_subtotal}")
    print(f"   Subtotal Match: {'✅' if abs(cart.subtotal - manual_subtotal) < 0.01 else '❌'}")

if __name__ == '__main__':
    test_cart_calculation() 