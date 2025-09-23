#!/usr/bin/env python
"""
Test script for email system
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

from shared.services import (
    send_verification_email, 
    send_password_reset_email, 
    send_welcome_email
)

def test_email_system():
    """Test the email system"""
    
    test_email = "test@example.com"
    test_otp = "123456"
    test_name = "تست کاربر"
    
    print("🧪 Testing Email System...")
    print("=" * 50)
    
    # Test 1: Verification Email
    print("\n📧 Test 1: Sending Verification Email")
    print("-" * 30)
    success1 = send_verification_email(test_email, test_otp, test_name)
    print(f"✅ Verification email sent: {success1}")
    
    # Test 2: Password Reset Email
    print("\n🔐 Test 2: Sending Password Reset Email")
    print("-" * 30)
    success2 = send_password_reset_email(test_email, test_otp, test_name)
    print(f"✅ Password reset email sent: {success2}")
    
    # Test 3: Welcome Email
    print("\n🎉 Test 3: Sending Welcome Email")
    print("-" * 30)
    success3 = send_welcome_email(test_email, test_name)
    print(f"✅ Welcome email sent: {success3}")
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Verification Email: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Password Reset Email: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Welcome Email: {'✅ PASS' if success3 else '❌ FAIL'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 All email tests passed!")
    else:
        print("\n⚠️ Some email tests failed. Check your email configuration.")
    
    return all([success1, success2, success3])

if __name__ == "__main__":
    test_email_system() 