#!/usr/bin/env python
"""
Test script for forgot password functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

import requests
import json
from users.models import User

def create_test_user():
    """Create a test user if it doesn't exist"""
    try:
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                'is_email_verified': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Test user created successfully")
        else:
            print("✅ Test user already exists")
        return user
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def test_forgot_password():
    """Test the forgot password functionality"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Forgot Password System...")
    print("=" * 50)
    
    # Create test user
    print("\n👤 Creating test user...")
    user = create_test_user()
    if not user:
        print("❌ Cannot proceed without test user")
        return
    
    # Test 1: Forgot Password Request
    print("\n📧 Test 1: Forgot Password Request")
    print("-" * 30)
    
    forgot_data = {
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/forgot-password/",
            json=forgot_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Forgot password request successful")
        else:
            print("❌ Forgot password request failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Reset Password (if we have OTP)
    print("\n🔐 Test 2: Reset Password")
    print("-" * 30)
    
    reset_data = {
        "email": "test@example.com",
        "otp_code": "123456",  # This would be the actual OTP from email
        "new_password": "newpassword123",
        "new_password_confirm": "newpassword123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/reset-password/confirm/",
            json=reset_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Password reset successful")
        else:
            print("❌ Password reset failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("1. Forgot Password Request: ✅ Tested")
    print("2. Password Reset: ✅ Tested")
    print("\n💡 Note: Check your email for OTP codes!")

if __name__ == "__main__":
    test_forgot_password() 