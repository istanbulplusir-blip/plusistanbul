#!/usr/bin/env python
"""
Comprehensive API Test: User Sessions, Tours, Cart Operations, Checkout
Tests all critical flows systematically
"""

import os
import sys
import django
from decimal import Decimal
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import authenticate
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from tours.models import Tour, TourVariant, TourSchedule

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    print(f"\n--- {title} ---")

def test_user_sessions():
    """Test 1: User Sessions and Cart Isolation"""
    print_section("1. USER SESSIONS AND CART ISOLATION")
    
    test_users = ['customer', 'testuser', 'admin', 'shahabshahrokhh', 'shahanshahrokh']
    user_sessions = {}
    
    for username in test_users:
        print_subsection(f"Testing User: {username}")
        
        # Authenticate user
        user = authenticate(username=username, password='testpass123')
        if not user:
            print(f"❌ Authentication failed for {username}")
            continue
        
        print(f"✅ Authentication successful for {username}")
        
        # Create API client with token
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Get cart
        cart_response = client.get('/api/v1/cart/')
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            if isinstance(cart_data, dict):
                total_items = cart_data.get('total_items', 0)
                items_count = len(cart_data.get('items', []))
                session_id = cart_data.get('session_id', 'N/A')
            else:
                total_items = len(cart_data) if hasattr(cart_data, '__len__') else 0
                items_count = total_items
                session_id = 'List Response'
            
            print(f"   Cart items: {total_items}")
            print(f"   Unique items: {items_count}")
            print(f"   Session ID: {session_id}")
            
            user_sessions[username] = {
                'user_id': str(user.id),
                'session_id': session_id,
                'cart_items': total_items,
                'client': client,
                'token': access_token
            }
        else:
            print(f"❌ Failed to get cart: {cart_response.status_code}")
    
    # Compare sessions
    print_subsection("Session Comparison")
    session_ids = set()
    for username, data in user_sessions.items():
        session_ids.add(data['session_id'])
        print(f"{username}: Session={data['session_id']}, Items={data['cart_items']}")
    
    if len(session_ids) == len(user_sessions):
        print("✅ Each user has a separate session")
    else:
        print("❌ Some users share the same session")
    
    return user_sessions

def test_tours():
    """Test 2: Tour Details and Pricing"""
    print_section("2. TOUR DETAILS AND PRICING")
    
    # Get tours list
    client = APIClient()
    tours_response = client.get('/api/v1/tours/')
    
    if tours_response.status_code != 200:
        print(f"❌ Failed to get tours: {tours_response.status_code}")
        return []
    
    tours_data = tours_response.json()
    if isinstance(tours_data, dict):
        available_tours = tours_data.get('results', [])
    else:
        available_tours = tours_data
    
    print(f"Found {len(available_tours)} tours")
    
    tour_details = []
    
    for tour in available_tours:
        print_subsection(f"Tour: {tour['slug']}")
        print(f"ID: {tour['id']}")
        print(f"Price: ${tour.get('price', 'N/A')}")
        
        # Get tour details
        tour_detail_response = client.get(f'/api/v1/tours/{tour["slug"]}/')
        if tour_detail_response.status_code == 200:
            tour_detail = tour_detail_response.json()
            
            # Check pricing_summary
            pricing_summary = tour_detail.get('pricing_summary', {})
            if pricing_summary:
                print(f"✅ Pricing summary exists")
                for age_group, price in pricing_summary.items():
                    print(f"   {age_group}: ${price}")
            else:
                print("❌ No pricing summary")
            
            # Check variants
            variants = tour_detail.get('variants', [])
            print(f"Variants: {len(variants)}")
            for variant in variants:
                base_price = variant.get('base_price', 0)
                print(f"   - {variant.get('name', 'Unknown')}: ${base_price}")
                try:
                    base_price_float = float(base_price) if base_price else 0
                    if base_price_float <= 0:
                        print(f"     ❌ Invalid base_price: {base_price}")
                except (ValueError, TypeError):
                    print(f"     ❌ Invalid base_price format: {base_price}")
            
            # Check schedules
            schedules = tour_detail.get('schedules', [])
            print(f"Schedules: {len(schedules)}")
            for schedule in schedules[:3]:  # Show first 3
                print(f"   - {schedule.get('start_date', 'Unknown')}: Available={schedule.get('is_available', False)}")
            
            # Check pricing factors
            for variant in variants:
                variant_id = variant.get('id')
                if variant_id:
                    # Check pricing for this variant
                    pricing = variant.get('pricing', [])
                    for price_info in pricing:
                        factor = price_info.get('factor', 0)
                        age_group = price_info.get('age_group', 'Unknown')
                        try:
                            factor_float = float(factor) if factor else 0
                            if factor_float <= 0 or factor_float > 2:
                                print(f"     ❌ Invalid factor for {age_group}: {factor}")
                            else:
                                print(f"     ✅ Valid factor for {age_group}: {factor}")
                        except (ValueError, TypeError):
                            print(f"     ❌ Invalid factor format for {age_group}: {factor}")
            
            tour_details.append({
                'slug': tour['slug'],
                'id': tour['id'],
                'detail': tour_detail,
                'variants': variants,
                'schedules': schedules
            })
        else:
            print(f"❌ Failed to get tour details: {tour_detail_response.status_code}")
    
    return tour_details

