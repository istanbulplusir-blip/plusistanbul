"""
Comprehensive tests for Transfer booking flow.
"""

import json
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TransferRoute, TransferRoutePricing, TransferOption, TransferBooking
from .services import TransferPricingService, TransferRouteService, TransferBookingService
from cart.models import Cart, CartItem, CartService
from orders.models import Order, OrderItem, OrderService

User = get_user_model()


class TransferModelTests(TestCase):
    """Test transfer models."""
    
    def setUp(self):
        """Set up test data."""
        self.route = TransferRoute.objects.create(
            name="Airport Transfer",
            description="Transfer from airport to city",
            origin="Istanbul Airport",
            destination="Taksim Square",
            slug="airport-transfer",
            peak_hour_surcharge=25.0,
            midnight_surcharge=50.0,
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=15.0,
            is_popular=True
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type="sedan",
            base_price=45.00,
            max_passengers=4,
            max_luggage=3
        )
        
        self.option = TransferOption.objects.create(
            route=self.route,
            name="Child Seat",
            description="Safety child seat",
            option_type="equipment",
            price_type="fixed",
            price=10.00,
            max_quantity=2
        )
    
    def test_route_creation(self):
        """Test route creation."""
        self.assertEqual(self.route.name, "Airport Transfer")
        self.assertEqual(self.route.origin, "Istanbul Airport")
        self.assertEqual(self.route.destination, "Taksim Square")
        self.assertTrue(self.route.is_popular)
        self.assertEqual(self.route.round_trip_discount_percentage, 15.0)
    
    def test_pricing_creation(self):
        """Test pricing creation."""
        self.assertEqual(self.pricing.route, self.route)
        self.assertEqual(self.pricing.vehicle_type, "sedan")
        self.assertEqual(self.pricing.base_price, 45.00)
        self.assertEqual(self.pricing.max_passengers, 4)
    
    def test_option_creation(self):
        """Test option creation."""
        self.assertEqual(self.option.route, self.route)
        self.assertEqual(self.option.name, "Child Seat")
        self.assertEqual(self.option.price, 10.00)
        self.assertEqual(self.option.option_type, "equipment")
    
    def test_route_time_surcharge_calculation(self):
        """Test time surcharge calculation."""
        base_price = Decimal('45.00')
        
        # Peak hour (8 AM)
        peak_surcharge = self.route.calculate_time_surcharge(base_price, 8)
        expected_peak = base_price * (Decimal('25.0') / Decimal('100'))
        self.assertEqual(peak_surcharge, expected_peak)
        
        # Midnight hour (11 PM)
        midnight_surcharge = self.route.calculate_time_surcharge(base_price, 23)
        expected_midnight = base_price * (Decimal('50.0') / Decimal('100'))
        self.assertEqual(midnight_surcharge, expected_midnight)
        
        # Normal hour (2 PM)
        normal_surcharge = self.route.calculate_time_surcharge(base_price, 14)
        self.assertEqual(normal_surcharge, Decimal('0.00'))
    
    def test_option_price_calculation(self):
        """Test option price calculation."""
        base_price = Decimal('45.00')
        
        # Fixed price option
        fixed_price = self.option.calculate_price(base_price)
        self.assertEqual(fixed_price, Decimal('10.00'))
        
        # Percentage option
        percentage_option = TransferOption.objects.create(
            route=self.route,
            name="Meet & Greet",
            description="Meet and greet service",
            option_type="service",
            price_type="percentage",
            price_percentage=20.0,
            max_quantity=1
        )
        
        percentage_price = percentage_option.calculate_price(base_price)
        expected_percentage = base_price * (Decimal('20.0') / Decimal('100'))
        self.assertEqual(percentage_price, expected_percentage)


