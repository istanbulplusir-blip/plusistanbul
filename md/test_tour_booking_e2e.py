#!/usr/bin/env python3
"""
E2E Test for Tour Booking System
Tests the complete flow from tour selection to cart addition with validation
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class TourBookingE2ETest:
    def __init__(self, base_url: str = "http://localhost:8000"):
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
    
    def test_tours_list(self) -> Optional[Dict]:
        """Test tours list endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tours/")
            if response.status_code == 200:
                tours = response.json()
                if tours and len(tours) > 0:
                    self.log_test("Tours List", True, f"Found {len(tours)} tours")
                    return tours[0]  # Return first tour for testing
                else:
                    self.log_test("Tours List", False, "No tours found")
                    return None
            else:
                self.log_test("Tours List", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Tours List", False, f"Error: {str(e)}")
            return None
    
    def test_tour_detail(self, tour_id: int) -> Optional[Dict]:
        """Test tour detail endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tours/{tour_id}/")
            if response.status_code == 200:
                tour = response.json()
                self.log_test("Tour Detail", True, f"Tour: {tour.get('title', 'Unknown')}")
                return tour
            else:
                self.log_test("Tour Detail", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Tour Detail", False, f"Error: {str(e)}")
            return None
    
    def test_cart_validation(self, tour_data: Dict) -> bool:
        """Test cart validation with various scenarios"""
        tour_id = tour_data.get('id')
        if not tour_id:
            self.log_test("Cart Validation", False, "No tour ID found")
            return False
        
        # Test 1: Valid booking
        valid_booking = {
            "product_type": "tour",
            "product_id": tour_id,
            "variant_id": tour_data.get('variants', [{}])[0].get('id') if tour_data.get('variants') else None,
            "schedule_id": tour_data.get('schedules', [{}])[0].get('id') if tour_data.get('schedules') else None,
            "participants": {
                "adult": 2,
                "child": 1,
                "infant": 0
            },
            "options": {},
            "special_requests": "Test booking request"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/cart/add/", json=valid_booking)
            if response.status_code in [200, 201]:
                self.log_test("Valid Booking", True, "Successfully added to cart")
            else:
                self.log_test("Valid Booking", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Valid Booking", False, f"Error: {str(e)}")
        
        # Test 2: Invalid booking (too many participants)
        invalid_booking = valid_booking.copy()
        invalid_booking["participants"] = {
            "adult": 50,  # Exceeds max participants
            "child": 0,
            "infant": 0
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/cart/add/", json=invalid_booking)
            if response.status_code == 400:
                self.log_test("Invalid Booking (Too Many Participants)", True, "Correctly rejected")
            else:
                self.log_test("Invalid Booking (Too Many Participants)", False, f"Should be rejected, got: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Booking (Too Many Participants)", False, f"Error: {str(e)}")
        
        # Test 3: Invalid booking (too many infants)
        invalid_infant_booking = valid_booking.copy()
        invalid_infant_booking["participants"] = {
            "adult": 2,
            "child": 0,
            "infant": 5  # Exceeds max infants (2)
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/cart/add/", json=invalid_infant_booking)
            if response.status_code == 400:
                self.log_test("Invalid Booking (Too Many Infants)", True, "Correctly rejected")
            else:
                self.log_test("Invalid Booking (Too Many Infants)", False, f"Should be rejected, got: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Booking (Too Many Infants)", False, f"Error: {str(e)}")
        
        return True
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        try:
            # Make multiple rapid requests
            for i in range(12):  # More than the 10 request limit
                response = self.session.post(f"{self.base_url}/api/v1/cart/add/", json={
                    "product_type": "tour",
                    "product_id": 999,  # Non-existent tour
                    "participants": {"adult": 1, "child": 0, "infant": 0}
                })
                
                if response.status_code == 429:  # Rate limit exceeded
                    self.log_test("Rate Limiting", True, f"Rate limit triggered after {i+1} requests")
                    return True
                time.sleep(0.1)  # Small delay between requests
            
            self.log_test("Rate Limiting", False, "Rate limit not triggered")
            return False
            
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all E2E tests"""
        print("🚀 Starting Tour Booking E2E Tests...\n")
        
        # Test API health
        if not self.test_api_health():
            return {"success": False, "message": "API not accessible"}
        
        # Test tours list
        tours = self.test_tours_list()
        if not tours:
            return {"success": False, "message": "No tours available for testing"}
        
        # Test tour detail
        tour_detail = self.test_tour_detail(tours['id'])
        if not tour_detail:
            return {"success": False, "message": "Tour detail not accessible"}
        
        # Test cart validation
        self.test_cart_validation(tour_detail)
        
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
    """Main function to run E2E tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tour Booking E2E Tests")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    # Run tests
    tester = TourBookingE2ETest(args.url)
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
