#!/usr/bin/env python
"""
Comprehensive System Check for Peykan Tourism Platform
Checks all critical components: Users, Tours, Cart functionality
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import authenticate
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

from users.models import User
from tours.models import Tour, TourVariant, TourSchedule, TourPricing
from cart.models import Cart, CartItem, CartService

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    print(f"\n--- {title} ---")

def check_users():
    """Check user authentication and availability"""
    print_section("USER AUTHENTICATION CHECK")
    
    # Check active users
    active_users = User.objects.filter(is_active=True)
    print(f"Active users found: {active_users.count()}")
    
    for user in active_users:
        print(f"  - Username: {user.username}")
        print(f"    Email: {user.email}")
        print(f"    Role: {user.role}")
        print(f"    Is_active: {user.is_active}")
        
        # Test authentication
        if user.username and user.password:
            auth_user = authenticate(username=user.username, password='testpass123')
            if auth_user:
                print(f"    ✅ Authentication: SUCCESS")
            else:
                print(f"    ❌ Authentication: FAILED")
        print()
    
    # Test specific users
    test_users = ['customer', 'testuser', 'admin']
    for username in test_users:
        try:
            user = User.objects.get(username=username, is_active=True)
            auth_user = authenticate(username=username, password='testpass123')
            if auth_user:
                print(f"✅ {username}: Authentication successful")
            else:
                print(f"❌ {username}: Authentication failed")
        except User.DoesNotExist:
            print(f"❌ {username}: User not found")

def check_tours():
    """Check tour availability and pricing"""
    print_section("TOUR AVAILABILITY CHECK")
    
    # Check active tours
    active_tours = Tour.objects.filter(is_active=True)
    print(f"Active tours found: {active_tours.count()}")
    
    for tour in active_tours[:3]:  # Check first 3 tours
        print_subsection(f"Tour: {tour.title}")
        print(f"Slug: {tour.slug}")
        print(f"Is_active: {tour.is_active}")
        
        # Check variants
        variants = tour.variants.all()
        print(f"Variants: {variants.count()}")
        
        for variant in variants:
            print(f"  - {variant.name}: base_price=${variant.base_price}")
            
            # Check pricing for each age group
            pricing = variant.pricing.all()
            print(f"    Pricing records: {pricing.count()}")
            
            for price in pricing:
                print(f"      {price.age_group}: factor={price.factor}, is_free={price.is_free}")
        
        # Check schedules
        schedules = tour.schedules.filter(is_available=True)
        print(f"Available schedules: {schedules.count()}")
        
        for schedule in schedules[:2]:  # Show first 2 schedules
            print(f"  - Date: {schedule.start_date}, Available: {schedule.is_available}")
            print(f"    Max capacity: {schedule.max_capacity}, Current: {schedule.current_capacity}")
            
            # Check variant capacities
            if schedule.variant_capacities:
                print(f"    Variant capacities: {schedule.variant_capacities}")
        
        # Test price calculation
        try:
            if variants.exists() and schedules.exists():
                variant = variants.first()
                schedule = schedules.first()
                
                # Test pricing calculation
                adult_pricing = variant.pricing.filter(age_group='adult').first()
                if adult_pricing:
                    base_price = variant.base_price
                    factor = adult_pricing.factor
                    final_price = base_price * factor
                    print(f"    Price test: ${base_price} * {factor} = ${final_price}")
                    
                    if final_price > 0:
                        print(f"    ✅ Price calculation: VALID")
                    else:
                        print(f"    ❌ Price calculation: INVALID (zero or negative)")
                else:
                    print(f"    ❌ No adult pricing found")
        except Exception as e:
            print(f"    ❌ Price calculation error: {e}")
        
        print()

def check_cart_functionality():
    """Check cart API functionality"""
    print_section("CART FUNCTIONALITY CHECK")
    
    # Create test client
    client = APIClient()
    
    # Test user login
    test_username = 'customer'
    test_password = 'testpass123'
    
    try:
        user = User.objects.get(username=test_username, is_active=True)
        print(f"Test user: {user.username}")
        
        # Authenticate and get token
        auth_user = authenticate(username=test_username, password=test_password)
        if auth_user:
            refresh = RefreshToken.for_user(auth_user)
            access_token = str(refresh.access_token)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
    except User.DoesNotExist:
        print(f"❌ Test user '{test_username}' not found")
        return
    
    # Test cart endpoints
    print_subsection("Cart API Endpoints")
    
    # 1. Get cart
    try:
        response = client.get('/api/v1/cart/')
        print(f"GET /cart/: {response.status_code}")
        if response.status_code == 200:
            cart_data = response.json()
            # Handle both dict and list responses
            if isinstance(cart_data, dict):
                print(f"  Cart items: {cart_data.get('total_items', 0)}")
            else:
                print(f"  Cart response: {type(cart_data)} - {len(cart_data) if hasattr(cart_data, '__len__') else 'unknown'}")
        else:
            print(f"  Error: {response.content}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 2. Get available tours for testing
    try:
        tours_response = client.get('/api/v1/tours/')
        if tours_response.status_code == 200:
            tours_data = tours_response.json()
            available_tours = tours_data.get('results', [])
            print(f"Available tours for testing: {len(available_tours)}")
            
            if available_tours:
                test_tour = available_tours[0]
                tour_id = test_tour['id']
                tour_slug = test_tour['slug']
                print(f"Using tour: {test_tour['title']} (ID: {tour_id})")
                
                # 3. Test add to cart
                print_subsection("Add to Cart Test")
                
                # Get tour details to find variants and schedules
                tour_detail_response = client.get(f'/api/v1/tours/{tour_slug}/')
                if tour_detail_response.status_code == 200:
                    tour_detail = tour_detail_response.json()
                    variants = tour_detail.get('variants', [])
                    schedules = tour_detail.get('schedules', [])
                    
                    if variants and schedules:
                        variant = variants[0]
                        schedule = schedules[0]
                        
                        add_to_cart_data = {
                            'product_type': 'tour',
                            'product_id': tour_id,
                            'variant_id': variant['id'],
                            'quantity': 1,
                            'booking_date': schedule['start_date'],
                            'selected_options': []
                        }
                        
                        add_response = client.post('/api/v1/cart/add/', add_to_cart_data, format='json')
                        print(f"POST /cart/add/: {add_response.status_code}")
                        
                        if add_response.status_code in [200, 201]:
                            add_data = add_response.json()
                            print("✅ Add to cart successful")
                            
                            # Get cart item ID for update test
                            cart_item = add_data.get('cart_item', {})
                            item_id = cart_item.get('id')
                            
                            if item_id:
                                print(f"Cart item ID: {item_id}")
                                
                                # 4. Test update cart item
                                print_subsection("Update Cart Item Test")
                                update_data = {
                                    'quantity': 2,
                                    'selected_options': []
                                }
                                
                                update_response = client.put(f'/api/v1/cart/items/{item_id}/update/', update_data, format='json')
                                print(f"PUT /cart/items/{item_id}/update/: {update_response.status_code}")
                                
                                if update_response.status_code == 200:
                                    print("✅ Update cart item successful")
                                else:
                                    print(f"❌ Update failed: {update_response.content}")
                                
                                # 5. Test remove from cart
                                print_subsection("Remove from Cart Test")
                                remove_response = client.delete(f'/api/v1/cart/items/{item_id}/remove/')
                                print(f"DELETE /cart/items/{item_id}/remove/: {remove_response.status_code}")
                                
                                if remove_response.status_code == 200:
                                    print("✅ Remove from cart successful")
                                else:
                                    print(f"❌ Remove failed: {remove_response.content}")
                            else:
                                print("❌ No cart item ID returned")
                        else:
                            print(f"❌ Add to cart failed: {add_response.content}")
                    else:
                        print("❌ No variants or schedules available for testing")
                else:
                    print(f"❌ Could not get tour details: {tour_detail_response.status_code}")
            else:
                print("❌ No tours available for testing")
        else:
            print(f"❌ Could not get tours: {tours_response.status_code}")
            
    except Exception as e:
        print(f"❌ Cart testing error: {e}")

def check_pricing_calculation():
    """Check pricing calculation logic"""
    print_section("PRICING CALCULATION CHECK")
    
    tours = Tour.objects.filter(is_active=True)[:3]
    
    for tour in tours:
        print_subsection(f"Tour: {tour.title}")
        
        variants = tour.variants.all()
        for variant in variants:
            print(f"Variant: {variant.name}")
            print(f"Base price: ${variant.base_price}")
            
            # Check pricing for all age groups
            pricing_records = variant.pricing.all()
            
            for pricing in pricing_records:
                try:
                    if pricing.is_free:
                        final_price = Decimal('0.00')
                    else:
                        final_price = variant.base_price * pricing.factor
                    
                    print(f"  {pricing.age_group}: factor={pricing.factor}, final_price=${final_price}")
                    
                    if final_price >= 0:
                        print(f"    ✅ Price valid")
                    else:
                        print(f"    ❌ Price invalid (negative)")
                        
                except Exception as e:
                    print(f"    ❌ Price calculation error: {e}")
            
            print()

def main():
    """Run all checks"""
    print("🚀 Starting Comprehensive System Check")
    print("=" * 60)
    
    try:
        check_users()
        check_tours()
        check_pricing_calculation()
        check_cart_functionality()
        
        print_section("CHECK COMPLETE")
        print("✅ All checks completed successfully!")
        
    except Exception as e:
        print(f"❌ System check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 