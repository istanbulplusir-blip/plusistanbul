#!/usr/bin/env python3
"""
Test script for tour booking flow including capacity management and duplicate booking restrictions.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from tours.models import Tour, TourVariant, TourSchedule, TourPricing
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

User = get_user_model()

class TourBookingFlowTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_user = None
        self.test_tour = None
        self.test_variant = None
        self.test_schedule = None
        self.session_id = None
        self.auth_token = None
        
    def setup_test_data(self):
        """Setup test data including user, tour, variant, and schedule."""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.test_user, created = User.objects.get_or_create(
            username='test_booking_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'phone_number': '+1234567890'
            }
        )
        if created:
            self.test_user.set_password('testpass123')
            self.test_user.save()
        print(f"✅ Test user: {self.test_user.username}")
        
        # Get or create test tour
        self.test_tour = Tour.objects.filter(slug='test-tour-16329065').first()
        if not self.test_tour:
            print("❌ Test tour not found. Please create tour with slug 'test-tour-16329065'")
            return False
        print(f"✅ Test tour: {self.test_tour.title}")
        
        # Get test variant
        self.test_variant = self.test_tour.variants.filter(is_active=True).first()
        if not self.test_variant:
            print("❌ No active variants found for test tour")
            return False
        print(f"✅ Test variant: {self.test_variant.name} (Capacity: {self.test_variant.capacity})")
        
        # Get or create test schedule
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.test_schedule, created = TourSchedule.objects.get_or_create(
            tour=self.test_tour,
            start_date=tomorrow,
            defaults={
                'end_date': tomorrow,
                'start_time': '09:00:00',
                'end_time': '17:00:00',
                'is_available': True,
                'variant_capacities_raw': {
                    str(self.test_variant.id): {
                        'total': self.test_variant.capacity,
                        'booked': 0,
                        'available': self.test_variant.capacity
                    }
                }
            }
        )
        if created:
            print(f"✅ Created test schedule for {tomorrow}")
        else:
            print(f"✅ Using existing schedule for {self.test_schedule.start_date}")
        
        # Setup pricing
        for age_group in ['adult', 'child', 'infant']:
            TourPricing.objects.get_or_create(
                tour=self.test_tour,
                variant=self.test_variant,
                age_group=age_group,
                defaults={
                    'factor': Decimal('1.0') if age_group == 'adult' else Decimal('0.5') if age_group == 'child' else Decimal('0.0'),
                    'is_free': age_group == 'infant',
                    'final_price': self.test_variant.base_price if age_group == 'adult' else self.test_variant.base_price * Decimal('0.5') if age_group == 'child' else Decimal('0')
                }
            )
        
        return True
    
    def authenticate_user(self):
        """Authenticate test user and get token."""
        print("🔐 Authenticating test user...")
        
        # Use session-based authentication for cart operations
        session = requests.Session()
        
        # Get CSRF token first
        try:
            csrf_response = session.get(f"{self.base_url}/api/v1/auth/login/")
            csrf_token = session.cookies.get('csrftoken')
            if csrf_token:
                print(f"   🔑 CSRF token obtained")
        except:
            csrf_token = None
        
        # Login to get session
        auth_data = {
            "username": self.test_user.username,
            "password": "testpass123"
        }
        
        try:
            print(f"   🔍 Attempting login with: {auth_data}")
            headers = {'Content-Type': 'application/json'}
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            
            response = session.post(
                f"{self.base_url}/api/v1/auth/login/",
                json=auth_data,
                headers=headers
            )
            
            print(f"   📡 Response status: {response.status_code}")
            print(f"   📡 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('tokens', {}).get('access')
                self.session = session
                print(f"   ✅ Authentication successful")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   📄 Response content: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication exception: {str(e)}")
            return False
    
    def get_initial_capacity(self):
        """Get initial capacity information."""
        print("\n📊 Initial Capacity Information:")
        
        # Get schedule capacity
        schedule = TourSchedule.objects.get(id=self.test_schedule.id)
        variant_capacities = schedule.variant_capacities_raw or {}
        variant_id = str(self.test_variant.id)
        
        if variant_id in variant_capacities:
            total = variant_capacities[variant_id].get('total', 0)
            booked = variant_capacities[variant_id].get('booked', 0)
            available = variant_capacities[variant_id].get('available', 0)
            
            print(f"   Schedule Capacity:")
            print(f"   - Total: {total}")
            print(f"   - Booked: {booked}")
            print(f"   - Available: {available}")
        
        # Count existing orders
        existing_orders = OrderItem.objects.filter(
            product_type='tour',
            product_id=self.test_tour.id,
            variant_id=self.test_variant.id,
            booking_date=self.test_schedule.start_date,
            order__status__in=['pending', 'confirmed', 'paid', 'completed']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Count cart items
        existing_cart = CartItem.objects.filter(
            product_type='tour',
            product_id=self.test_tour.id,
            variant_id=self.test_variant.id,
            booking_date=self.test_schedule.start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        print(f"   Database Counts:")
        print(f"   - Existing Orders: {existing_orders}")
        print(f"   - Cart Items: {existing_cart}")
        
        return {
            'schedule_total': total,
            'schedule_booked': booked,
            'schedule_available': available,
            'db_orders': existing_orders,
            'db_cart': existing_cart
        }
    
    def test_add_to_cart(self, participants):
        """Test adding tour to cart."""
        print(f"\n🛒 Testing Add to Cart with participants: {participants}")
        
        cart_data = {
            "product_type": "tour",
            "product_id": str(self.test_tour.id),
            "variant_id": str(self.test_variant.id),
            "quantity": 1,
            "booking_data": {
                "schedule_id": str(self.test_schedule.id),
                "participants": participants
            },
            "selected_options": []
        }
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            # Add CSRF token if available
            csrf_token = self.session.cookies.get('csrftoken')
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            
            response = self.session.post(
                f"{self.base_url}/api/v1/cart/add/",
                json=cart_data,
                headers=headers
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Success: {result.get('message', 'Item added to cart')}")
                return True, result
            else:
                try:
                    error = response.json()
                    print(f"   ❌ Error: {error.get('error', 'Unknown error')}")
                    return False, error
                except:
                    print(f"   ❌ Error: {response.text[:200]}")
                    return False, {'error': response.text}
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False, {'error': str(e)}
    
    def test_checkout(self):
        """Test checkout process."""
        print(f"\n💳 Testing Checkout Process")
        
        # Get user's cart
        try:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            response = self.session.get(f"{self.base_url}/api/v1/cart/", headers=headers)
            if response.status_code != 200:
                print(f"   ❌ Failed to get cart: {response.status_code}")
                return False, None
            
            cart_data = response.json()
            if not cart_data.get('items'):
                print(f"   ❌ No items in cart")
                return False, None
            
            print(f"   ✅ Cart has {len(cart_data['items'])} items")
            
            # Simulate checkout (create order)
            checkout_data = {
                "payment_method": "test",
                "customer_notes": "Test order"
            }
            
            headers = {'Content-Type': 'application/json'}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            # Add CSRF token if available
            csrf_token = self.session.cookies.get('csrftoken')
            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
            
            response = self.session.post(
                f"{self.base_url}/api/v1/orders/create/",
                json=checkout_data,
                headers=headers
            )
            
            print(f"   Checkout Status Code: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ Order created: {result.get('order_number', 'Unknown')}")
                return True, result
            else:
                try:
                    error = response.json()
                    print(f"   ❌ Checkout failed: {error.get('error', 'Unknown error')}")
                    return False, error
                except:
                    print(f"   ❌ Checkout failed: Non-JSON response")
                    print(f"   Response text: {response.text[:200]}")
                    return False, {'error': 'Non-JSON response'}
                
        except Exception as e:
            print(f"   ❌ Checkout exception: {str(e)}")
            return False, {'error': str(e)}
    
    def test_duplicate_booking(self, participants):
        """Test duplicate booking restriction."""
        print(f"\n🔄 Testing Duplicate Booking Restriction")
        
        cart_data = {
            "product_type": "tour",
            "product_id": str(self.test_tour.id),
            "variant_id": str(self.test_variant.id),
            "quantity": participants['adult'] + participants['child'],
            "booking_date": self.test_schedule.start_date.isoformat(),
            "booking_data": {
                "schedule_id": str(self.test_schedule.id),
                "participants": participants,
                "special_requests": "Duplicate test booking"
            },
            "selected_options": []
        }
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            response = self.session.post(
                f"{self.base_url}/api/v1/cart/add/",
                json=cart_data,
                headers=headers
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                result = response.json()
                if result.get('code') == 'DUPLICATE_BOOKING':
                    print(f"   ✅ Duplicate booking correctly blocked: {result.get('error')}")
                    return True
                else:
                    print(f"   ❌ Unexpected error: {result.get('error')}")
                    return False
            else:
                print(f"   ❌ Duplicate booking should have been blocked")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def check_capacity_after_booking(self):
        """Check capacity after booking."""
        print(f"\n📊 Capacity After Booking:")
        
        # Refresh schedule data
        schedule = TourSchedule.objects.get(id=self.test_schedule.id)
        variant_capacities = schedule.variant_capacities_raw or {}
        variant_id = str(self.test_variant.id)
        
        if variant_id in variant_capacities:
            total = variant_capacities[variant_id].get('total', 0)
            booked = variant_capacities[variant_id].get('booked', 0)
            available = variant_capacities[variant_id].get('available', 0)
            
            print(f"   Schedule Capacity:")
            print(f"   - Total: {total}")
            print(f"   - Booked: {booked}")
            print(f"   - Available: {available}")
        
        # Count orders
        existing_orders = OrderItem.objects.filter(
            product_type='tour',
            product_id=self.test_tour.id,
            variant_id=self.test_variant.id,
            booking_date=self.test_schedule.start_date,
            order__status__in=['pending', 'confirmed', 'paid', 'completed']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        print(f"   Database Orders: {existing_orders}")
        
        return {
            'schedule_total': total,
            'schedule_booked': booked,
            'schedule_available': available,
            'db_orders': existing_orders
        }
    
    def test_capacity_overflow(self, participants):
        """Test capacity overflow protection."""
        print(f"\n🚫 Testing Capacity Overflow Protection")
        
        cart_data = {
            "product_type": "tour",
            "product_id": str(self.test_tour.id),
            "variant_id": str(self.test_variant.id),
            "quantity": participants['adult'] + participants['child'],
            "booking_date": self.test_schedule.start_date.isoformat(),
            "booking_data": {
                "schedule_id": str(self.test_schedule.id),
                "participants": participants,
                "special_requests": "Overflow test booking"
            },
            "selected_options": []
        }
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            
            response = self.session.post(
                f"{self.base_url}/api/v1/cart/add/",
                json=cart_data,
                headers=headers
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                result = response.json()
                if result.get('code') == 'INSUFFICIENT_CAPACITY':
                    print(f"   ✅ Capacity overflow correctly blocked: {result.get('error')}")
                    return True
                else:
                    print(f"   ❌ Unexpected error: {result.get('error')}")
                    return False
            else:
                print(f"   ❌ Capacity overflow should have been blocked")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Cleanup test data."""
        print(f"\n🧹 Cleaning up test data...")
        
        # Delete test orders
        test_orders = Order.objects.filter(user=self.test_user)
        order_count = test_orders.count()
        test_orders.delete()
        print(f"   Deleted {order_count} test orders")
        
        # Delete test cart items
        test_cart_items = CartItem.objects.filter(
            product_type='tour',
            product_id=self.test_tour.id,
            booking_date=self.test_schedule.start_date
        )
        cart_count = test_cart_items.count()
        test_cart_items.delete()
        print(f"   Deleted {cart_count} test cart items")
        
        # Reset schedule capacity
        schedule = TourSchedule.objects.get(id=self.test_schedule.id)
        variant_id = str(self.test_variant.id)
        capacities = schedule.variant_capacities_raw or {}
        if variant_id in capacities:
            capacities[variant_id]['booked'] = 0
            capacities[variant_id]['available'] = capacities[variant_id]['total']
            schedule.variant_capacities_raw = capacities
            schedule.save()
        print(f"   Reset schedule capacity")
    
    def run_complete_test(self):
        """Run complete booking flow test."""
        print("🚀 Starting Complete Tour Booking Flow Test")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_data():
            print("❌ Setup failed")
            return
        
        # Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed")
            return
        
        # Initial capacity
        initial_capacity = self.get_initial_capacity()
        
        # Test 1: Add to cart
        participants = {'adult': 2, 'child': 1, 'infant': 1}
        success, result = self.test_add_to_cart(participants)
        if not success:
            print("❌ Add to cart failed")
            return
        
        # Test 2: Checkout
        success, order_result = self.test_checkout()
        if not success:
            print("❌ Checkout failed")
            return
        
        # Check capacity after booking
        after_capacity = self.check_capacity_after_booking()
        
        # Test 3: Duplicate booking
        duplicate_success = self.test_duplicate_booking(participants)
        
        # Test 4: Capacity overflow
        overflow_participants = {'adult': 50, 'child': 10, 'infant': 2}
        overflow_success = self.test_capacity_overflow(overflow_participants)
        
        # Summary
        print(f"\n📋 Test Summary:")
        print(f"=" * 60)
        print(f"✅ Add to Cart: {'PASS' if success else 'FAIL'}")
        print(f"✅ Checkout: {'PASS' if order_result else 'FAIL'}")
        print(f"✅ Duplicate Booking Blocked: {'PASS' if duplicate_success else 'FAIL'}")
        print(f"✅ Capacity Overflow Blocked: {'PASS' if overflow_success else 'FAIL'}")
        
        print(f"\n📊 Capacity Changes:")
        print(f"   Initial Available: {initial_capacity['schedule_available']}")
        print(f"   After Booking: {after_capacity['schedule_available']}")
        print(f"   Capacity Reduced: {initial_capacity['schedule_available'] - after_capacity['schedule_available']}")
        
        # Cleanup
        self.cleanup_test_data()
        
        print(f"\n🎉 Test completed!")

def main():
    """Main test runner."""
    test = TourBookingFlowTest()
    test.run_complete_test()

if __name__ == "__main__":
    main()