class TransferPricingServiceTests(TestCase):
    """Test transfer pricing service."""
    
    def setUp(self):
        """Set up test data."""
        self.route = TransferRoute.objects.create(
            name="Airport Transfer",
            description="Transfer from airport to city",
            origin="Istanbul Airport",
            destination="Taksim Square",
            slug="airport-transfer",
            peak_hour_surcharge=25.0,
            midnight_surcharge=50.0,
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=15.0
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type="sedan",
            base_price=45.00,
            max_passengers=4,
            max_luggage=3
        )
        
        self.option = TransferOption.objects.create(
            route=self.route,
            name="Child Seat",
            description="Safety child seat",
            option_type="equipment",
            price_type="fixed",
            price=10.00,
            max_quantity=2
        )
    
    def test_one_way_normal_hour_pricing(self):
        """Test one-way transfer pricing during normal hours."""
        booking_time = time(14, 0)  # 2 PM
        
        result = TransferPricingService.calculate_price(
            route=self.route,
            pricing=self.pricing,
            booking_time=booking_time,
            return_time=None,
            selected_options=[]
        )
        
        self.assertEqual(result['price_breakdown']['base_price'], 45.0)
        self.assertEqual(result['price_breakdown']['outbound_price'], 45.0)
        self.assertEqual(result['price_breakdown']['outbound_surcharge'], 0.0)
        self.assertEqual(result['price_breakdown']['return_price'], 0.0)
        self.assertEqual(result['price_breakdown']['round_trip_discount'], 0.0)
        self.assertEqual(result['price_breakdown']['final_price'], 45.0)
    
    def test_one_way_peak_hour_pricing(self):
        """Test one-way transfer pricing during peak hours."""
        booking_time = time(8, 0)  # 8 AM (peak)
        
        result = TransferPricingService.calculate_price(
            route=self.route,
            pricing=self.pricing,
            booking_time=booking_time,
            return_time=None,
            selected_options=[]
        )
        
        expected_surcharge = 45.0 * 0.25  # 25% surcharge
        expected_total = 45.0 + expected_surcharge
        
        self.assertEqual(result['price_breakdown']['base_price'], 45.0)
        self.assertEqual(result['price_breakdown']['outbound_surcharge'], expected_surcharge)
        self.assertEqual(result['price_breakdown']['final_price'], expected_total)
    
    def test_round_trip_with_discount(self):
        """Test round trip pricing with discount."""
        booking_time = time(8, 0)  # 8 AM (peak)
        return_time = time(18, 0)  # 6 PM (peak)
        
        result = TransferPricingService.calculate_price(
            route=self.route,
            pricing=self.pricing,
            booking_time=booking_time,
            return_time=return_time,
            selected_options=[]
        )
        
        base_price = 45.0
        outbound_surcharge = base_price * 0.25
        return_surcharge = base_price * 0.25
        outbound_total = base_price + outbound_surcharge
        return_total = base_price + return_surcharge
        
        total_before_discount = outbound_total + return_total
        discount = total_before_discount * 0.15  # 15% discount
        final_price = total_before_discount - discount
        
        self.assertEqual(result['price_breakdown']['outbound_price'], outbound_total)
        self.assertEqual(result['price_breakdown']['return_price'], return_total)
        self.assertEqual(result['price_breakdown']['round_trip_discount'], discount)
        self.assertEqual(result['price_breakdown']['final_price'], final_price)
    
    def test_pricing_with_options(self):
        """Test pricing with selected options."""
        booking_time = time(14, 0)  # 2 PM
        selected_options = [
            {
                'option_id': str(self.option.id),
                'quantity': 1
            }
        ]
        
        result = TransferPricingService.calculate_price(
            route=self.route,
            pricing=self.pricing,
            booking_time=booking_time,
            return_time=None,
            selected_options=selected_options
        )
        
        expected_total = 45.0 + 10.0  # Base price + option price
        
        self.assertEqual(result['price_breakdown']['options_total'], 10.0)
        self.assertEqual(result['price_breakdown']['final_price'], expected_total)
        self.assertEqual(len(result['options_breakdown']), 1)
        self.assertEqual(result['options_breakdown'][0]['name'], 'Child Seat')
    
    def test_midnight_surcharge(self):
        """Test midnight surcharge calculation."""
        booking_time = time(23, 30)  # 11:30 PM
        
        result = TransferPricingService.calculate_price(
            route=self.route,
            pricing=self.pricing,
            booking_time=booking_time,
            return_time=None,
            selected_options=[]
        )
        
        expected_surcharge = 45.0 * 0.5  # 50% surcharge
        expected_total = 45.0 + expected_surcharge
        
        self.assertEqual(result['price_breakdown']['outbound_surcharge'], expected_surcharge)
        self.assertEqual(result['price_breakdown']['final_price'], expected_total)
        self.assertEqual(result['time_info']['time_category'], 'midnight')


