#!/usr/bin/env python3
"""
Quick Test Script for Tour Booking System
Simple validation tests for the implemented features
"""

import requests
import json

def test_cart_validation():
    """Test cart validation endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Cart Validation...")
    
    # Test data
    test_cases = [
        {
            "name": "Valid Booking",
            "data": {
                "product_type": "tour",
                "product_id": 1,
                "quantity": 1,
                "participants": {"adult": 2, "child": 1, "infant": 0},
                "options": {},
                "special_requests": "Test request"
            },
            "expected_status": [200, 201]
        },
        {
            "name": "Too Many Infants",
            "data": {
                "product_type": "tour",
                "product_id": 1,
                "quantity": 1,
                "participants": {"adult": 2, "child": 0, "infant": 5},
                "options": {},
                "special_requests": ""
            },
            "expected_status": [400]
        },
        {
            "name": "No Participants",
            "data": {
                "product_type": "tour",
                "product_id": 1,
                "quantity": 1,
                "participants": {"adult": 0, "child": 0, "infant": 0},
                "options": {},
                "special_requests": ""
            },
            "expected_status": [400]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{base_url}/api/v1/cart/add/",
                json=test_case["data"],
                timeout=10
            )
            
            success = response.status_code in test_case["expected_status"]
            status = "✅ PASS" if success else "❌ FAIL"
            
            print(f"{status} {test_case['name']}: Status {response.status_code}")
            
            if not success:
                print(f"   Response: {response.text[:200]}...")
            
            results.append({
                "test": test_case["name"],
                "success": success,
                "status_code": response.status_code
            })
            
        except Exception as e:
            print(f"❌ FAIL {test_case['name']}: Error - {str(e)}")
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": str(e)
            })
    
    return results

def test_api_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000"
    
    print("\n🌐 Testing API Endpoints...")
    
    endpoints = [
        {"name": "API Root", "url": "/api/v1/"},
        {"name": "Tours List", "url": "/api/v1/tours/"},
        {"name": "Cart List", "url": "/api/v1/cart/"},
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint['url']}", timeout=10)
            success = response.status_code == 200
            status = "✅ PASS" if success else "❌ FAIL"
            
            print(f"{status} {endpoint['name']}: Status {response.status_code}")
            
            results.append({
                "endpoint": endpoint["name"],
                "success": success,
                "status_code": response.status_code
            })
            
        except Exception as e:
            print(f"❌ FAIL {endpoint['name']}: Error - {str(e)}")
            results.append({
                "endpoint": endpoint["name"],
                "success": False,
                "error": str(e)
            })
    
    return results

def main():
    """Main test function"""
    print("🚀 Quick Test for Tour Booking System")
    print("=" * 50)
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Test cart validation
    cart_results = test_cart_validation()
    
    # Summary
    total_tests = len(api_results) + len(cart_results)
    passed_tests = sum(1 for r in api_results + cart_results if r.get("success", False))
    
    print(f"\n📊 Test Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! System is ready for manual testing.")
    else:
        print("\n⚠️  Some tests failed. Please check the system before manual testing.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
