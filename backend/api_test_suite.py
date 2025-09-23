#!/usr/bin/env python
"""
Comprehensive API Test Suite
Test all User system API endpoints
"""

import os
import sys
import django
import json
import uuid
import requests
import time
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from users.models import User, UserProfile, UserActivity, OTPCode
from agents.models import AgentProfile, AgentCustomer

User = get_user_model()


class APITestSuite:
    """Comprehensive API testing suite"""
    
    def __init__(self):
        self.base_url = 'http://localhost:8000'
        self.test_results = []
        self.test_users = {}
        self.test_tokens = {}
        
    def log_test_result(self, test_id, description, expected, actual, status, error=None):
        """Log test result"""
        result = {
            'test_id': test_id,
            'description': description,
            'expected': expected,
            'actual': actual,
            'status': status,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} Test {test_id}: {description}")
        if error:
            print(f"   Error: {error}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual}")
        print()
    
    def create_test_user(self, role='customer', **kwargs):
        """Create test user with profile"""
        user_data = {
            'username': f'test_{role}_{uuid.uuid4().hex[:8]}',
            'email': f'test_{role}_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'testpass123',
            'first_name': f'Test {role.title()}',
            'last_name': 'User',
            'role': role,
            'is_active': True,
            'is_email_verified': True,
            'is_phone_verified': True,
            **kwargs
        }
        
        user = User.objects.create_user(**user_data)
        # Create profile manually
        UserProfile.objects.create(user=user)
        self.test_users[role] = user
        return user
    
    def get_auth_headers(self, user):
        """Get authentication headers for user"""
        if user not in self.test_tokens:
            # Get JWT token by logging in
            login_data = {
                'username': user.username,
                'password': 'testpass123'
            }
            
            response = requests.post(f'{self.base_url}/api/users/login/', json=login_data)
            if response.status_code == 200:
                response_data = response.json()
                self.test_tokens[user] = response_data['tokens']['access']
            else:
                return {}
        
        return {'Authorization': f'Bearer {self.test_tokens[user]}'}
    
    def test_1_registration_endpoint(self):
        """Test 1: User Registration API"""
        try:
            registration_data = {
                'username': f'test_reg_{uuid.uuid4().hex[:8]}',
                'email': f'test_reg_{uuid.uuid4().hex[:8]}@example.com',
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'customer'
            }
            
            response = requests.post(f'{self.base_url}/api/users/register/', json=registration_data)
            
            assert response.status_code == 201
            response_data = response.json()
            assert 'user' in response_data
            assert response_data['user']['email'] == registration_data['email']
            assert response_data['user']['role'] == 'customer'
            assert response_data['email_verification_required'] == True
            
            self.log_test_result(
                '1', 'User Registration API',
                'User created with email verification required',
                f'Status: {response.status_code}, Email: {response_data["user"]["email"]}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '1', 'User Registration API',
                'User created with email verification required',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_2_login_endpoint(self):
        """Test 2: User Login API"""
        try:
            customer = self.test_users['customer']
            
            login_data = {
                'username': customer.username,
                'password': 'testpass123'
            }
            
            response = requests.post(f'{self.base_url}/api/users/login/', json=login_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert 'tokens' in response_data
            assert 'access' in response_data['tokens']
            assert 'refresh' in response_data['tokens']
            assert response_data['user']['email'] == customer.email
            
            self.log_test_result(
                '2', 'User Login API',
                'JWT tokens returned with user data',
                f'Status: {response.status_code}, Has tokens: {"tokens" in response_data}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '2', 'User Login API',
                'JWT tokens returned with user data',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_3_login_with_email(self):
        """Test 3: Login with Email API"""
        try:
            customer = self.test_users['customer']
            
            login_data = {
                'username': customer.email,  # Use email as username
                'password': 'testpass123'
            }
            
            response = requests.post(f'{self.base_url}/api/users/login/', json=login_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert 'tokens' in response_data
            assert response_data['user']['email'] == customer.email
            
            self.log_test_result(
                '3', 'Login with Email API',
                'JWT tokens returned with user data',
                f'Status: {response.status_code}, Has tokens: {"tokens" in response_data}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '3', 'Login with Email API',
                'JWT tokens returned with user data',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_4_agent_create_customer(self):
        """Test 4: Agent Create Customer API"""
        try:
            agent = self.test_users['agent']
            headers = self.get_auth_headers(agent)
            
            customer_data = {
                'name': 'Agent Customer',
                'email': f'agent_customer_{uuid.uuid4().hex[:8]}@example.com',
                'phone': '+1234567890',
                'first_name': 'Agent',
                'last_name': 'Customer',
                'address': 'Test Address',
                'city': 'Test City',
                'country': 'Test Country'
            }
            
            response = requests.post(f'{self.base_url}/api/agents/customers/', json=customer_data, headers=headers)
            
            assert response.status_code == 201
            response_data = response.json()
            assert 'customer' in response_data
            assert response_data['customer']['email'] == customer_data['email']
            assert response_data['customer']['role'] == 'customer'
            
            # Verify AgentCustomer relationship
            agent_customer = AgentCustomer.objects.filter(
                agent=agent,
                customer__email=customer_data['email']
            ).first()
            assert agent_customer is not None
            assert agent_customer.created_by_agent == True
            
            self.log_test_result(
                '4', 'Agent Create Customer API',
                'Customer created with AgentCustomer relationship',
                f'Status: {response.status_code}, Customer: {response_data["customer"]["email"]}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '4', 'Agent Create Customer API',
                'Customer created with AgentCustomer relationship',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_5_agent_list_customers(self):
        """Test 5: Agent List Customers API"""
        try:
            agent = self.test_users['agent']
            headers = self.get_auth_headers(agent)
            
            response = requests.get(f'{self.base_url}/api/agents/customers/', headers=headers)
            
            assert response.status_code == 200
            response_data = response.json()
            assert isinstance(response_data, list)
            
            # Verify all customers belong to this agent
            for customer_data in response_data:
                assert customer_data['created_by_agent'] == True
            
            self.log_test_result(
                '5', 'Agent List Customers API',
                'List of agent customers returned',
                f'Status: {response.status_code}, Count: {len(response_data)}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '5', 'Agent List Customers API',
                'List of agent customers returned',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_6_permission_control(self):
        """Test 6: Role-Based Access Control API"""
        try:
            customer = self.test_users['customer']
            agent = self.test_users['agent']
            admin = self.test_users['admin']
            
            # Test customer accessing agent endpoint
            customer_headers = self.get_auth_headers(customer)
            response = requests.get(f'{self.base_url}/api/agents/customers/', headers=customer_headers)
            assert response.status_code == 403
            
            # Test agent accessing admin endpoint
            agent_headers = self.get_auth_headers(agent)
            response = requests.get(f'{self.base_url}/api/users/admin/users/', headers=agent_headers)
            assert response.status_code == 403
            
            # Test admin accessing admin endpoint
            admin_headers = self.get_auth_headers(admin)
            response = requests.get(f'{self.base_url}/api/users/admin/users/', headers=admin_headers)
            assert response.status_code == 200
            
            self.log_test_result(
                '6', 'Role-Based Access Control API',
                'Users can only access resources appropriate to their role',
                f'Customer: 403, Agent: 403, Admin: 200',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '6', 'Role-Based Access Control API',
                'Users can only access resources appropriate to their role',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_7_password_change(self):
        """Test 7: Password Change API"""
        try:
            customer = self.test_users['customer']
            headers = self.get_auth_headers(customer)
            
            password_data = {
                'current_password': 'testpass123',
                'new_password': 'newpass123',
                'new_password_confirm': 'newpass123'
            }
            
            response = requests.post(f'{self.base_url}/api/users/change-password/', json=password_data, headers=headers)
            
            assert response.status_code == 200
            response_data = response.json()
            assert 'sessions_invalidated' in response_data
            
            # Verify password was changed
            customer.refresh_from_db()
            assert customer.check_password('newpass123')
            
            # Check if password change was logged
            password_activities = UserActivity.objects.filter(
                user=customer,
                activity_type='password_change'
            )
            assert password_activities.exists()
            
            self.log_test_result(
                '7', 'Password Change API',
                'Password changed with session invalidation and logging',
                f'Status: {response.status_code}, Sessions invalidated: {response_data["sessions_invalidated"]}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '7', 'Password Change API',
                'Password changed with session invalidation and logging',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_8_duplicate_email_registration(self):
        """Test 8: Duplicate Email Registration API"""
        try:
            existing_user = self.test_users['customer']
            
            registration_data = {
                'username': 'different_username',
                'email': existing_user.email,  # Same email
                'password': 'testpass123',
                'password_confirm': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'customer'
            }
            
            response = requests.post(f'{self.base_url}/api/users/register/', json=registration_data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert 'error' in response_data or 'message' in response_data
            
            self.log_test_result(
                '8', 'Duplicate Email Registration API',
                'Error message for duplicate email',
                f'Status: {response.status_code}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '8', 'Duplicate Email Registration API',
                'Error message for duplicate email',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_9_invalid_login_credentials(self):
        """Test 9: Invalid Login Credentials API"""
        try:
            login_data = {
                'username': 'nonexistent@example.com',
                'password': 'wrongpassword'
            }
            
            response = requests.post(f'{self.base_url}/api/users/login/', json=login_data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert 'non_field_errors' in response_data or 'message' in response_data
            
            # Check if failed login was logged
            failed_activities = UserActivity.objects.filter(
                activity_type='login_failed'
            )
            assert failed_activities.exists()
            
            self.log_test_result(
                '9', 'Invalid Login Credentials API',
                'Error message and failed attempt logged',
                f'Status: {response.status_code}, Failed activities: {failed_activities.count()}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '9', 'Invalid Login Credentials API',
                'Error message and failed attempt logged',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_10_admin_user_management(self):
        """Test 10: Admin User Management API"""
        try:
            admin = self.test_users['admin']
            headers = self.get_auth_headers(admin)
            
            # Test admin can list users
            response = requests.get(f'{self.base_url}/api/users/admin/users/', headers=headers)
            assert response.status_code == 200
            
            # Test admin can get user statistics
            response = requests.get(f'{self.base_url}/api/users/admin/stats/', headers=headers)
            assert response.status_code == 200
            response_data = response.json()
            assert 'total_users' in response_data
            assert 'active_users' in response_data
            
            # Test admin can get user activities
            response = requests.get(f'{self.base_url}/api/users/admin/activities/', headers=headers)
            assert response.status_code == 200
            
            self.log_test_result(
                '10', 'Admin User Management API',
                'Admin can access user management endpoints',
                f'Users: 200, Stats: 200, Activities: 200',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '10', 'Admin User Management API',
                'Admin can access user management endpoints',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 60)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Test server connectivity
        try:
            response = requests.get(f'{self.base_url}/api/health/', timeout=5)
            print(f"✅ Server is running (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Server is not accessible: {e}")
            print("Please start the server with: python manage.py runserver")
            return 0, 0
        
        # Define test methods
        test_methods = [
            ('1', self.test_1_registration_endpoint, 'User Registration API'),
            ('2', self.test_2_login_endpoint, 'User Login API'),
            ('3', self.test_3_login_with_email, 'Login with Email API'),
            ('4', self.test_4_agent_create_customer, 'Agent Create Customer API'),
            ('5', self.test_5_agent_list_customers, 'Agent List Customers API'),
            ('6', self.test_6_permission_control, 'Role-Based Access Control API'),
            ('7', self.test_7_password_change, 'Password Change API'),
            ('8', self.test_8_duplicate_email_registration, 'Duplicate Email Registration API'),
            ('9', self.test_9_invalid_login_credentials, 'Invalid Login Credentials API'),
            ('10', self.test_10_admin_user_management, 'Admin User Management API'),
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_id, test_method, description in test_methods:
            print(f"\n🔄 Running Test {test_id}: {description}")
            try:
                success = test_method()
                if success:
                    passed_tests += 1
                    print(f"✅ Test {test_id} PASSED")
                else:
                    print(f"❌ Test {test_id} FAILED")
            except Exception as e:
                print(f"❌ Test {test_id} FAILED with exception: {e}")
        
        # Generate final report
        self.generate_final_report(passed_tests, total_tests)
        
        return passed_tests, total_tests
    
    def generate_final_report(self, passed_tests, total_tests):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE API TEST REPORT")
        print("=" * 60)
        
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - Test {result['test_id']}: {result['description']}")
                    print(f"    Error: {result['error']}")
        
        print("\n📋 TEST SUMMARY BY CATEGORY:")
        categories = {
            'Authentication Flows': [1, 2, 3],
            'Agent-Customer Workflows': [4, 5],
            'Permission System': [6],
            'Security Features': [7],
            'Edge Cases': [8, 9],
            'Admin Features': [10]
        }
        
        for category, test_ids in categories.items():
            category_results = [r for r in self.test_results if int(r['test_id']) in test_ids]
            category_passed = len([r for r in category_results if r['status'] == 'PASS'])
            category_total = len(category_results)
            print(f"  {category}: {category_passed}/{category_total} ✅")
        
        # Save detailed results to file
        with open('api_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: api_test_results.json")
        
        # Final assessment
        if success_rate == 100:
            print("\n🎉 ALL API TESTS PASSED! User system APIs are working correctly.")
        elif success_rate >= 80:
            print("\n✅ Most API tests passed. Minor issues remain.")
        elif success_rate >= 60:
            print("\n⚠️ Some API tests passed. Significant issues need attention.")
        else:
            print("\n❌ Many API tests failed. Major issues need to be addressed.")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }


if __name__ == '__main__':
    # Clean up any existing test data
    User.objects.filter(username__startswith='test_').delete()
    
    # Run API test suite
    test_suite = APITestSuite()
    results = test_suite.run_all_tests()
    
    # Clean up test data
    User.objects.filter(username__startswith='test_').delete()
    AgentCustomer.objects.filter(customer__username__startswith='test_').delete()
    AgentProfile.objects.filter(user__username__startswith='test_').delete()
    UserActivity.objects.filter(user__username__startswith='test_').delete()
    OTPCode.objects.filter(user__username__startswith='test_').delete()
    
    print("\n🧹 Test data cleaned up")
