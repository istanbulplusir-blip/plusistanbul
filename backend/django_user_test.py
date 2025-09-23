#!/usr/bin/env python
"""
Django Test Suite for User System
Proper Django testing with test database and settings
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django with test settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, UserProfile, UserActivity, OTPCode
from agents.models import AgentProfile, AgentCustomer

User = get_user_model()


class UserSystemTestCase(TestCase):
    """Django TestCase for User system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.test_users = {}
        
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
        refresh = RefreshToken.for_user(user)
        return {'Authorization': f'Bearer {str(refresh.access_token)}'}
    
    def test_1_user_model_creation(self):
        """Test 1: User Model Creation"""
        # Test customer creation
        customer = self.create_test_user('customer')
        self.assertEqual(customer.role, 'customer')
        self.assertTrue(customer.is_active)
        self.assertTrue(customer.is_email_verified)
        self.assertEqual(customer.preferred_language, 'fa')
        self.assertEqual(customer.preferred_currency, 'USD')
        
        # Test agent creation
        agent = self.create_test_user('agent')
        self.assertEqual(agent.role, 'agent')
        self.assertIsNotNone(agent.agent_code)
        self.assertTrue(agent.agent_code.startswith('AG'))
        
        # Test admin creation
        admin = self.create_test_user('admin')
        self.assertEqual(admin.role, 'admin')
        
        print("✅ Test 1: User Model Creation - PASSED")
    
    def test_2_user_profile_creation(self):
        """Test 2: UserProfile Creation"""
        customer = self.test_users['customer']
        profile = customer.profile
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, customer)
        self.assertEqual(profile.preferred_language, 'fa')
        self.assertEqual(profile.timezone, 'Asia/Tehran')
        
        print("✅ Test 2: UserProfile Creation - PASSED")
    
    def test_3_agent_profile_creation(self):
        """Test 3: AgentProfile Creation"""
        agent = self.test_users['agent']
        
        # Create AgentProfile manually
        agent_profile = AgentProfile.objects.create(
            user=agent,
            company_name='Test Travel Agency',
            commission_rate=Decimal('10.00')
        )
        
        self.assertEqual(agent_profile.user, agent)
        self.assertEqual(agent_profile.commission_rate, Decimal('10.00'))
        self.assertTrue(agent_profile.is_active)
        
        print("✅ Test 3: AgentProfile Creation - PASSED")
    
    def test_4_registration_endpoint(self):
        """Test 4: Direct Registration"""
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
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('user', response_data)
        self.assertEqual(response_data['user']['email'], registration_data['email'])
        self.assertEqual(response_data['user']['role'], 'customer')
        self.assertTrue(response_data['email_verification_required'])
        
        print("✅ Test 4: Direct Registration - PASSED")
    
    def test_5_login_endpoint(self):
        """Test 5: Login with Username"""
        customer = self.test_users['customer']
        
        login_data = {
            'username': customer.username,
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/users/login/', login_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('tokens', response_data)
        self.assertIn('access', response_data['tokens'])
        self.assertIn('refresh', response_data['tokens'])
        self.assertEqual(response_data['user']['email'], customer.email)
        
        print("✅ Test 5: Login with Username - PASSED")
    
    def test_6_login_with_email(self):
        """Test 6: Login with Email"""
        customer = self.test_users['customer']
        
        login_data = {
            'username': customer.email,  # Use email as username
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/users/login/', login_data)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('tokens', response_data)
        self.assertEqual(response_data['user']['email'], customer.email)
        
        print("✅ Test 6: Login with Email - PASSED")
    
    def test_7_agent_create_customer(self):
        """Test 7: Agent Create Customer"""
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
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn('customer', response_data)
        self.assertEqual(response_data['customer']['email'], customer_data['email'])
        self.assertEqual(response_data['customer']['role'], 'customer')
        
        # Verify AgentCustomer relationship
        agent_customer = AgentCustomer.objects.filter(
            agent=agent,
            customer__email=customer_data['email']
        ).first()
        self.assertIsNotNone(agent_customer)
        self.assertTrue(agent_customer.created_by_agent)
        
        print("✅ Test 7: Agent Create Customer - PASSED")
    
    def test_8_agent_list_customers(self):
        """Test 8: Agent List Customers"""
        agent = self.test_users['agent']
        headers = self.get_auth_headers(agent)
        
        response = self.client.get('/api/agents/customers/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        
        # Verify all customers belong to this agent
        for customer_data in response_data:
            self.assertTrue(customer_data['created_by_agent'])
        
        print("✅ Test 8: Agent List Customers - PASSED")
    
    def test_9_permission_control(self):
        """Test 9: Role-Based Access Control"""
        customer = self.test_users['customer']
        agent = self.test_users['agent']
        admin = self.test_users['admin']
        
        # Test customer accessing agent endpoint
        customer_headers = self.get_auth_headers(customer)
        response = self.client.get('/api/agents/customers/', headers=customer_headers)
        self.assertEqual(response.status_code, 403)
        
        # Test agent accessing admin endpoint
        agent_headers = self.get_auth_headers(agent)
        response = self.client.get('/api/users/admin/users/', headers=agent_headers)
        self.assertEqual(response.status_code, 403)
        
        # Test admin accessing admin endpoint
        admin_headers = self.get_auth_headers(admin)
        response = self.client.get('/api/users/admin/users/', headers=admin_headers)
        self.assertEqual(response.status_code, 200)
        
        print("✅ Test 9: Role-Based Access Control - PASSED")
    
    def test_10_activity_logging(self):
        """Test 10: Activity Logging"""
        customer = self.test_users['customer']
        
        # Check if login activity was logged
        login_activities = UserActivity.objects.filter(
            user=customer,
            activity_type='login'
        )
        
        self.assertTrue(login_activities.exists())
        
        # Check if API request activities are logged
        api_activities = UserActivity.objects.filter(
            user=customer,
            activity_type='api_request'
        )
        
        self.assertTrue(api_activities.exists())
        
        print("✅ Test 10: Activity Logging - PASSED")
    
    def test_11_duplicate_email_registration(self):
        """Test 11: Duplicate Email Registration"""
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
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertTrue('error' in response_data or 'message' in response_data)
        
        print("✅ Test 11: Duplicate Email Registration - PASSED")
    
    def test_12_invalid_login_credentials(self):
        """Test 12: Invalid Login Credentials"""
        login_data = {
            'username': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/users/login/', login_data)
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertTrue('non_field_errors' in response_data or 'message' in response_data)
        
        # Check if failed login was logged
        failed_activities = UserActivity.objects.filter(
            activity_type='login_failed'
        )
        self.assertTrue(failed_activities.exists())
        
        print("✅ Test 12: Invalid Login Credentials - PASSED")
    
    def test_13_password_change(self):
        """Test 13: Password Change"""
        customer = self.test_users['customer']
        headers = self.get_auth_headers(customer)
        
        password_data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post('/api/users/change-password/', password_data, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('sessions_invalidated', response_data)
        
        # Verify password was changed
        customer.refresh_from_db()
        self.assertTrue(customer.check_password('newpass123'))
        
        # Check if password change was logged
        password_activities = UserActivity.objects.filter(
            user=customer,
            activity_type='password_change'
        )
        self.assertTrue(password_activities.exists())
        
        print("✅ Test 13: Password Change - PASSED")
    
    def test_14_rate_limiting(self):
        """Test 14: Rate Limiting"""
        # Test login rate limiting
        login_data = {
            'username': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        # Make multiple failed login attempts
        for i in range(6):  # Should trigger rate limit after 5
            response = self.client.post('/api/users/login/', login_data)
        
        # The 6th attempt should be rate limited
        self.assertEqual(response.status_code, 429)
        
        print("✅ Test 14: Rate Limiting - PASSED")
    
    def test_15_admin_user_management(self):
        """Test 15: Admin User Management"""
        admin = self.test_users['admin']
        headers = self.get_auth_headers(admin)
        
        # Test admin can list users
        response = self.client.get('/api/users/admin/users/', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Test admin can get user statistics
        response = self.client.get('/api/users/admin/stats/', headers=headers)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('total_users', response_data)
        self.assertIn('active_users', response_data)
        
        # Test admin can get user activities
        response = self.client.get('/api/users/admin/activities/', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        print("✅ Test 15: Admin User Management - PASSED")


if __name__ == '__main__':
    import unittest
    
    # Run all tests
    unittest.main()