def test_cart_operations(user_sessions, tour_details):
    """Test 3: Cart Operations (Add, View, Update, Remove)"""
    print_section("3. CART OPERATIONS")
    
    if not tour_details:
        print("❌ No tour details available for testing")
        return
    
    # Use first user and first tour for testing
    test_username = list(user_sessions.keys())[0]
    test_user_data = user_sessions[test_username]
    test_tour = tour_details[0]
    
    print_subsection(f"Testing with user: {test_username}")
    print(f"Tour: {test_tour['slug']}")
    
    client = test_user_data['client']
    
    # Add to cart
    print_subsection("Adding to Cart")
    if test_tour['variants'] and test_tour['schedules']:
        variant = test_tour['variants'][0]
        schedule = test_tour['schedules'][0]
        
        add_data = {
            'product_type': 'tour',
            'product_id': test_tour['id'],
            'variant_id': variant['id'],
            'quantity': 1,
            'booking_date': schedule['start_date'],
            'selected_options': []
        }
        
        add_response = client.post('/api/v1/cart/add/', add_data, format='json')
        if add_response.status_code in [200, 201]:
            add_result = add_response.json()
            cart_item = add_result.get('cart_item', {})
            item_id = cart_item.get('id')
            
            print(f"✅ Added to cart successfully")
            print(f"   Item ID: {item_id}")
            print(f"   Variant: {cart_item.get('variant_name', 'Unknown')}")
            print(f"   Quantity: {cart_item.get('quantity', 0)}")
            print(f"   Unit Price: ${cart_item.get('unit_price', 0)}")
            print(f"   Total Price: ${cart_item.get('total_price', 0)}")
            
            # Check cart contents
            print_subsection("Checking Cart Contents")
            cart_response = client.get('/api/v1/cart/')
            if cart_response.status_code == 200:
                cart_data = cart_response.json()
                if isinstance(cart_data, dict):
                    total_items = cart_data.get('total_items', 0)
                    items = cart_data.get('items', [])
                    subtotal = cart_data.get('subtotal', 0)
                    total = cart_data.get('total_price', 0)
                    
                    print(f"✅ Cart contents:")
                    print(f"   Total items: {total_items}")
                    print(f"   Unique items: {len(items)}")
                    print(f"   Subtotal: ${subtotal}")
                    print(f"   Total: ${total}")
                    
                    if items:
                        item = items[0]
                        print(f"   Item details:")
                        print(f"     Title: {item.get('product_title', 'Unknown')}")
                        print(f"     Quantity: {item.get('quantity', 0)}")
                        print(f"     Price: ${item.get('unit_price', 0)}")
                        print(f"     Total: ${item.get('total_price', 0)}")
                    else:
                        print("   ⚠️ Cart appears empty despite successful add")
                else:
                    print(f"   ⚠️ Unexpected cart response type: {type(cart_data)}")
            else:
                print(f"❌ Failed to get cart: {cart_response.status_code}")
            
            # Update cart item
            if item_id:
                print_subsection("Updating Cart Item")
                update_data = {
                    'quantity': 2,
                    'selected_options': []
                }
                
                update_response = client.put(f'/api/v1/cart/items/{item_id}/update/', update_data, format='json')
                if update_response.status_code == 200:
                    print("✅ Cart item updated successfully")
                    
                    # Check cart after update
                    cart_response = client.get('/api/v1/cart/')
                    if cart_response.status_code == 200:
                        cart_data = cart_response.json()
                        if isinstance(cart_data, dict):
                            total_items = cart_data.get('total_items', 0)
                            subtotal = cart_data.get('subtotal', 0)
                            total = cart_data.get('total_price', 0)
                            print(f"   After update - Total items: {total_items}, Subtotal: ${subtotal}, Total: ${total}")
                else:
                    print(f"❌ Failed to update cart item: {update_response.status_code}")
                
                # Remove from cart
                print_subsection("Removing from Cart")
                remove_response = client.delete(f'/api/v1/cart/items/{item_id}/remove/')
                if remove_response.status_code == 200:
                    print("✅ Item removed successfully")
                    
                    # Check cart after removal
                    cart_response = client.get('/api/v1/cart/')
                    if cart_response.status_code == 200:
                        cart_data = cart_response.json()
                        if isinstance(cart_data, dict):
                            total_items = cart_data.get('total_items', 0)
                            items = cart_data.get('items', [])
                            print(f"   After removal - Total items: {total_items}, Unique items: {len(items)}")
                            if total_items == 0 and len(items) == 0:
                                print("✅ Cart is empty after removal")
                            else:
                                print("❌ Cart not empty after removal")
                else:
                    print(f"❌ Failed to remove item: {remove_response.status_code}")
        else:
            print(f"❌ Failed to add to cart: {add_response.status_code}")
            print(f"   Response: {add_response.content}")
    else:
        print("❌ Tour missing variants or schedules")

