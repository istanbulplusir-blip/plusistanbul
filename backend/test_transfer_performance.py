"""
Performance Tests for Transfer Pricing Calculations
Tests performance under load and edge cases
"""

import pytest
import time
import threading
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

from transfers.models import TransferRoute, TransferRoutePricing, TransferOption
from agents.models import Agent
from agents.pricing_service import AgentPricingService
from test_fixtures import TransferTestFixtures, TransferTestData

User = get_user_model()


class TransferPerformanceTests(TestCase):
    """Performance tests for Transfer pricing calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create test environment
        self.agent = TransferTestFixtures.create_test_agent()
        self.route = TransferTestFixtures.create_test_route()
        self.pricing = TransferTestFixtures.create_test_pricing(self.route)
        
        # Create multiple options for testing
        self.options = []
        for i in range(10):
            option = TransferTestFixtures.create_test_option(
                name=f'Option {i}',
                price=Decimal(f'{i + 1}.00')
            )
            self.options.append(option)

    def test_single_pricing_calculation_performance(self):
        """Test performance of single pricing calculation"""
        start_time = time.time()
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 100ms
        self.assertLess(execution_time, 0.1)
        self.assertTrue(result['success'])
        
        print(f"Single pricing calculation: {execution_time:.4f}s")

    def test_bulk_pricing_calculations_performance(self):
        """Test performance of bulk pricing calculations"""
        start_time = time.time()
        
        # Calculate pricing for 100 different scenarios
        results = []
        for i in range(100):
            result = AgentPricingService.calculate_transfer_price_for_agent(
                route=self.route,
                vehicle_type='sedan',
                agent=self.agent,
                passenger_count=(i % 4) + 1,
                trip_type='one_way' if i % 2 == 0 else 'round_trip',
                hour=(i % 24),
                return_hour=(i % 24) + 2 if i % 2 == 1 else None
            )
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 5 seconds for 100 calculations
        self.assertLess(execution_time, 5.0)
        
        # All calculations should succeed
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), 100)
        
        print(f"Bulk pricing calculations (100): {execution_time:.4f}s")
        print(f"Average per calculation: {execution_time/100:.4f}s")

    def test_concurrent_pricing_calculations(self):
        """Test performance under concurrent load"""
        def calculate_pricing(thread_id):
            """Calculate pricing in a thread"""
            start_time = time.time()
            
            result = AgentPricingService.calculate_transfer_price_for_agent(
                route=self.route,
                vehicle_type='sedan',
                agent=self.agent,
                passenger_count=(thread_id % 4) + 1,
                trip_type='one_way' if thread_id % 2 == 0 else 'round_trip',
                hour=(thread_id % 24),
                return_hour=(thread_id % 24) + 2 if thread_id % 2 == 1 else None
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                'thread_id': thread_id,
                'success': result['success'],
                'execution_time': execution_time,
                'result': result
            }
        
        # Run 50 concurrent calculations
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(calculate_pricing, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_execution_time = end_time - start_time
        
        # Should complete within 10 seconds
        self.assertLess(total_execution_time, 10.0)
        
        # All calculations should succeed
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), 50)
        
        # Calculate average execution time
        avg_execution_time = sum(r['execution_time'] for r in results) / len(results)
        
        print(f"Concurrent pricing calculations (50 threads): {total_execution_time:.4f}s")
        print(f"Average per calculation: {avg_execution_time:.4f}s")

    def test_pricing_with_many_options_performance(self):
        """Test performance with many options"""
        selected_options = [
            {'id': opt.id, 'name': opt.name, 'price': opt.price}
            for opt in self.options
        ]
        
        start_time = time.time()
        
        result = AgentPricingService.calculate_transfer_price_for_agent(
            route=self.route,
            vehicle_type='sedan',
            agent=self.agent,
            passenger_count=2,
            trip_type='one_way',
            hour=14,
            selected_options=selected_options
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 200ms even with many options
        self.assertLess(execution_time, 0.2)
        self.assertTrue(result['success'])
        
        print(f"Pricing with {len(selected_options)} options: {execution_time:.4f}s")

    def test_database_query_performance(self):
        """Test database query performance for pricing"""
        # Test with multiple routes and pricing configurations
        routes = []
        pricing_configs = []
        
        # Create 20 routes
        for i in range(20):
            route = TransferTestFixtures.create_test_route(
                name=f'Route {i}',
                from_location=f'City {i}',
                to_location=f'City {i + 1}'
            )
            routes.append(route)
        
        # Create pricing for each route
        for route in routes:
            for vehicle_type in ['sedan', 'van', 'bus']:
                pricing = TransferTestFixtures.create_test_pricing(
                    route=route,
                    vehicle_type=vehicle_type,
                    base_price=Decimal(f'{100 + i * 10}.00')
                )
                pricing_configs.append(pricing)
        
        start_time = time.time()
        
        # Calculate pricing for all combinations
        results = []
        for route in routes:
            for vehicle_type in ['sedan', 'van', 'bus']:
                result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=route,
                    vehicle_type=vehicle_type,
                    agent=self.agent,
                    passenger_count=2,
                    trip_type='one_way',
                    hour=14
                )
                results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 15 seconds for 60 calculations
        self.assertLess(execution_time, 15.0)
        
        # All calculations should succeed
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), 60)
        
        print(f"Database query performance (60 calculations): {execution_time:.4f}s")
        print(f"Average per calculation: {execution_time/60:.4f}s")

    def test_memory_usage_performance(self):
        """Test memory usage during pricing calculations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many calculations
        results = []
        for i in range(1000):
            result = AgentPricingService.calculate_transfer_price_for_agent(
                route=self.route,
                vehicle_type='sedan',
                agent=self.agent,
                passenger_count=(i % 4) + 1,
                trip_type='one_way' if i % 2 == 0 else 'round_trip',
                hour=(i % 24)
            )
            results.append(result)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50)
        
        print(f"Memory usage increase: {memory_increase:.2f}MB")
        print(f"Initial memory: {initial_memory:.2f}MB")
        print(f"Final memory: {final_memory:.2f}MB")

    def test_edge_case_performance(self):
        """Test performance with edge cases"""
        edge_cases = [
            # Midnight hour
            {'hour': 0, 'expected_night_surcharge': Decimal('25.00')},
            # Early morning
            {'hour': 5, 'expected_night_surcharge': Decimal('25.00')},
            # Late night
            {'hour': 23, 'expected_night_surcharge': Decimal('25.00')},
            # Noon
            {'hour': 12, 'expected_night_surcharge': Decimal('0.00')},
            # Evening
            {'hour': 18, 'expected_night_surcharge': Decimal('0.00')},
        ]
        
        start_time = time.time()
        
        results = []
        for case in edge_cases:
            result = AgentPricingService.calculate_transfer_price_for_agent(
                route=self.route,
                vehicle_type='sedan',
                agent=self.agent,
                passenger_count=2,
                trip_type='one_way',
                hour=case['hour']
            )
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 100ms
        self.assertLess(execution_time, 0.1)
        
        # All calculations should succeed
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), len(edge_cases))
        
        print(f"Edge case performance: {execution_time:.4f}s")

    def test_round_trip_performance(self):
        """Test performance of round trip calculations"""
        start_time = time.time()
        
        # Calculate 100 round trip scenarios
        results = []
        for i in range(100):
            result = AgentPricingService.calculate_transfer_price_for_agent(
                route=self.route,
                vehicle_type='sedan',
                agent=self.agent,
                passenger_count=2,
                trip_type='round_trip',
                hour=14,
                return_hour=16
            )
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 5 seconds
        self.assertLess(execution_time, 5.0)
        
        # All calculations should succeed
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), 100)
        
        print(f"Round trip performance (100 calculations): {execution_time:.4f}s")

    def test_capacity_validation_performance(self):
        """Test performance of capacity validation"""
        start_time = time.time()
        
        # Test capacity validation for different passenger counts
        results = []
        for passenger_count in range(1, 21):  # Test 1-20 passengers
            result = AgentPricingService.calculate_transfer_price_for_agent(
                route=self.route,
                vehicle_type='sedan',
                agent=self.agent,
                passenger_count=passenger_count,
                trip_type='one_way',
                hour=14
            )
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 1 second
        self.assertLess(execution_time, 1.0)
        
        # Some should succeed (valid capacity), some should fail (invalid capacity)
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        # Should have some successful and some failed results
        self.assertGreater(len(successful_results), 0)
        self.assertGreater(len(failed_results), 0)
        
        print(f"Capacity validation performance: {execution_time:.4f}s")
        print(f"Successful: {len(successful_results)}, Failed: {len(failed_results)}")


