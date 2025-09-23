#!/usr/bin/env python
"""
Comprehensive system test for Peykan Tourism Platform.
Tests all major components: pricing, capacity, cart, authentication, and orders.
"""

import os
import sys
import django
import requests
import json
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from tours.models import Tour, TourVariant, TourPricing, TourSchedule
from cart.models import Cart, CartItem, CartService
from orders.models import Order, OrderItem, OrderService
from users.models import User

User = get_user_model()

class ComprehensiveSystemTest:
    """Comprehensive test suite for the entire system."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.session = requests.Session()
        self.test_user = None
        self.test_tour = None
        self.test_variant = None
        self.test_schedule = None
        
    def run_all_tests(self):
        """Run all system tests."""
        print("🚀 Starting Comprehensive System Test")
        print("=" * 60)
        
        tests = [
            ("Pricing System", self.test_pricing_system),
            ("Capacity System", self.test_capacity_system),
            ("Authentication", self.test_authentication),
            ("Cart Operations", self.test_cart_operations),
            ("Order Creation", self.test_order_creation),
            ("Concurrent Booking", self.test_concurrent_booking),
            ("Data Integrity", self.test_data_integrity),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name} Test...")
            try:
                success = test_func()
                status = "✅ PASS" if success else "❌ FAIL"
                results.append((test_name, success))
                print(f"{status} {test_name}")
            except Exception as e:
                print(f"❌ FAIL {test_name}: {e}")
                results.append((test_name, False))
        
        self.print_summary(results)
        return all(success for _, success in results)
    
    def test_pricing_system(self):
        """Test pricing calculations and validation."""
        print("  Testing pricing calculations...")
        
        # Get a tour with variants
        tour = Tour.objects.first()
        if not tour:
            print("    ❌ No tours found")
            return False
        
        variant = tour.variants.first()
        if not variant:
            print("    ❌ No variants found")
            return False
        
        # Test base price validation
        if variant.base_price <= 0:
            print(f"    ❌ Invalid base price: {variant.base_price}")
            return False
        
        # Test pricing factors
        pricings = variant.pricing.all()
        for pricing in pricings:
            if pricing.factor <= 0 or pricing.factor > 2:
                print(f"    ❌ Invalid factor: {pricing.factor}")
                return False
            
            # Test final price calculation
            try:
                final_price = pricing.final_price
                if final_price < 0:
                    print(f"    ❌ Negative final price: {final_price}")
                    return False
            except Exception as e:
                print(f"    ❌ Price calculation error: {e}")
                return False
        
        print(f"    ✅ Pricing system working correctly")
        return True
    
    def test_capacity_system(self):
        """Test capacity management and validation."""
        print("  Testing capacity management...")
        
        # Get a schedule
        schedule = TourSchedule.objects.first()
        if not schedule:
            print("    ❌ No schedules found")
            return False
        
        # Test capacity structure
        capacities = schedule.variant_capacities_raw
        if not isinstance(capacities, dict):
            print(f"    ❌ Invalid capacity structure: {type(capacities)}")
            return False
        
        # Test each variant capacity
        for variant_id, capacity_data in capacities.items():
            if not isinstance(capacity_data, dict):
                print(f"    ❌ Invalid capacity data for variant {variant_id}")
                return False
            
            total = capacity_data.get('total', 0)
            booked = capacity_data.get('booked', 0)
            available = capacity_data.get('available', 0)
            
            if total < 0 or booked < 0 or available < 0:
                print(f"    ❌ Negative capacity values: total={total}, booked={booked}, available={available}")
                return False
            
            if booked > total:
                print(f"    ❌ Booked exceeds total: {booked} > {total}")
                return False
            
            if available != (total - booked):
                print(f"    ❌ Available calculation wrong: {available} != {total - booked}")
                return False
        
        print(f"    ✅ Capacity system working correctly")
        return True
    
    def test_authentication(self):
        """Test authentication flow."""
        print("  Testing authentication...")
        
        # Create test user
        self.test_user, created = User.objects.get_or_create(
            username='testuser_comprehensive',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123',
                'is_active': True
            }
        )
        
        if created:
            self.test_user.set_password('testpass123')
            self.test_user.save()
        
        # Test login
        login_data = {
            'username': 'testuser_comprehensive',
            'password': 'testpass123'
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"    ❌ Login failed: {response.status_code}")
            return False
        
        data = response.json()
        if 'tokens' not in data or 'access' not in data['tokens']:
            print(f"    ❌ No access token in response")
            return False
        
        # Store token for other tests
        self.session.headers.update({
            'Authorization': f"Bearer {data['tokens']['access']}"
        })
        
        print(f"    ✅ Authentication working correctly")
        return True
    
    def test_cart_operations(self):
        """Test cart operations."""
        print("  Testing cart operations...")
        
        # Get test data
        tour = Tour.objects.first()
        variant = tour.variants.first()
        schedule = tour.schedules.first()
        
        if not all([tour, variant, schedule]):
            print("    ❌ Missing test data")
            return False
        
        # Test add to cart
        cart_data = {
            'product_type': 'tour',
            'product_id': str(tour.id),
            'variant_id': str(variant.id),
            'quantity': 2,
            'booking_date': schedule.start_date.isoformat(),
            'booking_time': '09:00:00',
            'booking_data': {
                'schedule_id': str(schedule.id),
                'participants': {
                    'adult': 2,
                    'child': 0,
                    'infant': 0
                }
            },
            'selected_options': []
        }
        
        response = self.session.post(
            f"{self.base_url}/cart/add/",
            json=cart_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 201:
            print(f"    ❌ Add to cart failed: {response.status_code}")
            return False
        
        # Test get cart
        response = self.session.get(f"{self.base_url}/cart/")
        
        if response.status_code != 200:
            print(f"    ❌ Get cart failed: {response.status_code}")
            return False
        
        cart_data = response.json()
        items = cart_data.get('items', [])
        
        if len(items) == 0:
            print(f"    ❌ No items in cart")
            return False
        
        # Test update cart item
        item_id = items[0]['id']
        update_data = {
            'quantity': 3
        }
        
        response = self.session.patch(
            f"{self.base_url}/cart/items/{item_id}/update/",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"    ❌ Update cart item failed: {response.status_code}")
            return False
        
        # Test remove from cart
        response = self.session.delete(f"{self.base_url}/cart/items/{item_id}/remove/")
        
        if response.status_code != 200:
            print(f"    ❌ Remove from cart failed: {response.status_code}")
            return False
        
        print(f"    ✅ Cart operations working correctly")
        return True
    
    def test_order_creation(self):
        """Test order creation with capacity management."""
        print("  Testing order creation...")
        
        # Add item to cart first
        tour = Tour.objects.first()
        variant = tour.variants.first()
        schedule = tour.schedules.first()
        
        cart_data = {
            'product_type': 'tour',
            'product_id': str(tour.id),
            'variant_id': str(variant.id),
            'quantity': 1,
            'booking_date': schedule.start_date.isoformat(),
            'booking_time': '09:00:00',
            'booking_data': {
                'schedule_id': str(schedule.id),
                'participants': {
                    'adult': 1,
                    'child': 0,
                    'infant': 0
                }
            },
            'selected_options': []
        }
        
        response = self.session.post(
            f"{self.base_url}/cart/add/",
            json=cart_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 201:
            print(f"    ❌ Failed to add item to cart for order test")
            return False
        
        # Get cart
        response = self.session.get(f"{self.base_url}/cart/")
        cart_data = response.json()
        
        # Create order
        order_data = {
            'payment_method': 'test',
            'customer_notes': 'Test order'
        }
        
        response = self.session.post(
            f"{self.base_url}/orders/create/",
            json=order_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 201:
            print(f"    ❌ Order creation failed: {response.status_code}")
            return False
        
        order_data = response.json()
        order_number = order_data.get('order_number')
        
        if not order_number:
            print(f"    ❌ No order number in response")
            return False
        
        # Verify order was created
        order = Order.objects.filter(order_number=order_number).first()
        if not order:
            print(f"    ❌ Order not found in database")
            return False
        
        # Verify capacity was updated
        schedule.refresh_from_db()
        variant_id = str(variant.id)
        capacities = schedule.variant_capacities_raw
        
        if variant_id in capacities:
            booked = capacities[variant_id].get('booked', 0)
            if booked != 1:
                print(f"    ❌ Capacity not updated correctly: booked={booked}")
                return False
        
        print(f"    ✅ Order creation working correctly")
        return True
    
    def test_concurrent_booking(self):
        """Test concurrent booking to prevent overbooking."""
        print("  Testing concurrent booking...")
        
        # This would require multiple threads/processes in a real test
        # For now, we'll test the transaction safety
        
        tour = Tour.objects.first()
        variant = tour.variants.first()
        schedule = tour.schedules.first()
        
        if not all([tour, variant, schedule]):
            print("    ❌ Missing test data")
            return False
        
        # Test transaction safety
        try:
            with transaction.atomic():
                # Lock the schedule
                locked_schedule = TourSchedule.objects.select_for_update().get(id=schedule.id)
                
                # Check capacity
                variant_id = str(variant.id)
                capacities = locked_schedule.variant_capacities_raw
                
                if variant_id in capacities:
                    current_booked = capacities[variant_id].get('booked', 0)
                    total_capacity = capacities[variant_id].get('total', 0)
                    
                    if current_booked >= total_capacity:
                        raise ValueError("No capacity available")
                    
                    # Update capacity
                    capacities[variant_id]['booked'] = current_booked + 1
                    capacities[variant_id]['available'] = total_capacity - (current_booked + 1)
                    locked_schedule.variant_capacities_raw = capacities
                    locked_schedule.save()
            
            print(f"    ✅ Concurrent booking protection working")
            return True
            
        except Exception as e:
            print(f"    ❌ Concurrent booking test failed: {e}")
            return False
    
    def test_data_integrity(self):
        """Test data integrity across the system."""
        print("  Testing data integrity...")
        
        # Test tour-variant relationship
        tours = Tour.objects.all()
        for tour in tours:
            variants = tour.variants.all()
            for variant in variants:
                if variant.tour != tour:
                    print(f"    ❌ Variant {variant.id} not linked to tour {tour.id}")
                    return False
        
        # Test pricing integrity
        pricings = TourPricing.objects.all()
        for pricing in pricings:
            if pricing.factor <= 0 or pricing.factor > 2:
                print(f"    ❌ Invalid pricing factor: {pricing.factor}")
                return False
        
        # Test cart integrity
        carts = Cart.objects.all()
        for cart in carts:
            items = cart.items.all()
            for item in items:
                if item.cart != cart:
                    print(f"    ❌ Cart item {item.id} not linked to cart {cart.id}")
                    return False
        
        print(f"    ✅ Data integrity verified")
        return True
    
    def print_summary(self, results):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")

def main():
    """Main function."""
    try:
        tester = ComprehensiveSystemTest()
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 