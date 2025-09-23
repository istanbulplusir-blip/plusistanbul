#!/usr/bin/env python3
"""
Simple test for Agent-Customer Authentication functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from users.models import User
from agents.models import AgentProfile, AgentCustomer
from agents.utils import generate_secure_password, check_existing_customer


def test_password_generation():
    """Test secure password generation"""
    print("🔐 Testing password generation...")
    
    password = generate_secure_password()
    print(f"Generated password: {password}")
    print(f"Password length: {len(password)}")
    
    # Check password contains different character types
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*" for c in password)
    
    print(f"Contains lowercase: {has_lower}")
    print(f"Contains uppercase: {has_upper}")
    print(f"Contains digits: {has_digit}")
    print(f"Contains special chars: {has_special}")
    
    if all([has_lower, has_upper, has_digit, has_special]):
        print("✅ Password generation test PASSED")
        return True
    else:
        print("❌ Password generation test FAILED")
        return False


def test_customer_creation():
    """Test customer creation flow"""
    print("\n👤 Testing customer creation...")
    
    try:
        # Create test agent
        agent = User.objects.create_user(
            username='test_agent@example.com',
            email='test_agent@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Agent',
            role='agent',
            is_active=True
        )
        print(f"Created agent: {agent.email}")
        
        # Create agent profile
        agent_profile = AgentProfile.objects.create(
            user=agent,
            company_name='Test Travel Agency',
            license_number='TA123456',
            commission_rate=10.0,
            is_active=True
        )
        print(f"Created agent profile: {agent_profile.company_name}")
        
        # Test customer data
        customer_data = {
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
        
        # Create customer
        customer = User.objects.create_user(
            username=customer_data['email'],
            email=customer_data['email'],
            password=generate_secure_password(),
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            phone_number=customer_data['phone'],
            role='customer',
            is_email_verified=False,
            is_active=True
        )
        print(f"Created customer: {customer.email}")
        
        # Create agent-customer relationship
        agent_customer = AgentCustomer.objects.create(
            agent=agent,
            customer=customer,
            customer_name=f"{customer.first_name} {customer.last_name}",
            customer_email=customer.email,
            customer_phone=customer.phone_number or '',
            relationship_notes=customer_data['relationship_notes'],
            created_by_agent=True,
            requires_verification=True,
            credentials_sent=False
        )
        print(f"Created agent-customer relationship: {agent_customer.id}")
        
        # Test existing customer check
        existing = check_existing_customer(customer_data['email'])
        if existing:
            print(f"Found existing customer: {existing['email']}")
        
        print("✅ Customer creation test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Customer creation test FAILED: {e}")
        return False


def test_model_fields():
    """Test new model fields"""
    print("\n📊 Testing model fields...")
    
    try:
        # Check if AgentCustomer has new fields
        agent_customer = AgentCustomer()
        
        # Check new fields exist
        fields_to_check = [
            'requires_verification',
            'credentials_sent',
            'credentials_sent_at',
            'last_login_at',
            'login_count'
        ]
        
        for field in fields_to_check:
            if hasattr(agent_customer, field):
                print(f"✅ Field '{field}' exists")
            else:
                print(f"❌ Field '{field}' missing")
                return False
        
        print("✅ Model fields test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Model fields test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running Simple Agent-Customer Authentication Tests...")
    print("=" * 60)
    
    tests = [
        test_password_generation,
        test_customer_creation,
        test_model_fields
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! Implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests FAILED. Please check the implementation.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
