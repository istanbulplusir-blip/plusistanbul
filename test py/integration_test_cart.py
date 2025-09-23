#!/usr/bin/env python3
"""
Integration test script for cart system consistency.
Tests the complete flow: login -> add variants -> verify cart -> check pricing
"""

import os
import sys
import django
import json
import requests
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import authenticate
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from users.models import User
from tours.models import Tour, TourVariant, TourSchedule, TourCategory
from cart.models import Cart, CartItem, CartService
from cart.views import AddToCartView
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class CartIntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.client = APIClient()
        self.user = None
        self.token = None
        self.tour = None
        self.variants = []
        self.schedule = None
        
    def log(self, message):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def setup_test_data(self):
        """Create test user, tour, and variants"""
        self.log("Setting up test data...")
        
        # Create test user
        self.user, created = User.objects.get_or_create(
            username='test_cart_user',
            defaults={
                'email': 'test_cart@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                'is_email_verified': True
            }
        )
        if created:
            self.user.set_password('testpass123')
            self.user.save()
            
        # Create test category first
        category, created = TourCategory.objects.get_or_create(
            slug='test-category',
            defaults={
                'name': 'Test Category',
                'description': 'Test category description',
                'is_active': True
            }
        )
        
        # Create test tour
        self.tour, created = Tour.objects.get_or_create(
            slug='test-tour-cart',
            defaults={
                'title': 'Test Tour for Cart',
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
        
        # Create test variants
        variant_data = [
            {'name': 'Eco', 'base_price': Decimal('80.00')},
            {'name': 'VIP', 'base_price': Decimal('150.00')},
        ]
        
        for variant_info in variant_data:
            variant, created = TourVariant.objects.get_or_create(
                tour=self.tour,
                name=variant_info['name'],
                defaults={
                    'description': f"{variant_info['name']} variant",
                    'base_price': variant_info['base_price'],
                    'capacity': 10,  # BaseVariantModel has 'capacity' not 'max_capacity'
                    'is_active': True
                }
            )
            self.variants.append(variant)
            
        # Create test schedule
        self.schedule, created = TourSchedule.objects.get_or_create(
            tour=self.tour,
            start_date=datetime.now().date() + timedelta(days=7),
            defaults={
                'end_date': datetime.now().date() + timedelta(days=7),
                'start_time': datetime.now().time(),
                'end_time': (datetime.now() + timedelta(hours=8)).time(),
                'day_of_week': 0,
                'max_capacity': 20,  # BaseScheduleModel field
                'current_capacity': 0,
                'variant_capacities_raw': {
                    str(self.variants[0].id): 10,
                    str(self.variants[1].id): 10
                },
                'is_available': True
            }
        )
        
        self.log(f"Created test data: User={self.user.username}, Tour={self.tour.title}, Variants={len(self.variants)}")
        
    def login_user(self):
        """Login user and get JWT token"""
        self.log("Logging in user...")
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.log(f"User logged in successfully. Token: {self.token[:20]}...")
        
    def test_session_id_generation(self):
        """Test session ID generation consistency"""
        self.log("Testing session ID generation...")
        
        # Test Django session
        factory = RequestFactory()
        request = factory.get('/')
        request.session = SessionStore()
        request.session.create()
        
        # Test CartService session ID generation
        session_id = CartService.get_session_id(request)
        
        self.log(f"Django session key: {request.session.session_key}")
        self.log(f"CartService session ID: {session_id}")
        
        # Test backend session handling
        request.user = self.user
        cart = CartService.get_or_create_cart(session_id=session_id, user=self.user)
        
        self.log(f"Cart created with session_id: {cart.session_id}")
        
        return session_id, cart
        
    def add_tour_variant_to_cart(self, variant, quantity=1):
        """Add a tour variant to cart via API"""
        self.log(f"Adding {variant.name} variant to cart (quantity: {quantity})...")
        
        # Prepare cart data
        cart_data = {
            'product_type': 'tour',
            'product_id': str(self.tour.id),
            'variant_id': str(variant.id),
            'quantity': quantity,
            'booking_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'booking_time': '09:00:00',
            'booking_data': {
                'participants': {
                    'adult': quantity,
                    'child': 0,
                    'infant': 0
                },
                'special_requests': f'Test booking for {variant.name}',
                'schedule_id': str(self.schedule.id)
            },
            'selected_options': []
        }
        
        # Make API call
        response = self.client.post(f"{self.base_url}/cart/add/", cart_data, format='json')
        
        if response.status_code == 201:
            self.log(f"✓ Successfully added {variant.name} variant to cart")
            return response.data
        else:
            self.log(f"✗ Failed to add {variant.name} variant: {response.status_code}")
            self.log(f"Response: {response.data}")
            return None
            
    def get_cart_content(self):
        """Get cart content via API"""
        self.log("Retrieving cart content...")
        
        response = self.client.get(f"{self.base_url}/cart/")
        
        if response.status_code == 200:
            cart_data = response.data
            self.log(f"✓ Cart retrieved successfully")
            self.log(f"Cart items: {len(cart_data.get('items', []))}")
            self.log(f"Cart total: {cart_data.get('total', 0)}")
            return cart_data
        else:
            self.log(f"✗ Failed to retrieve cart: {response.status_code}")
            return None
            
    def verify_pricing_calculation(self, cart_data):
        """Verify pricing calculations are correct"""
        self.log("Verifying pricing calculations...")
        
        if not cart_data or 'items' not in cart_data:
            self.log("✗ No cart data to verify")
            return False
            
        total_calculated = Decimal('0.00')
        
        for item in cart_data['items']:
            self.log(f"Item: {item.get('variant_name', 'Unknown')}")
            self.log(f"  Unit price: {item.get('unit_price', 0)}")
            self.log(f"  Quantity: {item.get('quantity', 0)}")
            self.log(f"  Options total: {item.get('options_total', 0)}")
            self.log(f"  Total price: {item.get('total_price', 0)}")
            
            # Calculate expected total
            unit_price = Decimal(str(item.get('unit_price', 0)))
            quantity = Decimal(str(item.get('quantity', 0)))
            options_total = Decimal(str(item.get('options_total', 0)))
            
            expected_total = (unit_price * quantity) + options_total
            actual_total = Decimal(str(item.get('total_price', 0)))
            
            self.log(f"  Expected total: {expected_total}")
            self.log(f"  Actual total: {actual_total}")
            
            if expected_total != actual_total:
                self.log(f"✗ Price calculation mismatch for item {item.get('id')}")
                return False
            else:
                self.log(f"✓ Price calculation correct for item {item.get('id')}")
                
            total_calculated += actual_total
            
        # Check cart total
        cart_total = Decimal(str(cart_data.get('total', 0)))
        self.log(f"Cart total calculated: {total_calculated}")
        self.log(f"Cart total from API: {cart_total}")
        
        if total_calculated != cart_total:
            self.log("✗ Cart total calculation mismatch")
            return False
        else:
            self.log("✓ Cart total calculation correct")
            return True
            
    def verify_variant_logic(self, cart_data):
        """Verify variant logic is working correctly"""
        self.log("Verifying variant logic...")
        
        if not cart_data or 'items' not in cart_data:
            self.log("✗ No cart data to verify")
            return False
            
        # Check that we have items for both variants
        variant_ids = [str(v.id) for v in self.variants]
        cart_variant_ids = [item.get('variant_id') for item in cart_data['items']]
        
        self.log(f"Expected variant IDs: {variant_ids}")
        self.log(f"Cart variant IDs: {cart_variant_ids}")
        
        for variant_id in variant_ids:
            if variant_id not in cart_variant_ids:
                self.log(f"✗ Missing variant {variant_id} in cart")
                return False
                
        self.log("✓ All variants present in cart")
        
        # Check that pricing reflects variant differences
        eco_item = next((item for item in cart_data['items'] if item.get('variant_name') == 'Eco'), None)
        vip_item = next((item for item in cart_data['items'] if item.get('variant_name') == 'VIP'), None)
        
        if not eco_item or not vip_item:
            self.log("✗ Missing Eco or VIP variant items")
            return False
            
        eco_price = Decimal(str(eco_item.get('unit_price', 0)))
        vip_price = Decimal(str(vip_item.get('unit_price', 0)))
        
        self.log(f"Eco price: {eco_price}")
        self.log(f"VIP price: {vip_price}")
        
        if vip_price <= eco_price:
            self.log("✗ VIP price should be higher than Eco price")
            return False
            
        self.log("✓ Variant pricing logic correct")
        return True
        
    def test_backend_direct_cart_access(self):
        """Test direct backend cart access"""
        self.log("Testing direct backend cart access...")
        
        # Get cart directly from backend
        session_id = f"test-session-{self.user.id}"
        cart = CartService.get_or_create_cart(session_id=session_id, user=self.user)
        
        # Check cart items
        items = cart.items.all()
        self.log(f"Backend cart items: {len(items)}")
        
        for item in items:
            self.log(f"  Item: {item.product_type} - {item.variant_name}")
            self.log(f"  Unit price: {item.unit_price}")
            self.log(f"  Total price: {item.total_price}")
            self.log(f"  Booking data: {item.booking_data}")
            
        return cart
        
    def run_full_test(self):
        """Run the complete integration test"""
        self.log("=" * 60)
        self.log("STARTING CART INTEGRATION TEST")
        self.log("=" * 60)
        
        try:
            # Setup
            self.setup_test_data()
            self.login_user()
            
            # Test session ID generation
            session_id, cart = self.test_session_id_generation()
            
            # Add variants to cart
            for i, variant in enumerate(self.variants):
                result = self.add_tour_variant_to_cart(variant, quantity=i+1)
                if not result:
                    self.log(f"✗ Failed to add variant {variant.name}")
                    return False
                    
            # Get cart content
            cart_data = self.get_cart_content()
            if not cart_data:
                self.log("✗ Failed to retrieve cart content")
                return False
                
            # Verify pricing
            pricing_ok = self.verify_pricing_calculation(cart_data)
            
            # Verify variant logic
            variant_ok = self.verify_variant_logic(cart_data)
            
            # Test backend direct access
            backend_cart = self.test_backend_direct_cart_access()
            
            # Final summary
            self.log("=" * 60)
            self.log("TEST RESULTS SUMMARY")
            self.log("=" * 60)
            self.log(f"✓ Test data setup: OK")
            self.log(f"✓ User login: OK")
            self.log(f"✓ Session ID generation: OK")
            self.log(f"✓ Add variants to cart: OK")
            self.log(f"✓ Retrieve cart content: OK")
            self.log(f"{'✓' if pricing_ok else '✗'} Pricing calculation: {'OK' if pricing_ok else 'FAILED'}")
            self.log(f"{'✓' if variant_ok else '✗'} Variant logic: {'OK' if variant_ok else 'FAILED'}")
            self.log(f"✓ Backend direct access: OK")
            
            overall_success = pricing_ok and variant_ok
            self.log(f"OVERALL TEST: {'PASSED' if overall_success else 'FAILED'}")
            
            return overall_success
            
        except Exception as e:
            self.log(f"✗ Test failed with exception: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
            
    def cleanup(self):
        """Clean up test data"""
        self.log("Cleaning up test data...")
        
        # Remove cart items
        CartItem.objects.filter(cart__user=self.user).delete()
        
        # Remove carts
        Cart.objects.filter(user=self.user).delete()
        
        # Note: We keep the test user and tour for future tests
        self.log("Cleanup completed")

if __name__ == "__main__":
    test = CartIntegrationTest()
    
    try:
        success = test.run_full_test()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        test.log("Test interrupted by user")
        exit_code = 1
    except Exception as e:
        test.log(f"Test failed with exception: {str(e)}")
        exit_code = 1
    finally:
        test.cleanup()
        
    sys.exit(exit_code) 