#!/usr/bin/env python
"""
Simple E2E Test Script for Cart and Order Flow
Tests basic functionality without complex scenarios
"""

import os
import sys
import django
import requests
import json
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import SystemSettings
from cart.models import Cart, CartItem, CartService
from orders.models import Order, OrderItem, OrderService
from tours.models import Tour, TourVariant, TourSchedule

User = get_user_model()

class SimpleE2ETester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.user_token = None
        self.test_user = None
        
    def setup_test_data(self):
        """Setup test data and user"""
        print("🔧 Setting up test data...")
        
        # Get or create test user
        self.test_user, created = User.objects.get_or_create(
            username='test_simple',
            defaults={
                'email': 'test_simple@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Set password for test user
        self.test_user.set_password('testpass123')
        self.test_user.save()
        
        # Clear existing data
        Cart.objects.filter(user=self.test_user).delete()
        Order.objects.filter(user=self.test_user).delete()
        
        # Get system settings
        self.settings = SystemSettings.get_settings()
        print(f"📊 System Settings:")
        print(f"   Guest Items: {self.settings.cart_max_items_guest}")
        print(f"   Guest Total: {self.settings.cart_max_total_guest}")
        print(f"   User Items: {self.settings.cart_max_items_user}")
        print(f"   User Total: {self.settings.cart_max_total_user}")
        
    def test_user_login(self):
        """Test user login"""
        print("\n🧪 Testing User Login...")
        
        # Login as test user
        login_data = {
            'username': 'test_simple',
            'password': 'testpass123'
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ User login successful")
            data = response.json()
            self.user_token = data.get('tokens', {}).get('access')
            
            if self.user_token:
                # Update session headers with token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.user_token}'
                })
                return True
            else:
                print("❌ No access token in login response")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_cart_add(self):
        """Test adding item to cart"""
        print("\n🧪 Testing Cart Add...")
        
        # Get a tour for testing
        tour = Tour.objects.filter(is_active=True).first()
        if not tour:
            print("❌ No active tours found!")
            return False
            
        schedule = tour.schedules.filter(is_active=True).first()
        if not schedule:
            print("❌ No active schedules found!")
            return False
            
        variant = tour.variants.filter(is_active=True).first()
        if not variant:
            print("❌ No active variants found!")
            return False
            
        print(f"🎯 Testing with Tour: {tour.title}")
        print(f"   Schedule: {schedule.start_date}")
        print(f"   Variant: {variant.name}")
        
        # Test adding item to cart
        cart_data = {
            'product_type': 'tour',
            'product_id': str(tour.id),
            'variant_id': str(variant.id),
            'quantity': 1,
            'booking_date': schedule.start_date.strftime('%Y-%m-%d'),
            'booking_data': {
                'schedule_id': str(schedule.id),
                'participants': {
                    'adult': 2,
                    'child': 1,
                    'infant': 0
                }
            }
        }
        
        # Add to cart
        response = self.session.post(
            f"{self.base_url}/api/v1/cart/add/",
            json=cart_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("✅ Cart item added successfully")
            return True
        else:
            print(f"❌ Failed to add cart item: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_cart_list(self):
        """Test cart list"""
        print("\n🧪 Testing Cart List...")
        
        response = self.session.get(
            f"{self.base_url}/api/v1/cart/",
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Cart list retrieved successfully")
            data = response.json()
            print(f"   Items count: {len(data.get('items', []))}")
            return True
        else:
            print(f"❌ Failed to get cart list: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_order_creation(self):
        """Test order creation"""
        print("\n🧪 Testing Order Creation...")
        
        # Get cart items first
        cart_response = self.session.get(
            f"{self.base_url}/api/v1/cart/",
            headers={'Content-Type': 'application/json'}
        )
        
        if cart_response.status_code != 200:
            print("❌ Failed to get cart items")
            return False
            
        cart_data = cart_response.json()
        cart_items = cart_data.get('items', [])
        
        if not cart_items:
            print("❌ No items in cart to create order")
            return False
        
        # Create order with cart items
        order_data = {
            'payment_method': 'whatsapp',
            'customer_info': {
                'full_name': 'Test User',
                'email': 'test_simple@example.com',
                'phone': '+1234567890',
                'special_requests': 'Test order'
            },
            'items': cart_items,
            'total_amount': cart_data.get('total_price', 0),
            'currency': cart_data.get('currency', 'USD')
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/orders/",
            json=order_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            print("✅ Order created successfully")
            order_data = response.json()
            self.order_id = order_data.get('id')
            print(f"   Order ID: {self.order_id}")
            return True
        else:
            print(f"❌ Order creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_order_list(self):
        """Test order list"""
        print("\n🧪 Testing Order List...")
        
        response = self.session.get(
            f"{self.base_url}/api/v1/orders/",
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Order list retrieved successfully")
            data = response.json()
            
            # Handle both list and paginated response formats
            if isinstance(data, list):
                orders_count = len(data)
            else:
                orders_count = len(data.get('results', []))
            
            print(f"   Orders count: {orders_count}")
            return True
        else:
            print(f"❌ Failed to get order list: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_duplicate_booking_prevention(self):
        """Test duplicate booking prevention"""
        print("\n🧪 Testing Duplicate Booking Prevention...")
        
        # Try to add the same item again
        tour = Tour.objects.filter(is_active=True).first()
        schedule = tour.schedules.filter(is_active=True).first()
        variant = tour.variants.filter(is_active=True).first()
        
        cart_data = {
            'product_type': 'tour',
            'product_id': str(tour.id),
            'variant_id': str(variant.id),
            'quantity': 1,
            'booking_date': schedule.start_date.strftime('%Y-%m-%d'),
            'booking_data': {
                'schedule_id': str(schedule.id),
                'participants': {
                    'adult': 2,
                    'child': 1,
                    'infant': 0
                }
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/cart/add/",
            json=cart_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print("✅ Duplicate booking prevented")
            return True
        else:
            print(f"❌ Duplicate booking not prevented: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def run_complete_test(self):
        """Run complete E2E test"""
        print("🚀 Starting Simple E2E Test...")
        
        self.setup_test_data()
        
        tests = [
            ("User Login", self.test_user_login),
            ("Cart Add", self.test_cart_add),
            ("Cart List", self.test_cart_list),
            ("Order Creation", self.test_order_creation),
            ("Order List", self.test_order_list),
            ("Duplicate Booking Prevention", self.test_duplicate_booking_prevention),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n📊 Test Results Summary:")
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
        return passed == len(results)

if __name__ == "__main__":
    tester = SimpleE2ETester()
    success = tester.run_complete_test()
    sys.exit(0 if success else 1)
