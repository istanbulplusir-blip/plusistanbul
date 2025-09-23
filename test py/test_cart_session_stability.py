#!/usr/bin/env python
"""
Comprehensive test script for cart session stability.
Tests the fixes implemented for session consistency issues.
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from cart.models import Cart, CartItem, CartService
from tours.models import Tour, TourVariant, TourSchedule

User = get_user_model()

class CartSessionStabilityTest:
    """Test class for cart session stability."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.client = Client()
        self.session = requests.Session()
        self.test_user = None
        self.test_tour = None
        self.test_variant = None
        self.test_schedule = None
        
    def setup_test_data(self):
        """Setup test data for cart testing."""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.test_user, created = User.objects.get_or_create(
            username='testuser_cart',
            defaults={
                'email': 'testuser_cart@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        if created:
            self.test_user.set_password('testpass123')
            self.test_user.save()
            print(f"✅ Created test user: {self.test_user.username}")
        else:
            print(f"✅ Using existing test user: {self.test_user.username}")
        
        # Get or create test tour
        self.test_tour = Tour.objects.filter(is_active=True).first()
        if not self.test_tour:
            print("❌ No active tours found. Please create a tour first.")
            return False
        
        # Get or create test variant
        self.test_variant = TourVariant.objects.filter(tour=self.test_tour, is_active=True).first()
        if not self.test_variant:
            print("❌ No active tour variants found. Please create a variant first.")
            return False
        
        # Get or create test schedule
        self.test_schedule = TourSchedule.objects.filter(tour=self.test_tour, is_available=True).first()
        if not self.test_schedule:
            print("❌ No available tour schedules found. Please create a schedule first.")
            return False
        
        print(f"✅ Test data setup complete:")
        print(f"   - Tour: {self.test_tour.title}")
        print(f"   - Variant: {self.test_variant.name}")
        print(f"   - Schedule: {self.test_schedule.start_date}")
        
        return True
    
    def login_user(self):
        """Login the test user and get JWT token."""
        print("🔐 Logging in test user...")
        
        login_data = {
            'username': self.test_user.username,
            'password': 'testpass123'
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            if token:
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                print("✅ Login successful")
                return True
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_cart_session_consistency(self):
        """Test that cart session remains consistent across requests."""
        print("\n🧪 Testing cart session consistency...")
        
        # Test 1: Add item to cart
        print("   📝 Adding item to cart...")
        add_data = {
            'product_type': 'tour',
            'product_id': str(self.test_tour.id),
            'variant_id': str(self.test_variant.id),
            'quantity': 2,
            'selected_options': [],
            'booking_data': {
                'schedule_id': str(self.test_schedule.id),
                'participants': {
                    'adult': 2,
                    'child': 0,
                    'infant': 0
                },
                'special_requests': 'Test request'
            }
        }
        
        add_response = self.session.post(
            f"{self.base_url}/cart/add/",
            json=add_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if add_response.status_code != 201:
            print(f"❌ Failed to add item: {add_response.status_code} - {add_response.text}")
            return False
        
        add_data = add_response.json()
        cart_item_id = add_data.get('cart_item', {}).get('id')
        print(f"✅ Item added successfully. Cart item ID: {cart_item_id}")
        
        # Test 2: Get cart immediately after adding
        print("   📋 Getting cart contents...")
        get_response = self.session.get(f"{self.base_url}/cart/")
        
        if get_response.status_code != 200:
            print(f"❌ Failed to get cart: {get_response.status_code} - {get_response.text}")
            return False
        
        cart_data = get_response.json()
        items = cart_data.get('items', [])
        
        if not items:
            print("❌ Cart is empty after adding item!")
            return False
        
        print(f"✅ Cart contains {len(items)} items")
        
        # Test 3: Verify session consistency
        print("   🔍 Verifying session consistency...")
        
        # Get session ID from response headers
        session_cookie = self.session.cookies.get('sessionid')
        if session_cookie:
            print(f"   Session ID: {session_cookie}")
        else:
            print("   ⚠️  No session cookie found")
        
        # Test 4: Get cart again to verify consistency
        print("   🔄 Getting cart again to verify consistency...")
        get_response2 = self.session.get(f"{self.base_url}/cart/")
        
        if get_response2.status_code != 200:
            print(f"❌ Failed to get cart second time: {get_response2.status_code}")
            return False
        
        cart_data2 = get_response2.json()
        items2 = cart_data2.get('items', [])
        
        if len(items) != len(items2):
            print(f"❌ Cart item count changed: {len(items)} -> {len(items2)}")
            return False
        
        print("✅ Cart session consistency verified")
        return True
    
    def test_cart_persistence_after_refresh(self):
        """Test that cart persists after page refresh simulation."""
        print("\n🧪 Testing cart persistence after refresh...")
        
        # Get cart before "refresh"
        print("   📋 Getting cart before refresh...")
        get_response = self.session.get(f"{self.base_url}/cart/")
        
        if get_response.status_code != 200:
            print(f"❌ Failed to get cart: {get_response.status_code}")
            return False
        
        cart_data = get_response.json()
        items_before = cart_data.get('items', [])
        item_count_before = len(items_before)
        
        print(f"   Items before refresh: {item_count_before}")
        
        # Simulate page refresh by making another request
        print("   🔄 Simulating page refresh...")
        time.sleep(1)  # Small delay to simulate refresh
        
        get_response2 = self.session.get(f"{self.base_url}/cart/")
        
        if get_response2.status_code != 200:
            print(f"❌ Failed to get cart after refresh: {get_response2.status_code}")
            return False
        
        cart_data2 = get_response2.json()
        items_after = cart_data2.get('items', [])
        item_count_after = len(items_after)
        
        print(f"   Items after refresh: {item_count_after}")
        
        if item_count_before != item_count_after:
            print(f"❌ Cart item count changed after refresh: {item_count_before} -> {item_count_after}")
            return False
        
        print("✅ Cart persistence after refresh verified")
        return True
    
    def test_cart_service_logic(self):
        """Test the CartService logic directly."""
        print("\n🧪 Testing CartService logic...")
        
        # Test CartService.get_session_id
        print("   🔍 Testing session ID generation...")
        
        # Create a mock request object
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.test_user
        
        # Ensure session is created
        if not request.session.session_key:
            request.session.create()
        
        session_id = CartService.get_session_id(request)
        print(f"   Generated session ID: {session_id}")
        
        # Test CartService.get_or_create_cart
        print("   🔍 Testing cart creation/retrieval...")
        
        cart1 = CartService.get_or_create_cart(session_id, self.test_user)
        print(f"   First cart ID: {cart1.id}")
        
        cart2 = CartService.get_or_create_cart(session_id, self.test_user)
        print(f"   Second cart ID: {cart2.id}")
        
        if cart1.id != cart2.id:
            print("❌ Different carts created for same session/user")
            return False
        
        print("✅ CartService logic verified")
        return True
    
    def test_cart_migration_logic(self):
        """Test cart migration from session to user."""
        print("\n🧪 Testing cart migration logic...")
        
        # Create a session cart first
        print("   📝 Creating session cart...")
        
        # Create a mock request for session cart
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = None  # Anonymous user
        
        if not request.session.session_key:
            request.session.create()
        
        session_id = CartService.get_session_id(request)
        
        # Create session cart
        session_cart = CartService.get_or_create_cart(session_id, None)
        print(f"   Session cart ID: {session_cart.id}")
        
        # Add an item to session cart
        cart_item = CartItem.objects.create(
            cart=session_cart,
            product_type='tour',
            product_id=self.test_tour.id,
            booking_date=self.test_schedule.start_date,
            booking_time=self.test_schedule.start_time,
            quantity=1,
            unit_price=100.00,
            currency='USD',
            selected_options=[],
            booking_data={}
        )
        print(f"   Added item to session cart: {cart_item.id}")
        
        # Test migration
        print("   🔄 Testing cart migration...")
        migrated_cart = CartService.migrate_session_cart_to_user(session_id, self.test_user)
        
        if not migrated_cart:
            print("❌ Cart migration failed")
            return False
        
        print(f"   Migrated cart ID: {migrated_cart.id}")
        print(f"   Migrated cart user: {migrated_cart.user}")
        
        # Verify items were migrated
        items = migrated_cart.items.all()
        if not items:
            print("❌ No items in migrated cart")
            return False
        
        print(f"   Migrated items: {len(items)}")
        print("✅ Cart migration logic verified")
        return True
    
    def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Clear test user's carts
        if self.test_user:
            Cart.objects.filter(user=self.test_user).delete()
            print("✅ Cleared test user carts")
        
        # Clear session carts
        Cart.objects.filter(user__isnull=True).delete()
        print("✅ Cleared session carts")
        
        print("✅ Cleanup complete")
    
    def run_all_tests(self):
        """Run all cart session stability tests."""
        print("🚀 Starting Cart Session Stability Tests")
        print("=" * 50)
        
        try:
            # Setup
            if not self.setup_test_data():
                return False
            
            # Login
            if not self.login_user():
                return False
            
            # Run tests
            tests = [
                ("Cart Session Consistency", self.test_cart_session_consistency),
                ("Cart Persistence After Refresh", self.test_cart_persistence_after_refresh),
                ("CartService Logic", self.test_cart_service_logic),
                ("Cart Migration Logic", self.test_cart_migration_logic),
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    if test_func():
                        passed += 1
                        print(f"✅ {test_name}: PASSED")
                    else:
                        print(f"❌ {test_name}: FAILED")
                except Exception as e:
                    print(f"❌ {test_name}: ERROR - {str(e)}")
            
            # Summary
            print(f"\n{'='*50}")
            print(f"📊 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed! Cart session stability is working correctly.")
            else:
                print("⚠️  Some tests failed. Please review the issues above.")
            
            return passed == total
            
        finally:
            self.cleanup_test_data()

def main():
    """Main function to run the tests."""
    print("Cart Session Stability Test Suite")
    print("This script tests the fixes for cart session consistency issues.")
    print()
    
    # Check if Django server is running
    try:
        response = requests.get("http://localhost:8000/api/v1/", timeout=5)
        if response.status_code != 200:
            print("❌ Django server is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Django server is not running. Please start the server first:")
        print("   python manage.py runserver")
        return
    
    # Run tests
    tester = CartSessionStabilityTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 Cart session stability issues have been resolved!")
        print("The system now properly handles:")
        print("  ✅ Consistent session ID generation")
        print("  ✅ Cart persistence across requests")
        print("  ✅ Proper user/session cart management")
        print("  ✅ Cart migration from guest to authenticated user")
    else:
        print("\n⚠️  Some issues remain. Please review the test results above.")

if __name__ == "__main__":
    main() 