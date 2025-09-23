"""
Integration Tests for Transfer Agent Order Flow
Tests complete agent order lifecycle: create pending → admin confirm → mark paid
"""

import pytest
import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import Mock, patch
from datetime import datetime, time, date, timedelta

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent
from agents.services import AgentBookingService
from orders.models import Order, OrderItem
from users.models import Customer

User = get_user_model()


class TransferAgentIntegrationTests(TestCase):
    """Integration tests for Transfer agent order flow"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.agent_user = User.objects.create_user(
            username='testagent',
            email='agent@test.com',
            password='testpass123'
        )
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create agent and customer
        self.agent = Agent.objects.create(
            user=self.agent_user,
            name='Test Agent',
            commission_rate=Decimal('0.10'),
            is_active=True
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            name='Test Customer',
            phone='09123456789',
            is_active=True
        )
        
        # Create test route and pricing
        self.route = TransferRoute.objects.create(
            name='Tehran to Isfahan',
            from_location='Tehran',
            to_location='Isfahan',
            distance=450,
            is_active=True
        )
        
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type='sedan',
            base_price=Decimal('150.00'),
            night_surcharge=Decimal('25.00'),
            return_discount=Decimal('0.20'),
            max_capacity=4,
            is_active=True
        )
        
        # Create test option
        self.option = TransferOption.objects.create(
            name='Extra Luggage',
            price=Decimal('10.00'),
            is_active=True
        )
        
        # Create test client
        self.client = Client()

    def test_complete_agent_order_flow(self):
        """Test complete agent order flow: create → confirm → pay"""
        # Step 1: Agent creates pending order for customer
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'selected_options': [{'id': self.option.id, 'name': 'Extra Luggage', 'price': '10.00'}],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        # Create order
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order_id = result['order_id']
        order = Order.objects.get(id=order_id)
        
        # Verify order is in pending status
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.payment_method, 'whatsapp')
        self.assertEqual(order.agent, self.agent)
        self.assertEqual(order.customer, self.customer)
        
        # Verify order item
        order_item = order.items.first()
        self.assertEqual(order_item.product_type, 'transfer')
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.unit_price, Decimal('160.00'))  # 150 + 10 option
        
        # Step 2: Admin confirms the order
        self.client.force_login(self.admin_user)
        confirm_url = reverse('admin:orders_order_change', args=[order.id])
        
        # Simulate admin confirmation
        order.status = 'confirmed'
        order.save()
        
        # Verify order is confirmed
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')
        
        # Step 3: Mark order as paid
        order.status = 'paid'
        order.payment_status = 'paid'
        order.paid_at = datetime.now()
        order.save()
        
        # Verify order is paid
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')
        self.assertEqual(order.payment_status, 'paid')
        self.assertIsNotNone(order.paid_at)

    def test_agent_order_with_round_trip(self):
        """Test agent order creation with round trip"""
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'round_trip',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'return_time': '16:00',
            'selected_options': [],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order = Order.objects.get(id=result['order_id'])
        
        # Verify pricing includes return discount
        # Base: 150, Return: 150 * 0.8 = 120, Total: 270
        expected_total = Decimal('150.00') + (Decimal('150.00') * Decimal('0.80'))
        self.assertEqual(order.total_amount, expected_total)

    def test_agent_order_with_night_surcharge(self):
        """Test agent order creation with night surcharge"""
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '23:00',  # Night time
            'selected_options': [],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order = Order.objects.get(id=result['order_id'])
        
        # Verify night surcharge is applied
        expected_total = Decimal('150.00') + Decimal('25.00')  # Base + night surcharge
        self.assertEqual(order.total_amount, expected_total)

    def test_agent_order_capacity_validation(self):
        """Test agent order creation with capacity validation"""
        # Test valid capacity
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 4,  # Max capacity
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'selected_options': [],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        
        # Test invalid capacity
        transfer_data['passenger_count'] = 5  # Exceeds max capacity
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertFalse(result['success'])
        self.assertIn('capacity', result['error'].lower())

    def test_agent_order_with_invalid_route(self):
        """Test agent order creation with invalid route"""
        transfer_data = {
            'route_id': 999,  # Non-existent route
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
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertFalse(result['success'])
        self.assertIn('route', result['error'].lower())

    def test_agent_order_with_invalid_vehicle_type(self):
        """Test agent order creation with invalid vehicle type"""
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'invalid_type',
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
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertFalse(result['success'])
        self.assertIn('vehicle', result['error'].lower())

    def test_agent_order_commission_calculation(self):
        """Test agent commission calculation in order"""
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'selected_options': [{'id': self.option.id, 'name': 'Extra Luggage', 'price': '10.00'}],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order = Order.objects.get(id=result['order_id'])
        
        # Verify commission calculation
        # Total: 150 + 10 = 160, Commission: 160 * 0.10 = 16
        expected_commission = Decimal('160.00') * Decimal('0.10')
        self.assertEqual(order.agent_commission, expected_commission)

    def test_agent_order_payment_method_handling(self):
        """Test different payment methods in agent orders"""
        # Test WhatsApp payment
        transfer_data = {
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
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order = Order.objects.get(id=result['order_id'])
        self.assertEqual(order.payment_method, 'whatsapp')
        self.assertEqual(order.status, 'pending')

    def test_agent_order_with_multiple_options(self):
        """Test agent order creation with multiple options"""
        # Create additional option
        option2 = TransferOption.objects.create(
            name='Child Seat',
            price=Decimal('15.00'),
            is_active=True
        )
        
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'selected_options': [
                {'id': self.option.id, 'name': 'Extra Luggage', 'price': '10.00'},
                {'id': option2.id, 'name': 'Child Seat', 'price': '15.00'}
            ],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order = Order.objects.get(id=result['order_id'])
        
        # Verify total includes all options
        # Base: 150 + Options: 10 + 15 = 25, Total: 175
        expected_total = Decimal('150.00') + Decimal('25.00')
        self.assertEqual(order.total_amount, expected_total)

    def test_agent_order_date_validation(self):
        """Test agent order creation with date validation"""
        # Test past date (should fail)
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() - timedelta(days=1)).isoformat(),  # Past date
            'booking_time': '14:00',
            'selected_options': [],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertFalse(result['success'])
        self.assertIn('date', result['error'].lower())

    def test_agent_order_time_validation(self):
        """Test agent order creation with time validation"""
        # Test invalid time format
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '25:00',  # Invalid time
            'selected_options': [],
            'customer_name': 'Test Customer',
            'customer_phone': '09123456789',
            'customer_email': 'customer@test.com',
            'payment_method': 'whatsapp'
        }
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertFalse(result['success'])
        self.assertIn('time', result['error'].lower())

    def test_agent_order_customer_creation(self):
        """Test agent order creation with new customer"""
        transfer_data = {
            'route_id': self.route.id,
            'vehicle_type': 'sedan',
            'passenger_count': 2,
            'trip_type': 'one_way',
            'booking_date': (date.today() + timedelta(days=1)).isoformat(),
            'booking_time': '14:00',
            'selected_options': [],
            'customer_name': 'New Customer',
            'customer_phone': '09987654321',
            'customer_email': 'newcustomer@test.com',
            'payment_method': 'whatsapp'
        }
        
        # Create new customer
        new_customer = Customer.objects.create(
            user=None,  # No user account
            name='New Customer',
            phone='09987654321',
            email='newcustomer@test.com',
            is_active=True
        )
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=new_customer,
            transfer_data=transfer_data
        )
        
        self.assertTrue(result['success'])
        order = Order.objects.get(id=result['order_id'])
        self.assertEqual(order.customer, new_customer)

    def test_agent_order_rollback_on_failure(self):
        """Test that order creation rolls back on failure"""
        # Mock a failure in order creation
        with patch('orders.models.Order.objects.create') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            transfer_data = {
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
            
            result = AgentBookingService.book_transfer_for_customer(
                agent=self.agent,
                customer=self.customer,
                transfer_data=transfer_data
            )
            
            self.assertFalse(result['success'])
            self.assertIn('error', result['error'].lower())
            
            # Verify no order was created
            self.assertEqual(Order.objects.count(), 0)

    def test_agent_order_with_inactive_agent(self):
        """Test agent order creation with inactive agent"""
        self.agent.is_active = False
        self.agent.save()
        
        transfer_data = {
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
        
        result = AgentBookingService.book_transfer_for_customer(
            agent=self.agent,
            customer=self.customer,
            transfer_data=transfer_data
        )
        
        self.assertFalse(result['success'])
        self.assertIn('agent', result['error'].lower())


if __name__ == '__main__':
    pytest.main([__file__])
