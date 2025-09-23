#!/usr/bin/env python3
"""
Simple test for Agent-Customer Authentication functionality without Django test runner
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
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
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Create test agent
        agent_username = f'test_agent_{unique_id}@example.com'
        agent = User.objects.create_user(
            username=agent_username,
            email=agent_username,
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
        customer_email = f'test_customer_{unique_id}@example.com'
        customer_data = {
            'email': customer_email,
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


def test_database_tables():
    """Test if required database tables exist"""
    print("\n🗄️ Testing database tables...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        # Check if users_user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_user'")
        result = cursor.fetchone()
        
        if result:
            print("✅ users_user table exists")
        else:
            print("❌ users_user table does not exist")
            return False
        
        # Check if agents_agentcustomer table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents_agentcustomer'")
        result = cursor.fetchone()
        
        if result:
            print("✅ agents_agentcustomer table exists")
            
            # Check if new fields exist in the agents_agentcustomer table
            cursor.execute("PRAGMA table_info(agents_agentcustomer)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_fields = ['requires_verification', 'credentials_sent', 'credentials_sent_at', 'last_login_at', 'login_count']
            missing_fields = []
            
            for field in required_fields:
                if field in column_names:
                    print(f"✅ Field '{field}' exists in agents_agentcustomer table")
                else:
                    print(f"❌ Field '{field}' missing from agents_agentcustomer table")
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ All required fields exist in agents_agentcustomer table")
                return True
            else:
                print(f"❌ Missing fields: {missing_fields}")
                return False
        else:
            print("❌ agents_agentcustomer table does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Database test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running Simple Agent-Customer Authentication Tests...")
    print("=" * 60)
    
    tests = [
        test_password_generation,
        test_model_fields,
        test_database_tables,
        test_customer_creation,
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
