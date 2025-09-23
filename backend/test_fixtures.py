"""
Test Fixtures and Data Setup for Transfer Product Testing
Provides reusable test data and fixtures for all test scenarios
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import datetime, time, date, timedelta

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent
from users.models import Customer
from orders.models import Order, OrderItem

User = get_user_model()


class TransferTestFixtures:
    """Test fixtures for Transfer product testing"""
    
    @staticmethod
    def create_test_user(username='testuser', email='test@example.com', is_staff=False, is_superuser=False):
        """Create a test user"""
        return User.objects.create_user(
            username=username,
            email=email,
            password='testpass123',
            is_staff=is_staff,
            is_superuser=is_superuser
        )
    
    @staticmethod
    def create_test_agent(user=None, name='Test Agent', commission_rate=Decimal('0.10'), is_active=True):
        """Create a test agent"""
        if user is None:
            user = TransferTestFixtures.create_test_user('testagent', 'agent@test.com')
        
        return Agent.objects.create(
            user=user,
            name=name,
            commission_rate=commission_rate,
            is_active=is_active
        )
    
    @staticmethod
    def create_test_customer(user=None, name='Test Customer', phone='09123456789', email='customer@test.com', is_active=True):
        """Create a test customer"""
        if user is None:
            user = TransferTestFixtures.create_test_user('testcustomer', email)
        
        return Customer.objects.create(
            user=user,
            name=name,
            phone=phone,
            email=email,
            is_active=is_active
        )
    
    @staticmethod
    def create_test_route(name='Test Route', from_location='Tehran', to_location='Isfahan', distance=450, is_active=True):
        """Create a test transfer route"""
        return TransferRoute.objects.create(
            name=name,
            from_location=from_location,
            to_location=to_location,
            distance=distance,
            is_active=is_active
        )
    
    @staticmethod
    def create_test_pricing(route, vehicle_type='sedan', base_price=Decimal('150.00'), 
                          night_surcharge=Decimal('25.00'), return_discount=Decimal('0.20'), 
                          max_capacity=4, is_active=True):
        """Create test transfer route pricing"""
        return TransferRoutePricing.objects.create(
            route=route,
            vehicle_type=vehicle_type,
            base_price=base_price,
            night_surcharge=night_surcharge,
            return_discount=return_discount,
            max_capacity=max_capacity,
            is_active=is_active
        )
    
    @staticmethod
    def create_test_option(name='Extra Luggage', price=Decimal('10.00'), is_active=True):
        """Create a test transfer option"""
        return TransferOption.objects.create(
            name=name,
            price=price,
            is_active=is_active
        )
    
    @staticmethod
    def create_test_order(agent, customer, total_amount=Decimal('150.00'), 
                         status='pending', payment_method='whatsapp', payment_status='pending'):
        """Create a test order"""
        return Order.objects.create(
            agent=agent,
            customer=customer,
            total_amount=total_amount,
            status=status,
            payment_method=payment_method,
            payment_status=payment_status,
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_test_order_item(order, product_type='transfer', quantity=1, 
                              unit_price=Decimal('150.00'), **kwargs):
        """Create a test order item"""
        return OrderItem.objects.create(
            order=order,
            product_type=product_type,
            quantity=quantity,
            unit_price=unit_price,
            **kwargs
        )


class TransferTestData:
    """Predefined test data for Transfer product testing"""
    
    # Test routes
    ROUTES = {
        'tehran_isfahan': {
            'name': 'Tehran to Isfahan',
            'from_location': 'Tehran',
            'to_location': 'Isfahan',
            'distance': 450,
            'is_active': True
        },
        'tehran_shiraz': {
            'name': 'Tehran to Shiraz',
            'from_location': 'Tehran',
            'to_location': 'Shiraz',
            'distance': 900,
            'is_active': True
        },
        'isfahan_yazd': {
            'name': 'Isfahan to Yazd',
            'from_location': 'Isfahan',
            'to_location': 'Yazd',
            'distance': 320,
            'is_active': True
        },
        'inactive_route': {
            'name': 'Inactive Route',
            'from_location': 'Tehran',
            'to_location': 'Mashhad',
            'distance': 800,
            'is_active': False
        }
    }
    
    # Test pricing configurations
    PRICING_CONFIGS = {
        'sedan': {
            'vehicle_type': 'sedan',
            'base_price': Decimal('150.00'),
            'night_surcharge': Decimal('25.00'),
            'return_discount': Decimal('0.20'),
            'max_capacity': 4,
            'is_active': True
        },
        'van': {
            'vehicle_type': 'van',
            'base_price': Decimal('200.00'),
            'night_surcharge': Decimal('30.00'),
            'return_discount': Decimal('0.15'),
            'max_capacity': 8,
            'is_active': True
        },
        'bus': {
            'vehicle_type': 'bus',
            'base_price': Decimal('300.00'),
            'night_surcharge': Decimal('40.00'),
            'return_discount': Decimal('0.25'),
            'max_capacity': 20,
            'is_active': True
        },
        'inactive_pricing': {
            'vehicle_type': 'limo',
            'base_price': Decimal('500.00'),
            'night_surcharge': Decimal('50.00'),
            'return_discount': Decimal('0.10'),
            'max_capacity': 2,
            'is_active': False
        }
    }
    
    # Test options
    OPTIONS = {
        'extra_luggage': {
            'name': 'Extra Luggage',
            'price': Decimal('10.00'),
            'is_active': True
        },
        'child_seat': {
            'name': 'Child Seat',
            'price': Decimal('15.00'),
            'is_active': True
        },
        'wifi': {
            'name': 'WiFi Access',
            'price': Decimal('5.00'),
            'is_active': True
        },
        'inactive_option': {
            'name': 'Inactive Option',
            'price': Decimal('20.00'),
            'is_active': False
        }
    }
    
    # Test agents
    AGENTS = {
        'active_agent': {
            'name': 'Active Agent',
            'commission_rate': Decimal('0.10'),
            'is_active': True
        },
        'high_commission_agent': {
            'name': 'High Commission Agent',
            'commission_rate': Decimal('0.15'),
            'is_active': True
        },
        'inactive_agent': {
            'name': 'Inactive Agent',
            'commission_rate': Decimal('0.10'),
            'is_active': False
        }
    }
    
    # Test customers
    CUSTOMERS = {
        'regular_customer': {
            'name': 'Regular Customer',
            'phone': '09123456789',
            'email': 'customer@test.com',
            'is_active': True
        },
        'vip_customer': {
            'name': 'VIP Customer',
            'phone': '09987654321',
            'email': 'vip@test.com',
            'is_active': True
        },
        'inactive_customer': {
            'name': 'Inactive Customer',
            'phone': '09111111111',
            'email': 'inactive@test.com',
            'is_active': False
        }
    }
    
    # Test booking scenarios
    BOOKING_SCENARIOS = {
        'day_trip': {
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_time': '14:00',
            'return_time': None,
            'selected_options': [],
            'expected_night_surcharge': Decimal('0.00')
        },
        'night_trip': {
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_time': '23:00',
            'return_time': None,
            'selected_options': [],
            'expected_night_surcharge': Decimal('25.00')
        },
        'round_trip': {
            'passenger_count': 2,
            'trip_type': 'round_trip',
            'booking_time': '14:00',
            'return_time': '16:00',
            'selected_options': [],
            'expected_return_discount': Decimal('30.00')
        },
        'with_options': {
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_time': '14:00',
            'return_time': None,
            'selected_options': ['extra_luggage', 'child_seat'],
            'expected_options_total': Decimal('25.00')
        },
        'max_capacity': {
            'passenger_count': 4,
            'trip_type': 'one_way',
            'booking_time': '14:00',
            'return_time': None,
            'selected_options': [],
            'expected_capacity_valid': True
        },
        'over_capacity': {
            'passenger_count': 5,
            'trip_type': 'one_way',
            'booking_time': '14:00',
            'return_time': None,
            'selected_options': [],
            'expected_capacity_valid': False
        }
    }


class TransferTestSetup:
    """Test setup utilities for Transfer product testing"""
    
    @staticmethod
    def setup_complete_test_environment():
        """Set up complete test environment with all necessary data"""
        # Create users
        agent_user = TransferTestFixtures.create_test_user('testagent', 'agent@test.com')
        customer_user = TransferTestFixtures.create_test_user('testcustomer', 'customer@test.com')
        admin_user = TransferTestFixtures.create_test_user('admin', 'admin@test.com', is_staff=True, is_superuser=True)
        
        # Create agent and customer
        agent = TransferTestFixtures.create_test_agent(agent_user)
        customer = TransferTestFixtures.create_test_customer(customer_user)
        
        # Create routes
        route1 = TransferTestFixtures.create_test_route(**TransferTestData.ROUTES['tehran_isfahan'])
        route2 = TransferTestFixtures.create_test_route(**TransferTestData.ROUTES['tehran_shiraz'])
        
        # Create pricing for different vehicle types
        sedan_pricing = TransferTestFixtures.create_test_pricing(route1, **TransferTestData.PRICING_CONFIGS['sedan'])
        van_pricing = TransferTestFixtures.create_test_pricing(route1, **TransferTestData.PRICING_CONFIGS['van'])
        bus_pricing = TransferTestFixtures.create_test_pricing(route2, **TransferTestData.PRICING_CONFIGS['bus'])
        
        # Create options
        extra_luggage = TransferTestFixtures.create_test_option(**TransferTestData.OPTIONS['extra_luggage'])
        child_seat = TransferTestFixtures.create_test_option(**TransferTestData.OPTIONS['child_seat'])
        wifi = TransferTestFixtures.create_test_option(**TransferTestData.OPTIONS['wifi'])
        
        return {
            'users': {
                'agent_user': agent_user,
                'customer_user': customer_user,
                'admin_user': admin_user
            },
            'agent': agent,
            'customer': customer,
            'routes': {
                'tehran_isfahan': route1,
                'tehran_shiraz': route2
            },
            'pricing': {
                'sedan': sedan_pricing,
                'van': van_pricing,
                'bus': bus_pricing
            },
            'options': {
                'extra_luggage': extra_luggage,
                'child_seat': child_seat,
                'wifi': wifi
            }
        }
    
    @staticmethod
    def setup_pricing_test_scenarios():
        """Set up test scenarios for pricing calculation"""
        scenarios = []
        
        # Day trip scenarios
        for vehicle_type in ['sedan', 'van', 'bus']:
            scenarios.append({
                'name': f'{vehicle_type}_day_trip',
                'vehicle_type': vehicle_type,
                'passenger_count': 2,
                'trip_type': 'one_way',
                'hour': 14,
                'return_hour': None,
                'selected_options': [],
                'expected_night_surcharge': Decimal('0.00')
            })
        
        # Night trip scenarios
        for vehicle_type in ['sedan', 'van', 'bus']:
            scenarios.append({
                'name': f'{vehicle_type}_night_trip',
                'vehicle_type': vehicle_type,
                'passenger_count': 2,
                'trip_type': 'one_way',
                'hour': 23,
                'return_hour': None,
                'selected_options': [],
                'expected_night_surcharge': TransferTestData.PRICING_CONFIGS[vehicle_type]['night_surcharge']
            })
        
        # Round trip scenarios
        for vehicle_type in ['sedan', 'van', 'bus']:
            base_price = TransferTestData.PRICING_CONFIGS[vehicle_type]['base_price']
            return_discount_rate = TransferTestData.PRICING_CONFIGS[vehicle_type]['return_discount']
            expected_return_discount = base_price * return_discount_rate
            
            scenarios.append({
                'name': f'{vehicle_type}_round_trip',
                'vehicle_type': vehicle_type,
                'passenger_count': 2,
                'trip_type': 'round_trip',
                'hour': 14,
                'return_hour': 16,
                'selected_options': [],
                'expected_return_discount': expected_return_discount
            })
        
        return scenarios
    
    @staticmethod
    def setup_capacity_test_scenarios():
        """Set up test scenarios for capacity validation"""
        scenarios = []
        
        for vehicle_type in ['sedan', 'van', 'bus']:
            max_capacity = TransferTestData.PRICING_CONFIGS[vehicle_type]['max_capacity']
            
            # Valid capacity scenarios
            for passenger_count in range(1, max_capacity + 1):
                scenarios.append({
                    'name': f'{vehicle_type}_capacity_{passenger_count}',
                    'vehicle_type': vehicle_type,
                    'passenger_count': passenger_count,
                    'expected_valid': True,
                    'expected_max_capacity': max_capacity
                })
            
            # Invalid capacity scenarios
            for passenger_count in range(max_capacity + 1, max_capacity + 4):
                scenarios.append({
                    'name': f'{vehicle_type}_over_capacity_{passenger_count}',
                    'vehicle_type': vehicle_type,
                    'passenger_count': passenger_count,
                    'expected_valid': False,
                    'expected_max_capacity': max_capacity
                })
        
        return scenarios


# Pytest fixtures
@pytest.fixture
def transfer_test_environment():
    """Pytest fixture for complete test environment"""
    return TransferTestSetup.setup_complete_test_environment()


@pytest.fixture
def transfer_test_route():
    """Pytest fixture for test route"""
    return TransferTestFixtures.create_test_route()


@pytest.fixture
def transfer_test_pricing(transfer_test_route):
    """Pytest fixture for test pricing"""
    return TransferTestFixtures.create_test_pricing(transfer_test_route)


@pytest.fixture
def transfer_test_agent():
    """Pytest fixture for test agent"""
    return TransferTestFixtures.create_test_agent()


@pytest.fixture
def transfer_test_customer():
    """Pytest fixture for test customer"""
    return TransferTestFixtures.create_test_customer()


@pytest.fixture
def transfer_test_option():
    """Pytest fixture for test option"""
    return TransferTestFixtures.create_test_option()


@pytest.fixture
def transfer_test_order(transfer_test_agent, transfer_test_customer):
    """Pytest fixture for test order"""
    return TransferTestFixtures.create_test_order(transfer_test_agent, transfer_test_customer)


@pytest.fixture
def transfer_pricing_scenarios():
    """Pytest fixture for pricing test scenarios"""
    return TransferTestSetup.setup_pricing_test_scenarios()


@pytest.fixture
def transfer_capacity_scenarios():
    """Pytest fixture for capacity test scenarios"""
    return TransferTestSetup.setup_capacity_test_scenarios()


# Django TestCase mixins
class TransferTestCaseMixin:
    """Mixin for Transfer-related test cases"""
    
    def setUp(self):
        """Set up test data"""
        self.test_environment = TransferTestSetup.setup_complete_test_environment()
        self.agent = self.test_environment['agent']
        self.customer = self.test_environment['customer']
        self.route = self.test_environment['routes']['tehran_isfahan']
        self.sedan_pricing = self.test_environment['pricing']['sedan']
        self.extra_luggage = self.test_environment['options']['extra_luggage']
    
    def create_booking_data(self, **kwargs):
        """Create booking data with defaults"""
        defaults = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'selected_options': [],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        defaults.update(kwargs)
        return defaults
    
    def assert_pricing_structure(self, pricing_result):
        """Assert pricing result has correct structure"""
        required_fields = [
            'base_price', 'night_surcharge', 'options_total',
            'return_price', 'return_discount', 'final_price',
            'agent_commission', 'customer_price'
        ]
        
        for field in required_fields:
            self.assertIn(field, pricing_result)
            self.assertIsInstance(pricing_result[field], Decimal)
    
    def assert_capacity_info_structure(self, capacity_info):
        """Assert capacity info has correct structure"""
        required_fields = ['is_valid', 'passenger_count', 'max_capacity']
        
        for field in required_fields:
            self.assertIn(field, capacity_info)
        
        self.assertIsInstance(capacity_info['is_valid'], bool)
        self.assertIsInstance(capacity_info['passenger_count'], int)
        self.assertIsInstance(capacity_info['max_capacity'], int)
    
    def assert_trip_info_structure(self, trip_info):
        """Assert trip info has correct structure"""
        required_fields = [
            'route_name', 'from_location', 'to_location',
            'vehicle_type', 'trip_type', 'passenger_count',
            'booking_time', 'return_time'
        ]
        
        for field in required_fields:
            self.assertIn(field, trip_info)
