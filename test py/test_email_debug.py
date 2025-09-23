#!/usr/bin/env python
"""
Debug script for email service
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

from users.models import User
from users.domain.entities import OTPType
from users.infrastructure.repositories import DjangoOTPCodeRepository
from users.infrastructure.services import DjangoEmailVerificationService
from users.domain.services import DjangoOTPService

def debug_email_service():
    """Debug the email service"""
    
    print("🔍 Debugging Email Service...")
    print("=" * 50)
    
    # Get test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"✅ Found test user: {user.email}")
    except User.DoesNotExist:
        print("❌ Test user not found")
        return
    
    # Initialize services
    otp_repository = DjangoOTPCodeRepository()
    otp_service = DjangoOTPService(otp_repository)
    email_service = DjangoEmailVerificationService(otp_service)
    
    print(f"\n📧 Testing email service for user: {user.email}")
    
    try:
        # Test sending password reset email
        success = email_service.send_password_reset_email(
            user_id=user.id,
            email=user.email,
            user_name=f"{user.first_name} {user.last_name}"
        )
        
        print(f"Email service result: {success}")
        
        if success:
            print("✅ Email sent successfully")
        else:
            print("❌ Email failed to send")
            
    except Exception as e:
        print(f"❌ Error in email service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_email_service() 