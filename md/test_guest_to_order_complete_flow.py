#!/usr/bin/env python3
"""
Complete E2E Test for Guest to Order Flow
Tests the entire user journey from guest browsing to completed order
Includes data consistency checks between frontend and backend
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class GuestToOrderCompleteFlowTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = str(uuid.uuid4())  # Simulate guest session
        self.test_results = []
        self.data_comparison = {
            'tour_detail': {},
            'cart_data': {},
            'user_data': {},
            'checkout_data': {},
            'order_data': {},
            'order_detail': {}
        }

        # Test user credentials
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

    def log_test(self, test_name: str, success: bool, message: str = "", data: Dict = None):
        """Log test result with optional data"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "data": data or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

    def compare_data_consistency(self, step_name: str, data1: Dict, data2: Dict, keys_to_compare: List[str]):
        """Compare data consistency between two steps"""
        print(f"\n🔍 Comparing data consistency for {step_name}:")

        inconsistencies = []
        for key in keys_to_compare:
            val1 = self._get_nested_value(data1, key)
            val2 = self._get_nested_value(data2, key)

            if val1 != val2:
                print(f"   ⚠️  {key}: {val1} ≠ {val2}")
                inconsistencies.append({
                    'key': key,
                    'value1': val1,
                    'value2': val2
                })
            else:
                print(f"   ✅ {key}: {val1}")

        return inconsistencies

    def _get_nested_value(self, data: Dict, key_path: str):
        """Get nested value from dictionary using dot notation"""
        keys = key_path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def test_guest_session_setup(self) -> bool:
        """Setup guest session"""
        try:
            # Set session cookie to simulate guest
            self.session.cookies.set('sessionid', self.session_id, domain='localhost')

            # Test API accessibility
            response = self.session.get(f"{self.base_url}/api/v1/")
            success = response.status_code == 200

            self.log_test("Guest Session Setup", success,
                         f"Session ID: {self.session_id[:8]}...")
            return success
        except Exception as e:
            self.log_test("Guest Session Setup", False, f"Error: {str(e)}")
            return False

    def test_tour_detail_retrieval(self) -> Optional[Dict]:
        """Retrieve tour details (Tour X - Cultural Experience)"""
        try:
            # First get list of tours
            response = self.session.get(f"{self.base_url}/api/v1/tours/")
            if response.status_code != 200:
                self.log_test("Tour List Retrieval", False, f"Status: {response.status_code}")
                return None

            tours = response.json()
            if not tours:
                self.log_test("Tour List Retrieval", False, "No tours found")
                return None

            # Find Tour X - Cultural Experience
            tour_x = None
            for tour in tours:
                if 'Tour X' in tour.get('title', '') or 'Cultural Experience' in tour.get('title', ''):
                    tour_x = tour
                    break

            if not tour_x:
                # Get first available tour for testing
                tour_x = tours[0]
                print(f"⚠️ Tour X not found, using: {tour_x.get('title')}")

            # Get detailed tour information
            tour_id = tour_x['id']
            response = self.session.get(f"{self.base_url}/api/v1/tours/{tour_id}/")

            if response.status_code == 200:
                tour_detail = response.json()

                # Store for comparison
                self.data_comparison['tour_detail'] = {
                    'id': tour_detail.get('id'),
                    'title': tour_detail.get('title'),
                    'base_price': tour_detail.get('base_price'),
                    'currency': tour_detail.get('currency'),
                    'variants': tour_detail.get('variants', []),
                    'options': tour_detail.get('options', []),
                    'schedules': tour_detail.get('schedules', [])
                }

                self.log_test("Tour Detail Retrieval", True,
                             f"Tour: {tour_detail.get('title')} - {len(tour_detail.get('variants', []))} variants, {len(tour_detail.get('options', []))} options")
                return tour_detail
            else:
                self.log_test("Tour Detail Retrieval", False, f"Status: {response.status_code}")
                return None

        except Exception as e:
            self.log_test("Tour Detail Retrieval", False, f"Error: {str(e)}")
            return None

    def test_guest_cart_addition(self, tour_detail: Dict) -> Optional[Dict]:
        """Add tour to guest cart with options"""
        try:
            # Select first available variant and schedule
            variants = tour_detail.get('variants', [])
            schedules = tour_detail.get('schedules', [])
            options = tour_detail.get('options', [])

            if not variants or not schedules:
                self.log_test("Guest Cart Addition", False, "No variants or schedules available")
                return None

            variant = variants[0]
            schedule = schedules[0]

            # Prepare cart data with options
            selected_options = []
            if options:
                # Select first 2 options for testing
                for i, option in enumerate(options[:2]):
                    selected_options.append({
                        'option_id': option['id'],
                        'name': option.get('name', f'Option {i+1}'),
                        'price': option.get('price', 0),
                        'quantity': 1
                    })

            cart_data = {
                'product_type': 'tour',
                'product_id': tour_detail['id'],
                'variant_id': variant['id'],
                'variant_name': variant.get('name', ''),
                'quantity': 3,  # 3 people total
                'unit_price': float(variant.get('base_price', 0)),
                'selected_options': selected_options,
                'booking_data': {
                    'schedule_id': schedule['id'],
                    'participants': {
                        'adult': 2,
                        'child': 1,
                        'infant': 0
                    },
                    'special_requests': 'Test booking from guest user'
                }
            }

            # Add to cart
            response = self.session.post(f"{self.base_url}/api/v1/cart/add/", json=cart_data)

            if response.status_code in [200, 201]:
                cart_result = response.json()

                # Store cart data for comparison
                self.data_comparison['cart_data'] = {
                    'product_type': cart_data['product_type'],
                    'product_id': cart_data['product_id'],
                    'variant_id': cart_data['variant_id'],
                    'variant_name': cart_data['variant_name'],
                    'quantity': cart_data['quantity'],
                    'unit_price': cart_data['unit_price'],
                    'selected_options': cart_data['selected_options'],
                    'booking_data': cart_data['booking_data'],
                    'cart_item_id': cart_result.get('cart_item', {}).get('id'),
                    'cart_total': cart_result.get('cart_item', {}).get('total_price')
                }

                self.log_test("Guest Cart Addition", True,
                             f"Added to cart - Total: ${cart_result.get('cart_item', {}).get('total_price', 0)}")
                return cart_result
            else:
                self.log_test("Guest Cart Addition", False,
                             f"Status: {response.status_code}, Response: {response.text}")
                return None

        except Exception as e:
            self.log_test("Guest Cart Addition", False, f"Error: {str(e)}")
            return None

    def test_user_authentication(self) -> Optional[Dict]:
        """Authenticate test user"""
        try:
            # First, try to create test user if doesn't exist
            self._create_test_user_if_needed()

            # Login
            login_data = {
                'username': self.test_user['username'],
                'password': self.test_user['password']
            }

            response = self.session.post(f"{self.base_url}/api/v1/auth/login/", json=login_data)

            if response.status_code == 200:
                auth_data = response.json()

                # Store user data for comparison
                self.data_comparison['user_data'] = {
                    'id': auth_data.get('user', {}).get('id'),
                    'username': auth_data.get('user', {}).get('username'),
                    'email': auth_data.get('user', {}).get('email'),
                    'is_authenticated': True
                }

                # Set authorization header for future requests
                if 'access' in auth_data:
                    self.session.headers.update({
                        'Authorization': f"Bearer {auth_data['access']}"
                    })

                self.log_test("User Authentication", True,
                             f"Logged in as: {auth_data.get('user', {}).get('username')}")
                return auth_data
            else:
                self.log_test("User Authentication", False,
                             f"Status: {response.status_code}, Response: {response.text}")
                return None

        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return None

    def _create_test_user_if_needed(self):
        """Create test user if doesn't exist"""
        try:
            register_data = {
                'username': self.test_user['username'],
                'email': self.test_user['email'],
                'password': self.test_user['password'],
                'password_confirm': self.test_user['password']
            }

            response = self.session.post(f"{self.base_url}/api/v1/auth/register/", json=register_data)

            if response.status_code == 201:
                print("📝 Test user created successfully")
            elif response.status_code == 400:
                # User might already exist
                error_data = response.json()
                if 'username' in str(error_data).lower() or 'email' in str(error_data).lower():
                    print("📝 Test user already exists")
                else:
                    print(f"⚠️ Unexpected error creating user: {error_data}")
            else:
                print(f"⚠️ Could not create test user: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Error creating test user: {str(e)}")

    def test_cart_merge_after_login(self) -> bool:
        """Test cart merge after user login"""
        try:
            # The cart should be automatically merged when user logs in
            # Check if cart items are still available
            response = self.session.get(f"{self.base_url}/api/v1/cart/")

            if response.status_code == 200:
                cart_data = response.json()
                items = cart_data.get('items', [])

                if items:
                    self.log_test("Cart Merge After Login", True,
                                 f"Cart merged successfully - {len(items)} items")
                    return True
                else:
                    self.log_test("Cart Merge After Login", False, "Cart is empty after login")
                    return False
            else:
                self.log_test("Cart Merge After Login", False,
                             f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Cart Merge After Login", False, f"Error: {str(e)}")
            return False

    def test_checkout_process(self) -> Optional[Dict]:
        """Process checkout"""
        try:
            # Get cart data first
            cart_response = self.session.get(f"{self.base_url}/api/v1/cart/")
            if cart_response.status_code != 200:
                self.log_test("Checkout Process", False, "Could not retrieve cart")
                return None

            cart_data = cart_response.json()
            cart_id = cart_data.get('id')

            if not cart_id:
                self.log_test("Checkout Process", False, "No cart ID found")
                return None

            # Create order from cart
            order_data = {
                'cart_id': cart_id,
                'special_requests': 'Complete E2E test order'
            }

            response = self.session.post(f"{self.base_url}/api/v1/orders/create/", json=order_data)

            if response.status_code in [200, 201]:
                order_result = response.json()

                # Store checkout/order data for comparison
                self.data_comparison['checkout_data'] = {
                    'cart_id': cart_id,
                    'order_id': order_result.get('id'),
                    'order_number': order_result.get('order_number'),
                    'status': order_result.get('status'),
                    'total_amount': order_result.get('total_amount'),
                    'subtotal': order_result.get('subtotal')
                }

                self.log_test("Checkout Process", True,
                             f"Order created: {order_result.get('order_number')} - Status: {order_result.get('status')}")
                return order_result
            else:
                self.log_test("Checkout Process", False,
                             f"Status: {response.status_code}, Response: {response.text}")
                return None

        except Exception as e:
            self.log_test("Checkout Process", False, f"Error: {str(e)}")
            return None

    def test_order_detail_retrieval(self, order: Dict) -> Optional[Dict]:
        """Retrieve order details"""
        try:
            order_number = order.get('order_number')
            if not order_number:
                self.log_test("Order Detail Retrieval", False, "No order number")
                return None

            response = self.session.get(f"{self.base_url}/api/v1/orders/{order_number}/")

            if response.status_code == 200:
                order_detail = response.json()

                # Store order detail data for comparison
                if order_detail.get('items'):
                    first_item = order_detail['items'][0]
                    self.data_comparison['order_detail'] = {
                        'order_number': order_detail.get('order_number'),
                        'status': order_detail.get('status'),
                        'total_amount': order_detail.get('total_amount'),
                        'product_title': first_item.get('product_title'),
                        'variant_name': first_item.get('variant_name'),
                        'quantity': first_item.get('quantity'),
                        'unit_price': first_item.get('unit_price'),
                        'total_price': first_item.get('total_price'),
                        'selected_options': first_item.get('selected_options', [])
                    }

                self.log_test("Order Detail Retrieval", True,
                             f"Order {order_number} - Status: {order_detail.get('status')}")
                return order_detail
            else:
                self.log_test("Order Detail Retrieval", False,
                             f"Status: {response.status_code}")
                return None

        except Exception as e:
            self.log_test("Order Detail Retrieval", False, f"Error: {str(e)}")
            return None

    def test_data_consistency_analysis(self):
        """Analyze data consistency across all steps"""
        print("\n" + "="*80)
        print("🔍 DATA CONSISTENCY ANALYSIS")
        print("="*80)

        # Compare Tour Detail vs Cart
        print("\n1. تور دیتیل vs کارت:")
        tour_cart_keys = [
            'title', 'base_price', 'currency',
            'variants.0.name', 'variants.0.base_price'
        ]
        tour_cart_inconsistencies = self.compare_data_consistency(
            "Tour Detail vs Cart",
            self.data_comparison['tour_detail'],
            self.data_comparison['cart_data'],
            tour_cart_keys
        )

        # Compare Cart vs Order
        print("\n2. کارت vs اوردر:")
        cart_order_keys = [
            'product_id', 'variant_id', 'variant_name',
            'quantity', 'unit_price', 'selected_options'
        ]
        cart_order_inconsistencies = self.compare_data_consistency(
            "Cart vs Order",
            self.data_comparison['cart_data'],
            self.data_comparison['order_detail'],
            cart_order_keys
        )

        # Check option names specifically
        print("\n3. بررسی نام گزینه‌ها:")
        cart_options = self.data_comparison['cart_data'].get('selected_options', [])
        order_options = self.data_comparison['order_detail'].get('selected_options', [])

        if len(cart_options) != len(order_options):
            print(f"   ⚠️ تعداد گزینه‌ها متفاوت: کارت({len(cart_options)}) ≠ اوردر({len(order_options)})")
        else:
            for i, (cart_opt, order_opt) in enumerate(zip(cart_options, order_options)):
                cart_name = cart_opt.get('name', 'No name')
                order_name = order_opt.get('name', 'No name')
                if cart_name != order_name:
                    print(f"   ⚠️ گزینه {i+1}: کارت('{cart_name}') ≠ اوردر('{order_name}')")
                else:
                    print(f"   ✅ گزینه {i+1}: '{cart_name}'")

        # Pricing consistency
        print("\n4. بررسی قیمت‌گذاری:")
        cart_total = self.data_comparison['cart_data'].get('cart_total', 0)
        order_total = self.data_comparison['order_detail'].get('total_price', 0)
        checkout_total = self.data_comparison['checkout_data'].get('total_amount', 0)

        print(f"   کارت: ${cart_total}")
        print(f"   آیتم اوردر: ${order_total}")
        print(f"   مجموع اوردر: ${checkout_total}")

        if abs(float(cart_total) - float(order_total)) > 0.01:
            print(f"   ⚠️ قیمت کارت و آیتم اوردر متفاوت!")
        else:
            print(f"   ✅ قیمت کارت و آیتم اوردر یکسان")

        if abs(float(order_total) - float(checkout_total)) > 0.01:
            print(f"   ⚠️ قیمت آیتم و مجموع اوردر متفاوت!")
        else:
            print(f"   ✅ قیمت آیتم و مجموع اوردر یکسان")

        return {
            'tour_cart_inconsistencies': len(tour_cart_inconsistencies),
            'cart_order_inconsistencies': len(cart_order_inconsistencies),
            'total_inconsistencies': len(tour_cart_inconsistencies) + len(cart_order_inconsistencies)
        }

    def run_complete_flow_test(self) -> Dict[str, Any]:
        """Run the complete guest to order flow test"""
        print("🚀 شروع تست کامل سناریوی کاربر مهمان تا سفارش\n")

        # Step 1: Guest session setup
        print("1️⃣ تنظیم سشن مهمان...")
        if not self.test_guest_session_setup():
            return {"success": False, "message": "Guest session setup failed"}

        # Step 2: Tour detail retrieval
        print("\n2️⃣ دریافت جزئیات تور...")
        tour_detail = self.test_tour_detail_retrieval()
        if not tour_detail:
            return {"success": False, "message": "Tour detail retrieval failed"}

        # Step 3: Guest cart addition
        print("\n3️⃣ اضافه کردن به کارت مهمان...")
        cart_result = self.test_guest_cart_addition(tour_detail)
        if not cart_result:
            return {"success": False, "message": "Guest cart addition failed"}

        # Step 4: User authentication
        print("\n4️⃣ احراز هویت کاربر...")
        auth_result = self.test_user_authentication()
        if not auth_result:
            return {"success": False, "message": "User authentication failed"}

        # Step 5: Cart merge after login
        print("\n5️⃣ ادغام کارت بعد از لاگین...")
        if not self.test_cart_merge_after_login():
            return {"success": False, "message": "Cart merge after login failed"}

        # Step 6: Checkout process
        print("\n6️⃣ فرآیند چک‌اوت...")
        order_result = self.test_checkout_process()
        if not order_result:
            return {"success": False, "message": "Checkout process failed"}

        # Step 7: Order detail retrieval
        print("\n7️⃣ دریافت جزئیات سفارش...")
        order_detail = self.test_order_detail_retrieval(order_result)
        if not order_detail:
            return {"success": False, "message": "Order detail retrieval failed"}

        # Step 8: Data consistency analysis
        print("\n8️⃣ تحلیل consistency داده‌ها...")
        consistency_results = self.test_data_consistency_analysis()

        # Calculate final results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"\n" + "="*80)
        print("📊 نتایج نهایی تست:")
        print(f"کل تست‌ها: {total_tests}")
        print(f"تست‌های موفق: {passed_tests}")
        print(f"تست‌های ناموفق: {failed_tests}")
        print(f"نرخ موفقیت: {(passed_tests/total_tests)*100:.1f}%")
        print(f"ناسازگاری‌های داده: {consistency_results['total_inconsistencies']}")
        print("="*80)

        # Success criteria: All tests pass AND no critical data inconsistencies
        critical_inconsistencies = consistency_results['cart_order_inconsistencies']
        success = failed_tests == 0 and critical_inconsistencies == 0

        if success:
            print("\n🎉 همه تست‌ها موفق! سناریوی کاربر مهمان تا سفارش کامل کار می‌کند.")
        else:
            print(f"\n⚠️ {failed_tests} تست ناموفق و {critical_inconsistencies} ناسازگاری داده وجود دارد.")

        return {
            "success": success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "data_consistency": consistency_results,
            "results": self.test_results,
            "data_comparison": self.data_comparison
        }

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Complete Guest to Order Flow Test")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    parser.add_argument("--user", default="testuser", help="Test username")
    parser.add_argument("--password", default="testpass123", help="Test password")

    args = parser.parse_args()

    # Update test user credentials
    test_user = {
        'username': args.user,
        'password': args.password,
        'email': f'{args.user}@example.com'
    }

    # Run complete flow test
    tester = GuestToOrderCompleteFlowTest(args.url)
    tester.test_user.update(test_user)

    results = tester.run_complete_flow_test()

    # Save results if output file specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 نتایج تست در فایل ذخیره شد: {args.output}")

    # Exit with appropriate code
    exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()
