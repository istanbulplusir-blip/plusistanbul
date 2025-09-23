#!/usr/bin/env python3
"""
Test script to verify pricing consistency between tour detail and cart.
This tests the fix for the pricing system issue.
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
from tours.models import Tour, TourVariant, TourSchedule, TourCategory, TourPricing
from cart.models import Cart, CartItem, CartService
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_pricing_consistency():
    """Test pricing consistency between tour detail API and cart calculation."""
    log("🧪 Testing pricing consistency between tour detail and cart...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_pricing_user',
        defaults={
            'email': 'test_pricing@example.com',
            'first_name': 'Test',
            'last_name': 'Pricing',
            'is_active': True,
            'is_email_verified': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    log(f"Using test user: {user.username}")
    
    # Get existing tour data
    tour = Tour.objects.filter(is_active=True).first()
    if not tour:
        log("❌ No active tours found")
        return False
    
    variant = tour.variants.filter(is_active=True).first()
    if not variant:
        log("❌ No active variants found")
        return False
    
    schedule = tour.schedules.filter(is_available=True).first()
    if not schedule:
        log("❌ No available schedules found")
        return False
    
    log(f"Testing with:")
    log(f"  Tour: {tour.title}")
    log(f"  Variant: {variant.name} (base_price: {variant.base_price})")
    log(f"  Schedule: {schedule.start_date}")
    
    # Test with realistic participant data
    participants = {
        'adult': 2,
        'child': 1,
        'infant': 1
    }
    
    log(f"  Participants: {participants}")
    
    # Step 1: Calculate expected price using TourPricing model (backend logic)
    expected_total = Decimal('0.00')
    pricing_breakdown = {}
    
    for age_group, count in participants.items():
        try:
            pricing = TourPricing.objects.get(
                tour=tour, 
                variant=variant, 
                age_group=age_group
            )
            final_price = pricing.final_price
            subtotal = final_price * count
            expected_total += subtotal
            pricing_breakdown[age_group] = {
                'count': count,
                'unit_price': final_price,
                'subtotal': subtotal
            }
            log(f"    {age_group}: {count} × {final_price} = {subtotal}")
        except TourPricing.DoesNotExist:
            log(f"❌ TourPricing not found for {age_group}")
            return False
    
    log(f"💰 Expected total from pricing model: {expected_total}")
    
    # Step 2: Test cart API
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Add to cart
    cart_data = {
        'product_type': 'tour',
        'product_id': str(tour.id),
        'variant_id': str(variant.id),
        'quantity': participants['adult'] + participants['child'] + participants['infant'],
        'booking_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
        'booking_time': '09:00:00',
        'booking_data': {
            'schedule_id': str(schedule.id),
            'participants': participants,
            'special_requests': 'Test pricing consistency'
        },
        'selected_options': []
    }
    
    log("📝 Adding item to cart...")
    response = client.post('/api/v1/cart/add/', cart_data, format='json')
    
    if response.status_code != 201:
        log(f"❌ Failed to add to cart: {response.status_code}")
        log(f"Response: {response.data}")
        return False
    
    cart_item_data = response.data.get('cart_item', {})
    backend_unit_price = Decimal(str(cart_item_data.get('unit_price', 0)))
    backend_total_price = Decimal(str(cart_item_data.get('total_price', 0)))
    
    log(f"✅ Item added to cart successfully")
    log(f"Backend calculated:")
    log(f"  Unit price: {backend_unit_price}")
    log(f"  Total price: {backend_total_price}")
    
    # Step 3: Get cart and verify pricing
    log("📋 Retrieving cart...")
    response = client.get('/api/v1/cart/')
    
    if response.status_code != 200:
        log(f"❌ Failed to retrieve cart: {response.status_code}")
        return False
    
    cart_data = response.data
    items = cart_data.get('items', [])
    
    if not items:
        log("❌ No items in cart")
        return False
    
    item = items[0]
    cart_unit_price = Decimal(str(item.get('unit_price', 0)))
    cart_total_price = Decimal(str(item.get('total_price', 0)))
    
    log(f"Cart API returned:")
    log(f"  Unit price: {cart_unit_price}")
    log(f"  Total price: {cart_total_price}")
    
    # Step 4: Compare pricing
    log("🔍 Comparing pricing methods...")
    
    # Check if backend calculation matches expected
    if backend_total_price == expected_total:
        log("✅ Backend pricing calculation is CORRECT")
        backend_correct = True
    else:
        log(f"❌ Backend pricing calculation is INCORRECT")
        log(f"   Expected: {expected_total}")
        log(f"   Got: {backend_total_price}")
        log(f"   Difference: {backend_total_price - expected_total}")
        backend_correct = False
    
    # Check consistency between add and get cart
    if cart_total_price == backend_total_price:
        log("✅ Cart API consistency is CORRECT")
        cart_consistent = True
    else:
        log(f"❌ Cart API consistency is INCORRECT")
        log(f"   Add response: {backend_total_price}")
        log(f"   Get response: {cart_total_price}")
        cart_consistent = False
    
    # Step 5: Test frontend calculation logic
    log("🖥️  Testing frontend calculation logic...")
    
    # Simulate frontend useCart logic (BEFORE fix)
    frontend_old_logic = cart_unit_price * Decimal(str(cart_data.get('quantity', 0)))
    
    # Simulate frontend useCart logic (AFTER fix)
    frontend_new_logic = cart_total_price  # Uses subtotal from backend
    
    log(f"Frontend calculations:")
    log(f"  Old logic (price × quantity): {frontend_old_logic}")
    log(f"  New logic (use subtotal): {frontend_new_logic}")
    
    if frontend_new_logic == expected_total:
        log("✅ Frontend NEW logic is CORRECT")
        frontend_correct = True
    else:
        log(f"❌ Frontend NEW logic is INCORRECT")
        frontend_correct = False
    
    if frontend_old_logic != expected_total:
        log("✅ Frontend OLD logic was indeed WRONG (as expected)")
        old_logic_was_wrong = True
    else:
        log("⚠️  Frontend OLD logic was actually correct (unexpected)")
        old_logic_was_wrong = False
    
    # Step 6: Summary
    log("📊 PRICING TEST SUMMARY:")
    log(f"   Backend calculation: {'✅ CORRECT' if backend_correct else '❌ INCORRECT'}")
    log(f"   Cart API consistency: {'✅ CORRECT' if cart_consistent else '❌ INCORRECT'}")
    log(f"   Frontend new logic: {'✅ CORRECT' if frontend_correct else '❌ INCORRECT'}")
    log(f"   Old logic was wrong: {'✅ YES' if old_logic_was_wrong else '❌ NO'}")
    
    # Overall result
    all_correct = backend_correct and cart_consistent and frontend_correct and old_logic_was_wrong
    
    if all_correct:
        log("🎉 ALL TESTS PASSED! Pricing system is working correctly.")
        return True
    else:
        log("❌ SOME TESTS FAILED! Pricing system needs attention.")
        return False

def cleanup():
    """Clean up test data"""
    log("🧹 Cleaning up test data...")
    try:
        user = User.objects.get(username='test_pricing_user')
        CartItem.objects.filter(cart__user=user).delete()
        Cart.objects.filter(user=user).delete()
        log("Cleanup completed")
    except User.DoesNotExist:
        pass

if __name__ == "__main__":
    try:
        success = test_pricing_consistency()
        exit_code = 0 if success else 1
    except Exception as e:
        log(f"Test failed with exception: {str(e)}")
        import traceback
        log(traceback.format_exc())
        exit_code = 1
    finally:
        cleanup()
        
    sys.exit(exit_code) 