class TransferLoadTests(TransactionTestCase):
    """Load tests for Transfer pricing under high load"""
    
    def setUp(self):
        """Set up test data"""
        self.agent = TransferTestFixtures.create_test_agent()
        self.route = TransferTestFixtures.create_test_route()
        self.pricing = TransferTestFixtures.create_test_pricing(self.route)

    def test_high_load_pricing_calculations(self):
        """Test pricing calculations under high load"""
        def calculate_pricing_batch(batch_id, batch_size=100):
            """Calculate pricing for a batch"""
            start_time = time.time()
            results = []
            
            for i in range(batch_size):
                result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=self.route,
                    vehicle_type='sedan',
                    agent=self.agent,
                    passenger_count=(i % 4) + 1,
                    trip_type='one_way' if i % 2 == 0 else 'round_trip',
                    hour=(i % 24),
                    return_hour=(i % 24) + 2 if i % 2 == 1 else None
                )
                results.append(result)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                'batch_id': batch_id,
                'batch_size': batch_size,
                'execution_time': execution_time,
                'successful_count': len([r for r in results if r['success']]),
                'failed_count': len([r for r in results if not r['success']])
            }
        
        # Run 10 batches of 100 calculations each (1000 total)
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(calculate_pricing_batch, i, 100) for i in range(10)]
            batch_results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_execution_time = end_time - start_time
        
        # Should complete within 30 seconds
        self.assertLess(total_execution_time, 30.0)
        
        # All batches should complete successfully
        total_successful = sum(batch['successful_count'] for batch in batch_results)
        total_failed = sum(batch['failed_count'] for batch in batch_results)
        
        self.assertEqual(total_successful, 1000)
        self.assertEqual(total_failed, 0)
        
        print(f"High load test (1000 calculations): {total_execution_time:.4f}s")
        print(f"Average per calculation: {total_execution_time/1000:.4f}s")
        
        # Print batch performance
        for batch in batch_results:
            print(f"Batch {batch['batch_id']}: {batch['execution_time']:.4f}s")

    def test_database_connection_pool_performance(self):
        """Test performance with database connection pooling"""
        def calculate_pricing_with_db_ops(thread_id):
            """Calculate pricing with database operations"""
            start_time = time.time()
            
            # Perform multiple database operations
            for i in range(10):
                result = AgentPricingService.calculate_transfer_price_for_agent(
                    route=self.route,
                    vehicle_type='sedan',
                    agent=self.agent,
                    passenger_count=(i % 4) + 1,
                    trip_type='one_way',
                    hour=(i % 24)
                )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                'thread_id': thread_id,
                'execution_time': execution_time,
                'success': result['success']
            }
        
        # Run 20 threads with 10 calculations each (200 total)
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(calculate_pricing_with_db_ops, i) for i in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_execution_time = end_time - start_time
        
        # Should complete within 20 seconds
        self.assertLess(total_execution_time, 20.0)
        
        # All calculations should succeed
        successful_results = [r for r in results if r['success']]
        self.assertEqual(len(successful_results), 20)
        
        print(f"Database connection pool test: {total_execution_time:.4f}s")


if __name__ == '__main__':
    pytest.main([__file__])
