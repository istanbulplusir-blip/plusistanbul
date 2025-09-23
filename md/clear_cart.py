#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from cart.models import Cart, CartItem
from users.models import User

# Find the test user
try:
    user = User.objects.get(username='testuser')
    print(f"Found user: {user.username}")
    
    # Get user's cart
    cart = Cart.objects.filter(user=user).first()
    if cart:
        print(f"Found cart with {cart.items.count()} items")
        
        # Clear all items
        cart.items.all().delete()
        print("Cart cleared successfully")
        
        # Update cart totals
        cart.total_items = 0
        cart.subtotal = 0
        cart.total_price = 0
        cart.save()
        print("Cart totals updated")
    else:
        print("No cart found for user")
        
except User.DoesNotExist:
    print("Test user not found")
except Exception as e:
    print(f"Error: {e}") 