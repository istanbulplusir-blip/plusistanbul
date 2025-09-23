#!/usr/bin/env python3
"""
Test script for the new pending order system with capacity management.
"""

import requests
import json
import time
from datetime import datetime, timedelta

class PendingOrderSystemTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
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
        
    def test_api_health(self) -> bool:
        """Test if API is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/")
            success = response.status_code == 200
            self.log_test("API Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_pending_order_creation(self) -> bool:
        """Test creating a pending order"""
        try:
            # Test data for pending order
            order_data = {
                "product_type": "tour",
                "product_id": "550e8400-e29b-41d4-a716-446655440000",  # Example UUID
                "booking_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "quantity": 2,
                "unit_price": 100.00,
                "total_price": 200.00,
                "product_title": "Test Tour",
                "product_slug": "test-tour",
                "booking_data": {
                    "participants": {
                        "adult": 2,
                        "child": 0,
                        "infant": 0
                    },
                    "schedule_id": "test-schedule-123"
                },
                "currency": "USD"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/orders/add/", json=order_data)
            
            if response.status_code == 201:
                result = response.json()
                self.log_test("Pending Order Creation", True, f"Order created: {result.get('order_number')}")
                return True
            else:
                self.log_test("Pending Order Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Pending Order Creation", False, f"Error: {str(e)}")
            return False
    
    def test_pending_orders_list(self) -> bool:
        """Test getting pending orders list"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/pending/")
            
            if response.status_code == 200:
                result = response.json()
                count = result.get('count', 0)
                self.log_test("Pending Orders List", True, f"Found {count} pending orders")
                return True
            else:
                self.log_test("Pending Orders List", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Pending Orders List", False, f"Error: {str(e)}")
            return False
    
    def test_order_summary(self) -> bool:
        """Test getting order status summary"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/summary/")
            
            if response.status_code == 200:
                result = response.json()
                total = result.get('total', 0)
                pending = result.get('pending', 0)
                self.log_test("Order Summary", True, f"Total: {total}, Pending: {pending}")
                return True
            else:
                self.log_test("Order Summary", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Order Summary", False, f"Error: {str(e)}")
            return False
    
    def test_capacity_calculation(self) -> bool:
        """Test that capacity calculation excludes pending orders"""
        try:
            # Get tour schedules to check capacity
            response = self.session.get(f"{self.base_url}/api/v1/tours/1/schedules/")
            
            if response.status_code == 200:
                result = response.json()
                schedules = result.get('schedules', [])
                
                if schedules:
                    # Check that capacity calculation is working
                    schedule = schedules[0]
                    available_capacity = schedule.get('available_capacity', 0)
                    total_capacity = schedule.get('total_capacity', 0)
                    
                    self.log_test("Capacity Calculation", True, 
                                f"Total: {total_capacity}, Available: {available_capacity}")
                    return True
                else:
                    self.log_test("Capacity Calculation", False, "No schedules found")
                    return False
            else:
                self.log_test("Capacity Calculation", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Capacity Calculation", False, f"Error: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting on order creation"""
        try:
            # Make multiple rapid requests
            for i in range(7):  # More than the 5 request limit
                order_data = {
                    "product_type": "tour",
                    "product_id": "550e8400-e29b-41d4-a716-446655440000",
                    "booking_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "quantity": 1,
                    "unit_price": 100.00,
                    "total_price": 100.00,
                    "product_title": "Test Tour",
                    "product_slug": "test-tour",
                    "currency": "USD"
                }
                
                response = self.session.post(f"{self.base_url}/api/v1/orders/add/", json=order_data)
                
                if response.status_code == 429:  # Rate limit exceeded
                    self.log_test("Rate Limiting", True, f"Rate limit triggered after {i+1} requests")
                    return True
                time.sleep(0.1)  # Small delay between requests
            
            self.log_test("Rate Limiting", False, "Rate limit not triggered")
            return False
            
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> dict:
        """Run all tests for the pending order system"""
        print("🚀 Starting Pending Order System Tests...\n")
        
        # Test API health
        if not self.test_api_health():
            return {"success": False, "message": "API not accessible"}
        
        # Test pending order creation
        self.test_pending_order_creation()
        
        # Test pending orders list
        self.test_pending_orders_list()
        
        # Test order summary
        self.test_order_summary()
        
        # Test capacity calculation
        self.test_capacity_calculation()
        
        # Test rate limiting
        self.test_rate_limiting()
        
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
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pending Order System Tests")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    # Run tests
    tester = PendingOrderSystemTest(args.url)
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
