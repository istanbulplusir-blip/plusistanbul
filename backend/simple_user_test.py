#!/usr/bin/env python
"""
Simplified User System Test Suite
Focus on core functionality testing
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, UserProfile, UserActivity, OTPCode
from agents.models import AgentProfile, AgentCustomer

User = get_user_model()


class SimpleUserSystemTest:
    """Simplified test suite for User system"""
    
    def __init__(self):
        self.client = APIClient()
        self.test_results = []
        self.test_users = {}
        
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
        """Create test user"""
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
        refresh = RefreshToken.for_user(user)
        return {'Authorization': f'Bearer {str(refresh.access_token)}'}
    
    def test_1_user_model_creation(self):
        """Test 1: User Model Creation"""
        try:
            # Test customer creation
            customer = self.create_test_user('customer')
            assert customer.role == 'customer'
            assert customer.is_active == True
            assert customer.is_email_verified == True
            assert customer.preferred_language == 'fa'
            assert customer.preferred_currency == 'USD'
            
            # Test agent creation
            agent = self.create_test_user('agent')
            assert agent.role == 'agent'
            assert agent.agent_code is not None
            assert agent.agent_code.startswith('AG')
            
            # Test admin creation
            admin = self.create_test_user('admin')
            assert admin.role == 'admin'
            
            self.log_test_result(
                '1', 'User Model Creation',
                'Users created with correct roles and defaults',
                f'Customer: {customer.role}, Agent: {agent.role}, Admin: {admin.role}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '1', 'User Model Creation',
                'Users created with correct roles and defaults',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_2_user_profile_creation(self):
        """Test 2: UserProfile Creation"""
        try:
            customer = self.test_users['customer']
            profile = customer.profile
            
            assert profile is not None
            assert profile.user == customer
            assert profile.preferred_language == 'fa'
            assert profile.timezone == 'Asia/Tehran'
            
            self.log_test_result(
                '2', 'UserProfile Creation',
                'Profile created automatically with User',
                f'Profile exists: {profile is not None}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '2', 'UserProfile Creation',
                'Profile created automatically with User',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_3_agent_profile_creation(self):
        """Test 3: AgentProfile Creation"""
        try:
            agent = self.test_users['agent']
            
            # Create AgentProfile manually
            agent_profile = AgentProfile.objects.create(
                user=agent,
                company_name='Test Travel Agency',
                commission_rate=Decimal('10.00')
            )
            
            assert agent_profile.user == agent
            assert agent_profile.commission_rate == Decimal('10.00')
            assert agent_profile.is_active == True
            
            self.log_test_result(
                '3', 'AgentProfile Creation',
                'AgentProfile linked to User with correct defaults',
                f'Profile created: {agent_profile.company_name}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '3', 'AgentProfile Creation',
                'AgentProfile linked to User with correct defaults',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_4_registration_endpoint(self):
        """Test 4: Direct Registration"""
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
            
            response = self.client.post('/api/users/register/', registration_data)
            
            assert response.status_code == 201
            response_data = response.json()
            assert 'user' in response_data
            assert response_data['user']['email'] == registration_data['email']
            assert response_data['user']['role'] == 'customer'
            assert response_data['email_verification_required'] == True
            
            self.log_test_result(
                '4', 'Direct Registration',
                'User created with email verification required',
                f'Status: {response.status_code}, Email: {response_data["user"]["email"]}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '4', 'Direct Registration',
                'User created with email verification required',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_5_login_endpoint(self):
        """Test 5: Login with Username"""
        try:
            customer = self.test_users['customer']
            
            login_data = {
                'username': customer.username,
                'password': 'testpass123'
            }
            
            response = self.client.post('/api/users/login/', login_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert 'tokens' in response_data
            assert 'access' in response_data['tokens']
            assert 'refresh' in response_data['tokens']
            assert response_data['user']['email'] == customer.email
            
            self.log_test_result(
                '5', 'Login with Username',
                'JWT tokens returned with user data',
                f'Status: {response.status_code}, Has tokens: {"tokens" in response_data}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '5', 'Login with Username',
                'JWT tokens returned with user data',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_6_login_with_email(self):
        """Test 6: Login with Email"""
        try:
            customer = self.test_users['customer']
            
            login_data = {
                'username': customer.email,  # Use email as username
                'password': 'testpass123'
            }
            
            response = self.client.post('/api/users/login/', login_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert 'tokens' in response_data
            assert response_data['user']['email'] == customer.email
            
            self.log_test_result(
                '6', 'Login with Email',
                'JWT tokens returned with user data',
                f'Status: {response.status_code}, Has tokens: {"tokens" in response_data}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '6', 'Login with Email',
                'JWT tokens returned with user data',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_7_agent_create_customer(self):
        """Test 7: Agent Create Customer"""
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
            
            response = self.client.post('/api/agents/customers/', customer_data, headers=headers)
            
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
                '7', 'Agent Create Customer',
                'Customer created with AgentCustomer relationship',
                f'Status: {response.status_code}, Customer: {response_data["customer"]["email"]}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '7', 'Agent Create Customer',
                'Customer created with AgentCustomer relationship',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_8_agent_list_customers(self):
        """Test 8: Agent List Customers"""
        try:
            agent = self.test_users['agent']
            headers = self.get_auth_headers(agent)
            
            response = self.client.get('/api/agents/customers/', headers=headers)
            
            assert response.status_code == 200
            response_data = response.json()
            assert isinstance(response_data, list)
            
            # Verify all customers belong to this agent
            for customer_data in response_data:
                assert customer_data['created_by_agent'] == True
            
            self.log_test_result(
                '8', 'Agent List Customers',
                'List of agent customers returned',
                f'Status: {response.status_code}, Count: {len(response_data)}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '8', 'Agent List Customers',
                'List of agent customers returned',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_9_permission_control(self):
        """Test 9: Role-Based Access Control"""
        try:
            customer = self.test_users['customer']
            agent = self.test_users['agent']
            admin = self.test_users['admin']
            
            # Test customer accessing agent endpoint
            customer_headers = self.get_auth_headers(customer)
            response = self.client.get('/api/agents/customers/', headers=customer_headers)
            assert response.status_code == 403
            
            # Test agent accessing admin endpoint
            agent_headers = self.get_auth_headers(agent)
            response = self.client.get('/api/users/admin/users/', headers=agent_headers)
            assert response.status_code == 403
            
            # Test admin accessing admin endpoint
            admin_headers = self.get_auth_headers(admin)
            response = self.client.get('/api/users/admin/users/', headers=admin_headers)
            assert response.status_code == 200
            
            self.log_test_result(
                '9', 'Role-Based Access Control',
                'Users can only access resources appropriate to their role',
                f'Customer: 403, Agent: 403, Admin: 200',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '9', 'Role-Based Access Control',
                'Users can only access resources appropriate to their role',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_10_activity_logging(self):
        """Test 10: Activity Logging"""
        try:
            customer = self.test_users['customer']
            
            # Check if login activity was logged
            login_activities = UserActivity.objects.filter(
                user=customer,
                activity_type='login'
            )
            
            assert login_activities.exists()
            
            # Check if API request activities are logged
            api_activities = UserActivity.objects.filter(
                user=customer,
                activity_type='api_request'
            )
            
            assert api_activities.exists()
            
            self.log_test_result(
                '10', 'Activity Logging',
                'User activities are logged',
                f'Login activities: {login_activities.count()}, API activities: {api_activities.count()}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '10', 'Activity Logging',
                'User activities are logged',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_11_duplicate_email_registration(self):
        """Test 11: Duplicate Email Registration"""
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
            
            response = self.client.post('/api/users/register/', registration_data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert 'error' in response_data or 'message' in response_data
            
            self.log_test_result(
                '11', 'Duplicate Email Registration',
                'Error message for duplicate email',
                f'Status: {response.status_code}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '11', 'Duplicate Email Registration',
                'Error message for duplicate email',
                str(e),
                'FAIL',
                str(e)
            )
    
    def test_12_invalid_login_credentials(self):
        """Test 12: Invalid Login Credentials"""
        try:
            login_data = {
                'username': 'nonexistent@example.com',
                'password': 'wrongpassword'
            }
            
            response = self.client.post('/api/users/login/', login_data)
            
            assert response.status_code == 400
            response_data = response.json()
            assert 'non_field_errors' in response_data or 'message' in response_data
            
            # Check if failed login was logged
            failed_activities = UserActivity.objects.filter(
                activity_type='login_failed'
            )
            assert failed_activities.exists()
            
            self.log_test_result(
                '12', 'Invalid Login Credentials',
                'Error message and failed attempt logged',
                f'Status: {response.status_code}, Failed activities: {failed_activities.count()}',
                'PASS'
            )
        except Exception as e:
            self.log_test_result(
                '12', 'Invalid Login Credentials',
                'Error message and failed attempt logged',
                str(e),
                'FAIL',
                str(e)
            )
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Simplified User System Test Suite")
        print("=" * 50)
        
        # Run all tests
        test_methods = [
            self.test_1_user_model_creation,
            self.test_2_user_profile_creation,
            self.test_3_agent_profile_creation,
            self.test_4_registration_endpoint,
            self.test_5_login_endpoint,
            self.test_6_login_with_email,
            self.test_7_agent_create_customer,
            self.test_8_agent_list_customers,
            self.test_9_permission_control,
            self.test_10_activity_logging,
            self.test_11_duplicate_email_registration,
            self.test_12_invalid_login_credentials,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 50)
        print("📊 FINAL TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - Test {result['test_id']}: {result['description']}")
                    print(f"    Error: {result['error']}")
        
        print("\n📋 TEST SUMMARY BY CATEGORY:")
        categories = {
            'Models & Relationships': [1, 2, 3],
            'Authentication Flows': [4, 5, 6],
            'Agent-Customer Workflows': [7, 8],
            'Permission System': [9],
            'Security Features': [10],
            'Edge Cases': [11, 12]
        }
        
        for category, test_ids in categories.items():
            category_results = [r for r in self.test_results if int(r['test_id']) in test_ids]
            category_passed = len([r for r in category_results if r['status'] == 'PASS'])
            category_total = len(category_results)
            print(f"  {category}: {category_passed}/{category_total} ✅")
        
        # Save detailed results to file
        with open('simple_user_system_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: simple_user_system_test_results.json")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'results': self.test_results
        }


if __name__ == '__main__':
    # Clean up any existing test data
    User.objects.filter(username__startswith='test_').delete()
    
    # Run test suite
    test_suite = SimpleUserSystemTest()
    results = test_suite.run_all_tests()
    
    # Clean up test data
    User.objects.filter(username__startswith='test_').delete()
    AgentCustomer.objects.filter(customer__username__startswith='test_').delete()
    AgentProfile.objects.filter(user__username__startswith='test_').delete()
    UserActivity.objects.filter(user__username__startswith='test_').delete()
    
    print("\n🧹 Test data cleaned up")
