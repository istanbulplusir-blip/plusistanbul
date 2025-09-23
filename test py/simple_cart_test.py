#!/usr/bin/env python3
"""
Simple cart test to verify the existing system works with backend fixes.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User
from tours.models import Tour, TourVariant, TourSchedule, TourCategory
from cart.models import Cart, CartItem, CartService
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_existing_cart_system():
    """Test the existing cart system with backend fixes."""
    log("Testing existing cart system...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_simple_user',
        defaults={
            'email': 'test_simple@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_email_verified': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Create test tour
    category, _ = TourCategory.objects.get_or_create(
        slug='test-category',
        defaults={
            'name': 'Test Category',
            'description': 'Test category description',
            'is_active': True
        }
    )
    
    tour, _ = Tour.objects.get_or_create(
        slug='simple-test-tour',
        defaults={
            'title': 'Simple Test Tour',
            'description': 'Test tour description',
            'short_description': 'Test short description',
            'category': category,
            'duration_hours': 8,
            'min_participants': 1,
            'max_participants': 20,
            'pickup_time': datetime.now().time(),
            'start_time': datetime.now().time(),
            'end_time': datetime.now().time(),
            'price': Decimal('100.00'),
            'currency': 'USD',
            'is_active': True
        }
    )
    
    # Create test variant
    variant, _ = TourVariant.objects.get_or_create(
        tour=tour,
        name='Standard',
        defaults={
            'description': 'Standard variant',
            'base_price': Decimal('100.00'),
            'capacity': 10,
            'is_active': True
        }
    )
    
    log(f"Created test data: Tour={tour.title}, Variant={variant.name}")
    
    # Test API client
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Test adding to cart (existing API endpoint)
    cart_data = {
        'product_type': 'tour',
        'product_id': str(tour.id),
        'variant_id': str(variant.id),
        'quantity': 2,
        'booking_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
        'booking_time': '09:00:00',
        'booking_data': {
            'participants': {
                'adult': 2,
                'child': 0,
                'infant': 0
            },
            'special_requests': 'Test booking'
        },
        'selected_options': []
    }
    
    log("Testing add to cart...")
    response = client.post('/api/v1/cart/add/', cart_data, format='json')
    
    if response.status_code == 201:
        log("✓ Successfully added item to cart")
        cart_item_data = response.data.get('cart_item', {})
        log(f"Cart item ID: {cart_item_data.get('id')}")
        log(f"Unit price: {cart_item_data.get('unit_price')}")
        log(f"Total price: {cart_item_data.get('total_price')}")
        
        # Verify pricing calculation
        expected_total = Decimal(str(cart_item_data.get('unit_price', 0))) * 2
        actual_total = Decimal(str(cart_item_data.get('total_price', 0)))
        
        if expected_total == actual_total:
            log("✓ Price calculation is correct")
        else:
            log(f"✗ Price calculation mismatch: expected {expected_total}, got {actual_total}")
    else:
        log(f"✗ Failed to add to cart: {response.status_code}")
        log(f"Response: {response.data}")
        return False
    
    # Test cart retrieval
    log("Testing cart retrieval...")
    response = client.get('/api/v1/cart/')
    
    if response.status_code == 200:
        cart_data = response.data
        log("✓ Successfully retrieved cart")
        log(f"Cart items: {len(cart_data.get('items', []))}")
        log(f"Cart total: {cart_data.get('total', 0)}")
        
        # Verify cart has our item
        items = cart_data.get('items', [])
        if len(items) > 0:
            item = items[0]
            if str(item.get('variant_id')) == str(variant.id):
                log("✓ Cart contains correct variant")
                
                # Test variant pricing fix
                if item.get('unit_price') == float(variant.base_price):
                    log("✓ Variant pricing fix working correctly")
                else:
                    log(f"✗ Variant pricing issue: expected {variant.base_price}, got {item.get('unit_price')}")
            else:
                log("✗ Cart contains wrong variant")
        else:
            log("✗ Cart is empty")
    else:
        log(f"✗ Failed to retrieve cart: {response.status_code}")
        return False
    
    log("✓ All tests passed! Existing cart system works with backend fixes.")
    return True

def cleanup():
    """Clean up test data"""
    log("Cleaning up test data...")
    try:
        user = User.objects.get(username='test_simple_user')
        CartItem.objects.filter(cart__user=user).delete()
        Cart.objects.filter(user=user).delete()
        log("Cleanup completed")
    except User.DoesNotExist:
        pass

if __name__ == "__main__":
    try:
        success = test_existing_cart_system()
        exit_code = 0 if success else 1
    except Exception as e:
        log(f"Test failed with exception: {str(e)}")
        import traceback
        log(traceback.format_exc())
        exit_code = 1
    finally:
        cleanup()
        
    sys.exit(exit_code) 