"""
Unit Tests for Transfer Pricing Calculation
Tests all pricing scenarios including day/night, return trips, surcharges, capacity overflow, options, and discounts
"""

import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from datetime import datetime, time, date

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent
from agents.pricing_service import AgentPricingService

User = get_user_model()


class TransferPricingUnitTests(TestCase):
    """Unit tests for Transfer pricing calculation scenarios"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and agent
        self.user = User.objects.create_user(
            username='testagent',
            email='agent@test.com',
            password='testpass123'
        )
        self.agent = Agent.objects.create(
            user=self.user,
            name='Test Agent',
            commission_rate=Decimal('0.10'),  # 10% commission
            is_active=True
        )
        
        # Create test route
        self.route = TransferRoute.objects.create(
            name='Test Route',
            from_location='Tehran',
            to_location='Isfahan',
            distance=450,
            is_active=True
        )
        
        # Create test vehicle type pricing
        self.pricing = TransferRoutePricing.objects.create(
            route=self.route,
            vehicle_type='sedan',
            base_price=Decimal('150.00'),
            night_surcharge=Decimal('25.00'),
            return_discount=Decimal('0.20'),  # 20% discount for return
            max_capacity=4,
            is_active=True
        )
        
        # Create test options
        self.option_1 = TransferOption.objects.create(
            name='Extra Luggage',
            price=Decimal('10.00'),
            is_active=True
        )
        self.option_2 = TransferOption.objects.create(
            name='Child Seat',
            price=Decimal('15.00'),
            is_active=True
        )

    def test_day_trip_pricing(self):
        """Test day trip pricing calculation"""
        # Day trip (hour < 22)
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14  # 2 PM
        )
        
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['base_price'], Decimal('150.00'))
        self.assertEqual(result['pricing']['night_surcharge'], Decimal('0.00'))
        self.assertEqual(result['pricing']['final_price'], Decimal('150.00'))
        self.assertEqual(result['pricing']['agent_commission'], Decimal('15.00'))
        self.assertEqual(result['pricing']['customer_price'], Decimal('150.00'))

    def test_night_trip_pricing(self):
        """Test night trip pricing with surcharge"""
        # Night trip (hour >= 22)
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=23  # 11 PM
        )
        
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['base_price'], Decimal('150.00'))
        self.assertEqual(result['pricing']['night_surcharge'], Decimal('25.00'))
        self.assertEqual(result['pricing']['final_price'], Decimal('175.00'))
        self.assertEqual(result['pricing']['agent_commission'], Decimal('17.50'))
        self.assertEqual(result['pricing']['customer_price'], Decimal('175.00'))

    def test_round_trip_pricing_with_discount(self):
        """Test round trip pricing with return discount"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='round_trip',
            hour=14,
            return_hour=16
        )
        
        # Base price: 150, Return price: 150 * 0.8 = 120, Total: 270
        expected_total = Decimal('150.00') + (Decimal('150.00') * Decimal('0.80'))
        expected_commission = expected_total * Decimal('0.10')
        
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['base_price'], Decimal('150.00'))
        self.assertEqual(result['pricing']['return_price'], Decimal('120.00'))
        self.assertEqual(result['pricing']['return_discount'], Decimal('30.00'))
        self.assertEqual(result['pricing']['final_price'], expected_total)
        self.assertEqual(result['pricing']['agent_commission'], expected_commission)

    def test_pricing_with_options(self):
        """Test pricing calculation with additional options"""
        selected_options = [
            {'id': self.option_1.id, 'name': 'Extra Luggage', 'price': Decimal('10.00')},
            {'id': self.option_2.id, 'name': 'Child Seat', 'price': Decimal('15.00')}
        ]
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14,
            selected_options=selected_options
        )
        
        expected_base = Decimal('150.00')
        expected_options = Decimal('25.00')  # 10 + 15
        expected_total = expected_base + expected_options
        expected_commission = expected_total * Decimal('0.10')
        
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['base_price'], expected_base)
        self.assertEqual(result['pricing']['options_total'], expected_options)
        self.assertEqual(result['pricing']['final_price'], expected_total)
        self.assertEqual(result['pricing']['agent_commission'], expected_commission)

    def test_capacity_validation_success(self):
        """Test successful capacity validation"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=4,  # Max capacity
            trip_type='one_way',
            hour=14
        )
        
        self.assertEqual(result['success'], True)
        self.assertEqual(result['capacity_info']['is_valid'], True)
        self.assertEqual(result['capacity_info']['passenger_count'], 4)
        self.assertEqual(result['capacity_info']['max_capacity'], 4)

    def test_capacity_validation_failure(self):
        """Test capacity validation failure"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=5,  # Exceeds max capacity
            trip_type='one_way',
            hour=14
        )
        
        self.assertEqual(result['success'], False)
        self.assertIn('capacity', result['error'].lower())
        self.assertEqual(result['capacity_info']['is_valid'], False)
        self.assertEqual(result['capacity_info']['passenger_count'], 5)
        self.assertEqual(result['capacity_info']['max_capacity'], 4)

    def test_invalid_route(self):
        """Test pricing with invalid route"""
        invalid_route = Mock()
        invalid_route.id = 999
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=invalid_route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        self.assertEqual(result['success'], False)
        self.assertIn('route', result['error'].lower())

    def test_invalid_vehicle_type(self):
        """Test pricing with invalid vehicle type"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='invalid_type',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        self.assertEqual(result['success'], False)
        self.assertIn('vehicle', result['error'].lower())

    def test_inactive_agent(self):
        """Test pricing with inactive agent"""
        self.agent.is_active = False
        self.agent.save()
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        self.assertEqual(result['success'], False)
        self.assertIn('agent', result['error'].lower())

    def test_edge_case_midnight_hour(self):
        """Test pricing at midnight (hour 0)"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=0  # Midnight
        )
        
        # Midnight should be considered night time
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['night_surcharge'], Decimal('25.00'))
        self.assertEqual(result['pricing']['final_price'], Decimal('175.00'))

    def test_edge_case_early_morning(self):
        """Test pricing in early morning (hour 5)"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=5  # 5 AM
        )
        
        # Early morning should be considered night time
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['night_surcharge'], Decimal('25.00'))
        self.assertEqual(result['pricing']['final_price'], Decimal('175.00'))

    def test_complex_pricing_scenario(self):
        """Test complex pricing with all factors"""
        selected_options = [
            {'id': self.option_1.id, 'name': 'Extra Luggage', 'price': Decimal('10.00')}
        ]
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=3,
            trip_type='round_trip',
            hour=23,  # Night time
            return_hour=1,  # Early morning return
            selected_options=selected_options
        )
        
        # Base: 150 + 25 (night) + 10 (option) = 185
        # Return: (150 + 25 + 10) * 0.8 = 148
        # Total: 185 + 148 = 333
        expected_total = Decimal('333.00')
        expected_commission = expected_total * Decimal('0.10')
        
        self.assertEqual(result['success'], True)
        self.assertEqual(result['pricing']['final_price'], expected_total)
        self.assertEqual(result['pricing']['agent_commission'], expected_commission)

    def test_commission_calculation_accuracy(self):
        """Test commission calculation accuracy with different rates"""
        # Test with 15% commission
        self.agent.commission_rate = Decimal('0.15')
        self.agent.save()
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        expected_commission = Decimal('150.00') * Decimal('0.15')
        self.assertEqual(result['pricing']['agent_commission'], expected_commission)

    def test_currency_handling(self):
        """Test proper currency handling in pricing"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        # All prices should be Decimal objects
        self.assertIsInstance(result['pricing']['base_price'], Decimal)
        self.assertIsInstance(result['pricing']['final_price'], Decimal)
        self.assertIsInstance(result['pricing']['agent_commission'], Decimal)
        self.assertIsInstance(result['pricing']['customer_price'], Decimal)

    def test_pricing_breakdown_structure(self):
        """Test that pricing breakdown has all required fields"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        required_fields = [
            'base_price', 'night_surcharge', 'options_total', 
            'return_price', 'return_discount', 'final_price',
            'agent_commission', 'customer_price'
        ]
        
        for field in required_fields:
            self.assertIn(field, result['pricing'])

    def test_trip_info_structure(self):
        """Test that trip info has all required fields"""
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='round_trip',
            hour=14,
            return_hour=16
        )
        
        required_fields = [
            'route_name', 'from_location', 'to_location', 
            'vehicle_type', 'trip_type', 'passenger_count',
            'booking_time', 'return_time'
        ]
        
        for field in required_fields:
            self.assertIn(field, result['trip_info'])


if __name__ == '__main__':
    pytest.main([__file__])