class TransferAPITests(APITestCase):
    """Test transfer API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.route = TransferRoute.objects.create(
            name="Airport Transfer",
            description="Transfer from airport to city",
            origin="Istanbul Airport",
            destination="Taksim Square",
            slug="airport-transfer",
            peak_hour_surcharge=25.0,
            midnight_surcharge=50.0,
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=15.0,
            is_popular=True
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type="sedan",
            base_price=45.00,
            max_passengers=4,
            max_luggage=3
        )
        
        self.option = TransferOption.objects.create(
            route=self.route,
            name="Child Seat",
            description="Safety child seat",
            option_type="equipment",
            price_type="fixed",
            price=10.00,
            max_quantity=2
        )
    
    def test_get_routes_list(self):
        """Test getting routes list."""
        url = reverse('transferroute-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Airport Transfer')
    
    def test_get_popular_routes(self):
        """Test getting popular routes."""
        url = reverse('transferroute-popular')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Airport Transfer')
    
    def test_get_route_detail(self):
        """Test getting route details."""
        url = reverse('transferroute-detail', kwargs={'pk': self.route.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Airport Transfer')
        self.assertEqual(len(response.data['pricing']), 1)
        self.assertEqual(len(response.data['options']), 1)
    
    def test_calculate_price(self):
        """Test price calculation endpoint."""
        url = reverse('transferroute-calculate-price', kwargs={'pk': self.route.id})
        data = {
            'vehicle_type': 'sedan',
            'booking_time': '08:30:00',
            'return_time': '18:00:00',
            'selected_options': [
                {
                    'option_id': str(self.option.id),
                    'quantity': 1
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('price_breakdown', response.data)
        self.assertIn('trip_info', response.data)
        self.assertIn('route_info', response.data)
        self.assertIn('time_info', response.data)
    
    def test_create_booking(self):
        """Test creating a booking."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        url = reverse('transferbooking-list')
        data = {
            'route_id': str(self.route.id),
            'vehicle_type': 'sedan',
            'trip_type': 'one_way',
            'outbound_date': '2024-02-15',
            'outbound_time': '14:00:00',
            'passenger_count': 2,
            'luggage_count': 1,
            'pickup_address': 'Istanbul Airport',
            'dropoff_address': 'Taksim Square',
            'contact_name': 'John Doe',
            'contact_phone': '+90 555 123 4567'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TransferBooking.objects.count(), 1)
        
        booking = TransferBooking.objects.first()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.route, self.route)
        self.assertEqual(booking.passenger_count, 2)
    
    def test_booking_validation_passenger_count(self):
        """Test booking validation for passenger count."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        url = reverse('transferbooking-list')
        data = {
            'route_id': str(self.route.id),
            'vehicle_type': 'sedan',
            'trip_type': 'one_way',
            'outbound_date': '2024-02-15',
            'outbound_time': '14:00:00',
            'passenger_count': 6,  # Exceeds max_passengers (4)
            'luggage_count': 1,
            'pickup_address': 'Istanbul Airport',
            'dropoff_address': 'Taksim Square',
            'contact_name': 'John Doe',
            'contact_phone': '+90 555 123 4567'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('passenger_count', str(response.data))


class TransferCartIntegrationTests(TransactionTestCase):
    """Test transfer integration with cart system."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.route = TransferRoute.objects.create(
            name="Airport Transfer",
            description="Transfer from airport to city",
            origin="Istanbul Airport",
            destination="Taksim Square",
            slug="airport-transfer",
            peak_hour_surcharge=25.0,
            midnight_surcharge=50.0,
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=15.0
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type="sedan",
            base_price=45.00,
            max_passengers=4,
            max_luggage=3
        )
        
        self.option = TransferOption.objects.create(
            route=self.route,
            name="Child Seat",
            description="Safety child seat",
            option_type="equipment",
            price_type="fixed",
            price=10.00,
            max_quantity=2
        )
    
    def test_add_transfer_to_cart(self):
        """Test adding transfer to cart."""
        cart = CartService.get_or_create_cart(
            session_id='test_session',
            user=self.user
        )
        
        product_data = {
            'product_type': 'transfer',
            'product_id': str(self.route.id),
            'booking_date': date(2024, 2, 15),
            'booking_time': time(14, 0),
            'quantity': 1,
            'booking_data': {
                'vehicle_type': 'sedan',
                'trip_type': 'one_way',
                'outbound_time': '14:00:00',
                'passenger_count': 2,
                'luggage_count': 1,
                'pickup_address': 'Istanbul Airport',
                'dropoff_address': 'Taksim Square',
                'contact_name': 'John Doe',
                'contact_phone': '+90 555 123 4567'
            },
            'selected_options': [
                {
                    'option_id': str(self.option.id),
                    'quantity': 1,
                    'price': 10.00
                }
            ]
        }
        
        result = CartService.add_to_cart(cart, product_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(cart.items.count(), 1)
        
        cart_item = cart.items.first()
        self.assertEqual(cart_item.product_type, 'transfer')
        self.assertEqual(cart_item.product_id, self.route.id)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart_item.unit_price, 45.00)
        self.assertEqual(cart_item.total_price, 55.00)  # 45 + 10 (option)
        self.assertEqual(cart_item.options_total, 10.00)
    
    def test_cart_to_order_conversion(self):
        """Test converting cart with transfer to order."""
        cart = CartService.get_or_create_cart(
            session_id='test_session',
            user=self.user
        )
        
        # Add transfer to cart
        product_data = {
            'product_type': 'transfer',
            'product_id': str(self.route.id),
            'booking_date': date(2024, 2, 15),
            'booking_time': time(14, 0),
            'quantity': 1,
            'booking_data': {
                'vehicle_type': 'sedan',
                'trip_type': 'one_way',
                'outbound_time': '14:00:00',
                'passenger_count': 2,
                'luggage_count': 1,
                'pickup_address': 'Istanbul Airport',
                'dropoff_address': 'Taksim Square',
                'contact_name': 'John Doe',
                'contact_phone': '+90 555 123 4567'
            },
            'selected_options': [
                {
                    'option_id': str(self.option.id),
                    'quantity': 1,
                    'price': 10.00
                }
            ]
        }
        
        CartService.add_to_cart(cart, product_data)
        
        # Convert to order
        order = OrderService.create_order_from_cart(cart, self.user)
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, 55.00)
        self.assertEqual(order.items.count(), 1)
        
        order_item = order.items.first()
        self.assertEqual(order_item.product_type, 'transfer')
        self.assertEqual(order_item.product_title, 'Airport Transfer')
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.total_price, 55.00)
        self.assertEqual(order_item.options_total, 10.00)
        
        # Verify booking data is preserved
        booking_data = order_item.booking_data
        self.assertEqual(booking_data['vehicle_type'], 'sedan')
        self.assertEqual(booking_data['trip_type'], 'one_way')
        self.assertEqual(booking_data['passenger_count'], 2)
        self.assertEqual(booking_data['contact_name'], 'John Doe')
        
        # Verify cart is cleared
        self.assertEqual(cart.items.count(), 0)


