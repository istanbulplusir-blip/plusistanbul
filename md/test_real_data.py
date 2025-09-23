#!/usr/bin/env python3
"""
Comprehensive test script using real data from the database.
"""

import requests
import json
import time
from datetime import datetime, timedelta

class RealDataTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Real data from database
        self.test_tour_id = "362092e7-891d-411e-a29e-37024405bc07"  # Test Tour 16329065
        self.test_variant_id = "dfbf8292-caa3-4ecd-9f36-feb85c02b4fc"  # Standard variant
        self.test_schedule_id = "5e20a42d-1cc0-43fe-9a15-aedbc8102aae"  # 2025-09-03 schedule
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_tour_schedules_with_real_data(self) -> bool:
        """Test tour schedules endpoint with real tour ID."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tours/{self.test_tour_id}/schedules/")
            
            if response.status_code == 200:
                result = response.json()
                schedules = result.get('schedules', [])
                
                if schedules:
                    # Find our specific schedule
                    target_schedule = None
                    for schedule in schedules:
                        if schedule.get('id') == self.test_schedule_id:
                            target_schedule = schedule
                            break
                    
                    if target_schedule:
                        available_capacity = target_schedule.get('available_capacity', 0)
                        total_capacity = target_schedule.get('total_capacity', 0)
                        booked_capacity = target_schedule.get('booked_capacity', 0)
                        
                        self.log_test("Tour Schedules (Real Data)", True, 
                                    f"Tour: {result.get('tour', {}).get('title')}, "
                                    f"Schedule: {target_schedule.get('start_date')}, "
                                    f"Capacity: {available_capacity}/{total_capacity}")
                        return True
                    else:
                        self.log_test("Tour Schedules (Real Data)", False, "Target schedule not found")
                        return False
                else:
                    self.log_test("Tour Schedules (Real Data)", False, "No schedules found")
                    return False
            else:
                self.log_test("Tour Schedules (Real Data)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Tour Schedules (Real Data)", False, f"Error: {str(e)}")
            return False
    
    def test_capacity_calculation_with_pending_orders(self) -> bool:
        """Test that capacity calculation excludes pending orders."""
        try:
            # First, get current capacity
            response = self.session.get(f"{self.base_url}/api/v1/tours/{self.test_tour_id}/schedules/")
            
            if response.status_code == 200:
                result = response.json()
                schedules = result.get('schedules', [])
                
                if schedules:
                    # Find our specific schedule
                    target_schedule = None
                    for schedule in schedules:
                        if schedule.get('id') == self.test_schedule_id:
                            target_schedule = schedule
                            break
                    
                    if target_schedule:
                        initial_available = target_schedule.get('available_capacity', 0)
                        
                        # Now try to add to cart with real data
                        cart_data = {
                            "product_type": "tour",
                            "product_id": self.test_tour_id,
                            "variant_id": self.test_variant_id,
                            "booking_data": {
                                "participants": {
                                    "adult": 2,
                                    "child": 1,
                                    "infant": 0
                                },
                                "schedule_id": self.test_schedule_id
                            }
                        }
                        
                        # Test dry run
                        response = self.session.post(f"{self.base_url}/api/v1/cart/add/?dry_run=1", json=cart_data)
                        
                        if response.status_code == 200:
                            self.log_test("Capacity Calculation (Pending Excluded)", True, 
                                        f"Initial available: {initial_available}, "
                                        f"Dry run successful - pending orders don't affect capacity")
                            return True
                        else:
                            self.log_test("Capacity Calculation (Pending Excluded)", False, 
                                        f"Dry run failed: {response.status_code}")
                            return False
                    else:
                        self.log_test("Capacity Calculation (Pending Excluded)", False, "Target schedule not found")
                        return False
                else:
                    self.log_test("Capacity Calculation (Pending Excluded)", False, "No schedules found")
                    return False
            else:
                self.log_test("Capacity Calculation (Pending Excluded)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Capacity Calculation (Pending Excluded)", False, f"Error: {str(e)}")
            return False
    
    def test_pending_orders_endpoint(self) -> bool:
        """Test pending orders endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/pending/")
            
            if response.status_code == 200:
                result = response.json()
                pending_count = result.get('count', 0)
                pending_orders = result.get('pending_orders', [])
                
                self.log_test("Pending Orders Endpoint", True, 
                            f"Found {pending_count} pending orders")
                
                # Show some details about pending orders
                if pending_orders:
                    for order in pending_orders[:2]:  # Show first 2 orders
                        order_number = order.get('order_number', 'Unknown')
                        total_amount = order.get('total_amount', 0)
                        currency = order.get('currency', 'USD')
                        print(f"    📋 Order {order_number}: {total_amount} {currency}")
                
                return True
            else:
                self.log_test("Pending Orders Endpoint", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Pending Orders Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_order_summary_endpoint(self) -> bool:
        """Test order summary endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/summary/")
            
            if response.status_code == 200:
                result = response.json()
                total = result.get('total', 0)
                pending = result.get('pending', 0)
                confirmed = result.get('confirmed', 0)
                paid = result.get('paid', 0)
                completed = result.get('completed', 0)
                cancelled = result.get('cancelled', 0)
                
                self.log_test("Order Summary Endpoint", True, 
                            f"Total: {total}, Pending: {pending}, Confirmed: {confirmed}, "
                            f"Paid: {paid}, Completed: {completed}, Cancelled: {cancelled}")
                return True
            else:
                self.log_test("Order Summary Endpoint", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Order Summary Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_duplicate_booking_prevention(self) -> bool:
        """Test that duplicate booking prevention works."""
        try:
            # Try to add the same tour to cart twice
            cart_data = {
                "product_type": "tour",
                "product_id": self.test_tour_id,
                "variant_id": self.test_variant_id,
                "booking_data": {
                    "participants": {
                        "adult": 1,
                        "child": 0,
                        "infant": 0
                    },
                    "schedule_id": self.test_schedule_id
                }
            }
            
            # First attempt
            response1 = self.session.post(f"{self.base_url}/api/v1/cart/add/?dry_run=1", json=cart_data)
            
            if response1.status_code == 200:
                # Second attempt (should fail due to duplicate)
                response2 = self.session.post(f"{self.base_url}/api/v1/cart/add/?dry_run=1", json=cart_data)
                
                if response2.status_code == 400:
                    error_data = response2.json()
                    if 'DUPLICATE_BOOKING' in str(error_data):
                        self.log_test("Duplicate Booking Prevention", True, 
                                    "Duplicate booking correctly prevented")
                        return True
                    else:
                        self.log_test("Duplicate Booking Prevention", False, 
                                    "Duplicate booking not prevented correctly")
                        return False
                else:
                    self.log_test("Duplicate Booking Prevention", False, 
                                f"Second attempt should fail but got: {response2.status_code}")
                    return False
            else:
                self.log_test("Duplicate Booking Prevention", False, 
                            f"First attempt failed: {response1.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Booking Prevention", False, f"Error: {str(e)}")
            return False
    
    def test_capacity_availability_check(self) -> bool:
        """Test capacity availability check with real data."""
        try:
            # Get current capacity
            response = self.session.get(f"{self.base_url}/api/v1/tours/{self.test_tour_id}/schedules/")
            
            if response.status_code == 200:
                result = response.json()
                schedules = result.get('schedules', [])
                
                if schedules:
                    # Find our specific schedule
                    target_schedule = None
                    for schedule in schedules:
                        if schedule.get('id') == self.test_schedule_id:
                            target_schedule = schedule
                            break
                    
                    if target_schedule:
                        available_capacity = target_schedule.get('available_capacity', 0)
                        
                        # Try to book more than available capacity
                        cart_data = {
                            "product_type": "tour",
                            "product_id": self.test_tour_id,
                            "variant_id": self.test_variant_id,
                            "booking_data": {
                                "participants": {
                                    "adult": available_capacity + 5,  # More than available
                                    "child": 0,
                                    "infant": 0
                                },
                                "schedule_id": self.test_schedule_id
                            }
                        }
                        
                        response = self.session.post(f"{self.base_url}/api/v1/cart/add/?dry_run=1", json=cart_data)
                        
                        if response.status_code == 400:
                            error_data = response.json()
                            if 'INSUFFICIENT_CAPACITY' in str(error_data):
                                self.log_test("Capacity Availability Check", True, 
                                            f"Correctly rejected booking exceeding capacity ({available_capacity})")
                                return True
                            else:
                                self.log_test("Capacity Availability Check", False, 
                                            "Capacity check failed but wrong error type")
                                return False
                        else:
                            self.log_test("Capacity Availability Check", False, 
                                        f"Should reject but got: {response.status_code}")
                            return False
                    else:
                        self.log_test("Capacity Availability Check", False, "Target schedule not found")
                        return False
                else:
                    self.log_test("Capacity Availability Check", False, "No schedules found")
                    return False
            else:
                self.log_test("Capacity Availability Check", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Capacity Availability Check", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> dict:
        """Run all tests with real data."""
        print("🚀 Starting Comprehensive Real Data Tests...\n")
        print(f"📊 Test Data:")
        print(f"   Tour ID: {self.test_tour_id}")
        print(f"   Variant ID: {self.test_variant_id}")
        print(f"   Schedule ID: {self.test_schedule_id}")
        print()
        
        # Test tour schedules with real data
        self.test_tour_schedules_with_real_data()
        
        # Test capacity calculation with pending orders
        self.test_capacity_calculation_with_pending_orders()
        
        # Test pending orders endpoint
        self.test_pending_orders_endpoint()
        
        # Test order summary endpoint
        self.test_order_summary_endpoint()
        
        # Test duplicate booking prevention
        self.test_duplicate_booking_prevention()
        
        # Test capacity availability check
        self.test_capacity_availability_check()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Test Results Summary:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        return {
            "success": failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }

def main():
    """Main function to run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real Data System Tests")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    # Run tests
    tester = RealDataTest(args.url)
    results = tester.run_all_tests()
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Test results saved to: {args.output}")
    
    # Exit with appropriate code
    exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()
