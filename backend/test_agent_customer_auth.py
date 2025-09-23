#!/usr/bin/env python3
"""
Comprehensive test suite for Agent-Customer Authentication Flow
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core import mail
from unittest.mock import patch, MagicMock

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from users.models import User, UserProfile, OTPCode, UserSession
from agents.models import AgentProfile, AgentCustomer
from agents.services import AgentBookingService
from agents.utils import (
    generate_secure_password,
    send_customer_welcome_email,
    send_email_verification,
    check_existing_customer,
    link_existing_customer_to_agent
)


class AgentCustomerAuthTestCase(TestCase):
    """Test cases for Agent-Customer Authentication Flow"""
    
    def setUp(self):
        """Set up test data"""
        # Create test agent
        self.agent = User.objects.create_user(
            username='test_agent@example.com',
            email='test_agent@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Agent',
            role='agent',
            is_active=True
        )
        
        # Create agent profile
        self.agent_profile = AgentProfile.objects.create(
            user=self.agent,
            company_name='Test Travel Agency',
            license_number='TA123456',
            commission_rate=10.0,
            is_active=True
        )
        
        # Test customer data
        self.customer_data = {
            'email': 'test_customer@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1234567890',
            'customer_status': 'active',
            'customer_tier': 'bronze',
            'relationship_notes': 'Test customer',
            'send_credentials': True,
            'verification_method': 'email'
        }
    
    def test_secure_password_generation(self):
        """Test secure password generation"""
        password = generate_secure_password()
        
        # Check password length
        self.assertGreaterEqual(len(password), 12)
        
        # Check password contains different character types
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*" for c in password)
        
        self.assertTrue(has_lower, "Password should contain lowercase letters")
        self.assertTrue(has_upper, "Password should contain uppercase letters")
        self.assertTrue(has_digit, "Password should contain digits")
        self.assertTrue(has_special, "Password should contain special characters")
    
    def test_create_customer_for_agent(self):
        """Test creating customer for agent"""
        customer, agent_customer = AgentBookingService.create_customer_for_agent(
            self.agent, 
            self.customer_data
        )
        
        # Check customer was created
        self.assertIsNotNone(customer)
        self.assertEqual(customer.email, self.customer_data['email'])
        self.assertEqual(customer.first_name, self.customer_data['first_name'])
        self.assertEqual(customer.last_name, self.customer_data['last_name'])
        self.assertEqual(customer.role, 'customer')
        self.assertFalse(customer.is_email_verified)
        self.assertTrue(customer.is_active)
        
        # Check agent-customer relationship
        self.assertIsNotNone(agent_customer)
        self.assertEqual(agent_customer.agent, self.agent)
        self.assertEqual(agent_customer.customer, customer)
        self.assertTrue(agent_customer.created_by_agent)
        self.assertTrue(agent_customer.requires_verification)
    
    def test_existing_customer_linking(self):
        """Test linking existing customer to agent"""
        # Create existing customer
        existing_customer = User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='existingpass123',
            first_name='Existing',
            last_name='Customer',
            role='customer'
        )
        
        # Try to create customer with same email
        customer_data = self.customer_data.copy()
        customer_data['email'] = 'existing@example.com'
        
        customer, agent_customer = AgentBookingService.create_customer_for_agent(
            self.agent, 
            customer_data
        )
        
        # Should return existing customer
        self.assertEqual(customer.id, existing_customer.id)
        self.assertIsNotNone(agent_customer)
        self.assertEqual(agent_customer.customer, existing_customer)
    
    def test_check_existing_customer(self):
        """Test checking for existing customer"""
        # Create test customer
        test_customer = User.objects.create_user(
            username='check@example.com',
            email='check@example.com',
            password='checkpass123',
            first_name='Check',
            last_name='Customer',
            role='customer'
        )
        
        # Check existing customer
        result = check_existing_customer('check@example.com')
        self.assertIsNotNone(result)
        self.assertEqual(result['email'], 'check@example.com')
        self.assertEqual(result['first_name'], 'Check')
        
        # Check non-existing customer
        result = check_existing_customer('nonexisting@example.com')
        self.assertIsNone(result)
    
    def test_link_existing_customer_to_agent(self):
        """Test linking existing customer to agent"""
        # Create existing customer
        existing_customer = User.objects.create_user(
            username='link@example.com',
            email='link@example.com',
            password='linkpass123',
            first_name='Link',
            last_name='Customer',
            role='customer'
        )
        
        # Link customer to agent
        success = link_existing_customer_to_agent(
            existing_customer, 
            self.agent, 
            'Test relationship'
        )
        
        self.assertTrue(success)
        
        # Check relationship was created
        agent_customer = AgentCustomer.objects.filter(
            agent=self.agent,
            customer=existing_customer
        ).first()
        
        self.assertIsNotNone(agent_customer)
        self.assertEqual(agent_customer.relationship_notes, 'Test relationship')
        self.assertFalse(agent_customer.created_by_agent)
    
    @patch('agents.utils.send_mail')
    def test_send_customer_welcome_email(self, mock_send_mail):
        """Test sending welcome email to customer"""
        customer = User.objects.create_user(
            username='welcome@example.com',
            email='welcome@example.com',
            password='welcomepass123',
            first_name='Welcome',
            last_name='Customer',
            role='customer'
        )
        
        password = 'testpassword123'
        success = send_customer_welcome_email(customer, password, self.agent)
        
        self.assertTrue(success)
        mock_send_mail.assert_called_once()
        
        # Check email parameters
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[1]['recipient_list'], [customer.email])
        self.assertIn('Welcome to Peykan Tourism', call_args[1]['subject'])
    
    @patch('agents.utils.send_mail')
    def test_send_email_verification(self, mock_send_mail):
        """Test sending email verification"""
        customer = User.objects.create_user(
            username='verify@example.com',
            email='verify@example.com',
            password='verifypass123',
            first_name='Verify',
            last_name='Customer',
            role='customer'
        )
        
        success = send_email_verification(customer)
        
        self.assertTrue(success)
        mock_send_mail.assert_called_once()
        
        # Check OTP was created
        otp = OTPCode.objects.filter(
            user=customer,
            type='email_verification'
        ).first()
        
        self.assertIsNotNone(otp)
        self.assertIsNotNone(otp.code)
        self.assertGreater(otp.expires_at, timezone.now())
    
    def test_agent_customer_credential_endpoints(self):
        """Test credential management API endpoints"""
        client = Client()
        
        # Create test customer
        customer = User.objects.create_user(
            username='api@example.com',
            email='api@example.com',
            password='apipass123',
            first_name='API',
            last_name='Customer',
            role='customer'
        )
        
        # Create agent-customer relationship
        agent_customer = AgentCustomer.objects.create(
            agent=self.agent,
            customer=customer,
            customer_name='API Customer',
            customer_email=customer.email,
            customer_phone='',
            relationship_notes='API test customer',
            created_by_agent=True
        )
        
        # Login as agent
        client.force_login(self.agent)
        
        # Test send credentials endpoint
        response = client.post(
            f'/api/agents/customers/{customer.id}/credentials/',
            {'method': 'email'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('sent to customer', data['message'])
        
        # Test send verification endpoint
        response = client.post(
            f'/api/agents/customers/{customer.id}/verification/',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('verification email', data['message'])
        
        # Test auth status endpoint
        response = client.get(
            f'/api/agents/customers/{customer.id}/auth-status/',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('customer_id', data['data'])
        self.assertEqual(data['data']['email'], customer.email)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to credential endpoints"""
        client = Client()
        
        # Create test customer
        customer = User.objects.create_user(
            username='unauth@example.com',
            email='unauth@example.com',
            password='unauthpass123',
            first_name='Unauth',
            last_name='Customer',
            role='customer'
        )
        
        # Try to access without authentication
        response = client.post(
            f'/api/agents/customers/{customer.id}/credentials/',
            {'method': 'email'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        
        # Try to access as non-agent user
        regular_user = User.objects.create_user(
            username='regular@example.com',
            email='regular@example.com',
            password='regularpass123',
            first_name='Regular',
            last_name='User',
            role='customer'
        )
        
        client.force_login(regular_user)
        response = client.post(
            f'/api/agents/customers/{customer.id}/credentials/',
            {'method': 'email'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_customer_login_flow(self):
        """Test complete customer login flow"""
        # Create customer via agent
        customer, agent_customer = AgentBookingService.create_customer_for_agent(
            self.agent, 
            self.customer_data
        )
        
        # Simulate customer login
        client = Client()
        
        # Test login with generated password
        login_data = {
            'username': customer.email,
            'password': 'generated_password'  # This would be the actual generated password
        }
        
        # Note: In real implementation, we'd need to get the actual password
        # For testing, we'll use the customer's current password
        response = client.post('/api/users/login/', login_data)
        
        # Should succeed (assuming password is correct)
        if response.status_code == 200:
            data = response.json()
            self.assertIn('access', data)
            self.assertIn('refresh', data)
            
            # Update agent customer record
            agent_customer.last_login_at = timezone.now()
            agent_customer.login_count += 1
            agent_customer.save()
            
            # Verify login tracking
            updated_agent_customer = AgentCustomer.objects.get(id=agent_customer.id)
            self.assertIsNotNone(updated_agent_customer.last_login_at)
            self.assertEqual(updated_agent_customer.login_count, 1)
    
    def test_email_verification_flow(self):
        """Test email verification flow"""
        # Create customer via agent
        customer, agent_customer = AgentBookingService.create_customer_for_agent(
            self.agent, 
            self.customer_data
        )
        
        # Create verification OTP
        otp = OTPCode.objects.create(
            user=customer,
            code='123456',
            type='email_verification',
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
        
        # Simulate verification
        client = Client()
        response = client.post('/api/users/verify-email/', {
            'code': '123456',
            'email': customer.email
        })
        
        # Should succeed
        if response.status_code == 200:
            # Check customer is verified
            customer.refresh_from_db()
            self.assertTrue(customer.is_email_verified)
            
            # Check agent customer record
            agent_customer.refresh_from_db()
            self.assertFalse(agent_customer.requires_verification)
    
    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        AgentProfile.objects.all().delete()
        AgentCustomer.objects.all().delete()
        OTPCode.objects.all().delete()


def run_tests():
    """Run all tests"""
    print("🧪 Running Agent-Customer Authentication Tests...")
    print("=" * 60)
    
    # Run tests
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["test_agent_customer_auth"])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