class TransferComplexPricingTests(TestCase):
    """Test complex pricing scenarios."""
    
    def setUp(self):
        """Set up test data."""
        self.route = TransferRoute.objects.create(
            name="Airport Transfer",
            description="Transfer from airport to city",
            origin="Istanbul Airport",
            destination="Taksim Square",
            slug="airport-transfer",
            peak_hour_surcharge=25.0,
            midnight_surcharge=50.0,
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=15.0
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type="sedan",
            base_price=100.00,  # Higher base price for easier calculation
            max_passengers=4,
            max_luggage=3
        )
        
        self.fixed_option = TransferOption.objects.create(
            route=self.route,
            name="Child Seat",
            description="Safety child seat",
            option_type="equipment",
            price_type="fixed",
            price=20.00,
            max_quantity=2
        )
        
        self.percentage_option = TransferOption.objects.create(
            route=self.route,
            name="Meet & Greet",
            description="Meet and greet service",
            option_type="service",
            price_type="percentage",
            price_percentage=10.0,
            max_quantity=1
        )
    
    def test_complex_round_trip_calculation(self):
        """Test complex round trip with peak hours, midnight, and options."""
        # Outbound: 8 AM (peak), Return: 11 PM (midnight)
        booking_time = time(8, 0)
        return_time = time(23, 0)
        
        selected_options = [
            {
                'option_id': str(self.fixed_option.id),
                'quantity': 2
            },
            {
                'option_id': str(self.percentage_option.id),
                'quantity': 1
            }
        ]
        
        result = TransferPricingService.calculate_price(
            route=self.route,
            pricing=self.pricing,
            booking_time=booking_time,
            return_time=return_time,
            selected_options=selected_options
        )
        
        # Expected calculations:
        base_price = 100.0
        
        # Outbound: 8 AM (peak +25%)
        outbound_surcharge = base_price * 0.25  # 25.0
        outbound_total = base_price + outbound_surcharge  # 125.0
        
        # Return: 11 PM (midnight +50%)
        return_surcharge = base_price * 0.50  # 50.0
        return_total = base_price + return_surcharge  # 150.0
        
        # Round trip discount (15% of total before options)
        total_before_discount = outbound_total + return_total  # 275.0
        round_trip_discount = total_before_discount * 0.15  # 41.25
        
        # Options
        fixed_option_total = 20.0 * 2  # 40.0
        percentage_option_total = base_price * 0.10  # 10.0
        options_total = fixed_option_total + percentage_option_total  # 50.0
        
        # Final price
        final_price = total_before_discount - round_trip_discount + options_total  # 283.75
        
        self.assertEqual(result['price_breakdown']['base_price'], base_price)
        self.assertEqual(result['price_breakdown']['outbound_price'], outbound_total)
        self.assertEqual(result['price_breakdown']['return_price'], return_total)
        self.assertEqual(result['price_breakdown']['round_trip_discount'], round_trip_discount)
        self.assertEqual(result['price_breakdown']['options_total'], options_total)
        self.assertEqual(result['price_breakdown']['final_price'], final_price)
        
        # Verify options breakdown
        self.assertEqual(len(result['options_breakdown']), 2)
        
        # Check trip info
        self.assertTrue(result['trip_info']['is_round_trip'])
        self.assertEqual(result['trip_info']['vehicle_type'], 'sedan')
        
        # Check time info
        self.assertEqual(result['time_info']['time_category'], 'peak')
        self.assertEqual(result['time_info']['booking_hour'], 8)


