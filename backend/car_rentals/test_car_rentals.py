"""
Comprehensive tests for Car Rental booking flow.
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
from django.utils import timezone

from .models import (
    CarRental, CarRentalCategory, CarRentalImage, CarRentalOption,
    CarRentalAvailability, CarRentalBooking
)
from cart.models import Cart, CartItem, CartService
from orders.models import Order, OrderItem

User = get_user_model()


class CarRentalModelTests(TestCase):
    """Test car rental models."""
    
    def setUp(self):
        """Set up test data."""
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        self.category = CarRentalCategory.objects.create(
            name="Economy",
            description="Economy class cars",
            sort_order=1
        )
        
        self.car_rental = CarRental.objects.create(
            title="BMW 3 Series",
            description="Luxury sedan",
            short_description="Comfortable luxury sedan",
            brand="BMW",
            model="3 Series",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            min_rent_days=1,
            max_rent_days=30,
            mileage_limit_per_day=200,
            deposit_amount=500.00,
            price_per_day=100.00,
            price_per_hour=15.00,
            weekly_discount_percentage=10.00,
            monthly_discount_percentage=20.00,
            pickup_location="Istanbul Airport",
            dropoff_location="Istanbul Airport",
            basic_insurance_included=True,
            comprehensive_insurance_price=25.00,
            is_available=True,
            advance_booking_days=30,
            agent=self.agent,
            city="Istanbul",
            country="Turkey",
            currency="USD"
        )
        
        self.option = CarRentalOption.objects.create(
            name="GPS Navigation",
            description="GPS navigation system",
            option_type="gps",
            price_type="daily",
            price=10.00,
            max_quantity=1
        )
        
        self.availability = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_available=True,
            max_quantity=2,
            booked_quantity=0
        )
    
    def test_car_rental_creation(self):
        """Test car rental creation."""
        self.assertEqual(self.car_rental.brand, "BMW")
        self.assertEqual(self.car_rental.model, "3 Series")
        self.assertEqual(self.car_rental.year, 2023)
        self.assertEqual(self.car_rental.seats, 5)
        self.assertEqual(self.car_rental.fuel_type, "gasoline")
        self.assertEqual(self.car_rental.transmission, "automatic")
        self.assertEqual(self.car_rental.price_per_day, 100.00)
        self.assertEqual(self.car_rental.agent, self.agent)
    
    def test_daily_price_with_discount(self):
        """Test daily price calculation with discounts."""
        # 1 day - no discount
        price_1_day = self.car_rental.get_daily_price_with_discount(1)
        self.assertEqual(price_1_day, 100.00)
        
        # 7 days - weekly discount
        price_7_days = self.car_rental.get_daily_price_with_discount(7)
        expected_weekly = 100.00 - (100.00 * 0.10)
        self.assertEqual(price_7_days, expected_weekly)
        
        # 30 days - monthly discount
        price_30_days = self.car_rental.get_daily_price_with_discount(30)
        expected_monthly = 100.00 - (100.00 * 0.20)
        self.assertEqual(price_30_days, expected_monthly)
    
    def test_calculate_total_price(self):
        """Test total price calculation."""
        # Daily only
        total_daily = self.car_rental.calculate_total_price(days=3)
        self.assertEqual(total_daily, 300.00)
        
        # Daily + hourly
        total_mixed = self.car_rental.calculate_total_price(days=2, hours=4)
        expected = (2 * 100.00) + (4 * 15.00)
        self.assertEqual(total_mixed, expected)
        
        # With insurance
        total_with_insurance = self.car_rental.calculate_total_price(days=3, include_insurance=True)
        expected = (3 * 100.00) + (3 * 25.00)
        self.assertEqual(total_with_insurance, expected)
    
    def test_availability_creation(self):
        """Test availability creation."""
        self.assertEqual(self.availability.car_rental, self.car_rental)
        self.assertEqual(self.availability.max_quantity, 2)
        self.assertEqual(self.availability.booked_quantity, 0)
        self.assertTrue(self.availability.is_available)
    
    def test_availability_quantity_management(self):
        """Test availability quantity management."""
        # Test available quantity
        self.assertEqual(self.availability.available_quantity, 2)
        
        # Test reservation
        self.assertTrue(self.availability.is_available_for_booking(1))
        self.assertTrue(self.availability.is_available_for_booking(2))
        self.assertFalse(self.availability.is_available_for_booking(3))
        
        # Test reserve quantity
        self.assertTrue(self.availability.reserve_quantity(1))
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.booked_quantity, 1)
        self.assertEqual(self.availability.available_quantity, 1)
        
        # Test release quantity
        self.availability.release_quantity(1)
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.booked_quantity, 0)
        self.assertEqual(self.availability.available_quantity, 2)
    
    def test_option_price_calculation(self):
        """Test option price calculation."""
        base_price = Decimal('100.00')
        
        # Fixed price option
        fixed_price = self.option.calculate_price(base_price, days=3, quantity=1)
        self.assertEqual(fixed_price, 30.00)  # 10.00 * 3 days
        
        # Percentage option
        percentage_option = CarRentalOption.objects.create(
            name="Premium Insurance",
            description="Premium insurance coverage",
            option_type="premium_insurance",
            price_type="percentage",
            price_percentage=15.0,
            max_quantity=1
        )
        
        percentage_price = percentage_option.calculate_price(base_price, days=2, quantity=1)
        expected = (base_price * Decimal('0.15')) * 2  # 15% of base price for 2 days
        self.assertEqual(percentage_price, expected)


class CarRentalSerializerTests(TestCase):
    """Test car rental serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        self.category = CarRentalCategory.objects.create(
            name="Economy",
            description="Economy class cars"
        )
        
        self.car_rental = CarRental.objects.create(
            title="BMW 3 Series",
            description="Luxury sedan",
            brand="BMW",
            model="3 Series",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            min_rent_days=1,
            max_rent_days=30,
            price_per_day=100.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey"
        )
    
    def test_car_rental_list_serializer(self):
        """Test car rental list serializer."""
        from .serializers import CarRentalListSerializer
        
        serializer = CarRentalListSerializer(self.car_rental)
        data = serializer.data
        
        self.assertEqual(data['brand'], "BMW")
        self.assertEqual(data['model'], "3 Series")
        self.assertEqual(data['year'], 2023)
        self.assertEqual(data['seats'], 5)
        self.assertEqual(data['price_per_day'], "100.00")
        self.assertIn('pricing_summary', data)
    
    def test_car_rental_detail_serializer(self):
        """Test car rental detail serializer."""
        from .serializers import CarRentalDetailSerializer
        
        serializer = CarRentalDetailSerializer(self.car_rental)
        data = serializer.data
        
        self.assertEqual(data['title'], "BMW 3 Series")
        self.assertEqual(data['description'], "Luxury sedan")
        self.assertEqual(data['brand'], "BMW")
        self.assertIn('pricing_summary', data)
        self.assertIn('is_available_today', data)
    
    def test_booking_create_serializer_validation(self):
        """Test booking create serializer validation."""
        from .serializers import CarRentalBookingCreateSerializer
        from .models import CarRentalAvailability
        
        # Create availability
        availability = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=10),
            is_available=True,
            max_quantity=1,
            booked_quantity=0
        )
        
        # Valid data
        valid_data = {
            'car_rental_id': str(self.car_rental.id),
            'pickup_date': date.today() + timedelta(days=1),
            'dropoff_date': date.today() + timedelta(days=3),
            'pickup_time': time(10, 0),
            'dropoff_time': time(10, 0),
            'driver_name': 'John Doe',
            'driver_license': 'DL123456',
            'driver_phone': '+1234567890',
            'driver_email': 'john@example.com'
        }
        
        serializer = CarRentalBookingCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Invalid data - pickup after dropoff
        invalid_data = valid_data.copy()
        invalid_data['pickup_date'] = date.today() + timedelta(days=5)
        invalid_data['dropoff_date'] = date.today() + timedelta(days=3)
        
        serializer = CarRentalBookingCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Pickup date must be before dropoff date', str(serializer.errors))
        
        # Invalid data - too short rental period
        invalid_data = valid_data.copy()
        invalid_data['pickup_date'] = date.today() + timedelta(days=1)
        invalid_data['dropoff_date'] = date.today() + timedelta(days=1)  # Same day
        
        serializer = CarRentalBookingCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class CarRentalAPITests(APITestCase):
    """Test car rental API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.category = CarRentalCategory.objects.create(
            name="Economy",
            description="Economy class cars"
        )
        
        self.car_rental = CarRental.objects.create(
            title="BMW 3 Series",
            description="Luxury sedan",
            brand="BMW",
            model="3 Series",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            min_rent_days=1,
            max_rent_days=30,
            price_per_day=100.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey",
            is_featured=True
        )
        
        self.availability = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_available=True,
            max_quantity=2,
            booked_quantity=0
        )
        
        self.option = CarRentalOption.objects.create(
            name="GPS Navigation",
            description="GPS navigation system",
            option_type="gps",
            price_type="daily",
            price=10.00,
            max_quantity=1
        )
    
    def test_get_car_rentals_list(self):
        """Test getting car rentals list."""
        url = reverse('car-rental-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['brand'], 'BMW')
    
    def test_get_car_rental_detail(self):
        """Test getting car rental details."""
        url = reverse('car-rental-detail', kwargs={'pk': self.car_rental.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['brand'], 'BMW')
        self.assertEqual(response.data['model'], '3 Series')
        self.assertIn('pricing_summary', response.data)
    
    def test_car_rental_search(self):
        """Test car rental search."""
        url = reverse('car-rental-search')
        data = {
            'query': 'BMW',
            'city': 'Istanbul',
            'min_seats': 4,
            'max_price': 150.00
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['brand'], 'BMW')
    
    def test_check_availability(self):
        """Test availability check."""
        url = reverse('car-rental-check-availability', kwargs={'pk': self.car_rental.id})
        data = {
            'pickup_date': date.today() + timedelta(days=1),
            'dropoff_date': date.today() + timedelta(days=3)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['available'])
        self.assertEqual(response.data['rental_days'], 2)
        self.assertIn('total_price', response.data)
    
    def test_get_featured_car_rentals(self):
        """Test getting featured car rentals."""
        url = reverse('car-rental-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['is_featured'])
    
    def test_get_categories(self):
        """Test getting categories."""
        url = reverse('car-rental-category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Economy')
    
    def test_get_options(self):
        """Test getting options."""
        url = reverse('car-rental-option-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'GPS Navigation')
    
    def test_create_booking(self):
        """Test creating a booking."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        url = reverse('car-rental-booking-list')
        data = {
            'car_rental_id': str(self.car_rental.id),
            'pickup_date': date.today() + timedelta(days=1),
            'dropoff_date': date.today() + timedelta(days=3),
            'pickup_time': time(10, 0),
            'dropoff_time': time(10, 0),
            'driver_name': 'John Doe',
            'driver_license': 'DL123456',
            'driver_phone': '+1234567890',
            'driver_email': 'john@example.com',
            'selected_options': [
                {
                    'id': str(self.option.id),
                    'quantity': 1
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CarRentalBooking.objects.count(), 1)
        
        booking = CarRentalBooking.objects.first()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.car_rental, self.car_rental)
        self.assertEqual(booking.driver_name, 'John Doe')
    
    def test_booking_validation_min_rent_days(self):
        """Test booking validation for minimum rent days."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        url = reverse('car-rental-booking-list')
        data = {
            'car_rental_id': str(self.car_rental.id),
            'pickup_date': date.today() + timedelta(days=1),
            'dropoff_date': date.today() + timedelta(days=1),  # Same day
            'pickup_time': time(10, 0),
            'dropoff_time': time(10, 0),
            'driver_name': 'John Doe',
            'driver_license': 'DL123456',
            'driver_phone': '+1234567890',
            'driver_email': 'john@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Minimum rental period', str(response.data))
    
    def test_booking_validation_max_rent_days(self):
        """Test booking validation for maximum rent days."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        url = reverse('car-rental-booking-list')
        data = {
            'car_rental_id': str(self.car_rental.id),
            'pickup_date': date.today() + timedelta(days=1),
            'dropoff_date': date.today() + timedelta(days=35),  # Exceeds max
            'pickup_time': time(10, 0),
            'dropoff_time': time(10, 0),
            'driver_name': 'John Doe',
            'driver_license': 'DL123456',
            'driver_phone': '+1234567890',
            'driver_email': 'john@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Maximum rental period', str(response.data))


class CarRentalCartIntegrationTests(TransactionTestCase):
    """Test car rental integration with cart system."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        self.category = CarRentalCategory.objects.create(
            name="Economy",
            description="Economy class cars"
        )
        
        self.car_rental = CarRental.objects.create(
            title="BMW 3 Series",
            description="Luxury sedan",
            brand="BMW",
            model="3 Series",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            min_rent_days=1,
            max_rent_days=30,
            price_per_day=100.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey"
        )
        
        self.availability = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=10),
            is_available=True,
            max_quantity=2,
            booked_quantity=0
        )
        
        self.option = CarRentalOption.objects.create(
            name="GPS Navigation",
            description="GPS navigation system",
            option_type="gps",
            price_type="daily",
            price=10.00,
            max_quantity=1
        )
    
    def test_add_car_rental_to_cart(self):
        """Test adding car rental to cart."""
        cart = CartService.get_or_create_cart(
            session_id='test_session',
            user=self.user
        )
        
        product_data = {
            'product_type': 'car_rental',
            'product_id': str(self.car_rental.id),
            'booking_date': date.today() + timedelta(days=1),
            'booking_time': time(10, 0),
            'quantity': 1,
            'unit_price': 200.00,  # 2 days * 100.00
            'total_price': 220.00,  # 200.00 + 20.00 (options)
            'currency': 'USD',
            'booking_data': {
                'car_rental_id': str(self.car_rental.id),
                'pickup_date': (date.today() + timedelta(days=1)).isoformat(),
                'dropoff_date': (date.today() + timedelta(days=3)).isoformat(),
                'pickup_time': '10:00:00',
                'dropoff_time': '10:00:00',
                'rental_days': 2,
                'driver_name': 'John Doe',
                'driver_license': 'DL123456',
                'driver_phone': '+1234567890',
                'driver_email': 'john@example.com',
                'availability_id': str(self.availability.id)
            },
            'selected_options': [
                {
                    'id': str(self.option.id),
                    'quantity': 1,
                    'price': 20.00  # 2 days * 10.00
                }
            ],
            'options_total': 20.00
        }
        
        cart_item = CartItem.objects.create(
            cart=cart,
            **product_data
        )
        
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart_item.product_type, 'car_rental')
        self.assertEqual(cart_item.product_id, self.car_rental.id)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart_item.unit_price, 200.00)
        self.assertEqual(cart_item.total_price, 220.00)
        self.assertEqual(cart_item.options_total, 20.00)
    
    def test_cart_to_order_conversion(self):
        """Test converting cart with car rental to order."""
        cart = CartService.get_or_create_cart(
            session_id='test_session',
            user=self.user
        )
        
        # Add car rental to cart
        cart_item = CartItem.objects.create(
            cart=cart,
            product_type='car_rental',
            product_id=self.car_rental.id,
            booking_date=date.today() + timedelta(days=1),
            booking_time=time(10, 0),
            quantity=1,
            unit_price=200.00,
            total_price=220.00,
            currency='USD',
            selected_options=[
                {
                    'id': str(self.option.id),
                    'quantity': 1,
                    'price': 20.00
                }
            ],
            options_total=20.00,
            booking_data={
                'car_rental_id': str(self.car_rental.id),
                'pickup_date': (date.today() + timedelta(days=1)).isoformat(),
                'dropoff_date': (date.today() + timedelta(days=3)).isoformat(),
                'pickup_time': '10:00:00',
                'dropoff_time': '10:00:00',
                'rental_days': 2,
                'driver_name': 'John Doe',
                'driver_license': 'DL123456',
                'driver_phone': '+1234567890',
                'driver_email': 'john@example.com',
                'availability_id': str(self.availability.id)
            }
        )
        
        # Create order
        order = Order.objects.create(
            user=self.user,
            agent=self.agent,
            customer_name='John Doe',
            customer_email='john@example.com',
            customer_phone='+1234567890',
            subtotal=200.00,
            total_amount=220.00,
            currency='USD',
            status='pending'
        )
        
        # Create order item
        order_item = OrderItem.objects.create(
            order=order,
            product_type='car_rental',
            product_id=self.car_rental.id,
            product_title='BMW 3 Series',
            product_slug='bmw-3-series',
            booking_date=date.today() + timedelta(days=1),
            booking_time=time(10, 0),
            quantity=1,
            unit_price=200.00,
            total_price=220.00,
            currency='USD',
            selected_options=[
                {
                    'id': str(self.option.id),
                    'quantity': 1,
                    'price': 20.00
                }
            ],
            options_total=20.00,
            booking_data={
                'car_rental_id': str(self.car_rental.id),
                'pickup_date': (date.today() + timedelta(days=1)).isoformat(),
                'dropoff_date': (date.today() + timedelta(days=3)).isoformat(),
                'pickup_time': '10:00:00',
                'dropoff_time': '10:00:00',
                'rental_days': 2,
                'driver_name': 'John Doe',
                'driver_license': 'DL123456',
                'driver_phone': '+1234567890',
                'driver_email': 'john@example.com',
                'availability_id': str(self.availability.id)
            }
        )
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, 220.00)
        self.assertEqual(order.items.count(), 1)
        
        order_item = order.items.first()
        self.assertEqual(order_item.product_type, 'car_rental')
        self.assertEqual(order_item.product_title, 'BMW 3 Series')
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.total_price, 220.00)
        self.assertEqual(order_item.options_total, 20.00)
        
        # Verify booking data is preserved
        booking_data = order_item.booking_data
        self.assertEqual(booking_data['car_rental_id'], str(self.car_rental.id))
        self.assertEqual(booking_data['rental_days'], 2)
        self.assertEqual(booking_data['driver_name'], 'John Doe')


class CarRentalComplexPricingTests(TestCase):
    """Test complex pricing scenarios."""
    
    def setUp(self):
        """Set up test data."""
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        self.category = CarRentalCategory.objects.create(
            name="Luxury",
            description="Luxury class cars"
        )
        
        self.car_rental = CarRental.objects.create(
            title="Mercedes S-Class",
            description="Luxury sedan",
            brand="Mercedes",
            model="S-Class",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            min_rent_days=1,
            max_rent_days=30,
            price_per_day=200.00,
            price_per_hour=30.00,
            weekly_discount_percentage=15.00,
            monthly_discount_percentage=25.00,
            comprehensive_insurance_price=50.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey"
        )
        
        self.fixed_option = CarRentalOption.objects.create(
            name="GPS Navigation",
            description="GPS navigation system",
            option_type="gps",
            price_type="daily",
            price=15.00,
            max_quantity=1
        )
        
        self.percentage_option = CarRentalOption.objects.create(
            name="Premium Insurance",
            description="Premium insurance coverage",
            option_type="premium_insurance",
            price_type="percentage",
            price_percentage=20.0,
            max_quantity=1
        )
    
    def test_complex_pricing_calculation(self):
        """Test complex pricing with discounts and options."""
        # 7 days rental with options and insurance
        rental_days = 7
        rental_hours = 4
        
        # Base price with weekly discount
        daily_price = self.car_rental.get_daily_price_with_discount(rental_days)
        expected_daily = 200.00 - (200.00 * 0.15)  # 170.00
        self.assertEqual(daily_price, expected_daily)
        
        # Total base price
        base_price = (daily_price * rental_days) + (self.car_rental.price_per_hour * rental_hours)
        expected_base = (170.00 * 7) + (30.00 * 4)  # 1190.00 + 120.00 = 1310.00
        self.assertEqual(base_price, expected_base)
        
        # Options calculation
        fixed_option_price = self.fixed_option.calculate_price(base_price, rental_days, 1)
        expected_fixed = 15.00 * rental_days  # 105.00
        self.assertEqual(fixed_option_price, expected_fixed)
        
        percentage_option_price = self.percentage_option.calculate_price(base_price, rental_days, 1)
        expected_percentage = (base_price * 0.20) * rental_days  # 262.00 * 7 = 1834.00
        self.assertEqual(percentage_option_price, expected_percentage)
        
        # Insurance
        insurance_price = self.car_rental.comprehensive_insurance_price * rental_days
        expected_insurance = 50.00 * rental_days  # 350.00
        self.assertEqual(insurance_price, expected_insurance)
        
        # Total price
        total_price = base_price + fixed_option_price + percentage_option_price + insurance_price
        expected_total = 1310.00 + 105.00 + 1834.00 + 350.00  # 3599.00
        self.assertEqual(total_price, expected_total)
    
    def test_monthly_discount_priority(self):
        """Test that monthly discount takes priority over weekly discount."""
        # 30 days rental
        rental_days = 30
        
        daily_price = self.car_rental.get_daily_price_with_discount(rental_days)
        expected_daily = 200.00 - (200.00 * 0.25)  # 150.00 (monthly discount)
        self.assertEqual(daily_price, expected_daily)
        
        # Should not apply weekly discount when monthly applies
        self.assertNotEqual(daily_price, 200.00 - (200.00 * 0.15))  # Not weekly discount


class CarRentalAvailabilityTests(TestCase):
    """Test availability management."""
    
    def setUp(self):
        """Set up test data."""
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        self.car_rental = CarRental.objects.create(
            title="BMW 3 Series",
            description="Luxury sedan",
            brand="BMW",
            model="3 Series",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            min_rent_days=1,
            max_rent_days=30,
            price_per_day=100.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey"
        )
    
    def test_availability_overlap_handling(self):
        """Test handling of overlapping availability periods."""
        # Create overlapping availability periods
        availability1 = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            is_available=True,
            max_quantity=2,
            booked_quantity=0
        )
        
        availability2 = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=15),
            is_available=True,
            max_quantity=1,
            booked_quantity=0
        )
        
        # Test availability for overlapping period
        pickup_date = date.today() + timedelta(days=7)
        dropoff_date = date.today() + timedelta(days=8)
        
        # Should find availability in both periods
        available_periods = CarRentalAvailability.objects.filter(
            car_rental=self.car_rental,
            start_date__lte=pickup_date,
            end_date__gte=dropoff_date,
            is_available=True
        )
        
        self.assertEqual(available_periods.count(), 2)
        
        # Test reservation in overlapping period
        for period in available_periods:
            if period.is_available_for_booking(1):
                period.reserve_quantity(1)
                break
        
        # Check that one period is now partially booked
        availability1.refresh_from_db()
        availability2.refresh_from_db()
        
        self.assertTrue(
            availability1.booked_quantity == 1 or availability2.booked_quantity == 1
        )
    
    def test_availability_price_override(self):
        """Test availability price override."""
        availability = CarRentalAvailability.objects.create(
            car_rental=self.car_rental,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            is_available=True,
            max_quantity=2,
            booked_quantity=0,
            price_override=80.00  # Override base price
        )
        
        # Test that price override is used
        self.assertEqual(availability.price_override, 80.00)
        
        # In a real implementation, this would be used in pricing calculations
        # For now, we just verify the field is set correctly
        self.assertIsNotNone(availability.price_override)


class CarRentalFilterTests(APITestCase):
    """Test car rental filtering and search."""
    
    def setUp(self):
        """Set up test data."""
        self.agent = User.objects.create_user(
            username='agent1',
            email='agent@example.com',
            password='testpass123',
            role='agent'
        )
        
        self.category1 = CarRentalCategory.objects.create(
            name="Economy",
            description="Economy class cars"
        )
        
        self.category2 = CarRentalCategory.objects.create(
            name="Luxury",
            description="Luxury class cars"
        )
        
        # Create multiple car rentals for testing
        self.car1 = CarRental.objects.create(
            title="BMW 3 Series",
            description="Luxury sedan",
            brand="BMW",
            model="3 Series",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            price_per_day=100.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey",
            category=self.category1,
            is_featured=True
        )
        
        self.car2 = CarRental.objects.create(
            title="Mercedes S-Class",
            description="Luxury sedan",
            brand="Mercedes",
            model="S-Class",
            year=2023,
            seats=5,
            fuel_type="gasoline",
            transmission="automatic",
            price_per_day=200.00,
            agent=self.agent,
            city="Istanbul",
            country="Turkey",
            category=self.category2,
            is_popular=True
        )
        
        self.car3 = CarRental.objects.create(
            title="Toyota Corolla",
            description="Economy sedan",
            brand="Toyota",
            model="Corolla",
            year=2022,
            seats=5,
            fuel_type="hybrid",
            transmission="automatic",
            price_per_day=50.00,
            agent=self.agent,
            city="Ankara",
            country="Turkey",
            category=self.category1
        )
    
    def test_filter_by_brand(self):
        """Test filtering by brand."""
        url = reverse('car-rental-list')
        response = self.client.get(url, {'brand': 'BMW'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['brand'], 'BMW')
    
    def test_filter_by_city(self):
        """Test filtering by city."""
        url = reverse('car-rental-list')
        response = self.client.get(url, {'city': 'Istanbul'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_filter_by_price_range(self):
        """Test filtering by price range."""
        url = reverse('car-rental-list')
        response = self.client.get(url, {'min_price': 80, 'max_price': 150})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['brand'], 'BMW')
    
    def test_filter_by_seats(self):
        """Test filtering by minimum seats."""
        url = reverse('car-rental-list')
        response = self.client.get(url, {'min_seats': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
    
    def test_filter_by_fuel_type(self):
        """Test filtering by fuel type."""
        url = reverse('car-rental-list')
        response = self.client.get(url, {'fuel_type': 'hybrid'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['brand'], 'Toyota')
    
    def test_search_by_query(self):
        """Test search by query."""
        url = reverse('car-rental-search')
        data = {'query': 'BMW'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['brand'], 'BMW')
    
    def test_search_by_multiple_criteria(self):
        """Test search with multiple criteria."""
        url = reverse('car-rental-search')
        data = {
            'city': 'Istanbul',
            'min_price': 50,
            'max_price': 150,
            'fuel_type': 'gasoline'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['brand'], 'BMW')
    
    def test_sort_by_price_asc(self):
        """Test sorting by price ascending."""
        url = reverse('car-rental-search')
        data = {'sort_by': 'price_asc'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [car['price_per_day'] for car in response.data['results']]
        self.assertEqual(prices, sorted(prices))
    
    def test_sort_by_price_desc(self):
        """Test sorting by price descending."""
        url = reverse('car-rental-search')
        data = {'sort_by': 'price_desc'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [car['price_per_day'] for car in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))
    
    def test_sort_by_year_desc(self):
        """Test sorting by year descending."""
        url = reverse('car-rental-search')
        data = {'sort_by': 'year_desc'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [car['year'] for car in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))