def test_checkout(user_sessions, tour_details):
    """Test 4: Checkout Process"""
    print_section("4. CHECKOUT PROCESS")
    
    if not tour_details:
        print("❌ No tour details available for testing")
        return
    
    # Use first user and first tour
    test_username = list(user_sessions.keys())[0]
    test_user_data = user_sessions[test_username]
    test_tour = tour_details[0]
    
    print_subsection(f"Testing checkout with user: {test_username}")
    
    client = test_user_data['client']
    
    # Add item to cart first
    if test_tour['variants'] and test_tour['schedules']:
        variant = test_tour['variants'][0]
        schedule = test_tour['schedules'][0]
        
        add_data = {
            'product_type': 'tour',
            'product_id': test_tour['id'],
            'variant_id': variant['id'],
            'quantity': 1,
            'booking_date': schedule['start_date'],
            'selected_options': []
        }
        
        add_response = client.post('/api/v1/cart/add/', add_data, format='json')
        if add_response.status_code in [200, 201]:
            print("✅ Item added to cart for checkout test")
            
            # Try checkout
            print_subsection("Attempting Checkout")
            checkout_data = {
                'payment_method': 'mock',
                'billing_address': {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'phone': '+1234567890'
                }
            }
            
            checkout_response = client.post('/api/v1/cart/checkout/', checkout_data, format='json')
            print(f"Checkout response status: {checkout_response.status_code}")
            
            if checkout_response.status_code in [200, 201]:
                checkout_result = checkout_response.json()
                print("✅ Checkout successful")
                print(f"   Order ID: {checkout_result.get('order_id', 'N/A')}")
                print(f"   Status: {checkout_result.get('status', 'N/A')}")
                
                # Check if cart is cleared
                cart_response = client.get('/api/v1/cart/')
                if cart_response.status_code == 200:
                    cart_data = cart_response.json()
                    if isinstance(cart_data, dict):
                        total_items = cart_data.get('total_items', 0)
                        items = cart_data.get('items', [])
                        print(f"   Cart after checkout - Total items: {total_items}, Unique items: {len(items)}")
                        if total_items == 0:
                            print("✅ Cart cleared after checkout")
                        else:
                            print("❌ Cart not cleared after checkout")
            else:
                print(f"❌ Checkout failed: {checkout_response.status_code}")
                print(f"   Response: {checkout_response.content}")
        else:
            print("❌ Failed to add item for checkout test")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive API Test")
    print("=" * 60)
    
    try:
        # Test 1: User Sessions
        user_sessions = test_user_sessions()
        
        # Test 2: Tour Details
        tour_details = test_tours()
        
        # Test 3: Cart Operations
        if user_sessions and tour_details:
            test_cart_operations(user_sessions, tour_details)
        
        # Test 4: Checkout
        if user_sessions and tour_details:
            test_checkout(user_sessions, tour_details)
        
        print_section("TEST COMPLETE")
        print("✅ All API tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 