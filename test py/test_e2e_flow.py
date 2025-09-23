#!/usr/bin/env python
"""
E2E Test Script for Cart and Order Flow
Tests the complete user journey from guest to authenticated user
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

class E2ETester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.guest_session_id = None
        self.user_token = None
        self.test_user = None
        
    def setup_test_data(self):
        """Setup test data and user"""
        print("🔧 Setting up test data...")
        
        # Get or create test user
        self.test_user, created = User.objects.get_or_create(
            username='test_e2e',
            defaults={
                'email': 'test_e2e@example.com',
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
        
    def test_guest_cart_flow(self):
        """Test guest user adding items to cart"""
        print("\n🧪 Testing Guest Cart Flow...")
        
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
        
        # Test adding item to guest cart
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
        
        # Add to cart as guest
        response = self.session.post(
            f"{self.base_url}/api/v1/cart/add/",
            json=cart_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("✅ Guest cart item added successfully")
            self.guest_session_id = self.session.cookies.get('sessionid')
            return True
        else:
            print(f"❌ Failed to add guest cart item: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_guest_limits(self):
        """Test guest cart limits"""
        print("\n🧪 Testing Guest Cart Limits...")
        
        # Get different tours for testing limits
        tours = Tour.objects.filter(is_active=True)[:self.settings.cart_max_items_guest + 1]
        
        if len(tours) < self.settings.cart_max_items_guest + 1:
            print(f"❌ Need at least {self.settings.cart_max_items_guest + 1} tours for testing")
            return False
        
        # Add items up to limit
        for i in range(self.settings.cart_max_items_guest + 1):
            tour = tours[i]
            schedule = tour.schedules.filter(is_active=True).first()
            variant = tour.variants.filter(is_active=True).first()
            
            if not schedule or not variant:
                print(f"❌ Tour {tour.title} missing schedule or variant")
                continue
                
            cart_data = {
                'product_type': 'tour',
                'product_id': str(tour.id),
                'variant_id': str(variant.id),
                'quantity': 1,
                'booking_date': schedule.start_date.strftime('%Y-%m-%d'),
                'booking_data': {
                    'schedule_id': str(schedule.id),
                    'participants': {
                        'adult': 1,
                        'child': 0,
                        'infant': 0
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/cart/add/",
                json=cart_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if i < self.settings.cart_max_items_guest:
                if response.status_code in [200, 201]:
                    print(f"✅ Item {i+1} added successfully ({tour.title})")
                else:
                    print(f"❌ Failed to add item {i+1}: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
            else:
                if response.status_code == 400:
                    print(f"✅ Limit enforced at item {i+1}")
                    return True
                else:
                    print(f"❌ Limit not enforced at item {i+1}: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
        
        return True
    
    def test_user_login(self):
        """Test user login"""
        print("\n🧪 Testing User Login...")
        
        # Login as test user
        login_data = {
            'username': 'test_e2e',
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
            self.user_token = data.get('access')
            
            # Update session headers with token
            self.session.headers.update({
                'Authorization': f'Bearer {self.user_token}'
            })
            
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_cart_merge(self):
        """Test cart merge functionality"""
        print("\n🧪 Testing Cart Merge...")
        
        if not self.guest_session_id:
            print("❌ No guest session to merge")
            return False
            
        # Merge guest cart
        merge_data = {
            'session_key': self.guest_session_id
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/cart/merge/",
            json=merge_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.user_token}'
            }
        )
        
        if response.status_code == 200:
            print("✅ Cart merge successful")
            return True
        else:
            print(f"❌ Cart merge failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_order_creation(self):
        """Test order creation"""
        print("\n🧪 Testing Order Creation...")
        
        order_data = {
            'payment_method': 'whatsapp',
            'customer_info': {
                'full_name': 'Test User',
                'email': 'test_e2e@example.com',
                'phone': '+1234567890',
                'special_requests': 'Test order'
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/orders/",
            json=order_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.user_token}'
            }
        )
        
        if response.status_code == 201:
            print("✅ Order created successfully")
            order_data = response.json()
            self.order_id = order_data.get('id')
            return True
        else:
            print(f"❌ Order creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_order_status_change(self):
        """Test order status change and capacity reduction"""
        print("\n🧪 Testing Order Status Change...")
        
        if not hasattr(self, 'order_id'):
            print("❌ No order to test")
            return False
            
        # Change order status to paid
        status_data = {
            'status': 'paid'
        }
        
        response = self.session.patch(
            f"{self.base_url}/api/v1/orders/{self.order_id}/",
            json=status_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.user_token}'
            }
        )
        
        if response.status_code == 200:
            print("✅ Order status changed to paid")
            
            # Check capacity reduction
            order = Order.objects.get(id=self.order_id)
            for item in order.items.all():
                if item.product_type == 'tour':
                    schedule = TourSchedule.objects.get(id=item.booking_data['schedule_id'])
                    print(f"   Schedule capacity: {schedule.booked_capacity}/{schedule.total_capacity}")
                    
            return True
        else:
            print(f"❌ Order status change failed: {response.status_code}")
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
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.user_token}'
            }
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
        print("🚀 Starting E2E Test...")
        
        self.setup_test_data()
        
        tests = [
            ("Guest Cart Flow", self.test_guest_cart_flow),
            ("Guest Limits", self.test_guest_limits),
            ("User Login", self.test_user_login),
            ("Cart Merge", self.test_cart_merge),
            ("Order Creation", self.test_order_creation),
            ("Order Status Change", self.test_order_status_change),
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
    tester = E2ETester()
    success = tester.run_complete_test()
    sys.exit(0 if success else 1)
