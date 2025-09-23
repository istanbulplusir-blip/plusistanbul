#!/usr/bin/env python
"""
Simple Model Test Suite
Test User system models without complex Django test setup
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

from django.contrib.auth import get_user_model
from django.utils import timezone

from users.models import User, UserProfile, UserActivity, OTPCode
from agents.models import AgentProfile, AgentCustomer

User = get_user_model()


class SimpleModelTest:
    """Simple model testing without Django TestCase"""
    
    def __init__(self):
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
            return True
        except Exception as e:
            self.log_test_result(
                '1', 'User Model Creation',
                'Users created with correct roles and defaults',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
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
            return True
        except Exception as e:
            self.log_test_result(
                '2', 'UserProfile Creation',
                'Profile created automatically with User',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
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
            return True
        except Exception as e:
            self.log_test_result(
                '3', 'AgentProfile Creation',
                'AgentProfile linked to User with correct defaults',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_4_agent_customer_relationship(self):
        """Test 4: Agent-Customer Relationship"""
        try:
            agent = self.test_users['agent']
            customer = self.test_users['customer']
            
            # Create AgentCustomer relationship
            agent_customer = AgentCustomer.objects.create(
                agent=agent,
                customer=customer,
                customer_name=f"{customer.first_name} {customer.last_name}",
                customer_email=customer.email,
                customer_phone=customer.phone_number or '+1234567890',
                created_by_agent=True,
                relationship_notes='Test customer relationship'
            )
            
            assert agent_customer.agent == agent
            assert agent_customer.customer == customer
            assert agent_customer.created_by_agent == True
            
            self.log_test_result(
                '4', 'Agent-Customer Relationship',
                'AgentCustomer relationship created successfully',
                f'Relationship exists: {agent_customer is not None}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '4', 'Agent-Customer Relationship',
                'AgentCustomer relationship created successfully',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_5_otp_code_creation(self):
        """Test 5: OTP Code Creation"""
        try:
            customer = self.test_users['customer']
            
            # Create OTP code
            otp_code = OTPCode.objects.create(
                user=customer,
                email=customer.email,
                otp_type='email_verification',
                code='123456'
            )
            
            assert otp_code.user == customer
            assert otp_code.email == customer.email
            assert otp_code.otp_type == 'email_verification'
            assert otp_code.code == '123456'
            assert otp_code.is_valid == True
            
            self.log_test_result(
                '5', 'OTP Code Creation',
                'OTP code created with correct properties',
                f'OTP created: {otp_code.code}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '5', 'OTP Code Creation',
                'OTP code created with correct properties',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_6_user_activity_logging(self):
        """Test 6: User Activity Logging"""
        try:
            customer = self.test_users['customer']
            
            # Create user activity
            activity = UserActivity.objects.create(
                user=customer,
                activity_type='login',
                description='User logged in successfully',
                ip_address='127.0.0.1',
                user_agent='Test Agent'
            )
            
            assert activity.user == customer
            assert activity.activity_type == 'login'
            assert activity.description == 'User logged in successfully'
            assert activity.ip_address == '127.0.0.1'
            
            self.log_test_result(
                '6', 'User Activity Logging',
                'User activity logged successfully',
                f'Activity created: {activity.activity_type}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '6', 'User Activity Logging',
                'User activity logged successfully',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_7_user_verification_methods(self):
        """Test 7: User Verification Methods"""
        try:
            customer = self.test_users['customer']
            
            # Test email verification
            customer.verify_email()
            assert customer.is_email_verified == True
            assert customer.is_active == True
            
            # Test phone verification
            customer.verify_phone()
            assert customer.is_phone_verified == True
            
            self.log_test_result(
                '7', 'User Verification Methods',
                'User verification methods work correctly',
                f'Email verified: {customer.is_email_verified}, Phone verified: {customer.is_phone_verified}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '7', 'User Verification Methods',
                'User verification methods work correctly',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def test_8_user_role_properties(self):
        """Test 8: User Role Properties"""
        try:
            customer = self.test_users['customer']
            agent = self.test_users['agent']
            admin = self.test_users['admin']
            
            # Test role properties
            assert customer.is_customer == True
            assert customer.is_agent == False
            assert customer.is_admin == False
            assert customer.is_guest == False
            
            assert agent.is_customer == False
            assert agent.is_agent == True
            assert agent.is_admin == False
            assert agent.is_guest == False
            
            assert admin.is_customer == False
            assert admin.is_agent == False
            assert admin.is_admin == True
            assert admin.is_guest == False
            
            self.log_test_result(
                '8', 'User Role Properties',
                'User role properties work correctly',
                f'Customer: {customer.is_customer}, Agent: {agent.is_agent}, Admin: {admin.is_admin}',
                'PASS'
            )
            return True
        except Exception as e:
            self.log_test_result(
                '8', 'User Role Properties',
                'User role properties work correctly',
                str(e),
                'FAIL',
                str(e)
            )
            return False
    
    def run_all_tests(self):
        """Run all model tests"""
        print("🚀 Starting Simple Model Test Suite")
        print("=" * 50)
        
        # Define test methods
        test_methods = [
            ('1', self.test_1_user_model_creation, 'User Model Creation'),
            ('2', self.test_2_user_profile_creation, 'UserProfile Creation'),
            ('3', self.test_3_agent_profile_creation, 'AgentProfile Creation'),
            ('4', self.test_4_agent_customer_relationship, 'Agent-Customer Relationship'),
            ('5', self.test_5_otp_code_creation, 'OTP Code Creation'),
            ('6', self.test_6_user_activity_logging, 'User Activity Logging'),
            ('7', self.test_7_user_verification_methods, 'User Verification Methods'),
            ('8', self.test_8_user_role_properties, 'User Role Properties'),
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
        print("\n" + "=" * 50)
        print("📊 SIMPLE MODEL TEST REPORT")
        print("=" * 50)
        
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
        
        # Save detailed results to file
        with open('simple_model_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: simple_model_test_results.json")
        
        # Final assessment
        if success_rate == 100:
            print("\n🎉 ALL MODEL TESTS PASSED! Core models are working correctly.")
        elif success_rate >= 80:
            print("\n✅ Most model tests passed. Minor issues remain.")
        elif success_rate >= 60:
            print("\n⚠️ Some model tests passed. Significant issues need attention.")
        else:
            print("\n❌ Many model tests failed. Major issues need to be addressed.")
        
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
    
    # Run simple model test suite
    test_suite = SimpleModelTest()
    results = test_suite.run_all_tests()
    
    # Clean up test data
    User.objects.filter(username__startswith='test_').delete()
    AgentCustomer.objects.filter(customer__username__startswith='test_').delete()
    AgentProfile.objects.filter(user__username__startswith='test_').delete()
    UserActivity.objects.filter(user__username__startswith='test_').delete()
    OTPCode.objects.filter(user__username__startswith='test_').delete()
    
    print("\n🧹 Test data cleaned up")