class TransferServiceTests(TestCase):
    """Test transfer service classes."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.route = TransferRoute.objects.create(
            name="Airport Transfer",
            description="Transfer from airport to city",
            origin="Istanbul Airport",
            destination="Taksim Square",
            slug="airport-transfer",
            peak_hour_surcharge=25.0,
            midnight_surcharge=50.0,
            round_trip_discount_enabled=True,
            round_trip_discount_percentage=15.0,
            is_popular=True
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type="sedan",
            base_price=45.00,
            max_passengers=4,
            max_luggage=3
        )
    
    def test_route_service_get_popular_routes(self):
        """Test getting popular routes."""
        routes = TransferRouteService.get_popular_routes(limit=5)
        
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].name, "Airport Transfer")
        self.assertTrue(routes[0].is_popular)
    
    def test_route_service_get_route_by_id(self):
        """Test getting route by ID."""
        route = TransferRouteService.get_route_by_id(self.route.id)
        
        self.assertEqual(route, self.route)
        self.assertEqual(route.name, "Airport Transfer")
    
    def test_route_service_search_routes(self):
        """Test searching routes."""
        # Search by origin
        results = TransferRouteService.search_routes(origin="Istanbul")
        self.assertEqual(results.count(), 1)
        
        # Search by destination
        results = TransferRouteService.search_routes(destination="Taksim")
        self.assertEqual(results.count(), 1)
        
        # Search by query
        results = TransferRouteService.search_routes(query="Airport")
        self.assertEqual(results.count(), 1)
        
        # Search by vehicle type
        results = TransferRouteService.search_routes(vehicle_type="sedan")
        self.assertEqual(results.count(), 1)
        
        # No results
        results = TransferRouteService.search_routes(origin="NonExistent")
        self.assertEqual(results.count(), 0)
    
    def test_booking_service_create_booking(self):
        """Test creating booking through service."""
        booking_data = {
            'outbound_date': date(2024, 2, 15),
            'outbound_time': time(14, 0),
            'trip_type': 'one_way',
            'passenger_count': 2,
            'luggage_count': 1,
            'pickup_address': 'Istanbul Airport',
            'dropoff_address': 'Taksim Square',
            'contact_name': 'John Doe',
            'contact_phone': '+90 555 123 4567'
        }
        
        booking = TransferBookingService.create_booking(
            user=self.user,
            route=self.route,
            pricing=self.pricing,
            booking_data=booking_data
        )
        
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.route, self.route)
        self.assertEqual(booking.pricing, self.pricing)
        self.assertEqual(booking.passenger_count, 2)
        self.assertEqual(booking.contact_name, 'John Doe')
        self.assertEqual(booking.final_price, 45.00)  # Base price for normal hour
    
    def test_booking_service_cancel_booking(self):
        """Test cancelling booking through service."""
        # Create booking first
        booking = TransferBooking.objects.create(
            user=self.user,
            route=self.route,
            pricing=self.pricing,
            trip_type='one_way',
            outbound_date=date(2024, 2, 15),
            outbound_time=time(14, 0),
            passenger_count=2,
            luggage_count=1,
            pickup_address='Istanbul Airport',
            dropoff_address='Taksim Square',
            contact_name='John Doe',
            contact_phone='+90 555 123 4567',
            outbound_price=45.00,
            final_price=45.00,
            status='pending'
        )
        
        # Cancel booking
        cancelled_booking = TransferBookingService.cancel_booking(
            booking_id=booking.id,
            user=self.user
        )
        
        self.assertEqual(cancelled_booking.status, 'cancelled')
        self.assertEqual(cancelled_booking.id, booking.id) 